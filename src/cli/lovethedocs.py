#!/usr/bin/env python
"""
Command-line entry-point.
"""

import argparse
from src.application import run_pipeline


def main() -> None:
    """
    Parse command-line arguments and run the documentation pipeline.

    This function sets up the argument parser, collects the paths to be documented,
    and invokes the pipeline to process the specified directories or files. Additional
    options control diff review.

    Returns
    -------
    None
        This function does not return a value.
    """
    parser = argparse.ArgumentParser(prog="lovethedocs")
    parser.add_argument(
        "paths",
        nargs="+",
        help="One or more directories or files whose code should be documented.",
    )
    parser.add_argument(
        "--review",
        action="store_true",
        help="Open diffs for review after processing",
    )
    args = parser.parse_args()

    print("Running pipeline with paths:", args.paths)
    run_pipeline.run_pipeline(
        args.paths,
        review_diffs=args.review,
    )


if __name__ == "__main__":
    main()
