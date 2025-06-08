import asyncio
import websockets
import json
import uuid


async def test_websocket_client():
    # 连接信息
    uri = "ws://localhost:8080"  # 根据您的服务器配置修改
    headers = {
        "device-id": "test_device_001",  # 设备ID
        "app-id": "test_app",            # 应用ID
        "version": "1.0.0"               # 版本号
    }

    async with websockets.connect(uri, extra_headers=headers) as websocket:
        # 接收欢迎消息
        welcome_msg = await websocket.recv()
        print(f"收到欢迎消息: {welcome_msg}")

        # 发送hello消息
        hello_msg = {
            "type": "hello",
            "session_id": str(uuid.uuid4())
        }
        await websocket.send(json.dumps(hello_msg))
        response = await websocket.recv()
        print(f"收到响应: {response}")

        while True:
            # 获取用户输入
            print("\n请选择操作：")
            print("1. 发送文本消息")
            print("2. 开始录音")
            print("3. 停止录音")
            print("4. 退出")
            choice = input("请输入选项（1-4）: ")

            if choice == "1":
                text = input("请输入要发送的文本: ")
                message = {
                    "type": "listen",
                    "state": "detect",
                    "text": text
                }
                await websocket.send(json.dumps(message))

            elif choice == "2":
                message = {
                    "type": "recording",
                    "state": "start",
                    "file": f"recording_{uuid.uuid4().hex[:8]}.txt"
                }
                await websocket.send(json.dumps(message))

            elif choice == "3":
                message = {
                    "type": "recording",
                    "state": "stop"
                }
                await websocket.send(json.dumps(message))

            elif choice == "4":
                print("退出测试客户端")
                break

            # 接收服务器响应
            try:
                while True:
                    response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    print(f"收到服务器响应: {response}")
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"接收消息出错: {e}")
                break


def ttt_workflow(input_txt_path, output_txt_path):
    import os
    # official coze sdk for Python [cozepy](https://github.com/coze-dev/coze-py)
    from cozepy import COZE_CN_BASE_URL
    from cozepy import Coze, TokenAuth, Stream, WorkflowEvent, WorkflowEventType  # noqa
    # 读取文本文件内容
    with open(input_txt_path, 'r', encoding='utf-8') as f:
        text_content = f.read().strip()

    if not text_content:
        print("输入文件内容为空")
        return None

    # 如果没有指定输出文件路径，则在输入文件同目录下创建
    if output_txt_path is None:
        input_dir = os.path.dirname(input_txt_path)
        input_filename = os.path.basename(input_txt_path)
        output_txt_path = os.path.join(input_dir, f"response_{input_filename}")

    # 获取 Coze 客户端
    coze_api_token = r"pat_jJCTCkErhARzwGQIM4csDeRVVeFeyzKuLAKuIZFzTO1zkBOGKkikRmf86jdKJpTA"
    coze_api_base = COZE_CN_BASE_URL
    coze = Coze(auth=TokenAuth(token=coze_api_token), base_url=coze_api_base)

    # 使用工作流处理文本
    workflow_id = "7513221650838519846"

    # 打开输出文件，准备写入结果
    with open(output_txt_path, 'w', encoding='utf-8') as out_file:
        # 使用 bot_id 方式
        for event in coze.workflows.runs.stream(
                workflow_id=workflow_id,
                bot_id="7486489889299677196",
                parameters={"USER_INPUT": text_content}
        ):
            if event.event == WorkflowEventType.MESSAGE:
                # 将结果写入文件
                out_file.write(event.message.content)
                out_file.flush()  # 确保内容立即写入文件
            else:
                print(f"处理文本时出现错误: {event.error}")
                return None

    return output_txt_path
    pass


import json
import lark_oapi as lark
from lark_oapi.api.im.v1 import *
import uuid


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
            print(
                f"发送消息失败, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}")
            return


    except Exception as e:
        print(f"发送消息失败: {str(e)}")


if __name__ == "__main__":
    # asyncio.run(test_websocket_client())
    ttt_workflow(r"data/transcripts/recording_20250607_224931.txt",
                 "data/transcripts/recording_res.txt")
    sendmessage2feishuhandle(None, r"data/transcripts/recording_res.txt")
