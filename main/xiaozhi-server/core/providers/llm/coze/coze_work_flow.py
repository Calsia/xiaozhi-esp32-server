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
    def __init__(self, config, workflow_id=None, use_app=False):
        self.personal_access_token = config.get("personal_access_token")
        self.bot_id = config.get("bot_id")
        self.user_id = config.get("user_id")
        self.app_id = config.get("app_id")
        self.workflow_id = config.get("workflow_id") if workflow_id is None else workflow_id
        self.session_conversation_map = {}  # 存储session_id和conversation_id的映射
        self.use_app = use_app
    def response(self, session_id, dialogue):
        """
        This example describes how to use the workflow interface to stream chat.
        """

        # Get an access_token through personal access token or oauth.
        coze_api_token = self.personal_access_token
        # The default access is api.coze.com, but if you need to access api.coze.cn,
        # please use base_url to configure the api endpoint to access
        coze_api_base = COZE_CN_BASE_URL

        # Init the Coze client through the access_token.
        coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

        # Create a workflow instance in Coze, copy the last number from the web link as the workflow's ID.
        workflow_id = self.workflow_id
        bot_id = self.bot_id
        app_id = self.app_id

        if self.use_app:
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user")
            for event in coze.workflows.runs.stream(
                    workflow_id=workflow_id,
                    app_id=app_id,
                    parameters={"USER_INPUT": last_msg["content"]},
            ):
                if event.event == WorkflowEventType.MESSAGE:
                    # print(event.message.content, end="", flush=True)
                    yield event.message.content, None
                else:
                    yield "不好意思没听明白，请再说一次", None
                    break
        else:
            last_msg = next(m for m in reversed(dialogue) if m["role"] == "user") if dialogue != "1" else dialogue
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
