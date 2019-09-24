from chart_builder.utils.helper import resource_payload_validator


class BaseBuilder(object):
    VALIDATION_SCHEMA = {}
    RESOURCE_TYPE = "BASE"

    def __init__(self, template):
        self.template = template
        self.values = {}

    def get_safe_payload(self, payload):
        resource_name = payload.get("name") or self.service_name
        return resource_payload_validator(resource_name, self.VALIDATION_SCHEMA, payload)

    def build(self, payload):
        raise NotImplementedError("build not implemented")
