import json
from .base import BaseBuilder, NAME_PATTERN

SERVICE_PORT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        "protocol": {
            "type": "string",
            "enum": ["TCP", "UDP"],
        },
        "port": {"type": "integer"},
        "targetPort": {"type": "integer"},
    },

    "required": ["name", "port"],
    "additionalProperties": False,
}

SERVICE_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        # 将根据 component 来确定 Selector
        "component_name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        "type": {
            "type": "string",
            "enum": ["ClusterIP", "NodePort"],
        },
        "is_headless": {"type": "boolean"},
        "selector": {"type": "object"},
        "ports": {
            "type": "array",
            "items": SERVICE_PORT_SCHEMA,
            "minItems": 1,
        }
    },

    "required": ["name", "type", "ports"],
    "additionalProperties": False,
}

SERVICE_TEMPLATE = """
---
apiVersion: v1
kind: Service
metadata:
  name: {resouce_name}
spec:
  type: {type}
  selector:
{selector}
  ports:
{ports}
"""


class ServiceBuilder(BaseBuilder):
    VALIDATION_SCHEMA = SERVICE_SCHEMA
    RESOURCE_TYPE = "Service"

    def get_resource_name(self):
        return "{{ .Release.Name }}-" + self.resource_name

    def _do_build(self):
        self.template = SERVICE_TEMPLATE.format(
            resouce_name=self.get_resource_name(),
            type=self.get_svc_type(),
            selector=self.get_selector(),
            ports=self.get_ports(),
        )

    def get_svc_type(self):
        self.values['serviceType'] = self.payload['type']
        return '{{ .Values.' + self.values_key + '.serviceType }}'

    def get_ports(self):
        content = ""
        for p in self.payload['ports']:
            content += "  - {}\n".format(json.dumps(p))

        return content

    def get_selector(self):
        # 默认使用 service name 作为 component name
        selector = self.default_selector
        if "selector" in self.payload:
            selector.update(self.payload['selector'])
        if "component_name" in self.payload:
            selector['app.kubernetes.io/component'] = self.payload['component_name']
        content = ""
        for k, v in selector.items():
            content += '    {}: "{}"\n'.format(k, v)

        return content
