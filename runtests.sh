#!/bin/sh

if command -v ipython3 >/dev/null; then
  ipdb='--pdbcls=IPython.terminal.debugger:TerminalPdb'
fi

exec pytest-3 $ipdb --color=no -rfExP --tb=native --showlocals --flake8 "$@"
