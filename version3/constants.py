# ===================== 两套固定Prompt（服务内置，客户端不可修改） =====================
# 主Prompt：第一个分片专用（提取基础信息+总分+当前题目成绩）
MAIN_PROMPT = """
请严格按照规则解析图片，仅返回标准JSON字符串，禁止额外文字、解释、换行、标点。
规则：
1. 以本次所有图片中的【第一张图片】为依据，提取：学号、姓名、班级、授课老师、卷面总成绩；字段缺失填空字符串。
2. 解析本次所有图片中的每一道题目，提取题号、对应得分，生成题目得分列表；无题目则返回空数组。
固定JSON结构：
{
  "base_info": {
    "student_id": "",
    "name": "",
    "class_name": "",
    "teacher": "",
    "total_score": ""
  },
  "current_item_scores": [
    {"question_no": "", "score": ""}
  ]
}
"""

# 辅Prompt：第二个及后续分片专用（仅提取题目成绩）
SUB_PROMPT = """
请严格按照规则解析图片，仅返回标准JSON字符串，禁止额外文字、解释、换行、标点。
规则：
1. 无需提取学号、姓名、班级、老师、总成绩。
2. 仅解析本次所有图片中的每一道题目，提取题号、对应得分，生成题目得分列表；无题目则返回空数组。
固定JSON结构：
{
  "current_item_scores": [
    {"question_no": "", "score": ""}
  ]
}
"""

# ===================== 接口统一响应工具 =====================
def standard_response(code: int, msg: str, data: dict = None) -> dict:
    return {
        "code": code,
        "message": msg,
        "data": data or {}
    }

# ===================== 错误码定义 =====================
CODE_SUCCESS = 200
CODE_PARAM_ERROR = 400        # 基础参数错误
CODE_IMAGE_ERROR = 400       # 图片格式/大小/编码错误
CODE_SERVICE_ERROR = 500      # 模型调用、服务异常
CODE_JSON_PARSE_ERROR = 501   # 模型返回JSON解析失败
