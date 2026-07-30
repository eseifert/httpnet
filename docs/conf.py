from email.utils import parseaddr
from importlib.metadata import metadata

_metadata = metadata('httpnet')
# Authors declared in pyproject.toml end up in "Author-email" as "Name <mail>".
_author_name, _ = parseaddr(_metadata['Author-email'])

project = _metadata['Name']
author = _author_name
copyright = author
version = _metadata['Version']
release = version

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

templates_path = ['_templates']
exclude_patterns = ['_build']

# The API of the package is small enough to be presented in source order, which
# keeps the reference documentation aligned with the structure of the codebase.
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
autodoc_default_options = {
    'members': True,
    'show-inheritance': True,
}

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ('https://requests.readthedocs.io/en/stable/', None),
}

nitpicky = True
nitpick_ignore = [
    # Type variable of the generic service classes, it has no documented target.
    ('py:class', 'httpnet._core.T'),
    ('py:obj', 'httpnet._core.T'),
]

html_theme = 'furo'
html_static_path = ['_static']
html_title = f'httpnet {version}'
