from unittest import TestCase, mock
from chart_builder import Builder

containers = [
    {
        "name": "nginx",
        "image": "nginx",
        "pull_policy": "Always",
        "env": [
            {"name": "debug", "value": "1"},
            {"name": "debug", "valueFrom": {"configMapKeyRef": {"name": "test-cm", "key": "TEST"}}},
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
    "volumes": [
        {
            "name": "config-volume",
            "hostPath": {"path": "/etc"},
        },
        {"name": "test-config-map", "configMap": {"name": "test-cm"}},
    ]
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
config_map = {
    "name": "test-cm",
    "data": {
        "key1": "value1",
        "key2": "value2",
    }
}

secret = {
    "name": "test-secret",
    "data": {
        "key1": "value1",
        "key2": "value2",
    }
}


class FakeRepo(object):
    def __init__(self, path):
        self.source_path = path

    def read(self, path):
        return b""

    def write(self, path, content):
        pass

    def touch(self, path):
        pass

    def mkdir(self, sub_path):
        pass

    def push(self):
        pass


class TestBuildChart(TestCase):
    def setUp(self):
        self.storage_patch = mock.patch("chart_builder.storage.LocalDir", new=FakeRepo)
        self.storage = {"type": "local", "source": {"path": "/test"}}

        self.storage_patch.start()

    def tearDown(self):
        self.storage_patch.stop()

    def test_builder(self):
        builder = Builder(
            "testChart",
            version="1.0",
            app_version="1.0",
            description="",
            storage=self.storage,
        )
        builder.add_deployment("test-service", deployment)
        builder.add_kube_service("test-service", kube_svc)
        builder.add_configmap(config_map)
        builder.add_secret(secret)
        print(builder._templates)
        print(builder._services)
        print(builder._values)

        builder.build_chart()
