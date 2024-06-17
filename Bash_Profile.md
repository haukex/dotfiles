Hauke's Notes on `.bashrc` and `.profile`
=========================================

* Optional: Disable `.bash_history` via `HISTFILE=`
  (I usually put this right after HISTSIZE and HISTFILESIZE)

* If color prompt isn't working, enable color in more terminals by changing the line
  `xterm-color) color_prompt=yes;;` to `xterm*|linux|screen*) color_prompt=yes;;`

* For `root`'s `PS1`, change `[01;32m\]` (green) to `[01;31m\]` (red)

* Example of adding directories to `PATH`:

        test -d /path/to/bin && PATH="/path/to/bin${PATH:+:${PATH}}"

Umask
-----

How to best change this has changed over the years.

Initially, it was a simple `umask 077` in the profile.

As of around 2021, it was required to find the lines that look like
`session optional pam_umask.so` in `/etc/pam.d/*` and append `umask=0077`,
though I believe the changes are system-wide.

Currently (2023), the "best" way I can tell to change the umask is
to run `chfn $USER` and set the "Other" field to `umask=077`.

See also `man login.defs`, `man pam_umask`, ...

