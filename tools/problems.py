"""Problems found in the list files, and how to report them."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

Level = Literal["error", "notice"]


@dataclass(frozen=True)
class Problem:
    path: str
    line: int | None
    message: str
    level: Level = "error"


def emit(problems: Iterable[Problem], *, annotations: bool) -> None:
    """Print problems as GitHub Actions annotations or as plain lines."""
    for problem in problems:
        if annotations:
            location = f"file={problem.path}"
            if problem.line is not None:
                location += f",line={problem.line}"
            print(f"::{problem.level} {location}::{problem.message}")
        elif problem.line is not None:
            print(f"{problem.path}:{problem.line}: {problem.message}")
        else:
            print(f"{problem.path}: {problem.message}")
