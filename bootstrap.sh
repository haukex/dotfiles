#!/bin/bash
set -euxo pipefail
cd "$( dirname "${BASH_SOURCE[0]}" )"

# Set up __git_ps1 and git bash completion
for WHAT in git-prompt.sh git-completion.bash; do
	test -e ~/".$WHAT" || curl -LsSfo ~/".$WHAT" "https://raw.githubusercontent.com/git/git/master/contrib/completion/$WHAT"
	grep -q "\.$WHAT" ~/.bashrc || echo "source ~/.$WHAT" >>~/.bashrc
done

function fallback {
	echo "ERROR: Something went wrong, falling back to basic (incomplete) file copying!"
	cp -av .bash_aliases .vimrc .gitconfig .screenrc ~
	#exit 0
}
trap 'fallback' ERR

PYTHON3BIN="${PYTHON3BIN:-python}"  # user can override this
# make sure we've got a recent version before continuing:
"$PYTHON3BIN" -c 'import sys; print(sys.version); sys.exit(0 if sys.version_info>=(3,9) else 1)'

mkdir -vp ~/.config/git ~/bin  # quick fix since apply.py doesn't do this yet

"$PYTHON3BIN" -m pip install 'colorama>=0.4.6' 'igbpyutils>=0.6.0'

# Since this is intended to run in e.g. GitHub Codespaces,
# use --copy because hard links won't work across FS boundaries.
# Otherwise you're free to re-run apply.py without the option to create hard links.
"$PYTHON3BIN" apply.py --copy

chmod -c 755 ~/bin/git_mysync.py  # workaround for apply.py not doing this yet
