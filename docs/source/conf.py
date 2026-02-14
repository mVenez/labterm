# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
import sys, os

sys.path.insert(0, os.path.abspath('../../src'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'labterm'
copyright = '2026, Matteo Veneziano'
author = 'Matteo Veneziano'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx.ext.todo",
    "myst_parser"
]

source_suffix = [".rst", ".md"]
templates_path = ['_templates']
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
pygments_style = "sphinx"       # enable syntax highlighting

# Napoleon settings for Google-style docstrings
napoleon_google_docstring = True


add_module_names = True
autosummary_generate = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_static_path = ['_static']
html_title = 'LabTerm Documentation'

html_theme_options = {
    "navigation_with_keys": True,
    # "top_of_page_button": "edit",
    "sidebar_includehidden": True,
    "external_links": [],
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/mVenez/labterm",
            "icon": "fa-brands fa-square-github",
            "type": "fontawesome",
        },
    ],
    "show_prev_next": False,
    "search_bar_text": "Search the docs ...",
    "navigation_with_keys": False,
    "collapse_navigation": False,
    "navigation_depth": 2,
    "show_nav_level": 1,
    "show_toc_level": 1,
    "navbar_align": "left",
    "header_links_before_dropdown": 5,
    "header_dropdown_text": "More",
    "pygments_light_style": "tango",
    "pygments_dark_style": "monokai",
}

html_sidebars = {   # removes the left sidebar on these pages
    "user_guide": [],  
    "install" : []
}

highlight_language = "python"