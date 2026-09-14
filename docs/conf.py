# Configuration file for the Sphinx documentation builder.

import tomllib
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROJECT_METADATA = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())[
    "project"
]

project = "Graffiti House"
copyright = "2026, Roy Rosenzweig Center for History and New Media"
author = "Roy Rosenzweig Center for History and New Media"
description = "Django web application and code for the Graffiti House project"

version = PROJECT_METADATA["version"]
release = version

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.coverage",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "alabaster"
html_static_path = ["_static"]
html_theme_options = {
    "description": description,
    "github_user": "chnm",
    "github_repo": "graffitihouse",
    "codecov_button": True,
}
html_sidebars = {
    "**": [
        "about.html",
        "navigation.html",
        "localtoc.html",
        "searchbox.html",
        "sidebar_footer.html",
    ],
}

intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "django": ("https://docs.djangoproject.com/en/stable/", None),
}

coverage_ignore_pyobjects = [
    "clean_fields",
    "get_deferred_fields",
    "get_(next|previous)_by_(created|last_modified|modified)",
    "refresh_from_db",
    "get_.*_display",
    "get_doc_relation_list",
]
