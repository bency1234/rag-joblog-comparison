import json
import re

from ai.chat.utils import pairwise
from ai.common.utils.cost import get_cost
from ai.common.utils.debug import time_it
from ai.llms.constants import (
    SEARCH_KWARGS,
    SEARCH_TYPE,
    SYSTEM_INPUT_COST,
    SYSTEM_MODEL,
    SYSTEM_OUTPUT_COST,
    TOKENS,
)
from ai.llms.openaillm import ChatOpenAILLMProvider
from ai.prompts.system_prompt import TOGGLE_OFF_SYSTEM_PROMPT, TOGGLE_ON_SYSTEM_PROMPT
from common.envs import logger
from langchain import LLMChain
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from .stream_handler import AWSStreamHandler


class GenerateResponse:
    def __init__(self, row, vector_store):
        self.row = row
        self.vector_store = vector_store

    def generate_raw_prompt(self, system_template, message_log):
        return (
            system_template + "Human prompt" + "Message_log" + json.dumps(message_log)
        )

    @time_it
    def chat_completion(
        self,
        user_input: str,
        message_log: list,
        client_id: None,
        connection_id: None,
        use_rag: bool,
    ):
        logger.info(f"User input: {user_input}, Toggle: {use_rag}")
        human_template = "{question}"
        system_template = (
            TOGGLE_ON_SYSTEM_PROMPT if use_rag == True else TOGGLE_OFF_SYSTEM_PROMPT
        )
        messages = [
            SystemMessagePromptTemplate.from_template(system_template)
            if use_rag == True
            else SystemMessage(content=system_template)
        ]
        logger.info(f"human_template: {human_template}, messages: {messages}")

        for human, ai in pairwise(message_log):
            messages.append(HumanMessage(content=human))
            messages.append(AIMessage(content=ai))

        messages.append(HumanMessagePromptTemplate.from_template(human_template))
        prompt = ChatPromptTemplate.from_messages(messages)

        llm = ChatOpenAILLMProvider(
            model_name=SYSTEM_MODEL,
            max_tokens=TOKENS,
        ).configure_model(
            callbacks=[AWSStreamHandler(client_id, connection_id)], streaming=True
        )
        if use_rag == True:
            chain_type_kwargs = {"prompt": prompt}
            chain = RetrievalQAWithSourcesChain.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=self.vector_store.as_retriever(
                    search_type=SEARCH_TYPE, search_kwargs=SEARCH_KWARGS
                ),
                chain_type_kwargs=chain_type_kwargs,
                return_source_documents=True,
            )
            chain_response = chain(user_input)
            response = chain_response["answer"].strip()
            source_documents = chain_response["source_documents"]
        else:
            chain = LLMChain(llm=llm, prompt=prompt)
            chain_response = chain({"question": user_input})
            logger.info(f"COMPLETE RESPONSE {chain_response}")
            response = chain_response["text"]
            logger.info(f"response........{response}")
            source_documents = []

        logger.info(
            f"Complete response: {chain_response}, Response: {response}, Source Documents: {source_documents}"
        )
        raw_prompt = self.generate_raw_prompt(
            system_template, json.dumps(message_log, indent=2)
        )

        total_cost = get_cost(
            SYSTEM_MODEL,
            SYSTEM_INPUT_COST,
            SYSTEM_OUTPUT_COST,
            system_template,
            user_input,
            response,
            source_documents=source_documents,
            message_log=message_log,
        )
        return raw_prompt, response, source_documents, total_cost

    def main(
        self,
        user_input: str,
        message_log: list,
        client_id: None,
        connection_id: None,
        use_rag: bool,
    ):
        bot_response = ""
        raw_prompt, bot_response, source_documents, total_cost = self.chat_completion(
            user_input, message_log, client_id, connection_id, use_rag
        )
        valid_query = not re.search(r"(sorry)", bot_response.lower())
        logger.info(f"Valid query: {valid_query}")
        return valid_query, raw_prompt, bot_response, source_documents, total_cost
