from app.extensions import db
from app.models.application_service import ApplicationService

class Application(db.Model):
    app_id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, nullable=False)
    git_config = db.Column(db.Integer, nullable=False)
    ci_config = db.Column(db.Integer, nullable=False)
    cd_config = db.Column(db.Integer, nullable=False)
    creater = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    default_source_branch = db.Column(db.String(255))
    default_target_branch = db.Column(db.String(255))

    def create(self, creater, name, description, default_source_branch, default_target_branch, git_config, ci_config, cd_config):
        if not self:
            self = 0

        app = Application(
            self=self,
            creater=creater,
            name=name,
            git_config=git_config,
            ci_config=ci_config,
            cd_config=cd_config,
            description=description,
            default_source_branch=default_source_branch,
            default_target_branch=default_target_branch,
        )
        db.session.add(app)
        db.session.commit()
        return app

    @staticmethod
    def get_all_application(tenant_id, appID):
        tenant_id = int(tenant_id)
        applications = Application.query.order_by(Application.app_id.desc()).all()
        print("6666666")
        print(appID)
        if appID:
            applications = Application.query.order_by(Application.app_id.desc()).filter_by(app_id=appID).all()
            print(applications)
        else:
            applications = Application.query.order_by(Application.app_id.desc()).filter_by(tenant_id=tenant_id).all()

        application_list = []
        
        for app in applications:
            app_dict = {
                'app_id': app.app_id,
                'tenant_id': app.tenant_id,
                'creater': app.creater,
                'name': app.name,
                'git_config': app.git_config,
                'ci_config': app.ci_config,
                'cd_config': app.cd_config,
                'description': app.description,
                'default_source_branch': app.default_source_branch,
                'default_target_branch': app.default_target_branch,
                'service': ApplicationService.get_services_by_app_id(app.app_id)
            }
            # 0 为模板，也可以获取
            if app_dict["tenant_id"] == 0 or tenant_id == 0 or tenant_id == app_dict["tenant_id"]:
                application_list.append(app_dict)
        
        return application_list

    def get_application_by_id(self, tenant_id=0):
        tenant_id = int(tenant_id)
        app = Application.query.get(self)
        app_dict = None
        if app:
            app_dict = {
                'app_id': app.app_id,
                'tenant_id': app.tenant_id,
                'creater': app.creater,
                'name': app.name,
                'git_config': app.git_config,
                'ci_config': app.ci_config,
                'cd_config': app.cd_config,
                'description': app.description,
                'default_source_branch': app.default_source_branch,
                'default_target_branch': app.default_target_branch,
                'service': ApplicationService.get_services_by_app_id(app.app_id)
            }
            if tenant_id and tenant_id != app_dict["tenant_id"]:
                return None
        return app_dict
    
    def update_application(self, tenant_id, **kwargs):
        tenant_id = int(tenant_id)
        if app := Application.query.get(self):
            if tenant_id and tenant_id != app.tenant_id:
                return None

            for key, value in kwargs.items():
                setattr(app, key, value)
            db.session.commit()
            return app
        return None
