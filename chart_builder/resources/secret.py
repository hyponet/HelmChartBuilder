from .base import BaseBuilder, NAME_PATTERN

SECRET_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        "data": {"type": "object"},
    },

    "required": ["name", "data"],
    "additionalProperties": False,
}

SECRET_TEMPLATE = """
---
apiVersion: v1
kind: Secret
metadata:
  name: {resource_name}
type: Opaque
data:
{data}
"""


class SecretBuilder(BaseBuilder):
    VALIDATION_SCHEMA = SECRET_SCHEMA
    RESOURCE_TYPE = "Secret"

    def get_resource_name(self):
        return "{{ .Release.Name }}-" + self.resource_name

    def _do_build(self):
        self.template = SECRET_TEMPLATE.format(
            resource_name=self.get_resource_name(),
            data=self.get_data(),
        )

    def get_data(self):
        data = self.payload['data']

        content = ""
        for k, v in data.items():
            self.values[k] = v
            content += "  {}: {}\n".format(
                k, "{{ " + ".Values.{}.{}".format(self.values_key, k) + " }}")
        return content
