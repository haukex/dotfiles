#!/usr/bin/env python
"""Script to install Hauke's .dotfiles.

Author, Copyright, and License
------------------------------
Copyright (c) 2023-2024 Hauke Daempfling (haukex@zero-g.net)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/
"""
import os
import re
import sys
import subprocess
from pathlib import Path
from difflib import unified_diff
from typing import Optional, NamedTuple
from collections.abc import Callable, Sequence, Generator, Iterable
from igbpyutils.file import replace_link, replacer, NamedTempFileDeleteLater  # type: ignore[import-untyped]
from colorama import Fore, Back, Style
assert sys.version_info >= (3,9)

ISWIN = sys.platform.startswith('win32') or sys.platform.startswith('cygwin')

FilterType = Callable[ [Sequence[str]], Generator[str, None, None] ]

def gitconf_copyfilt(lines :Iterable[str]) -> Generator[str, None, None]:
    assert ISWIN
    yield from ( ln[2:] if ln.startswith('#w') else ln for ln in lines )
_gitconf_cred_re = re.compile(r'''^\s*(helper\s*=|credentialStore\s*=\s*gpg\s*$)''', re.IGNORECASE)
_gitconf_cred_win_re = re.compile(r'''^\s*helper\s*=\s*manager\s*$''', re.IGNORECASE)
_gitconf_safe_re = re.compile(r'''^\s*directory\s*=''', re.IGNORECASE)
def gitconf_difffilt(lines :Sequence[str]) -> Generator[str, None, None]:
    insect = None
    # figure out if we can drop the entire [safe] section
    drop_safe = True
    for ln in lines:
        if ln.strip().startswith('['):
            insect = ln.strip().lower()
        elif insect == '[safe]' and not _gitconf_safe_re.match(ln):
            drop_safe = False
    insect = None  # don't keep state from the previous loop
    for ln in lines:
        if ln.strip().startswith('['):
            insect = ln.strip().lower()
        if insect == '[credential]' and _gitconf_cred_re.match(ln) and not (ISWIN and _gitconf_cred_win_re.match(ln)):
            continue
        if insect == '[safe]' and (drop_safe or _gitconf_safe_re.match(ln)):
            continue
        yield ln

_win_profile_diff_re = re.compile(r'^\s*(?:export\s+PATH=|ssh-add\b|$)')
def win_profile_difffile(lines :Iterable[str]) -> Generator[str, None, None]:
    assert ISWIN
    yield from ( ln for ln in lines if not _win_profile_diff_re.search(ln) )

def nullfilt(lines :Iterable[str]) -> Generator[str, None, None]:
    yield from lines

class FileEntry(NamedTuple):
    src :str
    dst :Optional[str] = None
    #TODO Later: perhaps a "clobber_ok" flag? (e.g. git_mysync.py)
    # NOTE "copy filter" is a bit of a misnomer, it's a filter that's *always* applied to the source...
    copy_filt :FilterType = nullfilt
    diff_filt :FilterType = nullfilt

thefiles = (  # Common files
    FileEntry(src='.bash_aliases'),
    FileEntry(src='.vimrc'),
    FileEntry(src='git_mysync.py', dst='~/bin/git_mysync.py'),  #TODO: set exec bit on Linux
) + ((  # Windows / Cygwin
    FileEntry(src='win_git_bash.profile', dst='.profile', diff_filt=win_profile_difffile),
    FileEntry(src='win.bashrc', dst='.bashrc'),
    FileEntry(src='.gitconfig', dst='~/AppData/Local/Programs/Git/etc/gitconfig',
              copy_filt=gitconf_copyfilt, diff_filt=gitconf_difffilt),
) if ISWIN else (  # assume Linux
    #TODO: in DevPod, .gitconfig is already "\n[credential]\n        helper = ...\n" - can we merge that in?
    FileEntry(src='.gitconfig', copy_filt=nullfilt, diff_filt=gitconf_difffilt),
    FileEntry(src='.perlcriticrc'),
    FileEntry(src='.perltidyrc'),
    FileEntry(src='.screenrc'),
    #TODO: create directories (the following and ~/bin)
    FileEntry(src='config_git_ignore', dst='~/.config/git/ignore'),
))

class UserOpts(NamedTuple):
    quiet :bool
    copy_not_link :bool
    dryrun :bool
    diff_nofilt :bool
    ask_clobber :bool
    ask_merge :bool

def link_or_copy(src :Path, dst :Path, *, copy_filt :FilterType, opts :UserOpts, are_identical :bool=False):
    if ISWIN or opts.copy_not_link or copy_filt is not nullfilt:
        if are_identical:
            if not opts.quiet: print("Files are 100% identical, don't need to copy")
        else:
            if not opts.quiet: print(f"Copying {src} => {dst}")
            if not opts.dryrun:
                with src.open(encoding='UTF-8') as ifh:
                    contents = ''.join( ln for ln in copy_filt(list(ifh)) )
                if dst.exists():
                    with replacer(dst, encoding='UTF-8') as (_, ofh):
                        ofh.write(contents)
                else:
                    with dst.open('w', encoding='UTF-8') as ofh:
                        ofh.write(contents)
    else:
        if not opts.quiet: print(f"{'Files are 100% identical, linking' if are_identical else 'Linking'} {src} => {dst}")
        if not opts.dryrun: replace_link(src, dst)  # "link pointing to src named dst"

def print_diff(diff :Iterable[str]):
    #TODO Later: Could sync with https://github.com/haukex/my-py-template/blob/main/apply.py
    for line in diff:
        if line.startswith('+') and not line.startswith('+++'):
            print(Fore.GREEN, end='')
        elif line.startswith('-') and not line.startswith('---'):
            print(Fore.RED, end='')
        elif line.startswith('@@'):
            print(Fore.CYAN, end='')
        print(line + Style.RESET_ALL)

def proc_files(files :Iterable[FileEntry], *, opts :UserOpts):
    for fe in files:
        dstn = fe.dst if fe.dst else fe.src
        srcp = Path(__file__).parent.joinpath(fe.src)
        dstp = Path(dstn).expanduser()
        if not dstp.is_absolute(): dstp = Path.home().joinpath(dstp)
        print(f"{Fore.BLACK}{Back.CYAN}# {srcp} => {dstp} {Style.RESET_ALL}", end='' if opts.quiet else '\n')
        with srcp.open(encoding='UTF-8') as fh:
            srcdata = fh.read()
        try:
            with dstp.open(encoding='UTF-8') as fh:
                dstdata = fh.read()
        except FileNotFoundError:
            if not opts.quiet: print("Destination doesn't exist")
            link_or_copy(srcp, dstp, copy_filt=fe.copy_filt, are_identical=False, opts=opts)
            if opts.quiet: print(f"\r{Fore.GREEN}# {srcp} => {dstp} - OK {Fore.RESET}")
            continue
        if srcdata == dstdata:  # files are 100% identical
            link_or_copy(srcp, dstp, copy_filt=fe.copy_filt, are_identical=True, opts=opts)
            if opts.quiet: print(f"\r{Fore.GREEN}# {srcp} => {dstp} - OK {Fore.RESET}")
            continue
        # else:  # files are NOT 100% identical
        srclns = list(fe.copy_filt(srcdata.splitlines()))
        dstlns = dstdata.splitlines()
        if srclns == dstlns:
            if opts.quiet: print(f"\r{Fore.GREEN}# {srcp} => {dstp} - OK {Fore.RESET}")
            else: print("Raw files differ, but are identical after applying filter")
            continue
        # Note we show diff in this order so it represents what would be done to the dest file on clobber
        diff = list(unified_diff(
            list(fe.diff_filt(dstlns)),
            list(fe.diff_filt(srclns)),
            #TODO Later: in the following output, some filenames include ~, prefix doesn't make sense
            fromfile='local/'+dstn, tofile='dotfiles/'+fe.src, lineterm=''))
        if diff:  # there are differences even with filters applied
            if opts.quiet:
                print(f"\r{Fore.BLACK}{Back.YELLOW}# {srcp} => {dstp} {Style.RESET_ALL}")
            print_diff(diff)
        else:  # there are no differences after applying filters
            if opts.quiet:
                if opts.diff_nofilt: print(f"\r{Back.GREEN}{Fore.BLACK}# {srcp} => {dstp} - OK {Fore.RESET}{Back.RESET}")
                else: print(f"\r{Fore.YELLOW}# {srcp} => {dstp} - {Fore.GREEN}OK {Fore.RESET}")
            elif not opts.diff_nofilt: print("Files differ, but not significantly")
            if opts.diff_nofilt:
                if not opts.quiet: print("Files differ, but not significantly - diff without filters:")
                print_diff(unified_diff(dstlns, srclns,
                    fromfile='local/'+dstn, tofile='dotfiles/'+fe.src, lineterm=''))
        if opts.ask_clobber:
            if input('Clobber destination file? [yN] ').lower().startswith('y'):
                link_or_copy(srcp, dstp, copy_filt=fe.copy_filt, are_identical=False, opts=opts)
        elif opts.ask_merge:
            with NamedTempFileDeleteLater('w', dir=dstp.parent, prefix=dstp.name+"_SKEL.tmp", encoding='UTF-8') as tf:
                for ln in srclns: print(ln, file=tf)
                tf.close()
                subprocess.run(
                    [os.environ['COMSPEC'], '/c', f"start /wait winmerge {tf.name} {dstp}"]
                    if ISWIN else ['meld', tf.name, str(dstp)], check=False )

if __name__ == '__main__':
    import argparse
    from igbpyutils.error import init_handlers  # type: ignore [import-untyped]
    from colorama import just_fix_windows_console
    just_fix_windows_console()
    init_handlers()
    parser = argparse.ArgumentParser(description="Hauke's Skel Setup Tool")
    parser.add_argument('-v', '--verbose', help="be more verbose", action="store_true")
    parser.add_argument('-c', '--copy', help="copy instead of hard link", action="store_true")
    parser.add_argument('-n', '--dry-run', help="don't actually do any operations", action="store_true")
    parser.add_argument('-d', '--diff', help="show diff without filter", action="store_true")
    parser.add_argument('-i', '--interactive', help="prompt whether to clobber changes (implies -d)", action="store_true")
    parser.add_argument('-m', '--mergetool', help="run merge tool (Meld or WinMerge)", action="store_true")
    args = parser.parse_args()
    if args.interactive and args.mergetool:
        parser.error("Can't use -i (interactive) and -m (mergetool) together")
    proc_files(thefiles, opts=UserOpts(quiet=not args.verbose, copy_not_link=args.copy, dryrun=args.dry_run,
        diff_nofilt=args.diff or args.interactive, ask_clobber=args.interactive, ask_merge=args.mergetool ) )
    if args.dry_run:
        print(f"{Style.BRIGHT}*** REMINDER: This was a dry-run! ***{Style.RESET_ALL}")
    sys.exit(0)
