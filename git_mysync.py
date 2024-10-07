#!/usr/bin/env python
"""This script checks a set of git repositories for synchronization with the server.

Author, Copyright, and License
------------------------------
Copyright (c) 2023 Hauke Daempfling (haukex@zero-g.net)
at the Leibniz Institute of Freshwater Ecology and Inland Fisheries (IGB),
Berlin, Germany, https://www.igb-berlin.de/

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
import re
import sys
import argparse
import subprocess
from pathlib import Path
from warnings import warn
from igbpyutils.error import init_handlers  # type: ignore[import-untyped]
from colorama import just_fix_windows_console, Fore, Style

DEFAULT_CONF_FILE = '~/.git-mysync'

init_handlers()
just_fix_windows_console()
parser = argparse.ArgumentParser(description='My Git Sync Checker')
parser.add_argument('-c', '--conf-file', help=f"alternate config file (default: {DEFAULT_CONF_FILE})")
parser.add_argument('-g', '--add-git', help="additional git repo(s) to check", action="append")
parser.add_argument('-s', '--search', help="search these dirs for git repos", action="append")
parser.add_argument('-f', '--fetch', help="do a git fetch first", action="store_true")
parser.add_argument('-l', '--changes', help="show local changes and stash", action="store_true")
parser.add_argument('-v', '--verbose', help="be more verbose", action="store_true")
args = parser.parse_args()

conf_file = Path( args.conf_file if args.conf_file else DEFAULT_CONF_FILE )
conf_repos :set[Path] = set()
try:
    conf_file = conf_file.expanduser().resolve(strict=True)
except FileNotFoundError:
    warn(f"configuration file {conf_file!r} not found!")
else:
    with conf_file.open(encoding='UTF-8') as fh:
        for line in fh:
            if line.lstrip().startswith('#') or not line.strip(): continue
            try:
                conf_repos.add( Path(line.strip()).expanduser().resolve(strict=True) )
            except FileNotFoundError as ex:
                raise FileNotFoundError(line) from ex
    if args.verbose: print(f"{Style.DIM}# read config file: {conf_file}{Style.RESET_ALL}")

xtra_repos :set[Path] = set()
if args.add_git:
    for p in args.add_git:
        xtra_repos.add( Path(p).expanduser().resolve(strict=True) )
if args.search:
    for p in args.search:
        for pth in Path(p).expanduser().resolve(strict=True).rglob('.git'):
            if pth.is_dir():
                xtra_repos.add( pth.parent )

if not conf_repos and not xtra_repos:
    raise RuntimeError('No git repositories to check!')

# https://git-scm.com/docs/git-status#_porcelain_format_version_2
head_re  = re.compile(r'''^# branch.head (.+)$''', re.MULTILINE)
upstream_re = re.compile(r'''^# branch.upstream (.+)$''', re.MULTILINE)
ahead_re = re.compile(r'''^# branch.ab \+(\d+) -(\d+)$''', re.MULTILINE)
stash_re = re.compile(r'''^# stash (\d+)$''', re.MULTILINE)

def finalize(output :str, warns :list[str]):
    print(output+Style.RESET_ALL+(f" {Fore.YELLOW}{', '.join(warnings)}{Fore.RESET}" if warns else ''))

issue_count = 0
warn_count = 0
for pth in sorted(conf_repos|xtra_repos):
    out = f"{('~'/pth.relative_to(Path.home()) if pth.is_relative_to(Path.home()) else pth) if args.verbose else pth.name} "
    print(out, end='', flush=True)
    warnings :list[str] = []
    if pth not in conf_repos:
        warnings.append('Not in config')
        warn_count += 1
    rv = subprocess.run(['git','remote'],
        cwd=pth, encoding='UTF-8', capture_output=True, check=True)
    if rv.stderr: raise subprocess.SubprocessError(f"stderr={rv.stderr!r}")
    remotes = rv.stdout.splitlines()
    if 'origin' in remotes:
        warnings.append('Remote named origin')
        warn_count += 1
    if not remotes:
        finalize(f"\r{Fore.RED}{out}No remotes", warnings)
        issue_count += 1
        continue
    if args.verbose:
        rem_str = f"{remotes=} "
        out += rem_str
        print(rem_str, end='', flush=True)
    if args.fetch:
        print("fetch-", end='', flush=True)
        try:
            rv = subprocess.run( ['git','fetch','--quiet'],
                cwd=pth, encoding='UTF-8', capture_output=True, check=True )
            if rv.stderr: raise subprocess.SubprocessError(f"stderr={rv.stderr!r}")
        except subprocess.SubprocessError as ex:
            finalize(f"\r{Fore.RED}{out}fetch-ERROR: {ex}", warnings)
            issue_count += 1
            continue
        else:
            out += "fetch-ok "
            print(f"{Fore.GREEN}ok{Fore.RESET} ", end='', flush=True)
    try:
        rv = subprocess.run(
            ['git','status','--porcelain=v2','--branch','--ahead-behind','--show-stash'],
            cwd=pth, encoding='UTF-8', capture_output=True, check=True )
        if rv.stderr: raise subprocess.SubprocessError(f"stderr={rv.stderr!r}")
    except subprocess.SubprocessError as ex:
        finalize(f"\r{Fore.RED}{out}git-status ERROR: {ex}", warnings)
        issue_count += 1
        continue
    if not ( m := head_re.search(rv.stdout) ):
        raise RuntimeError(f"failed to find branch.head in output {rv.stdout=}")
    head = m.group(1)
    print(f"{head=} ", end='', flush=True)
    if m := stash_re.search(rv.stdout):
        stash = int(m.group(1))
    else: stash = 0
    lines = [ x for x in rv.stdout.splitlines() if x.strip() and not x.startswith('#') ]
    if lines:
        warnings.append(f"{len(lines)} local change{'' if len(lines)==1 else 's'}")
        warn_count += 1
    if stash:
        warnings.append(f"{stash} stash entr{'y' if stash==1 else 'ies'}")
        warn_count += 1
    if m := upstream_re.search(rv.stdout):
        upstream = m.group(1)
        if m := ahead_re.search(rv.stdout):
            ahead = int(m.group(1))
            behind = int(m.group(2))
            if not ahead and not behind:
                finalize(f"\r{Fore.GREEN}{out}{head=} {upstream=} up-to-date", warnings)
            else:
                finalize(f"{upstream=} {Fore.RED}we are {ahead=} {behind=}", warnings)
                issue_count += 1
        else:
            raise RuntimeError(f"found branch.upstream but not ahead/behind info {rv.stdout=}")
    else:
        finalize(f"\r{Fore.RED}{out}{head=} No upstream", warnings)
        issue_count += 1
    if args.changes:
        subprocess.run( ['git','status','--short'], cwd=pth, check=True )
        # git stash list seems to break the color codes on the windows console, so work around by capturing...
        rv2 = subprocess.run( ['git','stash','list'],
            cwd=pth, encoding='UTF-8', capture_output=True, check=True )
        if rv2.stderr: print(rv2.stderr, end='', file=sys.stderr)
        if rv2.stdout: print(rv2.stdout, end='')

warn_str = f"{warn_count} warning{'' if warn_count==1 else 's'}"
if issue_count:
    warn_str = f" {Fore.YELLOW}and {warn_str}{Fore.RESET}" if warn_count else ''
    print(f"{Fore.RED}# {issue_count} issue{'' if issue_count==1 else 's'}{Fore.RESET}{warn_str}")
else:
    warn_str = f", {Fore.YELLOW}but {warn_str}{Fore.RESET}" if warn_count else ''
    print(f"{Fore.GREEN}# All OK:{Fore.RESET} Everything up-to-date{warn_str}")
sys.exit(issue_count)
