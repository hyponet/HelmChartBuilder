import copy
import logging

from chart_builder.utils.exceptions import TemplateGenError
from .deployment import DeploymentBuilder
from .service import ServiceBuilder
from .configmap import ConfigMapBuilder
from .secret import SecretBuilder

LOG = logging.getLogger(__name__)


class ResourceTemplate(object):

    def __init__(self,
                 chart_metadata, *,
                 service_name=None,
                 deployments=None,
                 services=None,
                 configmaps=None,
                 values=None):

        self.chart_metadata = chart_metadata
        self.service_name = service_name or ""

        self._deployments = copy.deepcopy(deployments or {})
        self._services = copy.deepcopy(services or {})
        self._configmaps = copy.deepcopy(configmaps or {})

        self.build_finish = False
        self._values = copy.deepcopy(values or {})
        self._template = None

    def gen_deployment(self, deploy_payload):
        builder = DeploymentBuilder(self)
        self._gen(builder, deploy_payload)

    def gen_kube_service(self, kube_service):
        builder = ServiceBuilder(self)
        self._gen(builder, kube_service)

    def gen_configmap(self, cm_payload):
        builder = ConfigMapBuilder(self)
        self._gen(builder, cm_payload)

    def gen_secret(self, cm_payload):
        builder = SecretBuilder(self)
        self._gen(builder, cm_payload)

    def _gen(self, builder, payload):
        if self.build_finish:
            return
        builder.build(payload)
        self._template = builder.template
        self._values = self._merge_values(builder.values)
        self.build_finish = True

    @property
    def template(self):
        if not self.build_finish:
            raise TemplateGenError(self.service_name, "Do not build anything")
        return self._template

    @property
    def values(self):
        if not self.build_finish:
            raise TemplateGenError(self.service_name, "Do not build anything")
        return self._values

    def _merge_values(self, values):
        overwrite = set(values.keys()) & set(self._values.keys())
        if overwrite:
            LOG.warning("Service {} has overwrite: {}".format(self.service_name, overwrite))
        self._values.update(values)
        return self._values
