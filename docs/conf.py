# Configuration file for the Sphinx documentation builder.

import os
import sys

# -- Path setup --------------------------------------------------------------
# Add src directory to Python path (ensure correct path to your package)
sys.path.insert(0, os.path.abspath('../src'))  # Your code
sys.path.insert(0, os.path.abspath('../../robolab_turtlebot/src/robolab_turtlebot'))  # Path to Turtle repo

# -- Project information -----------------------------------------------------
project = 'LAR_Messi'
copyright = '2025, Adam Hendrych, David Horňáček, Adam Hejtmánek'
author = 'Adam Hendrych, David Horňáček, Adam Hejtmánek'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',       # Core documentation generator
    'sphinx.ext.viewcode',      # Add links to source code
    'sphinx.ext.napoleon',      # Google-style docstring support
    'sphinx.ext.autosummary',   # Generate API summary
]

# Napoleon settings (Google-style docstrings)
napoleon_google_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False  # Disabled by default (avoid exposing private members)
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,   # Add class inheritance info
}

# Autosummary settings (generate stub files automatically)
autosummary_generate = True

# Exclude patterns (files/dirs to ignore)
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'  # Note: underscore, not hyphen!
html_static_path = ['_static']
html_show_sourcelink = True      # Add "View page source" links

# Theme-specific options (optional)
html_theme_options = {
    'navigation_depth': 4,       # Expand sidebar depth
    'collapse_navigation': False # Keep sidebar expanded
}