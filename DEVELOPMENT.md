# Development

This is an example of a workflow that describes the development process.

- Clone EasyDiffractionLib repository
  ```console
  git clone https://github.com/EasyScience/EasyDiffractionLib
  ```
- Go to the cloned directory
  ```console
  cd EasyDiffractionLib
  ```
- Checkout/switch to the `develop` branch
  ```console
  git checkout develop
  ```
- Create a new branch from the current one
  ```console
  git checkout -b new-feature
  ```
- Create Python environment and activate it
  ```console
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Upgrade PIP - package installer for Python
  ```console
  python -m pip install --upgrade pip
  ```
- Install easydiffraction from root with `dev` extras for development, `charts`
  extras for Jupyter notebooks and `docs` extras for building documentation
  ```console
  pip install '.[dev,charts,docs]'
  ```
- Make changes in the code
  ```console
  ...
  ```
- Check the validity of pyproject.toml
  ```console
  validate-pyproject pyproject.toml
  ```
- Run Ruff - Python linter and code formatter (configuration is in
  pyproject.toml)<br/> Linting (overwriting files)
  ```console
  ruff check . --fix
  ```
  Formatting (overwriting files)
  ```console
  ruff format .
  ```
- Install and run Prettier - code formatter for Markdown, YAML, TOML, etc. files
  (configuration in prettierrc.toml)<br/> Formatting (overwriting files)
  ```console
  npm install prettier prettier-plugin-toml --save-dev --save-exact
  npx prettier . --write --config=prettierrc.toml
  ```
- Run python tests
  ```console
  pytest tests/ --color=yes -n auto
  ```
- Clear all Jupyter notebooks output (Only those that were changed!). Replace
  `examples/*.ipynb` with the path to the notebook(s) you want to clear
  ```console
  jupyter nbconvert --clear-output --inplace examples/*.ipynb
  ```
- Run nbQA - Jupyter notebooks quality assurance package
  ```console
  nbqa ruff examples/ --fix
  ```
- Run Jupyter notebooks as tests
  ```console
  pytest --nbmake examples/ --ignore-glob='examples/*emcee*' --nbmake-timeout=300 --color=yes -n=auto
  ```
- Add extra files to build documentation (from `../assets-docs/` and
  `../assets-branding/` directories)
  ```console
  cp -R ../assets-docs/docs/assets/ docs/assets/
  cp -R ../assets-docs/includes/ includes/
  cp -R ../assets-docs/overrides/ overrides/
  mkdir -p docs/assets/images/
  cp ../assets-branding/EasyDiffraction/logos/ed-logo_dark.svg docs/assets/images/
  cp ../assets-branding/EasyDiffraction/logos/ed-logo_light.svg docs/assets/images/
  cp ../assets-branding/EasyDiffraction/logos/edl-logo_dark.svg docs/assets/images/logo_dark.svg
  cp ../assets-branding/EasyDiffraction/logos/edl-logo_light.svg docs/assets/images/logo_light.svg
  cp ../assets-branding/EasyDiffraction/icons/ed-icon_256x256.png docs/assets/images/favicon.png
  mkdir -p overrides/.icons/
  cp ../assets-branding/EasyDiffraction/icons/ed-icon_bw.svg overrides/.icons/easydiffraction.svg
  cp ../assets-branding/EasyScience/icons/es-icon_bw.svg overrides/.icons/easyscience.svg
  cp -R examples/ docs/examples/
  cp ../assets-docs/mkdocs.yml mkdocs.yml
  echo "" >> mkdocs.yml
  cat docs/mkdocs.yml >> mkdocs.yml
  ```
- Build documentation with MkDocs - static site generator
  ```console
  export JUPYTER_PLATFORM_DIRS=1
  mkdocs serve
  ```
- Test the documentation locally (built in the `site/` directory). E.g., on
  macOS, open the site in the default browser via the terminal
  ```console
  open http://127.0.0.1:8000
  ```
- Clean up after building documentation
  ```console
  rm -rf site/
  rm -rf docs/assets/
  rm -rf includes/
  rm -rf overrides/
  rm -rf docs/examples/
  rm -rf node_modules/
  rm mkdocs.yml
  rm package-lock.json
  rm package.json
  ```
- Commit changes
  ```console
  git add .
  git commit -m "Add new feature"
  ```
- Push the new branch to a remote repository
  ```console
  git push -u origin new-feature
  ```
