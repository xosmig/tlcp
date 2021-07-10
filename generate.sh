#!/usr/bin/env bash
set -eu

DIRNAME="antlrgenerated"
mkdir -p "$DIRNAME"
antlr4 -Dlanguage=Python3 -visitor tlcp.g4 -o "$DIRNAME"
