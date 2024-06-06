# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from typing import Any

from sphinx.application import Sphinx

from pyoda_time import __version__ as pyoda_time_version

# Project information
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Pyoda Time"
copyright = "2024, The Pyoda Time Authors"
author = "The Pyoda Time Authors"
release = pyoda_time_version

# General configuration
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    "sphinx.ext.autodoc",
]
templates_path = ["_templates"]
exclude_patterns: list[str] = []

# Options for HTML output
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_baseurl = "https://pyodatime.org/"

html_context = {
    "canonical_url": "https://pyodatime.org/",
}

html_static_path = ["_static"]

html_favicon = "_static/favicon.ico"

html_theme = "alabaster"

html_theme_options = {
    "logo_name": True,
    "logo": "pyoda-time.png",
    "touch_icon": "pyoda-time.png",
    "description": "A better date and time API for Python",
    "fixed_sidebar": True,
    "github_banner": True,
    "github_user": "chrisimcevoy",
    "github_repo": "pyoda-time",
    "body_text_align": "left",
    "logo_text_align": "center",
}

# Autodoc configuration
#
# Note that `members` and `undoc-members` directives are provided by sphinx-apidoc.
# See `docs.sphinx.html` in the repo root Makefile.
#
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options
autodoc_class_signature = "separated"
autodoc_default_options = {
    "show-inheritance": True,
    "special-members": ",".join(
        [
            "__add__",
            "__contains__",
            "__eq__",
            "__ge__",
            "__gt__",
            "__init__",
            "__iter__",
            "__le__",
            "__lt__",
            "__neg__",
            "__sub__",
        ]
    ),
}


def skip_default_special_methods(app: Sphinx, what: str, name: str, obj: Any, skip: bool, options: Any) -> bool:
    """Custom handler for the autodoc-skip-member event to skip dunder members which are inherited (e.g. from
    object)."""

    if hasattr(obj, "__qualname__") and name.startswith("__") and name.endswith("__"):
        # Check if the method is actually implemented in the current class
        # and not inherited from a parent class like `object`
        if obj.__qualname__.split(".")[0] == what:
            return False  # Do not skip, i.e., document this method

    # Default behavior
    return skip


def process_metaclass_properties(
    app: Sphinx, what: str, name: str, obj: Any, options: dict[str, Any], lines: list[str]
) -> None:
    """Custom handler for autodoc-process-docstring event to process 'class properties' defined in a metaclass."""

    if what == "class" and hasattr(obj, "__class__"):
        metaclass = type(obj)

        # Check if the metaclass is part of the 'pyoda_time' package
        if not metaclass.__module__.startswith("pyoda_time"):
            return

        for attr_name in dir(metaclass):
            if attr_name.startswith("_"):
                continue

            property_obj = getattr(metaclass, attr_name, None)

            if isinstance(property_obj, property):
                if not (property_docstring := getattr(property_obj, "__doc__")):
                    raise Exception(f"{name}.{attr_name} has no docstring")

                if not (property_annotations := getattr(property_obj.fget, "__annotations__")):
                    raise Exception(f"{name}.{attr_name} has no __annotations__")

                if not (property_return_type := property_annotations.get("return")):
                    raise Exception(f"{name}.{attr_name} has no return type annotation")

                # Prepare the documentation lines
                doc_lines = [
                    f".. py:property:: {attr_name}",
                    f"   :type: {property_return_type}",
                    "   :classmethod:",
                    "",
                ]

                # Add the property docstring, formatted as reStructuredText field lists.
                for paragraph in property_docstring.split("\n\n"):
                    # Sphinx is really finicky about whitespace, so we
                    # need to take control of that here.
                    paragraph = paragraph.strip()

                    if paragraph.startswith(":"):
                        # It's a field list, so we make sure it's properly indented.
                        current_field = ""
                        for line in paragraph.splitlines():
                            line = line.strip()
                            if line.startswith(":"):
                                if current_field:
                                    doc_lines.append(f"   {current_field.strip()}")
                                current_field = line
                            else:
                                current_field += " " + line
                        doc_lines.append(f"   {current_field.strip()}")

                    else:
                        # It's a regular line of the docstring, so we add it as is.
                        paragraph = " ".join(line.strip() for line in paragraph.splitlines())
                        doc_lines.append(f"      {paragraph}")

                    doc_lines.append("")

                lines.extend(doc_lines)


def setup(app: Sphinx) -> None:
    app.connect("autodoc-skip-member", skip_default_special_methods)
    app.connect("autodoc-process-docstring", process_metaclass_properties)
