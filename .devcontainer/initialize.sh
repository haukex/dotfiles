#!/bin/bash
set -euxo pipefail

# just an example of what an initialize script could do...

ln -svfn /workspaces ~/code

sudo apt-get update
sudo apt-get install -y vim
