import yaml
import logging

from hapi.chart.metadata_pb2 import Metadata
from hapi.chart.chart_pb2 import Chart
from chart_builder.storage import Storage
from hapi.chart.config_pb2 import Config
from hapi.chart.template_pb2 import Template
from chart_builder.resources import ResourceTemplate

LOG = logging.getLogger(__name__)


class Builder(object):
    def __init__(self, chart_name, version, app_version, description, storage):
        self.chart_name = chart_name
        self.version = version
        self.app_version = app_version
        self.description = description
        self.dependencies = []
        self.template_files = []
        self.non_template_files = []

        self.storage = Storage(
            storage_type=storage['type'],
            source=storage['source'],
        )

        self._templates = {
            "configmaps": [],
            "secrets": [],
        }
        self._values = {}
        self._services = {}
        self.chart_metadata = self._get_metadata()
        self._chart = None

        self.storage.init_workdir(chart_name)

    def add_deployment(self, service_name, deployment):
        if service_name not in self._services:
            self._create_service(service_name)
        generator = ResourceTemplate(
            self.chart_metadata,
            values=self._values[service_name],
            **self._services[service_name])
        generator.gen_deployment(deployment)

        self._services[service_name]["deployments"].append(generator.template)
        self._values[service_name] = generator.values

    def add_kube_service(self, service_name, kube_service):
        if service_name not in self._services:
            self._create_service(service_name)
        generator = ResourceTemplate(
            self.chart_metadata,
            values=self._values[service_name],
            **self._services[service_name])
        generator.gen_kube_service(kube_service)

        self._services[service_name]["services"].append(generator.template)
        self._values[service_name] = generator.values

    def add_configmap(self, configmap):
        generator = ResourceTemplate(self.chart_metadata, values=self._values, **self._templates)
        generator.gen_configmap(configmap)

        self._templates["configmaps"].append(generator.template)
        self._values = generator.values

    def add_secret(self, secret):
        generator = ResourceTemplate(self.chart_metadata, values=self._values, **self._templates)
        generator.gen_configmap(secret)

        self._templates["secrets"].append(generator.template)
        self._values = generator.values

    def set_dependencies(self, dependencies):
        self.dependencies = dependencies

    def _create_service(self, service_name):
        self._services[service_name] = {
            "service_name": service_name,
            "labels": {},
        }

        self._services[service_name]['deployments'] = []
        self._services[service_name]['services'] = []
        self._values[service_name] = {}

    def _update_template(self):
        for svc_name, rsc in self._services.items():
            file_name = "templates/{}_{}.yaml"

            for rsc_type in ['deployments', 'services']:
                _fn = file_name.format(svc_name, rsc_type)
                self.template_files.append(_fn)
                self.storage.write(
                    "{}/{}".format(self.chart_name, _fn),
                    "\n".join(rsc[rsc_type]),
                )

        file_name = "templates/{}.yaml"
        for rsc_type in ['configmaps', 'secrets']:
            _fn = file_name.format(rsc_type)
            self.template_files.append(_fn)
            self.storage.write(
                "{}/{}".format(self.chart_name, _fn),
                "\n".join(self._templates[rsc_type]),
            )

    def _update_value(self):
        return self.storage.write(
            "{}/values.yaml".format(self.chart_name), yaml.dump(self._values))

    def _update_metadata(self):
        metadata = self.chart_metadata
        chart_yaml = {
            "apiVersion": metadata.apiVersion,
            "name": metadata.name,
            "version": metadata.version,
            "appVersion": metadata.appVersion,
            "description": metadata.description,
        }
        self.storage.write("{}/Chart.yaml".format(self.chart_name), yaml.dump(chart_yaml))

    def _get_metadata(self):
        return Metadata(
            apiVersion="v1",
            name=self.chart_name,
            version=str(self.version),
            appVersion=str(self.app_version),
            description=self.description,
        )

    def _get_templates(self):
        templates = []
        for t_name in self.template_files:
            templates.append(Template(
                name=t_name,
                data=self.storage.read("{}/{}".format(self.chart_name, t_name))
            ))
        return templates

    def _get_values(self):
        return Config(raw=self.storage.read("values.yaml"))

    def push(self):
        self.storage.work_dir.push()

    def build_chart(self):
        self._update_metadata()
        self._update_value()
        self._update_template()

        templates = self._get_templates()
        values = self._get_values()

        chart = Chart(
            templates=templates,
            values=values,
            metadata=self.chart_metadata,
            files=self.non_template_files,
            dependencies=self.dependencies,
        )
        self._chart = chart
        return chart
