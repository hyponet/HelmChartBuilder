from .base import BaseBuilder

SERVICE_SCHEMA = {

}


class ServiceBuilder(BaseBuilder):
    VALIDATION_SCHEMA = SERVICE_SCHEMA
    RESOURCE_TYPE = "Service"

    @property
    def resource_name(self):
        return ""

    def build(self, payload):
        pass
