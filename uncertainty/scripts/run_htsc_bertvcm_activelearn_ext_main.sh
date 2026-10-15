#!/bin/bash

if [[ ! -d uncertainty ]]; then
  echo \
    "Error: directory uncertainty inaccessible." \
    "You should run this script in the top directory of the repository."
  exit 1
fi

if PYTHONPATH=uncertainty/model \
  uncertainty/scripts/run_htsc_bertvcm_activelearn_ext.sh 5 init; then 
  echo "Run completed with success"
else
  echo "Run exited with failure"
fi
