from ai.common.utils.stream import construct_bot_response, stream_response
from common.app_utils import get_app
from common.chatbot import UserFiles
from common.db import db
from common.envs import logger
from langchain.callbacks.base import BaseCallbackHandler

app = get_app(db)


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
    with app.app_context():

        def __init__(self, client=None, connection_id=None):
            self.client = client
            self.connection_id = connection_id
            self.text = ""
            self.sources = ""
            self.stop_streaming = False
            self.is_streaming = False
            self.streamed_content = ""
            self.seen_s3_urls = set()
            self.count = 0
            self.is_citations = "YES"  # Assuming this flag is set elsewhere
            self.is_citations_printed = False
            self.response = ""

        def on_llm_new_token(self, token, **kwargs):
            self.response += token
            response_has_props = False
            if "Sources" in token:
                self.is_streaming = True
            if self.is_streaming:
                self.streamed_content += token
                if ")" in token:
                    self._process_streamed_content()
            else:
                if self.response.strip().startswith("Content"):
                    response_has_props = True
                    if "Content: " in self.response:
                        self._stream_response(token, self.client, self.connection_id)
                elif not response_has_props:
                    self._stream_response(token, self.client, self.connection_id)

        def _process_streamed_content(self):
            start_index = self.streamed_content.find("[")
            end_index = self.streamed_content.find("]")
            file_name = self.streamed_content[start_index + 1 : end_index]
            if file_name.startswith("./"):
                file_name = file_name[2:]
            if file_name:
                self._process_file_name(file_name)

        def _process_file_name(self, file_name):
            file_na = f"%{file_name[:30]}%"
            user_file = UserFiles.query.filter(
                UserFiles.file_name.like(file_na)
            ).first()
            logger.info(f"user_file...{user_file}")
            if self.is_citations == "YES" and not self.is_citations_printed:
                self.is_citations_printed = True
                stream_response(
                    construct_bot_response("Citations:**  \n\n"),
                    self.client,
                    self.connection_id,
                )
            if user_file and file_name not in self.seen_s3_urls:
                self._process_user_file(user_file, file_name)
            else:
                stream_response(
                    construct_bot_response("No Source available"),
                    self.client,
                    self.connection_id,
                )

        def _process_user_file(self, user_file, file_name):
            s3_url = user_file.s3_url
            logger.info(f"File Name: {file_name}")
            self.seen_s3_urls.add(file_name)
            self.streamed_content = ""
            self.count += 1
            up_s3_url = s3_url.replace(" ", "+")
            up_file_name = file_name.split("_", 1)[1].rsplit(".", 1)[0]
            pdf_link = f"[{up_file_name}]({up_s3_url})"
            markdown_pdf_link = f"{self.count}. {pdf_link}"
            stream_response(
                construct_bot_response(f"{markdown_pdf_link} \n"),
                self.client,
                self.connection_id,
            )

        def _stream_response(self, token, client, connection_id):
            stream_response(
                construct_bot_response(token), self.client, self.connection_id
            )
