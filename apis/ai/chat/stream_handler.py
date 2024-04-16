from ai.common.utils.stream import construct_bot_response, stream_response
from common.envs import logger
from langchain.callbacks.base import BaseCallbackHandler


class OpenAIStreamHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
        self.sources = ""
        self.stop_streaming = False

    def on_llm_new_token(self, token, **kwargs):
        """
        Run on new LLM token. Only available when streaming is enabled.
        Args:
            token: The new LLM token.
            **kwargs: Additional keyword arguments.
        Returns:
            None
        """
        token = token.replace("\n", "\n\n ")
        self.text += token
        if "Sources" in self.text:
            self.stop_streaming = True
            self.sources += token
        else:
            stream_response(construct_bot_response(token))

    def on_llm_end(self, response, **kwargs):
        """Run when LLM ends running."""
        # TODO: Enable sources once we get appropriate response from OpenAI
        # self.sources = self.sources.replace("Sources:","\n\n**Sources:**")
        # if ".pdf" not in self.sources and "https" in self.sources:
        #     stream_response(construct_bot_response(self.sources))

    def on_chain_end(self, outputs, **kwargs):
        """Run when chain ends running."""
        logger.info("Done chain %s", outputs)


class AWSStreamHandler(BaseCallbackHandler):
    def __init__(self, client=None, connection_id=None):
        self.client = client
        self.connection_id = connection_id
        self.text = ""
        self.sources = ""
        self.stop_streaming = False

    def on_llm_new_token(self, token, **kwargs):
        """
        Run on new LLM token. Only available when streaming is enabled.
        Args:
            token: The new LLM token.
            **kwargs: Additional keyword arguments.
        Returns:
            None
        """
        token = token.replace("Claude,", "")
        token = token.replace("\n", "\n\n ")
        self.text += token

        if self.client:
            stream_response(
                construct_bot_response(token), self.client, self.connection_id
            )
        else:
            stream_response(construct_bot_response(token))

    def on_chain_end(self, outputs, **kwargs):
        """Run when chain ends running."""
        logger.info("Done chain %s", outputs)
