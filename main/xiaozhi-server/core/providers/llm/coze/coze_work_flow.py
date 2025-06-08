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

    def response2(self, input_txt_path, output_txt_path=None):
        """
        处理连续录音生成的文本文件，并将结果保存到新的文本文件
        
        Args:
            input_txt_path (str): 输入文本文件路径
            output_txt_path (str): 输出文本文件路径，如果不指定则在输入文件同目录下创建 response_结果.txt
            
        Returns:
            str: 输出文件路径
        """
        try:
            # 读取文本文件内容
            with open(input_txt_path, 'r', encoding='utf-8') as f:
                text_content = f.read().strip()
                
            if not text_content:
                logger.bind(tag=TAG).error("输入文件内容为空")
                return None
                
            # 如果没有指定输出文件路径，则在输入文件同目录下创建
            if output_txt_path is None:
                input_dir = os.path.dirname(input_txt_path)
                input_filename = os.path.basename(input_txt_path)
                output_txt_path = os.path.join(input_dir, f"response_{input_filename}")
                
            # 获取 Coze 客户端
            coze_api_token = self.personal_access_token
            coze_api_base = COZE_CN_BASE_URL
            coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)
            
            # 使用工作流处理文本
            workflow_id = self.workflow_id
            
            # 打开输出文件，准备写入结果
            with open(output_txt_path, 'w', encoding='utf-8') as out_file:
                # 使用 bot_id 方式
                for event in coze.workflows.runs.stream(
                    workflow_id=workflow_id,
                    bot_id=self.bot_id,
                    parameters={"USER_INPUT": text_content}
                ):
                    if event.event == WorkflowEventType.MESSAGE:
                        # 将结果写入文件
                        out_file.write(event.message.content)
                        out_file.flush()  # 确保内容立即写入文件
                    else:
                        logger.bind(tag=TAG).error(f"处理文本时出现错误: {event.error}")
                        return None
                        
            return output_txt_path
                        
        except FileNotFoundError:
            logger.bind(tag=TAG).error(f"找不到文件：{input_txt_path}")
            return None
        except Exception as e:
            logger.bind(tag=TAG).error(f"处理文本时发生错误：{str(e)}")
            return None


