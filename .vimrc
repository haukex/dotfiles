
" Note to self: in situations where ESC doesn't work, Ctrl-C works!

" Default character encoding. (Could also be "latin1", but this is prob. better)
set encoding=utf-8
" To do a per-file setting (I think): ":setlocal fileencoding=utf-8"
" Note you can query it via ":set fenc?". See also ":help fenc"!

syntax on

" in this color scheme on my machine: in quotes is "red"
" the "on" in "syntax" above is green
" "tabstop" below is purple
" | yellow | white
" v        v
color default
" Note that in the Gnome Terminal, I personally like the "White on Black" with XTerm colors best.

set tabstop=4
set shiftwidth=4
set autoindent
set smartindent
set breakindent
" Load indentation rules and plugins according to the detected filetype
filetype plugin indent on
set modeline

set ignorecase
set smartcase

" https://vimhelp.org/options.txt.html#'incsearch'
" https://vim.fandom.com/wiki/Highlight_all_search_pattern_matches
"set noincsearch
"set nohlsearch
set incsearch
" only enable "highlight all matches" while searching, not after
augroup vimrc-incsearch-highlight
	autocmd!
	autocmd CmdlineEnter /,\? :set hlsearch
	autocmd CmdlineLeave /,\? :set nohlsearch
augroup END

set nocursorline
" the following is line numbering
set nonumber
set wrap

" how to show some invisible non-space characters
set listchars=eol:$,tab:>-,trail:~,extends:+,precedes:<,nbsp:_
" but don't show them by default
set nolist

" showmatch jumps the cursor to a matching bracket (default is to just
" highlight I think)
set noshowmatch

" the following turns on everything shown in the bottom line
set showcmd
set showmode
set ruler

" but hide the window's extra status line if there's only one window
set laststatus=1
" and make the "command" line a little more helpful
set rulerformat=%25(C\ %-5(%c%V%)\ L\ %l/%L%=%p%%%)

" disable restoring of terminal:
"set t_ti= t_te=

" On a USB stick, the backups and swap files can slow vim down.
" The following would disable them:
set nobackup
"set nowritebackup
"set noswapfile
" Note: The above disables swap files and backups completely,
" the following just puts them all in a central place.
" (Although you might want to choose a directory in a tmpfs)
"set backupdir=~/.vim/backup/
"set directory=~/.vim/backup/

set mouse=a
set mousemodel=popup_setpos

" jump to the last position when reopening a file
autocmd BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\"" | endif

" Note: To control when a file should auto-wrap text to a certain column, the
" following command can be used:
":setlocal textwidth=78
" To see the current value, just do ":set textwidth?"
" There are a lot more formatting options: ":help formatting"!

" Note you can rewrap a block of text by selecting it (visual mode) and
" pressing "gq". To rewrap the current block (apparently sometimes only
" starting with the currently selected line?), use "gq}". The following binds
" that to Ctrl-j, which I've never otherwise used.
map <C-j> {gq}

" to turn on spell check:
" ":setlocal spell"
" but note that it's easier to use in the GUI, you can turn it on by default
" there with "set spell" in ".gvimrc", then you can just do ":gui"
set spelllang=en_us
autocmd Filetype pod setlocal spell
autocmd Filetype gitcommit setlocal spell
" two useful commands are "zg" (add to user dictionary) and "z=" (show suggestions)
" http://vimdoc.sourceforge.net/htmldoc/spell.html

autocmd Filetype python setlocal expandtab
autocmd Filetype arduino setlocal ts=2 sw=2 expandtab

" The following creates two new commands "s" and "S" which insert/append a single
" character, but can also be repeated, e.g. "3S." appends three periods...
function! RepeatChar(char, count)
	return repeat(a:char, a:count)
endfunction
nnoremap s :<C-U>exec "normal i".RepeatChar(nr2char(getchar()), v:count1)<CR>
nnoremap S :<C-U>exec "normal a".RepeatChar(nr2char(getchar()), v:count1)<CR>

" vim: set ft=vim :
