import os
import pathlib

from argparse import ArgumentParser, Namespace
from zlib import decompress

GIT_DIR = pathlib.Path(".git")
GIT_OBJ_DIR = pathlib.Path(".git/objects")
GIT_REF_DIR = pathlib.Path(".git/refs")
GIT_HEAD_FILE = pathlib.Path(".git/HEAD")


class GitObject:
    def __init__(self, file_content: str) -> None:
        header, content = file_content.split("\x00")
        self.type = header.split(" ")[0]
        self.size = int(header.split(" ")[1])
        self.content = content


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
        content = decompress(obj_file.read()).decode("utf-8")

    obj = GitObject(content)

    if args.pretty_print:
        print(obj.content, end="")
    elif args.show_type:
        print(obj.type)
    elif args.show_size:
        print(obj.size)


def parse_init(parser: ArgumentParser) -> None:
    parser.set_defaults(entry=git_init)


def parse_cat_file(parser: ArgumentParser) -> None:
    parser.add_argument("object")
    g = parser.add_mutually_exclusive_group()
    g.add_argument(
        "-p",
        dest="pretty_print",
        action="store_true",
        help="pretty-print object's content",
    )
    g.add_argument(
        "-t",
        dest="show_type",
        action="store_true",
        help="show object type",
    )
    g.add_argument(
        "-s",
        dest="show_size",
        action="store_true",
        help="show object size",
    )

    parser.set_defaults(entry=git_cat_file)


def parse_args() -> Namespace:
    arg_parser = ArgumentParser()
    sub_parsers = arg_parser.add_subparsers()

    parse_init(
        sub_parsers.add_parser(
            "init",
            help="Create an empty Git repository or reinitialize an existing one",
        )
    )
    parse_cat_file(sub_parsers.add_parser("cat-file"))

    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.entry(args)
