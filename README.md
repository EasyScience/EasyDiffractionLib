# [![License][50]][51] [![Release][32]][33] [![Downloads][70]][71] [![Unit Tests][20]][21]

[![CodeFactor][83]][84] [![Lines of code][81]](<>) [![Total lines][80]](<>) [![Files][82]](<>)


<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionLib/master/resources/images/ed_logo.svg" height="65">

**easyDiffractionLib** is the foundation of [*easyDiffraction*](https://github.com/easyScience/easyDiffraction), an intuitive application which
endeavors simplifying and accelerating the analysis of diffraction experiments. *easyDiffractionLib* provides:
* Scripting interface to simulate and analyse neutron diffraction patterns
* Optimization algorithms to minimize models to experimental data
* 3 pattern calculators; [cryspy](https://github.com/ikibalin/cryspy), [crysFML](https://www.ill.eu/sites/fullprof/php/programs24b7.html?pagina=Crysfml), [GSAS-II](https://subversion.xray.aps.anl.gov/trac/pyGSAS)

## Getting Started

**Currently easyDiffractionLib is in alpha and has not been released on pypi. Please use one of the alternative methods.**

### Download easyDiffractionLib repo
* Open **Terminal**
* Change the current working directory to the location where you want the **easyDiffractionLib** directory
* Clone **easyDiffractionLib** repo from GitHub using **git**
  ```
  git clone https://github.com/easyScience/easyDiffractionLib
  ```
* Or extract [this zip file](https://github.com/easyScience/easyDiffractionLib/archive/refs/heads/main.zip)

### Install easyDiffractionLib dependencies (Using poetry)
* Open **Terminal**
* Install [**Poetry**](https://python-poetry.org/docs/) (Python dependency manager)
  * osx / linux / bashonwindows
    ```
    curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
    ```
  * windows powershell
    ```
    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python
    ```
* Go to **easyDiffractionLib** directory
* Create virtual environment for **easyDiffractionLib** and install its dependencies using **poetry** (configuration file: **pyproject.toml**)
  ```
  poetry install
  ```

### Install easyDiffractionLib dependencies (Using requirements.txt)
* Open **Terminal**
* Activate any environment which you may want to use
* Go to **easyDiffractionLib** directory
* Install via
  ```
  pip install -r requirements.txt
  ```


### Using pip

Currently, **easyDiffractionLib** can be installed via pointing pip to this repository:
```
pip install https://github.com/easyScience/easyDiffractionLib
```


## Examples

### Run Jupyter Notebook examples that use easyDiffractionLib
* Open **Terminal**
* Go to **easyDiffractionLib** directory
* Run Jupyter Notebook server
  ```
  poetry run jupyter notebook
  ```
* In webbrowser open
  ```
  http://localhost:8888/
  ```
* Go to *examples* directory
* Select one of the *.ipynb files


## Test

The installation can be verified by running the test suite:

```python -m pytest```

## Documentation

Documentation can be found at:

[https://easyScience.github.io/easyDiffractionLib](https://easyScience.github.io/easyDiffractionLib)

## Contributing
We absolutely welcome contributions. **easyDiffractionLib** is maintained by the ESS and on a volunteer basis and thus we need to foster a community that can support user questions and develop new features to make this software a useful tool for all users while encouraging every member of the community to share their ideas.

## License
**easyDiffractionLib** is licenced under the  BSD-3-Clause license.

<!---CI Build Status--->

[20]: https://github.com/easyScience/easyDiffractionLib/workflows/unit_tests/badge.svg

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
