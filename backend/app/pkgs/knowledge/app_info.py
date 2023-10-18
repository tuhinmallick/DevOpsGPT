from app.pkgs.knowledge.app_info_basic import AppInfoBasic
from app.pkgs.knowledge.app_info_pro import AppInfoPro
from app.models.application import Application
from app.models.application_service import ApplicationService
from config import GRADE

def getAppArchitecture(appID):
    appID = int(appID)

    apps = Application.get_all_application(0, appID)
    appArchitecture = ""
    if len(apps) > 0:
        services = apps[0]["service"]
        for service in services:
            appArchitecture += "service name: "+service["name"]+"\nrole of service: "+service["role"]+"\ndevelopment_language: "+service["language"]+"\ndevelopment_framework: "+service["framework"]+"\n\n"

    return appArchitecture.strip(), True

def getServiceSwagger(appID, serviceName):
    appID = int(appID)

    swaggerDoc = ""
    apps = Application.get_all_application(0, appID)
    if len(apps) > 0:
        services = apps[0]["service"]
        for service in services:
            # todo get interface document content dynamically
            # todo Use llm to determine which interface documents to adjust
            swaggerDoc = service["api_location"]

    return swaggerDoc, True

def getServiceBasePrompt(appID, serviceName):
    appID = int(appID)

    appBasePrompt = ""
    apps = Application.get_all_application(0, appID)
    if len(apps) > 0:
        services = apps[0]["service"]
        service_names = []
        currentServiceStr = ""
        for service in services:
            service_names.append(service["name"])
            if service["name"] == serviceName:
                currentServiceStr = "and you are responsible for the development of "+service["name"]+" services. The service uses the "+service["language"]+" language and is developed under the "+service["framework"]+" framework"

        serviceNameStr = ','.join(service_names)
        appBasePrompt = f"The application consists of {serviceNameStr} services, {currentServiceStr}"

    return appBasePrompt, True

def getServiceIntro(appID, serviceName, tenantID):
    appID = int(appID)

    appInfo = ""
    apps = Application.get_all_application(tenantID, appID)
    if len(apps) > 0:
        services = apps[0]["service"]
        for service in services:
            if service["name"] == serviceName:
                appInfo = "service name: "+service["name"]+"\nrole of service: "+service["role"]+"\ndevelopment_language: "+service["language"]+"\ndevelopment_framework: "+service["framework"]

    return appInfo, True

def getServiceGitPath(appID, serviceName):
    serviceInfo = ApplicationService.get_service_by_name(appID, serviceName)
    gitPath = serviceInfo["git_path"]

    return gitPath, True

def getServiceDockerImage(appID, serviceName):
    appID = int(appID)

    apps = Application.get_all_application(0, appID)
    if len(apps) > 0:
        services = apps[0]["service"]
        for service in services:
            if service["name"] == serviceName:
                # todo 0
                gitWorkflow = service["cd_default_image"]

    return gitWorkflow, True

def getServiceLib(appID, serviceName):
    obj = AppInfoBasic() if GRADE == "base" else AppInfoPro()
    return obj.getServiceLib(appID, serviceName)

def getServiceStruct(appID, serviceName):
    obj = AppInfoBasic() if GRADE == "base" else AppInfoPro()
    return obj.getServiceStruct(appID, serviceName)

def getServiceSpecification(appID, serviceName, LibName):
    obj = AppInfoBasic() if GRADE == "base" else AppInfoPro()
    return obj.getServiceSpecification(appID, serviceName, LibName)

def analyzeService(tenant_id, gitPath):
    obj = AppInfoBasic() if GRADE == "base" else AppInfoPro()
    return obj.analyzeService(tenant_id, gitPath)
