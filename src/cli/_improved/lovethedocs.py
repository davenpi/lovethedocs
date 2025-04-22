#!/usr/bin/env python
"""
Command-line entry-point.
"""

import argparse
from src.application import run_pipeline


def main() -> None:
    """Parse command-line arguments and run the documentation pipeline.

This function sets up the argument parser for the command-line tool, collects the
paths to one or more directories containing Python files to be documented, and
invokes the documentation pipeline on those directories.

Returns
-------
None
    This function does not return a value; it executes the pipeline as a side effect.
"""
    parser = argparse.ArgumentParser(prog="lovethedocs")
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more directories whose Python files should be documented.",
    )
    args = parser.parse_args()
    print("Running pipeline with paths:", args.paths)
    run_pipeline.run_pipeline(args.paths)


if __name__ == "__main__":
    main()
