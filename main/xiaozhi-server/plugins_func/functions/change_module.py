from plugins_func.register import register_function,ToolType, ActionResponse, Action
from config.logger import setup_logging

TAG = __name__
logger = setup_logging()

# 模式id， workflow_id，回复， 是(否)使用app_id(bot_id)
prompts = {"普通聊天模式": [0, None, "", "聊些什么", False],
           "心理辅导模式": [1, "7498179336974499859", "你好", "聊些什么", True],
           "翻译模式": [2, "7498179309841072179", "1", "翻译成什么语言", False]}
change_module_function_desc = {
                "type": "function",
                "function": {
                    "name": "change_module",
                    "description": "当用户想切换模式/切换功能时调用,可选的模式有：[普通聊天模式,心理辅导模式,翻译模式]",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "module": {
                                "type": "string",
                                "description": "要切换的模式名字"
                            }
                        },
                        "required": ["module"]
                    }
                }
            }

@register_function('change_module', change_module_function_desc, ToolType.SYSTEM_CTL)
def change_module(conn, module: str):
    """切换模式"""
    if module not in prompts:
        return ActionResponse(action=Action.RESPONSE, result="切换模式失败", response="不支持的模式")
    new_module_info = prompts[module]
    conn.change_system_module(new_module_info)
    logger.bind(tag=TAG).info(f"切换模式:{module},模式名称:{module}")
    res = f"切换模式成功 进入{module}，你想要{new_module_info[3]}"
    return ActionResponse(action=Action.RESPONSE, result="切换模式已处理", response=res)
