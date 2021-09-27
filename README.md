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
