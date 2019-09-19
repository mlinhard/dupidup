#!/bin/bash
source .virtualenv/bin/activate
python3 demo.py $@
deactivate
