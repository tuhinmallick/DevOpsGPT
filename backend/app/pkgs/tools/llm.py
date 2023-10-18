import traceback
from app.pkgs.tools.llm_pro import LLMPro
from app.pkgs.tools.llm_basic import LLMBase
from config import GRADE

def chatCompletion(context, fackData=""):
    obj = LLMBase() if GRADE == "base" else LLMPro()
    message = ""
    success = False
    try:
        message, total_tokens, success = obj.chatCompletion(context, fackData)
    except Exception as e:
        print(f"chatCompletion failed first time:{str(e)}")
        try:
            message, total_tokens, success = obj.chatCompletion(context, fackData)
        except Exception as e:
            print(f"chatCompletion failed second time:{str(e)}")
            traceback.print_exc()
            raise Exception(e)
    return message, total_tokens, success