# Development

This is an example of a workflow that describes the development process. 

* Clone EasyDiffractionLib repository
  ```console
  git clone https://github.com/EasyScience/EasyDiffractionLib
  ```
* Go to the cloned directory
  ```console
  cd EasyDiffractionLib
  ```
* Checkout/switch to the `develop` branch
  ```console
  git checkout develop
  ```
* Create a new branch from the current one
  ```console
  git checkout -b new-feature
  ```
* Create Python environment and activate it
  ```console
  python3 -m venv .venv
  source .venv/bin/activate
  ```  
* Upgrade PIP - package installer for Python
  ```console
  python -m pip install --upgrade pip
  ```
* Install easydiffraction from root with `dev` extras for development 
  ```console
  pip install '.[dev]'
  ```
* Make changes in the code
* Run Ruff - Python linter and code formatter (configuration is in pyproject.toml)
  ```console
  ruff check . --fix 
  ```
* Run python tests
  ```console
  pytest tests/ --color=yes -n auto 
  ```
* Clear all Jupyter notebooks output
  ```console
  jupyter nbconvert --clear-output --inplace examples/*.ipynb
  ```
* Run nbQA - Jupyter notebooks quality assurance package
  ```console
  nbqa ruff examples/ --fix
  ```  
* Run Jupyter notebooks as tests
  ```console
  pytest --nbmake examples/*ipynb --nbmake-timeout=300 --color=yes -n=auto
  ```
* Commit changes
  ```console
  git add .
  git commit -m "Add new feature"
  ```
* Push the new branch to a remote repository
  ```console
  git push -u origin new-feature
  ```
