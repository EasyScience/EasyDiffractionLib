## [![Downloads][70]][71] [![Lines of code][81]](<>) [![Total lines][80]](<>) [![Files][82]](<>) [![License][50]][51]


<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionApp/master/resources/images/ed_logo.svg" height="65">

**easydiffractionLib** is a Python library for modelling and analysis of diffraction data, a base of the [**easyDiffraction**](https://easydiffraction.org)


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
While **easyDiffractionLib** is under the BSD-3 license, DFO_LS is subject to the GPL license.

<!---CI Build Status--->

[20]: https://github.com/easyScience/easyDiffractionLib/workflows/CI%20using%20pip/badge.svg

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

[83]: https://www.codefactor.io/repository/github/easyscience/easyDiffractionLib/badge

[84]: https://www.codefactor.io/repository/github/easyscience/easyDiffractionLib
