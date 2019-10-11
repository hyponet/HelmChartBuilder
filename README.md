# HelmChartBuilder

A tool set for quickly building helm charts.

## Usage

Init chart builder with chart metadata

```python
from chart_builder import Builder

storage = {"type": "local", "source": {"path": "/Users/hypo-mbp"}}
builder = Builder("newChart", version="1.0", app_version="1.0", description="chart demo", storage=storage)
```

Add Deployment

```python
deployment = {
    "name": "test-nginx",
    "containers": [
        {
           "name": "nginx",
            "image": "nginx",
            "pull_policy": "Always",
            "ports": [
                {"containerPort": 80},
            ],
            "resources": {"limits": {"cpu": "0.2", "memory": "0.5Gi"}},
        },
    ],
}

builder.add_deployment("web", deployment)
```

Add Service
````python
kube_svc = {
    "name": "try-nginx",
    "component_name": "test-nginx",
    "type": "ClusterIP",
    "selector": {"test": "true"},
    "ports": [
        {"name": "http", "protocol": "TCP", "port": 80},
    ],

}

builder.add_kube_service("web", kube_svc)
````

Build chart

```python
builder.build_chart()
```

## Helm gRPC

```bash
git clone https://github.com/kubernetes/helm ./helm
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/chart/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/services/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/release/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/version/*
```