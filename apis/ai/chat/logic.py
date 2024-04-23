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
from ai.prompts.system_prompt import PROMPT
from common.envs import logger
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage

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
    def chat_completion(self, user_input, message_log, client_id, connection_id):
        logger.info(f"user input......{user_input}")
        system_template = (
            PROMPT(user_input)
            + """
        Human: {question}
        chat_history: {chat_history}
        Bot: {summaries}
        ----------------
        """
        )
        logger.info(f"system template...........{system_template}")
        messages = [
            SystemMessagePromptTemplate.from_template(system_template),
        ]
        raw_messages = []
        window_memory = ConversationBufferWindowMemory(
            memory_key="chat_history", k=2, output_key="answer", input_key="question"
        )
        for human, ai in pairwise(message_log):
            window_memory.chat_memory.add_user_message(human)
            window_memory.chat_memory.add_ai_message(ai)
            raw_messages.append(HumanMessage(human))
            raw_messages.append(AIMessage(ai))
        messages.append(HumanMessagePromptTemplate.from_template("{question}"))

        prompt = ChatPromptTemplate.from_messages(messages)
        chain_type_kwargs = {"prompt": prompt}

        llm = ChatOpenAILLMProvider(
            model_name=SYSTEM_MODEL,
            max_tokens=TOKENS,
        ).configure_model(
            callbacks=[AWSStreamHandler(client_id, connection_id)], streaming=True
        )

        chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_type=SEARCH_TYPE, search_kwargs=SEARCH_KWARGS
            ),
            chain_type_kwargs=chain_type_kwargs,
            return_source_documents=True,
            memory=window_memory,
        )
        chain_response = chain(user_input)
        logger.info(f"COMPLETE RESPONSE {chain_response}")
        response = chain_response["answer"].strip()
        source_documents = chain_response["source_documents"]
        logger.info(f"Source Documents {source_documents}")

        raw_prompt = self.generate_raw_prompt(
            system_template, json.dumps(message_log, indent=2)
        )
        logger.info(f"raw prompt.........{raw_prompt}")

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

    def main(self, user_input, message_log, client_id, connection_id):
        valid_query = True
        bot_response = ""
        raw_prompt, bot_response, source_documents, total_cost = self.chat_completion(
            user_input, message_log, client_id, connection_id
        )
        pattern = r"(sorry)"
        if "utm_medium=referral" in bot_response.lower() or re.search(
            pattern, bot_response.lower()
        ):
            valid_query = False
        return valid_query, raw_prompt, bot_response, source_documents, total_cost
