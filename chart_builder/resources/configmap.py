from .base import BaseBuilder

CONFIGMAP_SCHEMA = {

}


class ConfigMapBuilder(BaseBuilder):
    VALIDATION_SCHEMA = CONFIGMAP_SCHEMA
    RESOURCE_TYPE = "ConfigMap"

    def get_resource_name(self):
        return ""

    def _do_build(self):
        pass
