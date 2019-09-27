import json
from chart_builder.utils.exceptions import TemplateGenError
from chart_builder.utils.helper import resource_payload_validator

NAME_PATTERN = r"^[a-z]([-a-z0-9]*[a-z0-9]){3,30}$"
IMAGE_PATTERN = r""

CONTAINER_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        "image": {
            "type": "string",
            # "pattern": IMAGE_PATTERN,
        },
        "version": {
            # Image tag
            # DEFAULT Chart AppVersion
            "type": "string",
        },
        "pull_policy": {
            "type": "string",
            "enum": ["Always", "IfNotPresent", "Never"],
        },
        "command": {
            "type": "array",
            "items": {"type": "string"}
        },
        "args": {
            "type": "array",
            "items": {"type": "string"}
        },
        "env": {
            "type": "array",
            "items": {"type": "object"}
        },
        "ports": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "containerPort": {"type": "integer"}
                },
                "required": ["containerPort"],
            }
        },
        "volume_mounts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                },
                "required": ["name"],
            }
        },
        "readiness_probe": {
            "type": "object",
            "properties": {
                "initialDelaySeconds": {"type": "integer"},
                "periodSeconds": {"type": "integer"},
                "httpGet": {"type": "object"},
                "tcpSocket": {"type": "object"},
                "exec": {"type": "object"},

            },
            "required": ["initialDelaySeconds", "periodSeconds"],
        },
        "liveness_probe": {
            "type": "object",
            "properties": {
                "initialDelaySeconds": {"type": "integer"},
                "periodSeconds": {"type": "integer"},
                "httpGet": {"type": "object"},
                "tcpSocket": {"type": "object"},
                "exec": {"type": "object"},

            },
            "required": ["initialDelaySeconds", "periodSeconds"],
        },
        "resources": {
            "type": "object",
        }
    },
    "required": ["name", "image"],
    "additionalProperties": False,
}

VOLUME_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
    },
    "required": ["name"],
    "additionalProperties": True,
}

CONTAINER_TEMPLATE = """
- name: {name}
  image: "{image}:{tag}"
  imagePullPolicy: {pull_policy}
  ports:
   - name: http
     containerPort: 80
     protocol: TCP
{command}
{args}
{env}
{ports}
{volume_mounts}
{liveness_probe}
{readiness_probe}
{resources}
"""


class BaseBuilder(object):
    VALIDATION_SCHEMA = {}
    RESOURCE_TYPE = "BASE"
    INSTANCE_NAME = "{release_name}-{resource_name}"

    def __init__(self, template):
        self.template = template
        self.values = {}

        self.payload = None
        self.resource_name = None
        self.values_key = None

    def get_safe_payload(self, payload):
        resource_name = payload.get("name") or self.template.service_name
        self.resource_name = resource_name
        self.payload = resource_payload_validator(resource_name, self.VALIDATION_SCHEMA, payload)

    @property
    def default_labels(self):
        resource_name = self.resource_name
        service_name = self.template.service_name
        chart_metadata = self.template.chart_metadata

        labels = {
            "app.kubernetes.io/name": str(chart_metadata.name),
            "app.kubernetes.io/version": str(chart_metadata.appVersion),
            "app.kubernetes.io/managed-by": "{{ .Release.Service }}",
            "helm.sh/chart": "{}-{}".format(str(chart_metadata.name),
                                            str(chart_metadata.version).replace("+", "-")),
        }

        if service_name:
            instance_name = self.INSTANCE_NAME.format(
                release_name="{{ .Release.Name }}", resource_name=service_name)
            labels.update({
                "app.kubernetes.io/instance": instance_name,
                "app.kubernetes.io/component": resource_name,
            })
        return labels

    @property
    def default_selector(self):
        resource_name = self.resource_name
        service_name = self.template.service_name
        if not service_name:
            raise TemplateGenError(
                self.RESOURCE_TYPE, "Has not service name.")
        chart_metadata = self.template.chart_metadata
        instance_name = self.INSTANCE_NAME.format(
            release_name="{{ .Release.Name }}", resource_name=service_name)

        return {
            "app.kubernetes.io/name": str(chart_metadata.name),
            "app.kubernetes.io/instance": instance_name,
            "app.kubernetes.io/component": resource_name,
            "app.kubernetes.io/version": str(chart_metadata.appVersion),
        }

    def get_containers(self, containers, indent):
        default_tag = self.template.chart_metadata.appVersion
        content = ""
        for c in containers:
            name = c['name']

            values = {}
            value_key = "{}.{}".format(self.values_key, name)

            image = c['image']
            values["imageVersion"] = c.get('version') or default_tag
            tag = '{{ .Value.' + value_key + '.imageVersion }}'

            pull_policy = "{{ .Value." + value_key + ".imagePullPolicy }}"
            values["imagePullPolicy"] = c.get("pull_policy") or "IfNotPresent"

            command = ""
            if "command" in c:
                command = "  command: {}".format(json.dumps(c['command']))

            args = ""
            if "args" in c:
                args = "  args: {}".format(json.dumps(c['args']))

            env = ""
            if "env" in c:
                val_envs = {}
                env = "  env:\n"
                for e in c['env']:
                    if "value" in e:
                        val_envs[e['name']] = e['value']
                        e['value'] = "{{ .Value." + value_key + ".env." + e['name'] + " }}"
                    env += "  - {}\n".format(json.dumps(e))
                if val_envs:
                    values['env'] = val_envs

            ports = ""
            if "ports" in c:
                ports = "  ports:\n"
                for p in c['ports']:
                    ports += "  - {}\n".format(json.dumps(p))

            volume_mounts = ""
            if "volume_mounts" in c:
                volume_mounts = "  volumeMounts:\n"
                for v in c['volume_mounts']:
                    volume_mounts += "  - {}\n".format(json.dumps(v))

            readiness_probe = ""
            if "readiness_probe" in c:
                readiness_probe = "  readinessProbe: {}".format(json.dumps(c['readiness_probe']))

            liveness_probe = ""
            if "liveness_probe" in c:
                liveness_probe = "  livenessProbe: {}".format(json.dumps(c['liveness_probe']))

            resources = ""
            if "resources" in c:
                resources = "  resources: {}".format(json.dumps(c['resources']))

            content += CONTAINER_TEMPLATE.format(
                name=name,
                image=image,
                tag=tag,
                pull_policy=pull_policy,
                command=command,
                args=args,
                env=env,
                ports=ports,
                volume_mounts=volume_mounts,
                readiness_probe=readiness_probe,
                liveness_probe=liveness_probe,
                resources=resources,
            )
            self.values[name] = values

        result = []
        lines = content.split("\n")
        for l in lines:
            if not l:
                # Delete empty line
                continue
            result.append(
                "{}{}".format(" " * indent, l)
            )

        return "\n".join(result)

    def _before_build(self):
        pass

    def _after_build(self):
        pass

    def _do_build(self):
        raise NotImplementedError("build not implemented")

    def build(self, payload):
        self.get_safe_payload(payload)

        if self.template.service_name:
            self.values_key = ".".join((self.template.service_name, self.resource_name))
        else:
            self.values_key = self.resource_name

        self._before_build()
        self._do_build()
        self._after_build()
        self.values = {self.resource_name: self.values}
