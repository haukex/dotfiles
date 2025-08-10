Haukes's Notes on Git Credential Management
===========================================

*Note* that on Windows, the Git installer takes care of this.

Basics:

	git config --global --unset-all credential.helper
	git config --global credential.helper 'cache --timeout=3600'
	git config --list --show-origin --show-scope

If you have a desktop environment:

	sudo apt-get install libsecret-1-0 libsecret-1-dev
	cd /usr/share/doc/git/contrib/credential/libsecret
	sudo make
	sudo chmod 755 git-credential-libsecret
	git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret

Note in a small desktop environment (e.g. RPi) you may need `sudo apt install seahorse`
for the GUI tool "Passwords and Keys".

In WSL (<https://github.com/git-ecosystem/git-credential-manager/blob/release/docs/wsl.md>):

	git config --global credential.helper /mnt/c/Users/<USERNAME>/AppData/Local/Programs/Git/mingw64/bin/git-credential-manager.exe

If you don't have a desktop environment, the following is based on
<https://github.com/git-ecosystem/git-credential-manager>
with <https://www.passwordstore.org/>

	sudo apt-get install --no-install-recommends pass
	gpg --gen-key
	pass init "<gpg-id>"
	echo 'export GPG_TTY=$(tty)' >>~/.profile

Then download the latest .deb from
<https://github.com/GitCredentialManager/git-credential-manager/releases/latest>

	sudo dpkg -i <path-to-package>

Or, on Raspberry Pi, based on the following:

- <https://github.com/git-ecosystem/git-credential-manager/blob/main/docs/install.md#net-tool>
- <https://learn.microsoft.com/en-us/dotnet/iot/deployment>

However, they may start releasing `.deb` packages for ARM:
<https://github.com/git-ecosystem/git-credential-manager/issues/1117#issuecomment-1474790084>

Download the latest .NET 6.0 SDK for Arm64 from
<https://dotnet.microsoft.com/en-us/download/dotnet/6.0>

	mkdir -vp $HOME/.dotnet
	tar zxvf dotnet-sdk-6.*-linux-arm64.tar.gz -C $HOME/.dotnet
	echo 'export DOTNET_ROOT=$HOME/.dotnet' >>~/.profile
	echo 'export PATH=$PATH:$HOME/.dotnet:$HOME/.dotnet/tools' >>~/.profile
	echo 'export DOTNET_CLI_TELEMETRY_OPTOUT=1' >>~/.profile
	# log out and in again for .profile changes to take effect
	dotnet tool install -g git-credential-manager

Then:

	git-credential-manager configure
	git config --global credential.credentialStore gpg

*Note* that the empty `credential.helper=` entry in the Git config is intentional, as per
<https://github.com/git-ecosystem/git-credential-manager/blob/11cecfd/docs/rename.md#troubleshooting>:
*"The blank entry is important as it makes sure GCM is the only credential helper that is configured, and overrides any helpers configured at the system/ machine-wide level."*

