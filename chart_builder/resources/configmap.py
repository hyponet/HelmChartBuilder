from .base import BaseBuilder, NAME_PATTERN

CONFIG_MAP_SCHEMA = {
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

CONFIG_MAP_TEMPLATE = """
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {resource_name}
data:
{data}
"""


class ConfigMapBuilder(BaseBuilder):
    VALIDATION_SCHEMA = CONFIG_MAP_SCHEMA
    RESOURCE_TYPE = "ConfigMap"

    def get_resource_name(self):
        return "{{ .Release.Name }}-" + self.resource_name

    def _do_build(self):
        self.template = CONFIG_MAP_TEMPLATE.format(
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
