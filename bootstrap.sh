#!/bin/bash
set -euxo pipefail
cd "$( dirname "${BASH_SOURCE[0]}" )"

PYTHON3BIN="${PYTHON3BIN:-python3}"  # user can override this
# make sure we've got a recent version before continuing:
"$PYTHON3BIN" -c 'import sys; print(sys.version); sys.exit(0 if sys.version_info>=(3,11) else 1)'

mkdir -vp ~/.config/git ~/bin  # quick fix since apply.py doesn't do this yet

"$PYTHON3BIN" -m pip install colorama igbpyutils

# Since this is intended to run in e.g. GitHub Codespaces,
# use --copy because hard links won't work across FS boundaries.
# Otherwise you're free to re-run apply.py without the option to create hard links.
"$PYTHON3BIN" apply.py --copy

chmod -c 755 ~/bin/git_mysync.py  # workaround for apply.py not doing this yet

# Set up __git_ps1 and git bash completion
for WHAT in git-prompt.sh git-completion.bash; do
	test -e ~/".$WHAT" || curl -LsSfo ~/".$WHAT" "https://raw.githubusercontent.com/git/git/master/contrib/completion/$WHAT"
	grep -q "\.$WHAT" ~/.bashrc || echo "source ~/.$WHAT" >>~/.bashrc
done

