# [![License][50]][51] [![Release][32]][33] [![Downloads][70]][71] [![Unit Tests][20]][21]


<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionApp/master/resources/images/ed_logo.svg" height="65">

**easydiffractionLib** is a Python library for modelling and analysis of diffraction data, a base of the [**easyDiffraction**](https://easydiffraction.org)

**easyDiffractionLib** is the foundation of [*easyDiffraction*](https://github.com/easyScience/easyDiffraction), an intuitive application which
endeavors simplifying and accelerating the analysis of diffraction experiments. *easyDiffractionLib* provides:
* Scripting interface to simulate and analyse neutron diffraction patterns
* Optimization algorithms to minimize models to experimental data
* 3 pattern calculators; [cryspy](https://github.com/ikibalin/cryspy), [crysFML](https://www.ill.eu/sites/fullprof/php/programs24b7.html?pagina=Crysfml), [GSAS-II](https://subversion.xray.aps.anl.gov/trac/pyGSAS)

## Getting Started

### Install easyDiffractionLib

Currently **easyDiffractionLib** is in **alpha** and has not been released on **pypi**. Please use the alternative method given below to install **easyDiffractionLib** from the [GitHub repo](https://github.com/easyScience/easyDiffractionLib) using our [custom Python Package Index](https://easyscience.github.io/pypi) for some dependencies, such as CrysFML and GSAS-II.

* Create and go to, e.g., **easyDiffraction** (*optional*)
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
  pip install git+https://github.com/easyScience/easyDiffractionLib@more_notebooks --extra-index-url https://easyscience.github.io/pypi
  ```


## Examples

### Jupyter Notebook examples that use easyDiffractionLib

* Install **easyDiffractionLib** as described above
* Install Jupyter Notebook and visualization libraries, such as matplotlib and py3Dmol
  ```
  pip install jupyter notebook ipympl matplotlib py3Dmol
  ```
* Download **easyDiffractionLib** Jupyter Notebook [examples](https://github.com/easyScience/easyDiffractionLib/tree/more_notebooks/examples) from GitHub, e.g., using svn
  ```
  svn export https://github.com/easyScience/easyDiffractionLib/branches/more_notebooks/examples
  ```
* Run Jupyter Notebook server
  ```
  jupyter notebook examples/
  ```
* In webbrowser open
  ```
  http://localhost:8888/
  ```
* Select one of the *.ipynb files

## Test

The installation can be verified by running the test suite:

```python -m pytest```

## Documentation

Documentation can be found at: [https://easyScience.github.io/easyDiffractionLib](https://easyScience.github.io/easyDiffractionLib)

## Contributing
We absolutely welcome contributions. **easyDiffractionLib** is maintained by the ESS and on a volunteer basis and thus we need to foster a community that can support user questions and develop new features to make this software a useful tool for all users while encouraging every member of the community to share their ideas.

## License
**easyDiffractionLib** is licenced under the  BSD-3-Clause license.

<!---CI Build Status--->

[20]: https://github.com/easyScience/easyDiffractionLib/actions/workflows/unit_test.yml/badge.svg

[21]: https://github.com/easyScience/easyDiffractionLib/actions


<!---Release--->

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
