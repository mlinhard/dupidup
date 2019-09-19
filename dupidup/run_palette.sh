#!/bin/bash
source .virtualenv/bin/activate
python3 palette.py $@
deactivate
