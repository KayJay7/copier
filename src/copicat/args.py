import argparse
import os
from pathlib import Path
from typing import Literal, NamedTuple, cast

__all__ = ["args", "Args", "InArgs", "OutArgs", "TypeArgs"]


class InArgs(NamedTuple):
    sub: Literal["in"]
    config: Path
    owner: str | int
    group: str | int
    mode: int
    dry_run: bool


class OutArgs(NamedTuple):
    sub: Literal["out"]
    config: Path
    dry_run: bool


class TypeArgs(NamedTuple):
    sub: Literal["type"]
    source: Path
    dest: Path
    keep_structure: bool
    hard_link: bool
    mimes: list[str]
    extensions: list[str]
    dry_types: bool
    dry_run: bool


type Args = InArgs | OutArgs | TypeArgs

_parser = argparse.ArgumentParser("copicat")
_subparsers = _parser.add_subparsers(
    title="subcommands", dest="sub", required=True, help="copicat subcommands"
)

_parser_out = _subparsers.add_parser(
    "out", help="Copy files from source to target location"
)
_parser_in = _subparsers.add_parser(
    "in", help="Copy files from target to source location"
)
_parser_type = _subparsers.add_parser(
    "type",
    help="Copy files from source to destination location based on mime type or extension",
)

_parser_out.add_argument(
    "config",
    nargs="?",
    help='Path to YAML config file. Default is "copicat.yml"',
    default="copicat.yml",
    type=Path,
)

_parser_in.add_argument(
    "config",
    nargs="?",
    help='Path to YAML config file. Default is "copicat.yml"',
    default="copicat.yml",
    type=Path,
)

_parser_in.add_argument(
    "owner",
    nargs="?",
    help="Username or UID of the owner of the files",
    default=os.getuid(),
)

_parser_in.add_argument(
    "group",
    nargs="?",
    help="Group name or GID of the group of the files",
    default=os.getgid(),
)

_parser_in.add_argument(
    "mode",
    nargs="?",
    type=int,
    help="Mode of the crated files in the same format as the config file",
    default="660",
)

_parser_type.add_argument("source", help="Source directory or file", type=Path)

_parser_type.add_argument("dest", help="Destination directory", type=Path)

_parser_type.add_argument(
    "-m",
    "--mimes",
    metavar="MIME",
    nargs="*",
    help='Half or full of mime types to copy (i.e.: both "video" and "video/x-matroska" will match a file with mimetype "video/x-matroska")',
    default=[],
)

_parser_type.add_argument(
    "-e",
    "--extensions",
    metavar="EXTENSION",
    nargs="*",
    help='Extensions with point of the files to copy (i.e.: ".srt" will match "subs.srt")',
    default=[],
)

_parser_type.add_argument(
    "-k",
    "--keep-structure",
    help="Keep the directory structure in the destination. Without this, only the files from the first level will be copied",
    action="store_true",
)

_parser_type.add_argument(
    "-H",
    "--hard-link",
    help="Hard-link files into destination instead of copying",
    action="store_true",
)

_parser_type.add_argument(
    "-T",
    "--dry-types",
    help="Just print the types of all candidate source files. Different implementations might identify types differently",
    action="store_true",
)


#### dry run on all parsers

_parser_type.add_argument(
    "-D",
    "--dry-run",
    help="Print the operation without performing any action",
    action="store_true",
)

_parser_in.add_argument(
    "-D",
    "--dry-run",
    help="Print the operation without performing any action",
    action="store_true",
)

_parser_out.add_argument(
    "-D",
    "--dry-run",
    help="Print the operation without performing any action",
    action="store_true",
)

####

args = cast(Args, _parser.parse_args())
