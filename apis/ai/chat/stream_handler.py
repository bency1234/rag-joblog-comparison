from ai.common.utils.stream import construct_bot_response, stream_response
from common.envs import logger
from langchain.callbacks.base import BaseCallbackHandler


class AWSStreamHandler(BaseCallbackHandler):
    def __init__(self, client=None, connection_id=None):
        self.client = client
        self.connection_id = connection_id
        self.text = ""

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
