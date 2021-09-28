# [![License][50]][51] [![Release][32]][33] [![Downloads][70]][71] [![CI Build][20]][21] 

[![CodeFactor][83]][84] [![Lines of code][81]](<>) [![Total lines][80]](<>) [![Files][82]](<>)


<img height="80"><img src="https://raw.githubusercontent.com/easyScience/easyDiffractionLib/master/resources/images/ed_logo.svg" height="65">

**easyDiffractionLib** is the foundation of the *easyScience* universe, providing the building blocks for libraries and applications which aim to make scientific data simulation and analysis easier.

## Install

**easyDiffractionLib** can be downloaded using pip:

```pip install easysciencecore```

Or direct from the repository:

```pip install https://github.com/easyScience/easyDiffractionLib```

## Getting Started

### Download easyDiffractionLib repo
* Open **Terminal**
* Change the current working directory to the location where you want the **easyDiffractionLib** directory
* Clone **easyDiffractionApp** repo from GitHub using **git**
  ```
  git clone https://github.com/easyScience/easyDiffractionApp
  ```
  
### Install easyDiffractionLib dependencies
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
* Create virtual environment for **easyDiffractionLib** and install its dependences using **poetry** (configuration file: **pyproject.toml**)
  ```
  poetry install
  ```
  
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

After installation, launch the test suite:

```python -m pytest```

## Documentation

Documentation can be found at:

[https://easyScience.github.io/easyDiffractionLib](https://easyScience.github.io/easyDiffractionLib)

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
