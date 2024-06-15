#!/bin/bash
set -euxo pipefail

# just an example of what an initialize script could do...

ln -svfn /workspaces ~/code

sudo apt install -y cpanminus liblocal-lib-perl
grep -q -- '-Mlocal::lib' ~/.bashrc || echo "eval \"\$(perl -I\$HOME/perl5/lib/perl5 -Mlocal::lib)\"" >>~/.bashrc
