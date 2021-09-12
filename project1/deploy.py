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


@contextmanager
def _servlet(war_path: Path) -> Iterator[None]:
    """
    Starts the backend servlet in a separate process.

    Args:
        war_path: The path to the WAR to deploy.
    """
    logger.debug("Starting the servlet.")
    asadmin_path = _find_tool("asadmin")

    # Start Glassfish.
    subprocess.run([asadmin_path.as_posix(), "start-domain"], check=True)
    try:
        # Deploy the application.
        with _working_dir(_REPO_ROOT):
            subprocess.run(
                [asadmin_path.as_posix(), "deploy", "--force", war_path.as_posix()],
                check=True,
            )

        yield
    finally:
        logger.debug("Stopping the servlet.")
        subprocess.run([asadmin_path.as_posix(), "stop-domain"], check=True)


def _generate_api_client(war_path: Path) -> None:
    """
    Generates a TypeScript client for the gateway API.

    Args:
        war_path: The path to the WAR to deploy.
    """
    with _servlet(war_path), _working_dir(_FRONTEND_ROOT):
        npm_path = _find_tool("npm")

        # Generate the API client.
        subprocess.run([npm_path.as_posix(), "run", "api"], check=True)
        subprocess.run([npm_path.as_posix(), "install"], check=True)


def _build_frontend(cli_args: Namespace) -> None:
    """
    Builds frontend code prior to deploying.

    Args:
        cli_args: The parsed CLI arguments.

    """
    logger.info("Building frontend code...")

    # Generate the API, if specified.
    if cli_args.war_path is not None:
        with _working_dir(_REPO_ROOT):
            _generate_api_client(Path(cli_args.war_path))

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
    subparsers = parser.add_subparsers(title="action", dest="action", required=True)

    build_parser = subparsers.add_parser("build", help="Build the frontend.")
    build_parser.add_argument(
        "-b",
        "--build-only",
        action="store_true",
        help="Only builds the frontend, without linting or formatting.",
    )
    build_parser.add_argument(
        "-w",
        "--war-path",
        help="Specifies a path to a WAR file. If there, it will use it to regenerate the API.",
    )
    build_parser.set_defaults(func=_build_frontend)

    return parser


def main() -> None:
    parser = _make_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
