#!/usr/bin/env python3

import argparse
import os
import sys
import glob
import shutil
import antlr4
from antlrgenerated.tlcpLexer import tlcpLexer
from antlrgenerated.tlcpParser import tlcpParser
from antlrgenerated.tlcpVisitor import tlcpVisitor
from antlrgenerated.tlcpListener import tlcpListener
from visitor import TlcpVisitor

EXTENSION = '.meta.cfg'
GENERATED_MODELS_DIR = 'tlcp_models'
ANTLR_HIDDEN_CHANNEL = 2

# def dir_path(string):
#     if os.path.isdir(string):
#         return string
#     else:
#         raise NotADirectoryError(string)

# def file_path(string):
#     if os.path.isfile(string):
#         return string
#     elif os.path.isdir(string):
#         return IsADirectoryError(string)
#     else:
#         raise FileNotFoundError(string)


def get_metacfg_files(dirs):
    return sum((glob.glob(os.path.join(d, "*{ext}".format(ext=EXTENSION))) for d in dirs), start=[])


def process_arguments(args):
    if not args.directory:
        for f in args.files:
            if not os.path.exists(f):
                print("File '{}' not found.".format(f), file=sys.stderr)
                sys.exit(2)
            if not os.path.isfile(f):
                print("'{}' is not a file.".format(f), file=sys.stderr)
                sys.exit(2)
            if not f.endswith(EXTENSION):
                print("File '{}' is not a {ext} file.".format(f, ext=EXTENSION), file=sys.stderr)
                sys.exit(2)

    if args.directory:
        for f in args.files:
            if not os.path.exists(f):
                print("Directory '{}' not found.".format(f), file=sys.stderr)
                sys.exit(2)
            if not os.path.isdir(f):
                print("'{}' is not a direcory.".format(f), file=sys.stderr)
                sys.exit(2)
        args.files = get_metacfg_files(args.files)
        if not args.files:
            print("Found no {ext} files.".format(ext=EXTENSION), file=sys.stderr)
            sys.exit(2)


def process_file(file, args):
    assert file.endswith(EXTENSION)
    config_dir = os.path.dirname(file)
    config_name = os.path.basename(file)[:-len(EXTENSION)]
    models_dir = os.path.join(config_dir, GENERATED_MODELS_DIR, config_name)
    
    if os.path.isdir(models_dir) and not os.path.islink(models_dir):
        shutil.rmtree(models_dir)
    
    os.makedirs(models_dir, exist_ok=True)
    
    input_stream = antlr4.FileStream(file)
    lexer = tlcpLexer(input_stream)
    stream = antlr4.CommonTokenStream(lexer)
    parser = tlcpParser(stream)
    tree = parser.config()
    configs = TlcpVisitor(basic_name=config_name).visit(tree)

    for config in configs:
        if config.family:
            family_dir = os.path.join(models_dir, config.family)
            os.makedirs(family_dir, exist_ok=True)
        else:
            family_dir = models_dir
        with open(os.path.join(family_dir, config.name + ".cfg"), mode="w") as f:
            ret = f.write(config.text)
            assert ret == len(config.text)


def main():
    parser = argparse.ArgumentParser(
        description="A preprocessor for TLC configuration files."
                    "Converts {ext} files to TLC .cfg files.".format(ext=EXTENSION))
    parser.add_argument(
        "--directory", "-d",
        default=False,
        action="store_true",
        help="Process all {ext} files in a directory.".format(ext=EXTENSION))
    parser.add_argument(
        "files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="The {ext} file. Or the directory with {ext} files if -d is used.".format(ext=EXTENSION))
    parser.add_argument(
        "--cleanup", "-c",
        default=False,
        action="store_true",
        help="Removes the old {dir} folder before generating new models.".format(dir=GENERATED_MODELS_DIR))
    args = parser.parse_args()

    process_arguments(args)

    if args.cleanup and os.path.exists(GENERATED_MODELS_DIR):
        shutil.rmtree(GENERATED_MODELS_DIR)

    for file in args.files:
        process_file(file, args)


if __name__ == "__main__":
    main()
