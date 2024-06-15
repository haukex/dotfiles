
# On Windows Git Bash, if there's no ~/.bashrc, this file can be used as a ~/.bashrc

# I used to set the following by editing ~/.bashrc, but with this here, I no longer need to do that.
# See /usr/lib/git-core/git-sh-prompt
GIT_PS1_SHOWDIRTYSTATE=1
GIT_PS1_SHOWUPSTREAM="auto"
GIT_PS1_SHOWSTASHSTATE=1
GIT_PS1_SHOWUNTRACKEDFILES=1
GIT_PS1_STATESEPARATOR=""
### Color:
GIT_PS1_SHOWCOLORHINTS=1
PROMPT_COMMAND='__git_ps1 "${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]" "\\\$ " "[%s]"'
#PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
#                      root: use 31 for red  here ^^
### No color:
#PROMPT_COMMAND='__git_ps1 "${debian_chroot:+($debian_chroot)}\u@\h:\w" "\\\$ " "[%s]"'
#PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '

# be paranoid
#alias cp='cp -ip'
#alias mv='mv -i'
#alias rm='rm -i'

alias ..='cd ..'
alias ...='cd ../..'
alias cd..='cd ..'

alias l='ls -lAh'
alias la='ls -la'
alias ll='ls -lh'
alias lt='ls -lht'
alias lcr='ls -lAR --color | less -RXF'

alias :w='echo "this is not vi"'
alias :q='echo "this is not vi"'
alias :wq='echo "this is not vi"'

alias prl='perl -wMstrict -MData::Dump'

alias grep="grep --color=auto --exclude-dir=.git --exclude-dir=__pycache__ --exclude-dir=.ipynb_checkpoints --exclude-dir='.venv*' --exclude-dir='.*cache' --exclude-dir=node_modules --exclude='.*.swp'"

