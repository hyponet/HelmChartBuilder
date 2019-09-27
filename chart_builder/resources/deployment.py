import json

from .base import BaseBuilder, \
    CONTAINER_SCHEMA, VOLUME_SCHEMA, NAME_PATTERN

DEPLOYMENT_SCHEMA = {
    "type": "object",
    "properties": {

        # Metadata
        "name": {
            "type": "string",
            "pattern": NAME_PATTERN,
        },
        "labels": {
            "type": "object",
            "additionalProperties": True,
        },
        "annotations": {
            "type": "object",
            "additionalProperties": True,
        },

        # Spec
        "replicas": {
            "type": "integer",
            "minimum": 1,
        },
        "strategy": {
            "type": "object",
            "properties": {
                "type": {
                    "type": "string",
                    "enum": ["Recreate", "RollingUpdate"],
                }
            },
        },

        # Spec.Template
        "init_containers": {
            "type": "array",
            "items": CONTAINER_SCHEMA,
        },
        "containers": {
            "type": "array",
            "minItems": 1,
            "items": CONTAINER_SCHEMA,
        },
        "volumes": {
            "type": "array",
            "items": VOLUME_SCHEMA,
        },
        "dns_policy": {
            "type": "string",
            "enum": ["Default", "ClusterFirst", "ClusterFirstWithHostNet", "None"],
        },
        "dns_config": {"type": "object"},
        "image_pull_secrets": {
            "type": "array",
            "items": {"type": "string"},
        }
    },
    "required": ["name", "containers"],
    "additionalProperties": False,
}

DEPLOYMENT_TEMPLATE = """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {resource_name}
  labels:
{deployment_labels}
{annotations}
spec:
  selector:
    matchLabels:
{selector}
  replicas: {replicas}
  strategy: {strategy}
  template:
    metadata:
      labels:
{pod_labels}
    spec:
{init_containers}
      containers:
{containers}
{volumes}
{dns_policy}
{dns_config}
{image_pull_secrets}
{scheduling_config}
"""

SCHEDULING_CONFIG_TEMPLATE = ""


class DeploymentBuilder(BaseBuilder):
    VALIDATION_SCHEMA = DEPLOYMENT_SCHEMA
    RESOURCE_TYPE = "Deployment"

    def __init__(self, template):
        super(DeploymentBuilder, self).__init__(template)

        self.labels = {}

    def _before_build(self):
        pass

    def _do_build(self):
        deploy_labels = self.get_labels(indent=4)
        pod_labels = self.get_labels(indent=8)

        annotations = ""
        if "annotations" in self.payload:
            annotations = "  annotations: {}".format(
                json.dumps(self.payload['annotations']))

        init_containers = ""
        if "init_containers" in self.payload:
            init_containers = "      initContainers:\n"
            init_containers += self.get_containers(
                self.payload['init_containers'], indent=6)

        volumes = ""
        if "volumes" in self.payload:
            volumes = "      volumes:\n"
            for v in self.payload["volumes"]:
                volumes += "      - {}\n".format(json.dumps(v))

        dns_policy = "      dnsPolicy: ClusterFirst"
        if "dns_policy" in self.payload:
            dns_policy = "      dnsPolicy: {}".format(self.payload['dns_policy'])

        dns_config = ""
        if "dns_config" in self.payload:
            dns_config = "      dnsConfig: {}".format(
                json.dumps(self.payload['dns_config']))

        image_pull_secrets = ""
        if "" in self.payload:
            image_pull_secrets = "      imagePullSecrets: {}".format(
                json.dumps(self.payload['image_pull_secrets']))

        self.template = DEPLOYMENT_TEMPLATE.format(
            resource_name=self.get_release_name(),
            deployment_labels=deploy_labels,
            annotations=annotations,
            replicas=self.get_replicas(),
            strategy=self.get_strategy(),
            selector=self.get_selector(),
            pod_labels=pod_labels,
            init_containers=init_containers,
            containers=self.get_containers(self.payload['containers'], indent=6),
            volumes=volumes,
            dns_policy=dns_policy,
            dns_config=dns_config,
            image_pull_secrets=image_pull_secrets,
            scheduling_config=self.get_scheduling_config(),
        )

    def get_release_name(self):
        return "{{ .Release.Name }}-" + self.resource_name

    def get_labels(self, indent):
        labels = self.payload.get("labels") or {}
        labels.update(self.default_labels)

        content = ""
        for k, v in labels.items():
            content += '{}{}: "{}"\n'.format(" " * indent, k, v)

        self.values['labels'] = {}
        return content

    def get_replicas(self):
        self.values['replicaCount'] = self.payload.get("replicas") or 1
        return "{{ .Values." + self.values_key + ".replicaCount }}"

    def get_strategy(self):
        strategy = self.payload.get("strategy") or "RollingUpdate"
        self.values['strategy'] = strategy
        return "{{ .Values." + self.values_key + ".strategy }}"

    def get_selector(self):
        selector = self.default_selector

        content = ""
        for k, v in selector.items():
            content += "      {}: {}\n".format(k, v)
        return content

    def get_scheduling_config(self):
        # TODO add scheduling config
        assert self.values_key
        return ""
