#!/bin/bash

SCRIPT_PATH=${BASH_SOURCE[0]}
SECURE_ERASE_DIR=$(dirname "$SCRIPT_PATH")
BLADE_RUNNER_DIR=$(dirname "$SECURE_ERASE_DIR")
APP_ROOT_DIR=$(dirname "$BLADE_RUNNER_DIR")

cd "$APP_ROOT_DIR"
sudo python -m blade_runner.secure_erase.secure_erase_internals
