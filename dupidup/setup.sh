#!/bin/bash
if [ "$1" != "update" ]; then
    rm -rf .virtualenv
    python3 -m virtualenv .virtualenv
    source .virtualenv/bin/activate
    pip3 install docopt pip
else
    source .virtualenv/bin/activate
fi

if [ "${MAGICUR_HOME}x" != "x" ]; then
    echo "################################# Building magicur ... #############################################"
    pushd $MAGICUR_HOME
    python3 setup.py install
    rm -rf build dist magicur.egg-info
    popd
    echo "####################################################################################################"
fi

python3 setup.py install
rm -rf build dist dupidup.egg-info
deactivate

if [ "$1" != "update" ]; then
    echo "Installation complete."
    echo "You can add the following to your ~/.bashrc to use dupidup more easily:"
    echo "#####################################################################################################"
    echo "export DUPIDUP_HOME=$PWD"
    echo "export PATH=\$DUPIDUP_HOME/bin:\$PATH"
    echo "#####################################################################################################"
fi

