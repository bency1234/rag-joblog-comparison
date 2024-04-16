from ai.llms.llm import LLMProvider
from langchain_openai import ChatOpenAI

from .constants import OPENAI_API_KEY


class ChatOpenAILLMProvider(LLMProvider):
    def __init__(self, model_name, max_tokens, openai_api_key=OPENAI_API_KEY):
        super().__init__()  # Initialize the base class
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        self.max_tokens = max_tokens

    def configure_model(self, streaming=False, callbacks=None):
        return ChatOpenAI(
            model_name=self.model_name,
            temperature=self.temperature,
            openai_api_key=self.openai_api_key,
            max_tokens=self.max_tokens,
            max_retries=self.max_retries,
            streaming=streaming,
            callbacks=callbacks,
        )
