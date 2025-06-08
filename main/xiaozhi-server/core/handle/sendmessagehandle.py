import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import uuid
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()


def sendmessage2feishuhandle(conn, file_path):
    """
    从文本文件读取内容并发送到飞书
    
    Args:
        file_path (str): 文本文件路径
    """
    app_id = "cli_a8cfbe7fe43ed00c"
    app_secret = "722kwQW8ybwWD8eI2awoudC6bxxGZ0Gh"
    send_config = {
        "target_type": "text",
        "target_info": "chat_id",  # open_id
        "target_id": "oc_c6452f49a47ddbcef48cdc4d8821a769" # "ou_08595b3daa216d51d45dbbaad7a56538"
    }
    try:

        # 读取文本文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            
        if not content:
            logger.bind(tag=TAG).error("文件内容为空")
            return
            
        # 创建client
        client = lark.Client.builder() \
            .app_id(app_id) \
            .app_secret(app_secret) \
            .log_level(lark.LogLevel.DEBUG) \
            .build()

        # 构造请求对象
        request: CreateMessageRequest = CreateMessageRequest.builder() \
            .receive_id_type(send_config["target_info"]) \
            .request_body(CreateMessageRequestBody.builder()
                          .receive_id(send_config["target_id"])
                          .msg_type(send_config["target_type"])
                          .content(json.dumps({"text": content}))  # 将文件内容作为消息发送
                          .uuid(str(uuid.uuid4()))  # 生成唯一的UUID
                          .build()) \
            .build()

        # 发起请求
        response: CreateMessageResponse = client.im.v1.message.create(request)

        # 处理失败返回
        if not response.success():
            logger.bind(tag=TAG).error(
                f"发送消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return

        # 处理业务结果
        logger.bind(tag=TAG).info(f"消息发送成功: {json.dumps(response.data, indent=4, ensure_ascii=False)}")
        
    except Exception as e:
        logger.bind(tag=TAG).error(f"发送消息失败: {str(e)}")