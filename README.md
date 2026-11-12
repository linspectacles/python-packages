<p align="center">
  <a href="https://github.com/brunonlinespace/brunonlinespace/blob/main/linspectacles/python-packages.png">
    <img
      src="https://raw.githubusercontent.com/brunonlinespace/brunonlinespace/main/linspectacles/python-packages.png"
      alt="Python Packages screenshot"
      width="900"
    >
  </a>
</p>

# Python Packages

**Expose. Explore. Explain.**

Python Packages is a read-only, explicit-scan inventory of Python distributions visible to the running Python environment.

Current release: **0.0.8**

Repository: <https://github.com/linspectacles/python-packages>

## What Python Packages is

Python Packages answers a focused question: **which Python distributions are visible here, what versions do they report, and what metadata is attached to each distribution?**

It keeps acquisition and interpretation close to the Linux interfaces actually used by the applet. When a source is unavailable, restricted, or does not report a field, the README does not imply that the applet can manufacture the missing information.

## Highlights

- Inventory through the standard-library `importlib.metadata.distributions()` interface.
- Version from `Distribution.version`.
- Metadata Details from the selected distribution's `Distribution.metadata` mapping.
- Local category classification using known package identities, reported Summary/Keywords/Classifiers and package-name heuristics.
- Explicit scanning rather than package installation or environment mutation.

## Data sources and acquisition

- Python standard library `importlib.metadata`.
- `Distribution.version` and `Distribution.metadata` for the selected distribution.

The applet uses those sources according to the acquisition paths implemented in this release. Optional tools or privileged helpers only affect the views/actions that explicitly use them; they are not treated as silent substitutes for unrelated sources.

## Interface

Python Packages follows the LinSpectacles inventory + **Metadata Details** pattern where applicable: an acquired inventory remains separate from the details for the selected record, and search/filter controls operate on the data the applet has actually collected.

The applet's **Options** surface provides the presentation/source/about controls implemented by this release, together with export controls where present in the source. Applet-specific actions remain explicit rather than being folded into background collection.

## Read-only and scope boundaries

Category is a LinSpectacles presentation classification, not package-manager metadata. Python Packages does not install, remove, upgrade or otherwise modify Python distributions.

## Running from source

The supplied source is directly runnable on Linux. The Python-side requirements are:

- Python 3.
- PyQt6 for the graphical interface.

Create a local virtual environment if you do not already have the required Python packages in the environment you want to use:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install PyQt6
python3 linspectacles_python_packages/standalone.py
```

Linux commands, procfs/sysfs interfaces, system services, or optional helpers mentioned in **Data sources and acquisition** are applet-specific runtime inputs. A missing optional source is handled by the applet's existing availability/error path; it is not replaced here with an invented dependency or capability.

No RPM installation instructions are included in this README.

## Source layout and LinSpectacles integration

The applet source is contained in:

```text
linspectacles_python_packages/
├── __init__.py
├── applet.json
├── README.md
├── standalone.py
├── LICENSE
└── python_packages/
    ├── __init__.py
    ├── applet.py
    ├── _support.py
    └── icon.png
```

`applet.json` supplies the LinSpectacles applet identity and entrypoint metadata. `standalone.py` launches the applet directly, while the package's applet factory provides the host-loadable LinSpectacles integration used by the source.

## Configuration

Presentation and inspection preferences are persisted only through the settings mechanisms already implemented by the applet. Persisted UI state does not grant the applet permission to modify the inspected Linux subsystem.

## Scope

Python Packages is intentionally specialist. Related Linux information that belongs to another LinSpectacles subsystem remains outside this applet rather than being inferred or duplicated here.

## License

GNU General Public License v3.0 or later. See [`LICENSE`](LICENSE).

## Links

- LinSpectacles organisation: <https://github.com/linspectacles/>
- Repository: <https://github.com/linspectacles/python-packages>
- Issues: <https://github.com/linspectacles/python-packages/issues>

<p align="center">
  <a href="https://github.com/linspectacles/python-packages">
    <img
      src="python_packages/icon.png"
      alt="Python Packages"
      width="256"
    >
  </a>
</p>
