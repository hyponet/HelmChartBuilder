# HelmChartBuilder

A tool set for quickly building helm charts.

## Usage

```python
from chart_builder import Builder

storage = {"type": "local", "source": {"path": "/workdir"}}
builder = Builder("newChart", version="1.0", app_version="1.0", description="chart demo", storage=storage)
```

## Helm gRPC

```bash
git clone https://github.com/kubernetes/helm ./helm
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/chart/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/services/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/release/*
python -m grpc_tools.protoc -I helm/_proto --python_out=. --grpc_python_out=. ./helm/_proto/hapi/version/*
```