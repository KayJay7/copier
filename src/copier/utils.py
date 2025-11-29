import os
import shutil
from collections.abc import Iterable
from grp import getgrnam
from pathlib import Path
from pwd import getpwnam
from typing import NamedTuple
import mimetypes

__all__ = [
    "ensure_uid",
    "ensure_gid",
    "Schema",
    "Item",
    "loop_files",
    "copy_and_own",
    "copytree",
    "copy_dir_structure",
    "copy_top_dir",
    "convert_mode",
    "copy_or_link_file",
    "better_guess",
]

type Schema = dict[str | int, dict[str | int, dict[int, dict[str, str]]]]


class Item(NamedTuple):
    owner: str | int
    group: str | int
    octal: int
    uid: int
    gid: int
    mode: int
    src: Path
    dst: Path


def ensure_uid(owner: str | int) -> int:
    if isinstance(owner, int):
        return owner
    else:
        return getpwnam(owner).pw_uid


def ensure_gid(group: str | int) -> int:
    if isinstance(group, int):
        return group
    else:
        return getgrnam(group).gr_gid


def convert_mode(mode: int) -> int:
    return int(str(mode), base=8)


def loop_files(config: Schema) -> Iterable[Item]:
    for owner, next in config.items():
        try:
            uid = ensure_uid(owner)
            for group, next in next.items():
                try:
                    gid = ensure_gid(group)
                    for octal, next in next.items():
                        for src, dst in next.items():
                            mode = convert_mode(octal)
                            yield Item(
                                owner,
                                group,
                                octal,
                                uid,
                                gid,
                                mode,
                                Path(src),
                                Path(dst),
                            )
                except Exception as ex:
                    print(ex)
        except Exception as ex:
            print(ex)


def copy_and_own(src: Path, dst: Path, uid: int, gid: int, mode: int):
    shutil.copy(src, dst)
    os.chown(dst, uid, gid)
    os.chmod(dst, mode & 0o7777)


def copytree(src: Path, dst: Path, uid: int, gid: int, mode: int):
    shutil.copytree(src, dst, dirs_exist_ok=True)
    for dir, dirs, files in dst.walk():
        for name in dirs:
            dest = dir / name
            os.chown(dest, uid, gid)
            os.chmod(
                dest,
                (mode >> 12 if mode >= 1 << 12 else ((mode & 0o7777) | 0o111)),
            )

        for name in files:
            dest = dir / name
            os.chown(dest, uid, gid)
            os.chmod(dest, mode & 0o7777)


def copy_top_dir(src: Path, dst: Path, hard_link: bool, mime: str, dry_types: bool):
    assert src.is_dir()
    for item in src.iterdir():
        copy_or_link_file(item, dst / item.name, hard_link, mime, dry_types=dry_types)


def copy_dir_structure(
    src: Path, dst: Path, hard_link: bool, mime: str, dry_types: bool
):
    assert src.is_dir()
    base = dst / src.name
    for dir, dirs, files in src.walk():
        # print(f"{dir}, {files}, {dirs}")
        inner = dir.relative_to(src)
        for file in files:
            copy_or_link_file(
                dir / file,
                base / inner / file,
                hard_link,
                mime,
                dry_types=dry_types,
                parents=True,
            )


def copy_or_link_file(
    src: Path,
    dst: Path,
    hard_link: bool,
    mime: str,
    dry_types: bool = False,
    parents: bool = False,
):
    try:
        actual = better_guess(src)
        if dry_types:
            print(f'"{src}": {actual}')
        elif match_mime(actual, mime):
            if parents:
                os.makedirs(dst.parent, exist_ok=True)
            if hard_link:
                print(f'link: "{src}"->"{dst}"')
                os.link(src, dst)
            else:
                print(f'copy: "{src}"->"{dst}"')
                shutil.copy(src, dst)
    except AttributeError:
        pass
    except Exception as ex:
        print(ex)


def match_mime(actual: str, mime: str):
    return ("/" in mime and actual == mime) or actual.startswith(mime + "/")


def better_guess(path: os.PathLike) -> str:
    return mimetypes.guess_file_type(path, strict=False)[0] or "text/plain"
