#!/bin/bash
set -euo pipefail
# scp a few basic files to a target host (e.g. RPi)
if [[ $# -ne 1 || -z "$1" ]]; then
    echo "Usage $0 TARGHOST"
    exit 1
fi
TARGHOST="$1"
cd "$( dirname "${BASH_SOURCE[0]}" )"
set -x
scp .bash_aliases .vimrc .gitconfig .screenrc \
    "$TARGHOST":
