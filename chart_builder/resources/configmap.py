from .base import BaseBuilder

CONFIGMAP_SCHEMA = {

}


class ConfigMapBuilder(BaseBuilder):
    VALIDATION_SCHEMA = CONFIGMAP_SCHEMA
    RESOURCE_TYPE = "ConfigMap"

    @property
    def resource_name(self):
        return ""

    def build(self, payload):
        pass
