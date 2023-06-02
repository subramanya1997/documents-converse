#!/bin/bash
# Copyright (c) Subramanya N. Licensed under the Apache License 2.0. All Rights Reserved

# This script will create a virtual environment and install all the dependencies
# required to run the server.py script. It will then run the server.py script
# inside the virtual environment.

PYTHON=python
VENV_NAME=py_venv

error_exit(){
    echo "$1" 1>&2
    exit 1
}

error_clean_exit(){
    echo Try again later! Removing the virtual environment dir...
    [ -e $VENV_NAME ] && rm -r $VENV_NAME
    error_exit "$1" 1>&2
}

cd "`dirname \"$0\"`"
if $PYTHON -c 'import sys; sys.exit(1 if sys.hexversion<0x03000000 else 0)'; then
    VENV=venv
else
    error_exit "Python 2 is not supported"
fi

# Check if virtual environment had been created
if [ ! -d "$VENV_NAME" ]; then 
    echo Checking pip is installed
    $PYTHON -m ensurepip --default-pip >/dev/null 2>&1
    $PYTHON -m pip >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo pip is still not installed!...
        echo Try to install it with sudo?
        echo Run: \"sudo $PYTHON -m ensurepip --default-pip\"
        exit 1
    fi
    echo Creating python virtual environment in "$VENV_NAME/"...
    $PYTHON -m $VENV $VENV_NAME || error_exit "Failed to create virtual environment"
    source $VENV_NAME/bin/activate || error_exit "Failed to source virtual environment"
    echo Upgrading pip...
    $PYTHON -m pip install --upgrade pip
    echo Installing all pip dependency inside virtual environment...
    $PYTHON -m pip install --no-cache-dir -r requirements.txt || error_clean_exit "Something went wrong while installing pip packages"
fi

# source the virtual environment
echo '----------------------------'
echo activating virtual environment...
source $VENV_NAME/bin/activate || error_exit "Failed to source virtual environment (try to delete '$VENV_NAME/' and re-run)"

# load environment variables from .env file
set -a
[ -f .env ] && . .env

# run the script
echo '----------------------------'
echo running app.py...
$PYTHON -W ignore app.py "$@"