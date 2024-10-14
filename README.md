# [![Unit Tests][20]][21] ![Release][31] [![Downloads][70]][71] [![Lines of code][81]](<>) [![Total lines][80]](<>) [![Files][82]](<>) [![License][50]][51] [![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/easyScience/easyDiffractionLib/develop)

[![](http://github-actions.40ants.com/easyScience/easyDiffractionLib/matrix.svg)](https://github.com/easyScience/easyDiffractionLib/actions)

<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionApp/master/resources/images/ed_logo.svg" height="65">

**Easydiffraction** is a Python library which provides:
* Scripting interface to simulate and analyse neutron diffraction patterns.
* Multiple optimization algorithms to minimize models to experimental data: [Lmfit](https://lmfit.github.io/lmfit-py/), [Bumps](https://github.com/bumps/bumps) and [DFO_LS](https://github.com/numericalalgorithmsgroup/dfols).
* Multiple calculation engines: [CrysPy](https://github.com/ikibalin/cryspy), [CrysFML](https://www.ill.eu/sites/fullprof/php/programs24b7.html?pagina=Crysfml).

**Easydiffraction** library is the foundation of [**EasyDiffraction** application](https://github.com/easyscience/easydiffractionapp), an intuitive application which endeavors simplifying and accelerating the analysis of diffraction experiments.

## Getting Started

### Install EasyDiffraction python library

Currently **easydiffraction** is in **alpha** and has not been released on **pypi**. Please use the alternative method given below to install **easydiffraction** from our GitHub repository.

* Create and go to, e.g., **easydiffraction** directory (*optional*)
  ```
  mkdir easydiffraction && cd easydiffraction
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
* Install **easydiffraction** with extras
  ```
  pip install 'easydiffraction[charts] @ git+https://github.com/easyscience/easydiffractionlib.git@new_job_dev'
  ```

## Examples

### Jupyter Notebook examples that use EasyDiffraction

#### Locally

* Install **easydiffraction** as described above, including `charts` extras for visualization 
* Install Jupyter Notebook
  ```
  pip install notebook
  ```
* Download **easyDiffractionLib** Jupyter Notebook [examples](https://github.com/easyscience/easydiffractionlib/tree/new_job_dev/examples) from GitHub, e.g., using **svn** (*if not done already*)
  ```
  svn export https://github.com/easyscience/easydiffractionlib/branches/new_job_dev/examples
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

#### Via Google Colab (interactive, requires google account)

##### Neutron powder diffraction

* [Fitting, constant wavelength, La0.5Ba0.5CoO3 - HRPT@PSI](https://colab.research.google.com/github/EasyScience/EasyDiffractionLib/blob/new_job_dev/examples/Fitting_PD-CW_La0.5Ba0.5CoO3-HRPT@PSI/fitting.ipynb)
* [Fitting, time-of-flight, Si - SEPD@Argonne](https://colab.research.google.com/github/EasyScience/EasyDiffractionLib/blob/new_job_dev/examples/Fitting_PD-TOF_Si-SEPD@Argonne/fitting.ipynb)

#### Via nbviewer (non-interactive preview)

* [Fitting, constant wavelength, La0.5Ba0.5CoO3 - HRPT@PSI](https://nbviewer.org/github/EasyScience/EasyDiffractionLib/blob/new_job_dev/examples/Fitting_PD-CW_La0.5Ba0.5CoO3-HRPT@PSI/fitting.ipynb)
* [Fitting, time-of-flight, Si - SEPD@Argonne](https://nbviewer.jupyter.org/github/easyScience/easyDiffractionLib/blob/master/examples/Fitting.ipynb)

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

[31]: https://img.shields.io/badge/release-v0.0.9--alpha-orange

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
