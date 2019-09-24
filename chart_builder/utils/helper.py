import codecs
from jsonschema import validate, ValidationError

from .exceptions import DateSchemaValidationError

HELM_IGNORE = """
# Patterns to ignore when building packages.
# This supports shell glob matching, relative path matching, and
# negation (prefixed with !). Only one pattern per line.
.DS_Store
# Common VCS dirs
.git/
.gitignore
.bzr/
.bzrignore
.hg/
.hgignore
.svn/
# Common backup files
*.swp
*.bak
*.tmp
*~
# Various IDEs
.project
.idea/
*.tmproj
"""


def read_file(path):
    with codecs.open(path, encoding='utf-8', errors='ignore') as fd:
        content = fd.read()
    return bytes(bytearray(content, encoding='utf-8'))


def write_file(path, content):
    with codecs.open(path, mode='w', encoding='utf-8', errors='ignore') as fd:
        fd.write(content)


def get_default_helm_ignore():
    return HELM_IGNORE


def resource_payload_validator(resource_name, schema, payload):
    """
    验证 request.json 中的数据是否合法
    schema 符合： http://json-schema.org
    :param resource_name:
    :param schema:
    :param payload:
    :return:
    """

    try:
        validate(payload, schema)
    except ValidationError as e:
        raise DateSchemaValidationError(resource_name, e)

    return payload
