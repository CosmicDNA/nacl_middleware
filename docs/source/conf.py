# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "NaCl Middleware"
copyright = "2024, Daniel de Souza"
author = "Daniel de Souza"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx_copybutton",
    "sphinx_favicon",
    "sphinx_reredirects",
    "sphinx_toolbox.collapse",
    "sphinx_toolbox.github",
    "sphinx_toolbox.sidebar_links",
    "sphinx_toolbox.tweaks.param_dash",
]

# GitHub-related options
github_username = "CosmicDNA"
github_repository = "nacl_middleware"

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"

SHARED_CSS_VARIABLES = {
    "admonition-font-size": "1rem",
    "admonition-title-font-size": "1rem",
    "sidebar-item-font-size": "115%",
}

html_theme_options = {
    "light_css_variables": {
        "font-stack--monospace": "Inconsolata,Consolas,ui-monospace,monospace",
        "at-color": "#830b2b",
        "at-val-color": "#bc103e",
        "body-color": "#14234b",
        "color-highlight-on-target": "#e5e8ed",
        "primary-header-color": "#0053d6",
        "row-odd-background-color": "#f0f3f7",
        "rst-content-a-color": "#2980b9",
        "secondary-header-color": "#123693",
        "wy-menu-vertical-background-color": "#0053d6",
        "wy-menu-vertical-color": "white",
        "wy-nav-side-background-color": "#0053d6",
    },
    "dark_css_variables": {
        "at-color": "#ffaab7",
        "at-val-color": "#ff95a6",
        "body-color": "#14234b",
        "color-admonition-background": "#1e1e21",
        "color-highlight-on-target": "#3d4045",
        "primary-header-color": "#a8caff",
        "row-odd-background-color": "#222326",
        "rst-content-a-color": "#2980b9",
        "secondary-header-color": "#458dff",
        "wy-menu-vertical-background-color": "#0053d6",
        "wy-menu-vertical-color": "white",
        "wy-nav-side-background-color": "#0053d6",
    },
}

for v in html_theme_options.values():
    if isinstance(v, dict):
        v.update(SHARED_CSS_VARIABLES)

pygments_style = "default"
pygments_dark_style = "monokai"

html_static_path = ["_static"]

sys.path.insert(0, os.path.abspath("../../"))
