#!/usr/bin/env python3

import argparse
import os
import sys
import glob
import shutil
import antlr4
from typing import List

from antlrgenerated.tlcpLexer import tlcpLexer
from antlrgenerated.tlcpParser import tlcpParser
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


def get_metacfg_files(dir_name: str) -> List[str]:
    return glob.glob(os.path.join(dir_name, "*{ext}".format(ext=EXTENSION)))


def process_arguments(args):
    files = []
    for f in args.files:
        if not os.path.exists(f):
            print("File '{}' not found.".format(f), file=sys.stderr)
            sys.exit(2)
        if os.path.isfile(f):
            if not f.endswith(EXTENSION):
                print("File '{}' is not a {ext} file.".format(f, ext=EXTENSION), file=sys.stderr)
                sys.exit(2)
            files += [f]
        if os.path.isdir(f):
            files += get_metacfg_files(f)

    if not files:
        print("Found no {ext} files.".format(ext=EXTENSION), file=sys.stderr)
        sys.exit(0)

    args.files = files


def copy_tla_files(dir_from: str, dir_to: str):
    for tla_file in glob.glob(os.path.join(dir_from, "*.tla")):
        if os.path.isfile(tla_file):
            shutil.copyfile(tla_file, os.path.join(dir_to, os.path.basename(tla_file)))


def create_tla_file(cfg_file: str, extend_module: str):
    assert cfg_file.endswith(".cfg")

    dir_path = os.path.dirname(cfg_file)
    module_name = os.path.basename(cfg_file)[:-len(".cfg")]

    tla_file = os.path.join(dir_path, module_name + ".tla")
    with open(tla_file, "w") as f:
        f.write("---- MODULE {} ----\n".format(module_name))
        f.write("\n")
        f.write("EXTENDS {}, TLC\n".format(extend_module))
        f.write("\n")
        f.write("====\n")


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

    if parser.getNumberOfSyntaxErrors() > 0:
        print("Skipping file '{}' due to syntax errors.".format(file), file=sys.stderr, flush=True)
        return

    configs = TlcpVisitor(basic_name=config_name).visit(tree)

    for config in configs:
        if config.family:
            family_dir = os.path.join(models_dir, config.family)
            os.makedirs(family_dir, exist_ok=True)
        else:
            family_dir = models_dir

        # copy all tla dependencies
        copy_tla_files(dir_from=config_dir, dir_to=family_dir)

        cfg_file = os.path.join(family_dir, config.name + ".cfg")
        with open(cfg_file, mode="w") as f:
            ret = f.write(config.text)
            assert ret == len(config.text)
        create_tla_file(cfg_file, extend_module=config_name)


def main():
    parser = argparse.ArgumentParser(
        description="A preprocessor for TLC configuration files."
                    "Converts {ext} files to TLC .cfg files.".format(ext=EXTENSION))
    parser.add_argument(
        "files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="Path to a {ext} file or a directory with {ext} files.".format(ext=EXTENSION))
    parser.add_argument(
        "--cleanup", "-c",
        default=False,
        action="store_true",
        help="Removes the old {dir} folder before generating new models.".format(dir=GENERATED_MODELS_DIR))

    # TODO: add auto-generated "run_all.sh" scripts in sub-folders.
    # parser.add_argument(
    #     "--no–bat",
    #     default=False,
    #     action="store_true",
    #     help="Don't create .bat script files.")
    # parser.add_argument(
    #     "--no-sh",
    #     default=False,
    #     action="store_true",
    #     help="Don't create .sh script files.")

    args = parser.parse_args()

    process_arguments(args)

    if args.cleanup and os.path.exists(GENERATED_MODELS_DIR):
        shutil.rmtree(GENERATED_MODELS_DIR)

    for file in args.files:
        process_file(file, args)


if __name__ == "__main__":
    main()
