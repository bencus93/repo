#!/usr/bin/python3

from lilaclib import *
from lilac2.api import _download_aur_pkgbuild, _g
import glob

def aur_pre_build_edit(
  name: Optional[str] = None, *, do_vcs_update: Optional[bool] = None,
) -> None:
  if os.path.exists('PKGBUILD'):
    pkgver, pkgrel = get_pkgver_and_pkgrel()
  else:
    pkgver = None

  _g.aur_pre_files = clean_directory()
  if name is None:
    name = os.path.basename(os.getcwd())
  _g.aur_building_files = _download_aur_pkgbuild(name)

  rev = "", ""
  for line in edit_file('PKGBUILD'):
    if line.strip().startswith('_rev='):
      rev = line[len('_rev='):].strip()
      print(line)
    elif line.strip().startswith('pkgrel='):
      # evaluate and replace pkgrel= variable
      print(f"pkgrel={rev}")
    else:
      print(line)

  new_pkgver, new_pkgrel = get_pkgver_and_pkgrel()
  if pkgver and pkgver == new_pkgver:
    # change to larger pkgrel
    update_pkgrel(max(pkgrel, new_pkgrel))

  if do_vcs_update is None:
    do_vcs_update = name.endswith(('-git', '-hg', '-svn', '-bzr'))

  if do_vcs_update:
    vcs_update()
    # recheck after sync, because AUR pkgver may lag behind
    new_pkgver, new_pkgrel = get_pkgver_and_pkgrel()
    if pkgver and pkgver == new_pkgver:
      update_pkgrel(max(pkgrel, new_pkgrel))


def pre_build():
    aur_pre_build_edit()
    for line in edit_file('PKGBUILD'):
        if line.strip().startswith('https://github.com/Eloston/ungoogled-chromium/archive/$pkgver-$pkgrel.tar.gz'):
            print('https://github.com/Eloston/ungoogled-chromium/archive/$pkgver-$_rev.tar.gz')
        elif line.strip().startswith('_ungoogled_repo="$srcdir/$pkgname-$pkgver-$pkgrel"'):
            print('  _ungoogled_repo="$srcdir/$pkgname-$pkgver-$_rev"')
        else:
            print(line)
    
    run_cmd(["updpkgsums"])


if __name__ == '__main__':
    single_main('extra-x86_64')

