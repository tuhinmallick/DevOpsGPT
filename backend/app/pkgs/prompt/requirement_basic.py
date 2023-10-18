import json
import re
from app.pkgs.tools.i18b import getI18n
from app.pkgs.tools.i18b import getCurrentLanguageName
from app.pkgs.tools.utils_tool import fix_llm_json_str
from app.pkgs.prompt.requirement_interface import RequirementInterface
from app.pkgs.tools.llm import chatCompletion
from app.models.application_service import ApplicationService
from app.pkgs.tools import storage

_ = getI18n("prompt")
DOC_FRONTEND = _("""
## Original Requirements
Develop one ... 

## Product Goals
```python
[
    "Create a ...",
]
```
                
## User Stories
```python
[
    "As a user, ...",
]
```
                
## UI/UX Design
```python
[
    "Three-column layout ...",
]
```
                
## Business logic
```python
[
    "Request the back-end interface to pass parameters ...",
]
""")
DOC_BACKEND = _("""
## Original Requirements
Develop one ... 

## Product Goals
```python
[
    "Create a ...",
]
```

## 接口类型
如RESTful API或GraphQL或GRPC等
               
## 请求方式
POST、GET、DELETE、PUT等，没有请忽略
               
## 调用路径或调用方法
path or method

## 请求体参数
```python
[
    "name, type",
]
```
               
## 响应体参数
```python
[
    "name, type",
]
```

## Business logic
```python
[
    "Accept request parameter: ...",
]
```
""")
DOC_GAME = _("""
## 游戏名称
pingpang game...
             
## Original Requirements
Develop one ... 

## Product Goals
```python
[
    "Create a ...",
]
```
             
## Similar game introduction
```python
[
    "...",
]
```
             
## 游戏详细规则
```python
[
    "Move with keyboard control ...",
]
```
""")

DOC_COMMON = """
## Original Requirements
Develop one ... 

## Product Goals
```python
[
    "Create a ...",
]
```

## User Stories
```python
[
    "As a user, ...",
]
```

## Competitive Analysis
```python
[
    "xxx can ...",
]
```

## Requirement Analysis
The product should be a ...

## Requirement Pool
```python
[
    "End game ..., P0",
]
```

## UI Design
```python
[
    "A button in the ...",
]
```
"""


class RequirementBasic(RequirementInterface):
    def clarifyRequirement(self, requirementID, userPrompt, globalContext, appArchitecture, req):
        _ = getI18n("prompt")
        firstPrompt = ""
        preContext = []
        try:
            preContext = json.loads(globalContext)
        except Exception as e:
            print(e)

        PRDTemplate = DOC_COMMON
        ServiceType = "COMMON"
        service_list = ApplicationService.get_services_by_app_id(req["app_id"])
        for service in service_list:
            ServiceType = service["service_type"]
            if ServiceType == "COMMON":
                PRDTemplate = DOC_COMMON
            elif ServiceType == "FRONTEND":
                PRDTemplate = DOC_FRONTEND
            elif ServiceType == "BACKEND":
                PRDTemplate = DOC_BACKEND
            elif ServiceType == "GAME":
                PRDTemplate = DOC_GAME

        # todo 这个参数暂时不要调整，过多的澄清会导致出现幻觉，并且程序在获取澄清列表的时候也需要调整
        maxCycle = 2
        message = ""
        clarified_list = ""
        if len(preContext) == 0:
            firstPrompt = userPrompt
        elif len(preContext) < maxCycle:
            firstPrompt = preContext[0]["content"]
            clarified_list = userPrompt

            preContext = preContext[1:]
            preContext.append({
                "role": "user",
                "content": userPrompt + """

Is there anything else unclear? If yes, continue asking less than 3 unclear questions in the same format as before, If no, only directly respond \"Nothing more to clarify.\"
"""
            })
        else:
            firstPrompt = preContext[0]["content"]
            clarified_list = userPrompt

        # 对已生成需求文档的修改
        if "development_requirements_detail" in globalContext:
            return adjust(requirementID, userPrompt, PRDTemplate, appArchitecture, service_list, ServiceType)
        # 澄清过程
        elif len(preContext) < maxCycle:
            finalContext = [
                {
                    "role": "system",
                    "content": """
Role: You are a professional full stack developer. Your task is to read user "software development requirement" and base on "Application Information" to clarify them to complete a requirement document(PRD) like:
```
"""+PRDTemplate+"""
```

Note that we should guide the user to make the requirements fit into the "Application implementation", and avoid completely deviating from the requirements of the application positioning.

Specifically you will summarise a list of super short bullets of areas that need clarification.and wait for an answer from the user.

Application Information:
```
"""+appArchitecture+"""
```

Software development requirement:
```
"""+firstPrompt+"""
```

You should only directly respond in JSON format as described below, Ensure the response must can be parsed by Python json.loads, Response Format example:
[{"question":"question","reasoning":"reasoning","answer_sample":"Answer sample"},{"question":"question","reasoning":"reasoning","answer_sample":"Answer sample"}]
Follow the JSON response exactly as above.

Note: Keep conversations in """+getCurrentLanguageName()+""".
"""
                }
            ]
            finalContext.extend(preContext)

            message, total_tokens, success = chatCompletion(
                finalContext, "")

            if message.find("Nothing more to clarify") != -1 or message.find('"question":""') != -1:
                return organize(requirementID, firstPrompt, PRDTemplate, appArchitecture, service_list, ServiceType, clarified_list)
        # 总结需求文档
        else:
            return organize(requirementID, firstPrompt, PRDTemplate, appArchitecture, service_list, ServiceType, clarified_list)

        message = fix_llm_json_str(message)
        return json.loads(message), success


def organize(requirementID, firstPrompt, PRDTemplate, appArchitecture, service_list, ServiceType, clarified_list):
    Organize = [
        {
            "role": "system",
            "content": """
Role: You are a professional software developer, you will organize a long and detailed requirement document based on the "software development requirement" and "Application Information" and "clarified list".
The final requirements document must match the positioning of the "Application Information". The Application can't develop features it's not good at.
Think step by step make sure the "clarified list" answers are all taken into account, do not miss any details.
The answers from the 'clarified list' are of utmost importance and must be included in the requirement document with as much detail as possible.

software development requirement:
```
"""
            + firstPrompt
            + """
```

clarified list:
```
"""
            + clarified_list
            + """
```

Application Information:
```
"""
            + appArchitecture
            + """
```

Output carefully referenced "Format example" in format.
## Format example
"""
            + PRDTemplate
            + """

Note: Please respond in """
            + getCurrentLanguageName()
            + """.
""",
        }
    ]
    message, total_tokens, success = chatCompletion(Organize, "")

    parsed_data = convert_code_blocks_to_markdown(message)
    print(parsed_data)
    services_involved = [
        {"service_name": service["name"], "reasoning": ""}
        for service in service_list
    ]
    re = {
        "development_requirements_overview": "",
        "development_requirements_detail": parsed_data,
        "services_involved": services_involved,
        "review": ""
    }

    # ssss
    storage.set("last_prd", parsed_data)

    re["review"] = review(requirementID, message, ServiceType, appArchitecture)

    return re, success

def adjust(requirementID, userPrompt, PRDTemplate, appArchitecture, service_list, ServiceType):
    # ssss
    last_prd = storage.get("last_prd")

    if len(last_prd) < 1:
        raise Exception("Failed to obtain the PRD document. 获取PRD文档失败。")

    Organize = [
        {
            "role": "system",
            "content": """
Role: You are a professional software developer, your task is to modify the requirements document based on the feedback received and provide the revised final document content without altering the original structure of the requirements document.

Directly modify the original content to give the final document, there is no need to explain which part is modified.

## requirements document
```
"""
            + last_prd
            + """
```

## feedback list
```
"""
            + userPrompt
            + """
```

Output modified requirement document content in """
            + getCurrentLanguageName()
            + """ directly.
""",
        }
    ]
    message, total_tokens, success = chatCompletion(Organize, "")

    print(message)
    services_involved = [
        {"service_name": service["name"], "reasoning": ""}
        for service in service_list
    ]
    re = {
        "development_requirements_overview": "",
        "development_requirements_detail": message,
        "services_involved": services_involved,
        "review": ""
    }

    return re, success

def review(requirementID, PRD, ServiceType, appArchitecture):
    Organize = [
        {
            "role": "system",
            "content": """
Role: You are a professional """
            + ServiceType
            + """ software developer, your task is to review the Product Requirements Document (PRD) to ensure that the requirements can be effectively developed within the existing application and that the requirements are sufficiently detailed. Please provide no more than three of the most constructive suggestions.

Note: suggestions need focus on functional requirements rather than technical requirements.

Requirement Document:
'''
"""
            + PRD
            + """
'''

existing application info:
```
"""
            + appArchitecture
            + """
```

Output carefully referenced "Format example" in format without explanation or dialogue.
Format example:
'''
```python
[
    "suggestions 1: ...",
]
'''

Note: List suggestions in """
            + getCurrentLanguageName()
            + """.
""",
        }
    ]
    message, total_tokens, success = chatCompletion(Organize, "")

    print(message)

    return convert_code_blocks_to_markdown(message)

def convert_code_blocks_to_markdown_items(input_text):
    # 按逗号分割字符串，并去除首尾的空格
    lines = [line.strip().strip('",').strip("',")
             for line in input_text.split('\n')]

    formatted_lines = ['- ' + line.strip('"') for line in lines if len(line) > 0]
    # 返回格式化后的文本
    return '\n'.join(formatted_lines)


def convert_code_blocks_to_markdown(input_text):
    result = input

    # 定义正则表达式模式，匹配目标格式的代码块
    pattern = r'```python\n\[(.*?)\]\n```'

    # 使用re.sub()函数进行替换
    def replace(match):
        content = match.group(1)
        return convert_code_blocks_to_markdown_items(content)

    # 执行替换
    result = re.sub(pattern, replace, input_text, flags=re.DOTALL)

    return result
