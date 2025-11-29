from collections.abc import Callable
from typing import cast

import yaml

from copier.args import *
from copier.utils import *


def main():
    print(args)
    match args.sub:
        case "in":
            iter_config(copy_in)
        case "out":
            iter_config(copy_out)
        case "type":
            type_sub()


def type_sub():
    assert args.sub == "type"
    if args.source.is_file():
        dst = args.dest / args.source.name
        copy_or_link_file(
            args.source, dst, args.hard_link, args.mime, dry_types=args.dry_types
        )
    elif args.source.is_dir() and args.dest.is_dir():
        if args.keep_structure:
            copy_dir_structure(
                args.source, args.dest, args.hard_link, args.mime, args.dry_types
            )
        else:
            copy_top_dir(
                args.source, args.dest, args.hard_link, args.mime, args.dry_types
            )


def iter_config(copy_routine: Callable[[Item], None]):
    assert args.sub == "in" or args.sub == "out"
    with open(args.config) as conf:
        config = cast(Schema, yaml.safe_load(conf))
        for item in loop_files(config):
            copy_routine(item)


def copy_in(item: Item):
    assert args.sub == "in"
    try:
        print(f'copy: {args.mode} {args.owner}:{args.group} "{item.dst}"->"{item.src}"')
        uid = ensure_uid(args.owner)
        gid = ensure_gid(args.group)
        mode = convert_mode(args.mode)
        if item.dst.is_dir():
            copytree(item.dst, item.src, uid, gid, mode)
        else:
            copy_and_own(item.dst, item.src, uid, gid, mode)
    except Exception as ex:
        print(ex)


def copy_out(item: Item):
    try:
        print(
            f'copy: {item.octal} {item.owner}:{item.group} "{item.src}"->"{item.dst}"'
        )
        if item.src.is_dir():
            copytree(item.src, item.dst, item.uid, item.gid, item.mode)
        else:
            copy_and_own(item.src, item.dst, item.uid, item.gid, item.mode)
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    main()
