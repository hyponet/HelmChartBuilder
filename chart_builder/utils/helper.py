import codecs

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
