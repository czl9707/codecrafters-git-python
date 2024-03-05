import os
import pathlib

from argparse import ArgumentParser, Namespace
from zlib import decompress

GIT_DIR = pathlib.Path(".git")
GIT_OBJ_DIR = pathlib.Path(".git/objects")
GIT_REF_DIR = pathlib.Path(".git/refs")
GIT_HEAD_FILE = pathlib.Path(".git/HEAD")


def git_init(args: Namespace) -> None:
    os.mkdir(GIT_DIR)
    os.mkdir(GIT_OBJ_DIR)
    os.mkdir(GIT_REF_DIR)
    with open(GIT_HEAD_FILE, "w") as f:
        f.write("ref: refs/heads/master\n")
    print("Initialized git directory")


def git_cat_file(args: Namespace) -> None:
    obj_name = args.object
    obj_folder_name = obj_name[0:2]
    obj_file_name = obj_name[2:]
    obj_path = GIT_OBJ_DIR.joinpath(obj_folder_name).joinpath(obj_file_name)

    with open(obj_path, "rb") as obj_file:
        bs = decompress(obj_file.read())

    if args.pretty_print:
        print(bs.decode("utf-8"), end="")


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()
    sub_parsers = arg_parser.add_subparsers()

    init_parser = sub_parsers.add_parser(
        "init", help="Create an empty Git repository or reinitialize an existing one"
    )
    init_parser.set_defaults(entry=git_init)

    cat_file_parser = sub_parsers.add_parser(
        "cat-file",
    )
    cat_file_parser.add_argument("object")
    cat_file_parser.add_argument(
        "-p",
        dest="pretty_print",
        action="store_true",
        help="pretty-print object's content",
    )
    cat_file_parser.set_defaults(entry=git_cat_file)

    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.entry(args)
