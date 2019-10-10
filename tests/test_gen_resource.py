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
deployment_template = """
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-test-nginx
  labels:
    chart.updev.cn: "test"
    app.kubernetes.io/name: "test-chart"
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/managed-by: "{{ .Release.Service }}"
    helm.sh/chart: "test-chart-0.1"
    app.kubernetes.io/instance: "{{ .Release.Name }}-test-web"
    app.kubernetes.io/component: "test-nginx"

  annotations: {"chart.updev.cn": "test"}
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: test-chart
      app.kubernetes.io/instance: {{ .Release.Name }}-test-web
      app.kubernetes.io/component: test-nginx
      app.kubernetes.io/version: 1.0.0

  replicas: {{ .Values.test-web.test-nginx.replicaCount }}
  strategy: {{ .Values.test-web.test-nginx.strategy }}
  template:
    metadata:
      labels:
        chart.updev.cn: "test"
        app.kubernetes.io/name: "test-chart"
        app.kubernetes.io/version: "1.0.0"
        app.kubernetes.io/managed-by: "{{ .Release.Service }}"
        helm.sh/chart: "test-chart-0.1"
        app.kubernetes.io/instance: "{{ .Release.Name }}-test-web"
        app.kubernetes.io/component: "test-nginx"

    spec:
      initContainers:
      - name: init
        image: "busybox:{{ .Values.test-web.test-nginx.init.imageVersion }}"
        imagePullPolicy: {{ .Values.test-web.test-nginx.init.imagePullPolicy }}
        ports:
         - name: http
           containerPort: 80
           protocol: TCP
        command: ["/bin/exec", "fortest"]
      containers:
      - name: nginx
        image: "nginx:{{ .Values.test-web.test-nginx.nginx.imageVersion }}"
        imagePullPolicy: {{ .Values.test-web.test-nginx.nginx.imagePullPolicy }}
        ports:
         - name: http
           containerPort: 80
           protocol: TCP
        env:
        - {"name": "debug", "value": "{{ .Values.test-web.test-nginx.nginx.env.debug }}"}
        - {"name": "debug", "valueFrom": {"configMapKeyRef": {"name": "{{ .Release.Name }}-test-cm", "key": "TEST"}}}
        ports:
        - {"containerPort": 80}
        volumeMounts:
        - {"name": "config-volume", "mountPath": "/etc/nginx/nginx.conf"}
        livenessProbe: {"initialDelaySeconds": 5, "periodSeconds": 5, "httpGet": {"path": "http://127.0.0.1", "port": 80}}
        readinessProbe: {"initialDelaySeconds": 5, "periodSeconds": 5, "httpGet": {"path": "http://127.0.0.1", "port": 80}}
        resources: {"limits": {"cpu": "0.2", "memory": "0.5Gi"}}
      - name: sidecar
        image: "sidecar:{{ .Values.test-web.test-nginx.sidecar.imageVersion }}"
        imagePullPolicy: {{ .Values.test-web.test-nginx.sidecar.imagePullPolicy }}
        ports:
         - name: http
           containerPort: 80
           protocol: TCP
        command: ["/bin/exec", "fortest"]
        args: ["XXX1", "XXX2"]
        resources: {"limits": {"cpu": "0.2", "memory": "0.5Gi"}}
      volumes:
      - {"name": "config-volume", "hostPath": {"path": "/etc"}}
      - {"name": "test-config-map", "configMap": {"name": "{{ .Release.Name }}-test-cm"}}
      dnsPolicy: ClusterFirst
"""
deployment_values = {'test-nginx': {'labels': {}, 'init': {'imageVersion': 'latest',
                                                           'imagePullPolicy': 'IfNotPresent'},
                                    'replicaCount': 1, 'strategy': 'RollingUpdate',
                                    'nginx': {'imageVersion': '1.0.0', 'imagePullPolicy': 'Always',
                                              'env': {'debug': '1'}},
                                    'sidecar': {'imageVersion': 'v1',
                                                'imagePullPolicy': 'IfNotPresent'}}}

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

kube_svc_template = """
---
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-try-nginx
spec:
  type: {{ .Values.test-web.try-nginx.serviceType }}
  selector:
    app.kubernetes.io/name: "test-chart"
    app.kubernetes.io/instance: "{{ .Release.Name }}-test-web"
    app.kubernetes.io/component: "test-nginx"
    app.kubernetes.io/version: "1.0.0"
    test: "true"

  ports:
  - {"name": "http", "protocol": "TCP", "port": 80}
  - {"name": "https", "protocol": "TCP", "port": 443, "targetPort": 30443}
"""

kube_svc_values = {'try-nginx': {'serviceType': 'ClusterIP'}}

config_map = {
    "name": "test-cm",
    "data": {
        "key1": "value1",
        "key2": "value2",
    }
}

config_map_template = """
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: {{ .Release.Name }}-test-cm
data:
  key1: {{ .Values.test-web.test-cm.key1 }}
  key2: {{ .Values.test-web.test-cm.key2 }}
"""
config_map_values = {'test-cm': {'key1': 'value1', 'key2': 'value2'}}

secret = {
    "name": "test-secret",
    "data": {
        "key1": "value1",
        "key2": "value2",
    }
}
secret_template = """
---
apiVersion: v1
kind: Secret
metadata:
  name: {{ .Release.Name }}-test-secret
type: Opaque
data:
  key1: {{ .Values.test-web.test-secret.key1 }}
  key2: {{ .Values.test-web.test-secret.key2 }}
"""
secret_values = {'test-secret': {'key1': 'value1', 'key2': 'value2'}}


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
        self.assertEqual(template.template.strip(), deployment_template.strip())
        print(template.values)
        self.assertEqual(template.values, deployment_values)

    def test_render_svc(self):
        template = ResourceTemplate(
            self.chart_metadata,
            service_name="test-web", services=[])
        template.gen_kube_service(kube_svc)
        print(template.template)
        self.assertEqual(template.template.strip(), kube_svc_template.strip())
        print(template.values)
        self.assertEqual(template.values, kube_svc_values)

    def test_render_config(self):
        cm_template = ResourceTemplate(self.chart_metadata, service_name="test-web")
        sec_template = ResourceTemplate(self.chart_metadata, service_name="test-web")

        # Test gen configmap
        cm_template.gen_configmap(config_map)
        print(cm_template.template)
        self.assertEqual(cm_template.template.strip(), config_map_template.strip())
        print(cm_template.values)
        self.assertEqual(cm_template.values, config_map_values)

        # Test gen secret
        sec_template.gen_secret(secret)
        print(sec_template.template)
        self.assertEqual(sec_template.template.strip(), secret_template.strip())
        print(sec_template.values)
        self.assertEqual(sec_template.values, secret_values)
