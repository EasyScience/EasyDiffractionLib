echo "\033[0;33m:::::: Check and fix code linting\033[0m"
ruff check . --fix

echo "\033[0;33m:::::: Check and fix code formatting\033[0m"
ruff format .

echo "\033[0;33m:::::: Check and fix notebook formatting\033[0m"
nbqa ruff examples/

echo "\033[0;33m:::::: Check and fix non-code formatting\033[0m"
npx prettier . --write --config=prettierrc.toml
