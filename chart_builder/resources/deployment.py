from .base import BaseBuilder

DEPLOYMENT_SCHEMA = {

}


class DeploymentBuilder(BaseBuilder):
    VALIDATION_SCHEMA = DEPLOYMENT_SCHEMA
    RESOURCE_TYPE = "Deployment"

    @property
    def resource_name(self):
        return ""

    def build(self, payload):
        pass
