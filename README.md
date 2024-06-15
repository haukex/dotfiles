Hauke's `.dotfiles`
===================

- `apply.py` hard links or copies the dotfiles, run it with `--help` for details
- `bootstrap.sh` installs prerequisites for `apply.py` and then runs that
	- e.g. for use in GitHub Codespaces:
	  <https://docs.github.com/en/codespaces/setting-your-user-preferences/personalizing-github-codespaces-for-your-account#dotfiles>
- `push_simple.sh` is for `scp`ing a few basic files to a remote host (e.g. RPi)

