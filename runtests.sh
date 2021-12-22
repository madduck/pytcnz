#!/bin/sh

if command -v ipython3 >/dev/null; then
  ipdb='--pdbcls=IPython.terminal.debugger:TerminalPdb'
fi

# --flake8 does not work if individual tests are specified, i.e. by passing
# e.g. tests/test_squashnz_player.py::test_vaccination_status_expired
case "$@" in
  (*.py::test*) flake=;;
  (*) flake=--flake8;;
esac

exec pytest-3 $ipdb --color=no -rfExP --tb=native --showlocals $flake "$@"
