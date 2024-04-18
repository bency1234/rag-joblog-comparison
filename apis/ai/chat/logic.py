import json
import re
import openai
from ai.chat.utils import pairwise
from ai.common.utils.cost import get_cost
from ai.common.utils.debug import debug_steps, time_it
from ai.llms.constants import (
    SEARCH_KWARGS,
    SEARCH_TYPE,
    SYSTEM_INPUT_COST,
    SYSTEM_MODEL,
    SYSTEM_OUTPUT_COST,
    TOKENS,
    TURBO_16k,
    TURBO_16k_COST,
    TEMPERATURE,
    MAX_RETRIES,
)
from langchain.chat_models import ChatOpenAI
from ai.prompts.system_prompt import PROMPT
from ai.chat.token import get_tokens
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema import AIMessage, HumanMessage
from langchain.memory import ConversationBufferWindowMemory
from .stream_handler import AWSStreamHandler
from common.envs import logger

class GenerateResponse:
    def __init__(self, row, vector_store):
        self.row = row
        self.vector_store = vector_store

    # def generate_raw_prompt(self, system_template, human_template, message_log):
    #     return (
    #         system_template
    #         + "Human prompt"
    #         + human_template
    #         + "Message_log"
    #         + json.dumps(message_log)
    #     )
    
    @time_it
    def chat_completion(self, user_input, message_log, client_id, connection_id):
        print("user input........................", user_input)
        MODEL = TURBO_16k
        system_template = (
            PROMPT(user_input)
            + """
        Human: {question}
        chat_history: {chat_history}
        Bot: {summaries}
        ----------------
        """
        )
        print("system template....................", system_template)
        #logger.info("SYSTEM TEMPLATE", system_template)
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
            raw_messages.append(human)
            raw_messages.append(ai)
        messages.append(HumanMessagePromptTemplate.from_template("{question}"))

        prompt = ChatPromptTemplate.from_messages(messages)
        chain_type_kwargs = {"prompt": prompt}
        llm = ChatOpenAI(
            model_name=MODEL,
            temperature=TEMPERATURE,
            max_retries=MAX_RETRIES,
            max_tokens=TOKENS,
            openai_api_key=openai.api_key,
            streaming=True,
        ) #.configure_model(
             #callbacks=[AWSStreamHandler(client_id, connection_id)], streaming=True)
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
        #debug_attribute("source documents", chain.source_documents)
        chain_response = chain(user_input)
        #logger.info("COMPLETE RESPONSE", chain_response)
        print("COMPLETE RESPONSE-->", chain_response)
        response = chain_response["answer"].strip()
        source_documents = chain_response["source_documents"]
        #logger.info("Source Documents", source_documents)

        raw_prompt = ""
        total_cost = ""
        return raw_prompt, response, source_documents, total_cost

    # @time_it
    # def chat_completion(self, user_input, message_log, client_id, connection_id):
    #     human_template = "{question}"

    #     system_template = PROMPT(user_input)

    #     messages = [
    #         SystemMessagePromptTemplate.from_template(system_template),
    #     ]

    #     for human, ai in pairwise(message_log):
    #         messages.append(HumanMessage(content=human))
    #         messages.append(AIMessage(content=ai))

    #     messages.append(HumanMessagePromptTemplate.from_template(human_template))
    #     prompt = ChatPromptTemplate.from_messages(messages)
    #     chain_type_kwargs = {"prompt": prompt}

    #     llm = ChatOpenAILLMProvider(
    #         model_name=SYSTEM_MODEL,
    #         max_tokens=TOKENS,
    #     ).configure_model(
    #         callbacks=[AWSStreamHandler(client_id, connection_id)], streaming=True
    #     )

    #     chain = RetrievalQAWithSourcesChain.from_chain_type(
    #         llm=llm,
    #         chain_type="stuff",
    #         retriever=self.vector_store.as_retriever(
    #             search_type=SEARCH_TYPE, search_kwargs=SEARCH_KWARGS
    #         ),
    #         chain_type_kwargs=chain_type_kwargs,
    #         return_source_documents=True,
    #     )

    #     chain_response = chain(user_input)
    #     response = chain_response["answer"]
    #     source_documents = chain_response["source_documents"]

    #     raw_prompt = self.generate_raw_prompt(
    #         system_template, human_template, json.dumps(message_log, indent=2)
    #     )

    #     total_cost = get_cost(
    #         SYSTEM_MODEL,
    #         SYSTEM_INPUT_COST,
    #         SYSTEM_OUTPUT_COST,
    #         system_template,
    #         human_template,
    #         user_input,
    #         response,
    #         source_documents=source_documents,
    #         message_log=message_log,
    #     )

    #     return raw_prompt, response, source_documents, total_cost

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
