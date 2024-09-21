#!/bin/bash
set -euxo pipefail
cd "$( dirname "${BASH_SOURCE[0]}" )"/..

# just an example of what an initialize script could do...

ln -svfn /workspaces ~/code
