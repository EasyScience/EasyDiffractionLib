# [![Unit Tests][20]][21] ![Release][31] [![Downloads][70]][71] [![Lines of code][81]](<>) [![Total lines][80]](<>) [![Files][82]](<>) [![License][50]][51] [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/easyScience/easyDiffractionLib/master)


<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionApp/master/resources/images/ed_logo.svg" height="65">

**easydiffractionLib** is a Python library which provides:
* Scripting interface to simulate and analyse neutron diffraction patterns.
* Multiple optimization algorithms to minimize models to experimental data: [Lmfit](https://lmfit.github.io/lmfit-py/), [Bumps](https://github.com/bumps/bumps) and [DFO_LS](https://github.com/numericalalgorithmsgroup/dfols).
* Multiple calculation engines: [CrysPy](https://github.com/ikibalin/cryspy), [CrysFML](https://www.ill.eu/sites/fullprof/php/programs24b7.html?pagina=Crysfml), [GSAS-II](https://subversion.xray.aps.anl.gov/trac/pyGSAS).

**easydiffractionLib** is the foundation of [**easyDiffraction**](https://github.com/easyScience/easyDiffraction), an intuitive application which endeavors simplifying and accelerating the analysis of diffraction experiments.

## Getting Started

### Install easyDiffractionLib

Currently **easyDiffractionLib** is in **alpha** and has not been released on **pypi**. Please use the alternative method given below to install **easyDiffractionLib** from our [custom Python Package Index](https://easyscience.github.io/pypi).

* Create and go to, e.g., **easyDiffraction** directory (*optional*)
  ```
  mkdir easyDiffraction && cd easyDiffraction
  ```
* Create virtual environment and activate it (*optional*)
  ```
  python -m venv .venv
  source .venv/bin/activate
  ```
* Upgrade pip (*optional*)
  ```
  pip install --upgrade pip
  ```
* Install **easyDiffractionLib**
  ```
  pip install easyDiffraction --extra-index-url https://easyscience.github.io/pypi
  ```

## Examples

### Jupyter Notebook examples that use easyDiffractionLib

#### Locally

* Install **easyDiffractionLib** as described above
* Install Jupyter Notebook and visualization libraries, such as **py3Dmol** and **bokeh** (*if not done already*)
  ```
  pip install notebook py3Dmol bokeh
  ```
* Download **easyDiffractionLib** Jupyter Notebook [examples](https://github.com/easyScience/easyDiffractionLib/tree/master/examples) from GitHub, e.g., using **svn** (*if not done already*)
  ```
  svn export https://github.com/easyScience/easyDiffractionLib/branches/master/examples
  ```
* Run Jupyter Notebook server
  ```
  jupyter notebook examples/
  ```
* In webbrowser open
  ```
  http://localhost:8888/
  ```
* Select one of the ***.ipynb** files

#### Via Binder (interactive)

Examples can also be run on the online service [**Binder**](https://mybinder.org/). Click [launch **Binder**](https://mybinder.org/v2/gh/easyScience/easyDiffractionLib/master) and navigate to the examples folder to run one of the notebooks or create your own.

#### Via nbviewer (non-interactive preview)

* [Simulation](https://nbviewer.jupyter.org/github/easyScience/easyDiffractionLib/blob/master/examples/Simulation.ipynb)
* [Fitting](https://nbviewer.jupyter.org/github/easyScience/easyDiffractionLib/blob/master/examples/Fitting.ipynb)

## Test

Testing is run via `pytest`, though it is not installed by default. Install it with:
```
pip install pytest
```

The installation can be verified by running the test suite:
```
python -m pytest
```

## Contributing
We absolutely welcome contributions. **easyDiffractionLib** is maintained by the ESS and on a volunteer basis and thus we need to foster a community that can support user questions and develop new features to make this software a useful tool for all users while encouraging every member of the community to share their ideas.

## License
**easyDiffractionLib** is licenced under the  BSD-3-Clause license, [DFO_LS](https://github.com/numericalalgorithmsgroup/dfols) is subject to the GPL license.

<!---CI Build Status--->

[20]: https://github.com/easyScience/easyDiffractionLib/actions/workflows/unit_test.yml/badge.svg

[21]: https://github.com/easyScience/easyDiffractionLib/actions


<!---Release--->

[31]: https://img.shields.io/badge/release-v0.0.1--alpha-orange

[32]: https://img.shields.io/pypi/v/easyScienceCore.svg

[33]: https://pypi.org/project/easyScienceCore


<!---License--->

[50]: https://img.shields.io/github/license/easyScience/easyDiffractionLib.svg

[51]: https://github.com/easyScience/easyDiffractionLib/blob/master/LICENSE.md


<!---Downloads--->

[70]: https://img.shields.io/pypi/dm/easyScienceCore.svg

[71]: https://pypi.org/project/easyScienceCore

<!---Code statistics--->

[80]: https://tokei.rs/b1/github/easyScience/easyDiffractionLib

[81]: https://tokei.rs/b1/github/easyScience/easyDiffractionLib?category=code

[82]: https://tokei.rs/b1/github/easyScience/easyDiffractionLib?category=files

[83]: https://www.codefactor.io/repository/github/easyscience/easydiffractionlib/badge

[84]: https://www.codefactor.io/repository/github/easyscience/easydiffractionlib
