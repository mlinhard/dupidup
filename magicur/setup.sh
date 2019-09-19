#!/bin/bash
if [ "$1" == "update" ]; then
    source .virtualenv/bin/activate
    python3 setup.py install
    rm -rf build dist magicur.egg-info
    deactivate
else
    rm -rf .virtualenv
    python3 -m virtualenv .virtualenv
    source .virtualenv/bin/activate
    pip3 install pip
    python3 setup.py install
    rm -rf build dist magicur.egg-info
    deactivate

    echo "Installation complete."
fi

