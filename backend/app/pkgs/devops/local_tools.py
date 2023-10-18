from app.pkgs.tools.file_tool import read_file_content
from app.pkgs.devops.local_tools_base import LocalToolsBase
from app.pkgs.devops.local_tools_pro import LocalToolsPro
from config import GRADE
from config import WORKSPACE_PATH

def getFileContent(file_path, repopath):
    path = WORKSPACE_PATH + repopath + "/" + file_path

    try:
        success, content = read_file_content(path)
        if not success:
            return False, ""
    except Exception as e:
        return False, ""

    return True, content 

def compileCheck(requirementID, ws_path,repo_path):
    obj = LocalToolsBase() if GRADE == "base" else LocalToolsPro()
    return obj.compileCheck(requirementID, ws_path,repo_path)

def lintCheck(requirementID, ws_path, repo_path, file_path):
    obj = LocalToolsBase() if GRADE == "base" else LocalToolsPro()
    return obj.lintCheck(requirementID, ws_path, repo_path, file_path)

def unitTest(requirementID, ws_path, repo_path, file_path):
    obj = LocalToolsBase() if GRADE == "base" else LocalToolsPro()
    return obj.unitTest(requirementID, ws_path, repo_path, file_path)

def apiTest(requirementID, ws_path, repo_path, file_path):
    obj = LocalToolsBase() if GRADE == "base" else LocalToolsPro()
    return obj.apiTest(requirementID, ws_path, repo_path, file_path)