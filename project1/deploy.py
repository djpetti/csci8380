"""
Deployment helper script for GAE.
"""


import os
import subprocess
from argparse import ArgumentParser, Namespace
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
import logging


logger = logging.getLogger("deploy")


_REPO_ROOT = Path(__file__).parent
"""
Path to the root directory of the repository.
"""
_FRONTEND_ROOT = _REPO_ROOT / "frontend"
"""
Root directory of the frontend package.
"""


def _find_tool(tool_name: str) -> Path:
    """
    Finds a particular command-line tool.

    Args:
        tool_name: The name of the tool.

    Returns:
        The path to the tool.

    """
    which_result = subprocess.run(
        ["/usr/bin/which", tool_name], check=True, capture_output=True
    )
    which_output = which_result.stdout.decode("utf8")
    if not which_output:
        raise OSError(f"Could not find '{tool_name}'. Is it installed?")

    tool_path = Path(which_output.rstrip("\n"))
    logger.debug("Using {} executable: {}", tool_name, tool_path)
    return tool_path


@contextmanager
def _working_dir(new_dir: Path) -> Iterator[None]:
    """
    Changes to a new working directory for the duration of the context manager.

    Args:
        new_dir: The new directory to change to.

    """
    current_dir = Path.cwd()
    logger.debug("Entering directory {}", new_dir)
    os.chdir(new_dir.as_posix())

    try:
        yield
    finally:
        # Return the to the original working directory.
        logger.debug("Entering directory {}", current_dir)
        os.chdir(current_dir.as_posix())


def _build_frontend(cli_args: Namespace) -> None:
    """
    Builds frontend code prior to deploying.

    Args:
        cli_args: The parsed CLI arguments.

    """
    logger.info("Building frontend code...")

    with _working_dir(_FRONTEND_ROOT):
        npm_path = _find_tool("npm")

        # Format, lint, build and bundle.
        if not cli_args.build_only:
            subprocess.run([npm_path.as_posix(), "run", "format"], check=True)
            subprocess.run([npm_path.as_posix(), "run", "lint"], check=True)
        subprocess.run([npm_path.as_posix(), "run", "build"], check=True)
        subprocess.run([npm_path.as_posix(), "run", "bundle"], check=True)


def _make_parser() -> ArgumentParser:
    """
    Creates a parser to use for command-line arguments.

    Returns:
        The parser that it created.

    """
    parser = ArgumentParser(description="Build and deploy to GAE.")
    subparsers = parser.add_subparsers(
        title="action", dest="action", required=True
    )

    build_parser = subparsers.add_parser("build", help="Build the frontend.")
    build_parser.add_argument(
        "-b",
        "--build-only",
        action="store_true",
        help="Only builds the frontend, without linting or re-generating the"
        " API client.",
    )
    build_parser.set_defaults(func=_build_frontend)

    return parser


def main() -> None:
    parser = _make_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
