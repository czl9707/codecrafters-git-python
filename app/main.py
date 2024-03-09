import os
import pathlib
import hashlib
import zlib

from argparse import ArgumentParser, Namespace

GIT_DIR = pathlib.Path(".git")
GIT_OBJ_DIR = pathlib.Path(".git/objects")
GIT_REF_DIR = pathlib.Path(".git/refs")
GIT_HEAD_FILE = pathlib.Path(".git/HEAD")


class GitObject:
    def __init__(
        self,
        _content: bytes,
        _size: int,
        _type: str,
    ) -> None:
        self.content = _content
        self.size = _size
        self.type = _type
        self._hash = None

    @property
    def hash(self):
        if not self._hash:
            self._hash = hashlib.sha1(self.git_file_content).hexdigest()
        return self._hash

    @property
    def git_file_content(self) -> bytes:
        return f"{self.type} {self.size}".encode() + b"\x00" + self.content

    @property
    def git_file_path(self) -> pathlib.Path:
        return GIT_OBJ_DIR.joinpath(self.hash[0:2]).joinpath(self.hash[2:])

    @staticmethod
    def from_hash(_hash: str) -> "GitObject":
        obj_folder_name = _hash[0:2]
        obj_file_name = _hash[2:]
        obj_path = GIT_OBJ_DIR.joinpath(obj_folder_name).joinpath(obj_file_name)

        with open(obj_path, "rb") as obj_file:
            file_content = zlib.decompress(obj_file.read())

        header, content = file_content.split(b"\x00")

        git_obj = GitObject(
            _type=header.split(b" ")[0].decode(),
            _size=int(header.split(b" ")[1].decode()),
            _content=content,
        )
        git_obj._hash = _hash
        return git_obj

    @staticmethod
    def from_file(_path: pathlib.Path, type: str) -> "GitObject":
        with open(_path, "rb") as obj_file:
            b_content = obj_file.read()
        return GitObject(
            _content=b_content,
            _size=len(b_content),
            _type=type,
        )

    def write_to_file(self) -> None:
        if os.path.isfile(self.git_file_path):
            return

        with open(self.git_file_path, "xb") as f:
            f.write(zlib.compress(self.git_file_content))


def git_init(args: Namespace) -> None:
    os.mkdir(GIT_DIR)
    os.mkdir(GIT_OBJ_DIR)
    os.mkdir(GIT_REF_DIR)
    with open(GIT_HEAD_FILE, "w") as f:
        f.write("ref: refs/heads/master\n")
    print("Initialized git directory")


def git_cat_file(args: Namespace) -> None:
    obj_hash = args.object
    obj = GitObject.from_hash(obj_hash)

    if args.pretty_print:
        print(obj.content.decode(), end="")
    elif args.show_type:
        print(obj.type)
    elif args.show_size:
        print(obj.size)


def git_hash_object(args: Namespace) -> None:
    obj_path = args.file
    git_obj = GitObject.from_file(obj_path, "blob")

    if args.write:
        git_obj.write_to_file()

    print(git_obj.hash)


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


def parse_hash_object(parser: ArgumentParser) -> None:
    parser.add_argument("file")
    parser.add_argument(
        "-w",
        dest="write",
        action="store_true",
        help="write the object into the object database",
    )

    parser.set_defaults(entry=git_hash_object)


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
    parse_hash_object(sub_parsers.add_parser("hash-object"))

    return arg_parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    args.entry(args)
