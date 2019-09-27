from unittest import TestCase

from chart_builder.resources import ResourceTemplate
from chart_builder.builder import Metadata

containers = [
    {
        "name": "nginx",
        "image": "nginx",
        "pull_policy": "Always",
        "env": [
            {"name": "debug", "value": "1"},
        ],
        "ports": [
            {"containerPort": 80},
        ],
        "volume_mounts": [
            {"name": "config-volume", "mountPath": "/etc/nginx/nginx.conf"},
        ],
        "readiness_probe": {
            "initialDelaySeconds": 5,
            "periodSeconds": 5,
            "httpGet": {
                "path": "http://127.0.0.1",
                "port": 80,
            },
        },
        "liveness_probe": {
            "initialDelaySeconds": 5,
            "periodSeconds": 5,
            "httpGet": {
                "path": "http://127.0.0.1",
                "port": 80,
            },
        },
        "resources": {"limits": {"cpu": "0.2", "memory": "0.5Gi"}},
    },
    {
        "name": "sidecar",
        "image": "sidecar",
        "version": "v1",
        "command": ["/bin/exec", "fortest"],
        "args": ["XXX1", "XXX2"],
        "resources": {"limits": {"cpu": "0.2", "memory": "0.5Gi"}},
    }
]

deployment = {
    "name": "test-nginx",
    "labels": {
        "chart.updev.cn": "test"
    },
    "annotations": {
        "chart.updev.cn": "test"
    },
    "init_containers": [{
        "name": "init",
        "image": "busybox",
        "version": "latest",
        "command": ["/bin/exec", "fortest"],
    }],
    "containers": containers,
    "volumes": [{
        "name": "config-volume",
        "hostPath": {"path": "/etc"},
    }]
}

kube_svc = {
    "name": "try-nginx",
    "component_name": "test-nginx",
    "type": "ClusterIP",
    "selector": {"test": "true"},
    "ports": [
        {"name": "http", "protocol": "TCP", "port": 80},
        {"name": "https", "protocol": "TCP", "port": 443, "targetPort": 30443}
    ],

}


class TestRenderTemplate(TestCase):
    def setUp(self):
        self.chart_metadata = Metadata(
            apiVersion="v1",
            name="test-chart",
            version="0.1",
            appVersion="1.0.0",
            description="desc",
        )

    def test_render_deployment(self):
        template = ResourceTemplate(
            self.chart_metadata,
            service_name="test-web", deployments=[])
        template.gen_deployment(deployment)
        print(template.template)
        print(template.values)

    def test_render_svc(self):
        template = ResourceTemplate(
            self.chart_metadata,
            service_name="test-web", services=[])
        template.gen_kube_service(kube_svc)
        print(template.template)
        print(template.values)
