#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# LinSpectacles - Linux Inspection Suite
# Copyright (C) 2026 brunonlinespace
# GPL-3.0-or-later

APPLET_ID = 'linspectacles-python-packages'
APPLET_NAME = 'Python Packages'
APPLET_VERSION = '0.0.8'
APPLET_AUTHOR = "brunonlinespace"
APPLET_EDITOR = "brunonlinespace"
APPLET_PUBLISHER = "brunonlinespace"
APPLET_ORGANIZATION_ID = "linspectacles"
APPLET_ORGANIZATION_URL = "https://github.com/linspectacles/"
APPLET_REPOSITORY = "https://github.com/linspectacles/python-packages"

import importlib.metadata
import re
from pathlib import Path

from PyQt6.QtCore import QSettings, Qt, QUrl
from PyQt6.QtGui import QBrush, QColor, QFont, QKeySequence, QPixmap, QShortcut, QTextCharFormat, QTextCursor
from PyQt6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout,
    QLabel, QMessageBox, QPushButton, QTabWidget, QTextEdit, QVBoxLayout, QWidget,
)
from ._support import BaseInspectorTab, export_records_dialog, metadata_font_qss


def _sources_text():
    return """Python package inventory
------------------------
Primary interface: Python standard library importlib.metadata
Inventory: importlib.metadata.distributions()
Version: Distribution.version
Package metadata: Distribution.metadata

Record details
--------------
The Metadata Details pane displays fields reported by the selected distribution's Distribution.metadata mapping.

Category classification
-----------------------
Category is a local LinSpectacles classification. Classification prefers known package identities, then considers package metadata reported through Distribution.metadata (Summary, Keywords and Classifier fields), with package-name heuristics as a fallback. It is not package-manager metadata and does not modify the Python environment.

Access model
------------
Read-only. Python Packages does not install, remove, upgrade, or modify distributions.
"""


def _apply_sources_colouring(canvas):
    """Use the Journal Inspector's bold-blue source-heading treatment."""
    heading_format = QTextCharFormat()
    heading_format.setForeground(QColor("#9cdcfe"))
    heading_format.setFontWeight(QFont.Weight.Bold.value)

    block = canvas.document().firstBlock()
    while block.isValid():
        text = block.text().strip()
        next_block = block.next()
        next_text = next_block.text().strip() if next_block.isValid() else ""
        if text and next_text and set(next_text) == {"-"}:
            cursor = QTextCursor(block)
            cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
            cursor.mergeCharFormat(heading_format)
        block = block.next()

    canvas.moveCursor(QTextCursor.MoveOperation.Start)


def _metadata_details_plain_text(record):
    dist = record.get("distribution") if isinstance(record, dict) else None
    try:
        if dist is None:
            dist = importlib.metadata.distribution(str(record.get("name", "")))
        lines = []
        for key, value in dist.metadata.items():
            if value:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)
    except Exception as exc:
        return f"Error: {exc}"


class PythonPackagesOptionsDialog(QDialog):
    """Established LinSpectacles Options treatment for Python Packages."""

    def __init__(self, owner):
        super().__init__(owner)
        self.owner = owner
        self.setWindowTitle("Options — Python Packages")
        self.resize(980, 720)

        root = QVBoxLayout(self)
        tabs = QTabWidget()
        root.addWidget(tabs, 1)

        # Appearance
        appearance_page = QWidget()
        appearance_layout = QVBoxLayout(appearance_page)
        appearance_layout.setContentsMargins(12, 12, 12, 12)
        appearance_layout.setSpacing(10)

        appearance_heading = QLabel("Metadata display")
        appearance_heading_font = appearance_heading.font()
        appearance_heading_font.setBold(True)
        appearance_heading.setFont(appearance_heading_font)
        appearance_layout.addWidget(appearance_heading)

        appearance_note = QLabel(
            "Choose how the inventory and Metadata Details panes are arranged. "
            "This Python Packages setting is remembered."
        )
        appearance_note.setWordWrap(True)
        appearance_layout.addWidget(appearance_note)

        layout_row = QHBoxLayout()
        layout_row.addWidget(QLabel("Record details layout:"))
        self.layout_combo = QComboBox()
        self.layout_combo.addItems(["Horizontal", "Vertical"])
        self.layout_combo.setCurrentText(
            "Vertical" if owner.details_orientation == "vertical" else "Horizontal"
        )
        self.layout_combo.currentTextChanged.connect(self._layout_changed)
        layout_row.addWidget(self.layout_combo)
        layout_row.addStretch(1)
        appearance_layout.addLayout(layout_row)

        self.show_metadata_panel = QCheckBox("Show Metadata Details panel (F3)")
        self.show_metadata_panel.setChecked(owner.metadata_panel_visible)
        self.show_metadata_panel.toggled.connect(self._metadata_panel_changed)
        appearance_layout.addWidget(self.show_metadata_panel)

        shortcuts_note = QLabel(
            "Shortcuts: F3 shows/hides Metadata Details; Ctrl+L switches "
            "Horizontal/Vertical; Shift+F5 scans again; Ctrl+/ opens Options; "
            "Ctrl+F focuses Search."
        )
        shortcuts_note.setWordWrap(True)
        appearance_layout.addWidget(shortcuts_note)
        appearance_layout.addStretch(1)
        tabs.addTab(appearance_page, "Appearance")

        # Sources
        sources_page = QWidget()
        sources_layout = QVBoxLayout(sources_page)
        sources_layout.setContentsMargins(12, 12, 12, 12)
        sources_layout.setSpacing(10)

        sources_heading = QLabel("Data Sources")
        sources_heading_font = sources_heading.font()
        sources_heading_font.setBold(True)
        sources_heading_font.setPointSize(max(sources_heading_font.pointSize(), 11))
        sources_heading.setFont(sources_heading_font)
        sources_layout.addWidget(sources_heading)

        sources_note = QLabel(
            "Python interfaces and local interpretation used by this read-only applet."
        )
        sources_note.setWordWrap(True)
        sources_layout.addWidget(sources_note)

        sources_text = QTextEdit()
        sources_text.setReadOnly(True)
        sources_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        chosen_font = getattr(owner, "_metadata_font", None)
        if chosen_font is not None:
            sources_text.setFont(chosen_font)
            sources_text.document().setDefaultFont(chosen_font)
            sources_text.setCurrentFont(chosen_font)
            font_rule = metadata_font_qss(chosen_font)
        else:
            font_rule = ""
        sources_text.setStyleSheet(
            "QTextEdit { "
            + font_rule
            + " background-color: #151719; color: #dcdcdc; "
              "border: 1px solid #333333; }"
        )
        sources_text.setPlainText(_sources_text())
        _apply_sources_colouring(sources_text)
        sources_layout.addWidget(sources_text, 1)
        tabs.addTab(sources_page, "Sources")

        # Export
        export_page = QWidget()
        export_layout = QVBoxLayout(export_page)
        export_layout.setContentsMargins(12, 12, 12, 12)
        export_layout.setSpacing(10)

        export_heading = QLabel("Export details")
        export_heading_font = export_heading.font()
        export_heading_font.setBold(True)
        export_heading.setFont(export_heading_font)
        export_layout.addWidget(export_heading)

        export_note = QLabel(
            "Select the Python Packages details to include in the export."
        )
        export_note.setWordWrap(True)
        export_layout.addWidget(export_note)

        self.export_name = QCheckBox("Package Name")
        self.export_category = QCheckBox("Category")
        self.export_version = QCheckBox("Version")
        self.export_summary = QCheckBox("Summary")
        self.export_metadata = QCheckBox("Metadata Details")
        for checkbox in (
            self.export_name,
            self.export_category,
            self.export_version,
            self.export_summary,
        ):
            checkbox.setChecked(True)
            export_layout.addWidget(checkbox)
        self.export_metadata.setChecked(False)
        export_layout.addWidget(self.export_metadata)

        export_layout.addStretch(1)
        export_row = QHBoxLayout()
        export_row.addStretch(1)
        export_button = QPushButton("Export...")
        export_button.clicked.connect(self._export_selected)
        export_row.addWidget(export_button)
        export_layout.addLayout(export_row)
        tabs.addTab(export_page, "Export")

        # About
        about_page = QWidget()
        about_layout = QVBoxLayout(about_page)
        about_layout.setContentsMargins(24, 20, 24, 18)
        about_layout.setSpacing(8)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(112, 112)
        icon_path = Path(__file__).resolve().parent / "icon.png"
        if icon_path.is_file():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                icon_label.setPixmap(
                    pixmap.scaled(
                        112,
                        112,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
        about_layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        name = QLabel("<h2 style='margin:0'>Python Packages</h2>")
        name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(name)

        version = QLabel(f"Version {APPLET_VERSION}")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(version)

        slogan = QLabel("<b>Expose. Explore. Explain.</b>")
        slogan.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(slogan)

        description = QLabel(
            "A read-only LinSpectacles applet for explicitly scanning Python distributions "
            "and inspecting their reported package metadata."
        )
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(description)

        details = QLabel(
            "<b>Build:</b> Standalone LinSpectacles applet<br>"
            "<b>Organisation ID:</b> "
            f"<a href='{APPLET_ORGANIZATION_URL}'>{APPLET_ORGANIZATION_ID}</a><br>"
            f"<b>Applet ID:</b> {APPLET_ID}"
        )
        details.setWordWrap(True)
        details.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
            | Qt.TextInteractionFlag.TextSelectableByMouse
        )
        details.setOpenExternalLinks(True)
        details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(details)

        copyright_label = QLabel(
            "Copyright © 2026 "
            "<a href='https://github.com/brunonlinespace'>brunonlinespace</a>"
        )
        copyright_label.setOpenExternalLinks(True)
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(copyright_label)

        license_label = QLabel("Licensed under GNU GPLv3 or later.")
        license_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(license_label)

        readme_url = QUrl.fromLocalFile(
            str(Path(__file__).resolve().parent.parent / "README.md")
        ).toString()
        license_url = QUrl.fromLocalFile(
            str(Path(__file__).resolve().parent.parent / "LICENSE")
        ).toString()
        links = QLabel(
            f"<a href='{readme_url}'>README</a> &nbsp;·&nbsp; "
            f"<a href='{license_url}'>License</a> &nbsp;·&nbsp; "
            f"<a href='{APPLET_REPOSITORY}'>Repository</a>"
        )
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(links)
        about_layout.addStretch(1)
        tabs.addTab(about_page, "About")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _layout_changed(self, text):
        self.owner.set_details_orientation(str(text).strip().lower(), persist=True)

    def _metadata_panel_changed(self, visible):
        self.owner.set_metadata_panel_visible(bool(visible), persist=True)

    def _export_selected(self):
        selected = []
        if self.export_name.isChecked():
            selected.append(("name", "Package Name", 170, "left"))
        if self.export_category.isChecked():
            selected.append(("category", "Category", 140, "left"))
        if self.export_version.isChecked():
            selected.append(("version", "Version", 90, "right"))
        if self.export_summary.isChecked():
            selected.append(("summary", "Summary", 220, "left"))
        if self.export_metadata.isChecked():
            selected.append(("metadata_details", "Metadata Details", 520, "left"))

        if not selected:
            QMessageBox.information(
                self, "Export", "Select at least one detail to export."
            )
            return

        source_records = self.owner.get_export_records()
        if not source_records:
            QMessageBox.information(
                self, "Export", "There is no collected data to export yet."
            )
            return

        records = []
        for record in source_records:
            item = dict(record)
            if self.export_metadata.isChecked():
                item["metadata_details"] = _metadata_details_plain_text(record)
            records.append(item)

        path = export_records_dialog(self, APPLET_NAME, records, columns=selected)
        if path is not None:
            self.owner.set_status(f"Exported data to {path}")


class PythonTab(BaseInspectorTab):
    """Python distribution inventory. Scanning is always explicit."""

    # Category colours use only the authoritative Kernel Modules palette.
    CATEGORY_COLORS = {
        "AI / Machine Learning": "#c586c0",
        "Async / Concurrency": "#9cdcfe",
        "Build / Packaging": "#b5cea8",
        "CLI / Terminal": "#dcdcaa",
        "Data / Scientific": "#c586c0",
        "Data Models / Validation": "#4ec9b0",
        "Database / Storage": "#ce9178",
        "Development Tools": "#dcdcaa",
        "Documentation / Interactive": "#9cdcfe",
        "Documents / File Formats": "#ce9178",
        "Geospatial / GIS": "#4ec9b0",
        "GUI / Desktop": "#4ec9b0",
        "Logging / Observability": "#9cdcfe",
        "Media / Graphics": "#dcdcaa",
        "Parsing / Templating": "#ce9178",
        "Runtime / Compatibility": "#b5cea8",
        "Security / Cryptography": "#ce9178",
        "Serialization / Data Formats": "#9cdcfe",
        "System / OS / Process": "#b5cea8",
        "Testing / QA": "#dcdcaa",
        "Utilities / Infrastructure": "#b5cea8",
        "Web / Network": "#4ec9b0",
        "Web Frameworks / APIs": "#4ec9b0",
        "Other / Uncategorized": "#9a9a9a",
    }

    CATEGORY_ORDER = (
        "AI / Machine Learning",
        "Async / Concurrency",
        "Build / Packaging",
        "CLI / Terminal",
        "Data / Scientific",
        "Data Models / Validation",
        "Database / Storage",
        "Development Tools",
        "Documentation / Interactive",
        "Documents / File Formats",
        "Geospatial / GIS",
        "GUI / Desktop",
        "Logging / Observability",
        "Media / Graphics",
        "Parsing / Templating",
        "Runtime / Compatibility",
        "Security / Cryptography",
        "Serialization / Data Formats",
        "System / OS / Process",
        "Testing / QA",
        "Utilities / Infrastructure",
        "Web / Network",
        "Web Frameworks / APIs",
        "Other / Uncategorized",
    )

    EXACT_PACKAGE_CATEGORIES = {
        # AI / machine learning
        "scikit-learn": "AI / Machine Learning", "sklearn": "AI / Machine Learning",
        "torch": "AI / Machine Learning", "torchvision": "AI / Machine Learning",
        "tensorflow": "AI / Machine Learning", "keras": "AI / Machine Learning",
        "transformers": "AI / Machine Learning", "xgboost": "AI / Machine Learning",
        "lightgbm": "AI / Machine Learning", "jax": "AI / Machine Learning",
        # scientific / data
        "numpy": "Data / Scientific", "pandas": "Data / Scientific",
        "scipy": "Data / Scientific", "polars": "Data / Scientific",
        "sympy": "Data / Scientific", "statsmodels": "Data / Scientific",
        # validation / models
        "pydantic": "Data Models / Validation", "marshmallow": "Data Models / Validation",
        "cerberus": "Data Models / Validation", "voluptuous": "Data Models / Validation",
        # web frameworks / APIs
        "django": "Web Frameworks / APIs", "flask": "Web Frameworks / APIs",
        "fastapi": "Web Frameworks / APIs", "starlette": "Web Frameworks / APIs",
        "sanic": "Web Frameworks / APIs", "bottle": "Web Frameworks / APIs",
        "falcon": "Web Frameworks / APIs", "tornado": "Web Frameworks / APIs",
        # web / network
        "requests": "Web / Network", "urllib3": "Web / Network",
        "httpx": "Web / Network", "aiohttp": "Web / Network",
        "websockets": "Web / Network", "websocket-client": "Web / Network",
        "dnspython": "Web / Network", "paramiko": "Web / Network",
        # database / storage
        "sqlalchemy": "Database / Storage", "psycopg2": "Database / Storage",
        "psycopg2-binary": "Database / Storage", "pymysql": "Database / Storage",
        "mysqlclient": "Database / Storage", "redis": "Database / Storage",
        "pymongo": "Database / Storage", "lmdb": "Database / Storage",
        # testing
        "pytest": "Testing / QA", "tox": "Testing / QA",
        "coverage": "Testing / QA", "hypothesis": "Testing / QA",
        "mock": "Testing / QA", "nose": "Testing / QA",
        # build / packaging
        "pip": "Build / Packaging", "setuptools": "Build / Packaging",
        "wheel": "Build / Packaging", "packaging": "Build / Packaging",
        "build": "Build / Packaging", "hatchling": "Build / Packaging",
        "poetry-core": "Build / Packaging", "flit-core": "Build / Packaging",
        # developer tools
        "black": "Development Tools", "ruff": "Development Tools",
        "flake8": "Development Tools", "pylint": "Development Tools",
        "mypy": "Development Tools", "pyright": "Development Tools",
        "isort": "Development Tools", "pre-commit": "Development Tools",
        "debugpy": "Development Tools",
        # CLI / terminal
        "click": "CLI / Terminal", "typer": "CLI / Terminal",
        "rich": "CLI / Terminal", "prompt-toolkit": "CLI / Terminal",
        "textual": "CLI / Terminal", "colorama": "CLI / Terminal",
        # GUI / desktop
        "pyqt6": "GUI / Desktop", "pyside6": "GUI / Desktop",
        "pygobject": "GUI / Desktop", "wxpython": "GUI / Desktop",
        # media / graphics
        "matplotlib": "Media / Graphics", "seaborn": "Media / Graphics",
        "plotly": "Media / Graphics", "bokeh": "Media / Graphics",
        "pillow": "Media / Graphics", "opencv-python": "Media / Graphics",
        "imageio": "Media / Graphics",
        # parsing / templating
        "jinja2": "Parsing / Templating", "mako": "Parsing / Templating",
        "beautifulsoup4": "Parsing / Templating", "lxml": "Parsing / Templating",
        "markdown": "Parsing / Templating", "mistune": "Parsing / Templating",
        # serialization / formats
        "pyyaml": "Serialization / Data Formats", "tomlkit": "Serialization / Data Formats",
        "tomli": "Serialization / Data Formats", "orjson": "Serialization / Data Formats",
        "ujson": "Serialization / Data Formats", "msgpack": "Serialization / Data Formats",
        "protobuf": "Serialization / Data Formats",
        # security
        "cryptography": "Security / Cryptography", "pyopenssl": "Security / Cryptography",
        "bcrypt": "Security / Cryptography", "pynacl": "Security / Cryptography",
        "passlib": "Security / Cryptography", "pyjwt": "Security / Cryptography",
        # system / OS
        "psutil": "System / OS / Process", "distro": "System / OS / Process",
        "pyudev": "System / OS / Process", "dbus-python": "System / OS / Process",
        "systemd-python": "System / OS / Process",
        # async / concurrency
        "anyio": "Async / Concurrency", "trio": "Async / Concurrency",
        "gevent": "Async / Concurrency", "greenlet": "Async / Concurrency",
        "uvloop": "Async / Concurrency",
        # documentation / interactive
        "sphinx": "Documentation / Interactive", "mkdocs": "Documentation / Interactive",
        "jupyter": "Documentation / Interactive", "notebook": "Documentation / Interactive",
        "ipython": "Documentation / Interactive", "nbformat": "Documentation / Interactive",
        "nbclient": "Documentation / Interactive", "nbconvert": "Documentation / Interactive",
        # documents / file formats
        "openpyxl": "Documents / File Formats", "odfpy": "Documents / File Formats",
        "python-docx": "Documents / File Formats", "docx2txt": "Documents / File Formats",
        "pypdf": "Documents / File Formats", "pypdfium2": "Documents / File Formats",
        "pdfplumber": "Documents / File Formats", "pymupdf": "Documents / File Formats",
        "camelot-py": "Documents / File Formats",
        # geospatial / GIS
        "geopandas": "Geospatial / GIS", "shapely": "Geospatial / GIS",
        "fiona": "Geospatial / GIS", "rasterio": "Geospatial / GIS",
        "pyproj": "Geospatial / GIS", "geopy": "Geospatial / GIS",
        "pyogrio": "Geospatial / GIS", "affine": "Geospatial / GIS",
        # logging / observability
        "loguru": "Logging / Observability", "structlog": "Logging / Observability",
        "datadog": "Logging / Observability", "ddtrace": "Logging / Observability",
        "prometheus-client": "Logging / Observability",
        "opentelemetry-api": "Logging / Observability",
        "opentelemetry-sdk": "Logging / Observability",
        "opentelemetry-proto": "Logging / Observability",
        "opentelemetry-semantic-conventions": "Logging / Observability",
        "opentelemetry-exporter-otlp": "Logging / Observability",
        "opentelemetry-exporter-otlp-proto-common": "Logging / Observability",
        "opentelemetry-exporter-otlp-proto-grpc": "Logging / Observability",
        # runtime / compatibility
        "attrs": "Runtime / Compatibility", "six": "Runtime / Compatibility",
        "typing-extensions": "Runtime / Compatibility", "importlib-metadata": "Runtime / Compatibility",
        "importlib-resources": "Runtime / Compatibility", "platformdirs": "Runtime / Compatibility",
        "filelock": "Runtime / Compatibility", "zipp": "Runtime / Compatibility",
        "exceptiongroup": "Runtime / Compatibility",
        # utilities / infrastructure
        "more-itertools": "Utilities / Infrastructure", "cachetools": "Utilities / Infrastructure",
        "decorator": "Utilities / Infrastructure", "deprecated": "Utilities / Infrastructure",
        "toolz": "Utilities / Infrastructure", "boltons": "Utilities / Infrastructure",
        "fsspec": "Utilities / Infrastructure", "cloudpickle": "Utilities / Infrastructure",
        "joblib": "Utilities / Infrastructure", "multidict": "Utilities / Infrastructure",
        "frozenlist": "Utilities / Infrastructure", "propcache": "Utilities / Infrastructure",
        "cffi": "Utilities / Infrastructure",
        # common family members
        "cython": "Development Tools", "jedi": "Development Tools",
        "asttokens": "Development Tools", "executing": "Development Tools",
        "pure-eval": "Development Tools", "pycparser": "Parsing / Templating",
        "antlr4-python3-runtime": "Parsing / Templating", "pyparsing": "Parsing / Templating",
        "regex": "Parsing / Templating", "pygments": "Parsing / Templating",
        "boto3": "Web / Network", "botocore": "Web / Network",
        "grpcio": "Web / Network", "h2": "Web / Network", "hpack": "Web / Network",
        "hyperframe": "Web / Network", "oauthlib": "Security / Cryptography",
        "certifi": "Web / Network", "charset-normalizer": "Web / Network",
        "chardet": "Web / Network", "idna": "Web / Network",
        "jaxlib": "AI / Machine Learning", "numba": "Data / Scientific",
        "mpmath": "Data / Scientific", "arviz": "Data / Scientific",
        "arviz-base": "Data / Scientific", "biopython": "Data / Scientific",
        "networkx": "Data / Scientific",
    }

    CLASSIFIER_RULES = (
        ("AI / Machine Learning", ("topic :: scientific/engineering :: artificial intelligence",)),
        ("Geospatial / GIS", ("topic :: scientific/engineering :: gis",)),
        ("Data / Scientific", ("topic :: scientific/engineering",)),
        ("Database / Storage", ("topic :: database",)),
        ("Testing / QA", ("topic :: software development :: testing", "topic :: software development :: quality assurance")),
        ("Build / Packaging", ("topic :: software development :: build tools",)),
        ("Development Tools", ("topic :: software development :: debuggers",)),
        ("Documentation / Interactive", ("topic :: documentation", "framework :: jupyter")),
        ("Media / Graphics", ("topic :: multimedia",)),
        ("Security / Cryptography", ("topic :: security",)),
        ("System / OS / Process", ("topic :: system :: monitoring", "topic :: system :: systems administration")),
        ("Parsing / Templating", ("topic :: text processing",)),
        ("CLI / Terminal", ("environment :: console",)),
        ("Async / Concurrency", ("framework :: asyncio",)),
        ("Web Frameworks / APIs", ("framework :: django", "framework :: flask", "framework :: fastapi")),
        ("Web / Network", ("topic :: internet", "topic :: communications")),
    )

    CLASSIFICATION_RULES = (
        ("AI / Machine Learning", (
            "artificial intelligence", "machine learning", "deep learning",
            "neural network", "transformer model", "computer vision model",
        )),
        ("Data / Scientific", (
            "scientific engineering", "scientific computing", "numerical computing",
            "data analysis", "statistics", "dataframe", "array computing",
        )),
        ("Data Models / Validation", (
            "data validation", "schema validation", "data model", "validation library",
        )),
        ("Web Frameworks / APIs", (
            "framework django", "framework flask", "web framework", "asgi framework",
            "wsgi framework", "rest api", "api framework",
        )),
        ("Database / Storage", (
            "database", "sql", "postgresql", "mysql", "mongodb", "redis",
            "orm", "object relational", "key value store",
        )),
        ("Testing / QA", (
            "software development testing", "testing framework", "test runner",
            "code coverage", "property based testing", "mocking",
        )),
        ("Build / Packaging", (
            "software development build tools", "build backend",
            "package installer", "packaging tool", "wheel builder", "distribution builder",
        )),
        ("Development Tools", (
            "software development quality assurance", "linter", "formatter",
            "type checker", "static analysis", "debugger", "developer tool",
        )),
        ("CLI / Terminal", (
            "command line", "command-line", "terminal", "console application",
            "cli framework", "terminal ui",
        )),
        ("Documents / File Formats", (
            "pdf", "office document", "spreadsheet", "xlsx", "docx", "odf",
        )),
        ("Geospatial / GIS", (
            "geospatial", "geographic information system", "gis", "cartographic",
        )),
        ("GUI / Desktop", (
            "desktop environment", "graphical user interface", "gui toolkit",
            "qt bindings", "gtk bindings", "desktop application",
        )),
        ("Logging / Observability", (
            "observability", "telemetry", "tracing", "metrics", "structured logging",
            "prometheus", "opentelemetry",
        )),
        ("Media / Graphics", (
            "image processing", "graphics", "visualization", "visualisation",
            "plotting", "audio processing", "video processing", "multimedia",
        )),
        ("Parsing / Templating", (
            "parser", "parsing", "template engine", "templating", "markup",
            "html parser", "xml parser",
        )),
        ("Serialization / Data Formats", (
            "serialization", "serialisation", "json", "yaml", "toml",
            "protocol buffers", "messagepack", "data format",
        )),
        ("Security / Cryptography", (
            "security", "cryptography", "encryption", "tls", "ssl",
            "authentication", "authorization", "hashing", "password",
        )),
        ("System / OS / Process", (
            "system administration", "process management",
            "filesystem monitoring", "udev", "dbus", "hardware monitoring",
        )),
        ("Async / Concurrency", (
            "asynchronous", "asyncio", "concurrency", "event loop",
            "coroutine", "greenlet",
        )),
        ("Documentation / Interactive", (
            "documentation", "sphinx", "mkdocs", "jupyter", "notebook",
            "interactive computing",
        )),
        ("Web / Network", (
            "http client", "http library", "networking", "network protocol",
            "websocket", "dns", "ssh", "url", "web client",
        )),
        ("Runtime / Compatibility", (
            "compatibility", "backport", "runtime support", "typing extensions",
            "platform directories", "importlib",
        )),
        ("Utilities / Infrastructure", (
            "utility library", "helper library", "caching", "plugin system",
            "filesystem abstraction", "dependency utilities",
        )),
    )

    NAME_FALLBACK_RULES = (
        ("Testing / QA", ("pytest", "tox", "coverage", "hypothesis", "unittest", "testing")),
        ("Build / Packaging", ("pip", "setuptools", "wheel", "packag", "build")),
        ("AI / Machine Learning", ("torch", "tensor", "keras", "sklearn", "scikit", "transformer")),
        ("Data / Scientific", ("numpy", "pandas", "scipy", "polars", "stats")),
        ("Web Frameworks / APIs", ("django", "flask", "fastapi", "starlette")),
        ("Web / Network", ("http", "urllib", "request", "socket", "websocket", "dns")),
        ("Database / Storage", ("sql", "redis", "mongo", "database", "sqlite")),
        ("Documents / File Formats", ("pdf", "docx", "xlsx", "openpyxl", "odf")),
        ("Geospatial / GIS", ("geo", "raster", "shapely", "fiona", "proj")),
        ("GUI / Desktop", ("pyqt", "pyside", "gtk", "wxpython")),
        ("Logging / Observability", ("telemetry", "opentelemetry", "prometheus", "trace", "logging")),
        ("Media / Graphics", ("image", "pillow", "opencv", "plot", "matplotlib")),
        ("Security / Cryptography", ("crypto", "openssl", "bcrypt", "jwt")),
        ("Serialization / Data Formats", ("yaml", "json", "toml", "protobuf", "msgpack")),
        ("Async / Concurrency", ("async", "trio", "anyio", "gevent", "uvloop")),
        ("Documentation / Interactive", ("sphinx", "mkdocs", "jupyter", "notebook", "ipython")),
        ("Development Tools", ("lint", "flake", "pylint", "mypy", "ruff", "debug")),
        ("CLI / Terminal", ("terminal", "prompt", "colorama", "typer")),
        ("System / OS / Process", ("systemd", "udev", "dbus", "psutil", "distro")),
        ("Parsing / Templating", ("jinja", "parser", "markdown", "beautifulsoup", "lxml")),
        ("Data Models / Validation", ("pydantic", "marshmallow", "validator")),
        ("Runtime / Compatibility", ("typing", "importlib", "backport", "platformdirs")),
        ("Utilities / Infrastructure", ("cache", "util", "helper", "plugin", "fsspec")),
    )

    def __init__(self, parent=None):
        columns = [
            ("name", "Package Name", 170, "left"),
            ("category", "Category", 170, "left"),
            ("version", "Version", 90, "right"),
            ("summary", "Summary", 220, "left"),
        ]
        categories = ["All Categories", *self.CATEGORY_ORDER]
        super().__init__("Python Packages", columns, categories, parent)
        self.export_title = APPLET_NAME
        self.has_scanned = False
        self.refresh_btn.setText("Scan Python Packages")
        self.stats_label.setText("Python Packages: Not scanned")
        self.set_status("Not scanned - select Scan Python Packages to inspect this environment.")

        # Standard Options treatment: retain scan action, replace top-level Export.
        self.export_btn.hide()
        export_index = self.dash_layout.indexOf(self.export_btn)
        self.options_btn = QPushButton("Options...")
        self.options_btn.clicked.connect(self.show_options)
        self.dash_layout.insertWidget(export_index, self.options_btn)

        self.details_orientation = "horizontal"
        self._load_details_orientation()
        self.metadata_panel_visible = True
        self._load_metadata_panel_visibility()
        self._install_shortcuts()

    def _install_shortcuts(self):
        self._shortcuts = []
        for sequence, handler in (
            ("F3", self.toggle_metadata_panel),
            ("Ctrl+L", self.toggle_details_orientation),
            ("Shift+F5", self.load_modules),
            ("Ctrl+/", self.show_options),
            ("Ctrl+F", self.focus_search),
        ):
            shortcut = QShortcut(QKeySequence(sequence), self)
            shortcut.setContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)
            shortcut.activated.connect(handler)
            self._shortcuts.append(shortcut)

    def focus_search(self):
        self.search_entry.setFocus(Qt.FocusReason.ShortcutFocusReason)

    def toggle_metadata_panel(self):
        self.set_metadata_panel_visible(not self.metadata_panel_visible, persist=True)

    def toggle_details_orientation(self):
        next_orientation = (
            "vertical" if self.details_orientation == "horizontal" else "horizontal"
        )
        self.set_details_orientation(next_orientation, persist=True)

    def _load_metadata_panel_visibility(self):
        settings = QSettings("brunonlinespace", "Python Packages")
        value = settings.value("metadata_panel_visible", True)
        if isinstance(value, str):
            visible = value.strip().lower() not in {"0", "false", "no", "off"}
        else:
            visible = bool(value)
        self.set_metadata_panel_visible(visible, persist=False)

    def set_metadata_panel_visible(self, visible, *, persist=True):
        self.metadata_panel_visible = bool(visible)
        details_panel = self.splitter.widget(1)
        if details_panel is not None:
            details_panel.setVisible(self.metadata_panel_visible)
        if self.metadata_panel_visible:
            self.set_details_orientation(self.details_orientation, persist=False)
        if persist:
            settings = QSettings("brunonlinespace", "Python Packages")
            settings.setValue("metadata_panel_visible", self.metadata_panel_visible)
            settings.sync()

    @staticmethod
    def _normalise_package_name(name):
        return re.sub(r"[-_.]+", "-", str(name or "").strip().lower())

    @staticmethod
    def _normalise_metadata_text(value):
        text = str(value or "").lower()
        text = re.sub(r"[^a-z0-9+.#/-]+", " ", text)
        return " ".join(text.split())

    @classmethod
    def _metadata_has_phrase(cls, haystack, phrase):
        phrase_text = cls._normalise_metadata_text(phrase)
        return bool(phrase_text) and f" {phrase_text} " in f" {haystack} "

    @classmethod
    def classify_package(cls, name, metadata=None):
        normalised_name = cls._normalise_package_name(name)
        exact = cls.EXACT_PACKAGE_CATEGORIES.get(normalised_name)
        if exact:
            return exact

        metadata = metadata or {}
        try:
            classifiers = metadata.get_all("Classifier") or []
        except Exception:
            classifiers = []
        try:
            keywords = metadata.get("Keywords") or ""
        except Exception:
            keywords = ""
        try:
            summary = metadata.get("Summary") or ""
        except Exception:
            summary = ""

        classifier_text = " | ".join(str(value).lower() for value in classifiers)
        for category, markers in cls.CLASSIFIER_RULES:
            if any(marker in classifier_text for marker in markers):
                return category

        metadata_text = cls._normalise_metadata_text(" ".join([summary, keywords]))
        for category, phrases in cls.CLASSIFICATION_RULES:
            if any(cls._metadata_has_phrase(metadata_text, phrase) for phrase in phrases):
                return category

        name_text = normalised_name.replace("-", " ")
        for category, fragments in cls.NAME_FALLBACK_RULES:
            if any(fragment in name_text for fragment in fragments):
                return category

        return "Other / Uncategorized"

    def style_table_item(self, item, column_id, record):
        if column_id != "category":
            return
        color = self.CATEGORY_COLORS.get(record.get("category"))
        if color:
            item.setForeground(QBrush(QColor(color)))

    def show_options(self):
        dialog = PythonPackagesOptionsDialog(self)
        dialog.exec()

    def _load_details_orientation(self):
        settings = QSettings("brunonlinespace", "Python Packages")
        orientation = str(
            settings.value("details_orientation", "horizontal") or "horizontal"
        ).lower()
        if orientation not in {"horizontal", "vertical"}:
            orientation = "horizontal"
        self.set_details_orientation(orientation, persist=False)

    def set_details_orientation(self, orientation, *, persist=True):
        orientation = str(orientation or "horizontal").lower()
        if orientation not in {"horizontal", "vertical"}:
            orientation = "horizontal"
        self.details_orientation = orientation

        details_panel = self.splitter.widget(1)
        details_layout = details_panel.layout() if details_panel is not None else None
        if orientation == "vertical":
            self.splitter.setOrientation(Qt.Orientation.Vertical)
            if details_layout is not None:
                details_layout.setContentsMargins(0, 8, 0, 0)
            self.splitter.setSizes([430, 330])
        else:
            self.splitter.setOrientation(Qt.Orientation.Horizontal)
            if details_layout is not None:
                details_layout.setContentsMargins(8, 0, 0, 0)
            self.splitter.setSizes([480, 700])

        if persist:
            settings = QSettings("brunonlinespace", "Python Packages")
            settings.setValue("details_orientation", orientation)
            settings.sync()

    def load_modules(self):
        self.modules_data.clear()
        self.export_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        self.set_status("Scanning Python packages...")
        QApplication.processEvents()
        try:
            for dist in importlib.metadata.distributions():
                metadata = dist.metadata
                name = metadata.get("Name") or getattr(dist, "name", "Unknown")
                self.modules_data.append({
                    "name": name,
                    "version": dist.version or "-",
                    "summary": metadata.get("Summary") or "-",
                    "category": self.classify_package(name, metadata),
                    "distribution": dist,
                })

            # Canonical inventory order is package name A-Z; category filters retain this order.
            self.modules_data.sort(
                key=lambda item: str(item.get("name", "")).casefold()
            )

            self.has_scanned = True
            self.stats_label.setText(f"Python Packages: {len(self.modules_data)}")
            self.filter_modules()
            self.clear_info()
            self.refresh_btn.setText("Scan Again")
            self.set_status(f"Scan complete - {len(self.modules_data)} Python packages found.")
        except Exception as exc:
            self.stats_label.setText("Python Packages: Scan failed")
            self.set_status(f"Error reading Python package metadata: {exc}")
            self.show_error("Python Packages", f"Failed to read package metadata:\n{exc}")
        finally:
            self.refresh_btn.setEnabled(True)

    def _scroll_details_to_top(self):
        cursor = self.info_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.Start)
        self.info_text.setTextCursor(cursor)
        self.info_text.ensureCursorVisible()
        scrollbar = self.info_text.verticalScrollBar()
        if scrollbar is not None:
            scrollbar.setValue(scrollbar.minimum())

    def on_module_select(self):
        record = self.current_record()
        if not record:
            return

        self.clear_info()
        dist = record.get("distribution")
        try:
            if dist is None:
                dist = importlib.metadata.distribution(record["name"])

            for key, value in dist.metadata.items():
                if value:
                    self.append_key_value(key, value)

            self.set_status(f"Auditing metadata for package: [{record['name']}]")
        except Exception as exc:
            self.append_info(f"Error: {exc}\n", "value")
            self.set_status(f"Could not read package metadata for [{record['name']}].")
        finally:
            self._scroll_details_to_top()


def create_applet(parent=None):
    return PythonTab(parent=parent)


def run_standalone():
    import sys
    from PyQt6.QtGui import QIcon
    from PyQt6.QtWidgets import QApplication, QMainWindow
    from ._support import STANDALONE_STYLESHEET
    app = QApplication(sys.argv)
    app.setApplicationName(APPLET_NAME)
    app.setOrganizationName(APPLET_AUTHOR)
    icon_path = Path(__file__).resolve().parent / "icon.png"
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))
    app.setStyleSheet(STANDALONE_STYLESHEET)
    window = QMainWindow()
    if icon_path.is_file():
        window.setWindowIcon(QIcon(str(icon_path)))
    window.setWindowTitle(f"{APPLET_NAME} {APPLET_VERSION} — LinSpectacles Applet")
    window.resize(1200, 780)
    window.setCentralWidget(create_applet())
    window.show()
    return app.exec()
