from config.logger import setup_logging
import requests
import json
import re
from core.providers.llm.base import LLMProviderBase
import os
# official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
from cozepy import COZE_CN_BASE_URL
from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa

TAG = __name__
logger = setup_logging()


class LLMProvider(LLMProviderBase):
    def __init__(self, config, workflow_id=None):
        self.personal_access_token = config.get("personal_access_token")
        self.bot_id = config.get("bot_id")
        self.user_id = config.get("user_id")
        self.workflow_id = config.get("workflow_id") if workflow_id is None else workflow_id
        self.session_conversation_map = {}  # 存储session_id和conversation_id的映射

    def response(self, dialogue):
        """
        This example describes how to use the workflow interface to stream chat.
        """

        # Get an access_token through personal access token or oauth.
        coze_api_token = self.personal_access_token
        # The default access is api.coze.com, but if you need to access api.coze.cn,
        # please use base_url to configure the api endpoint to access
        coze_api_base = COZE_CN_BASE_URL

        from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa

        # Init the Coze client through the access_token.
        coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

        # Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
        workflow_id = self.workflow_id
        bot_id = self.bot_id

        # The stream interface will return an iterator of WorkflowEvent. Developers should iterate
        # through this iterator to obtain WorkflowEvent and handle them separately according to
        # the type of WorkflowEvent.
        # def handle_workflow_iterator(stream: Stream[WorkflowEvent]):
        #     for event in stream:
        #         if event.event == WorkflowEventType.MESSAGE:
        #             print("got message", event.message)
        #             yield event.message.content
        #         elif event.event == WorkflowEventType.ERROR:
        #             print("got error", event.error)
        #         elif event.event == WorkflowEventType.INTERRUPT:
        #             handle_workflow_iterator(
        #                 coze.workflows.runs.resume(
        #                     workflow_id=workflow_id,
        #                     event_id=event.interrupt.interrupt_data.event_id,
        #                     resume_data="hey",
        #                     interrupt_type=event.interrupt.interrupt_data.type,
        #                 )
        #             )
        # handle_workflow_iterator(
        #     coze.workflows.runs.stream(
        #         workflow_id=workflow_id,
        #         bot_id=bot_id,
        #         parameters={"USER_INPUT": dialogue[-1]["content"]},
        #     )
        # )
        last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
        for event in coze.workflows.runs.stream(
                workflow_id=workflow_id,
                bot_id=bot_id,
                parameters={"USER_INPUT": last_msg["content"]},
            ):
            if event.event == WorkflowEventType.MESSAGE:
                print(event.message.content, end="", flush=True)
                yield event.message.content, None
            else:
                yield "不好意思没听明白，请再说一次", None
                break
