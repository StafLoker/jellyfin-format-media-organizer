from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..processors.result import ProcessResult

_WIDTH = 51
_DIVIDER = "  " + "─" * _WIDTH


def print_dry_run_banner() -> None:
    inner = _WIDTH - 2  # space inside box borders
    title = "DRY RUN MODE"
    sub = "No files will be modified"
    print("┌" + "─" * inner + "┐")
    print("│" + title.center(inner) + "│")
    print("│" + sub.center(inner) + "│")
    print("└" + "─" * inner + "┘")
    print()


def print_header(count: int) -> None:
    noun = "entry" if count == 1 else "entries"
    print(f"Processing {count} {noun}...")
    print()


def print_entry_header(name: str, *, is_dir: bool) -> None:
    kind = "directory" if is_dir else "file"
    print(f"  \u25b6 {name} ({kind})")
    print()


def print_result(r: ProcessResult) -> None:
    tick = "\u2713" if r.success else "\u2717"
    print(f"  {r.media_kind.value:<6} {r.source}")
    print(f"         \u2192 {r.dest}  {tick}")
    print()


def print_summary(results: list[ProcessResult], skipped: int, dry_run: bool) -> None:
    print(_DIVIDER)
    linked = sum(1 for r in results if r.success)
    failed = sum(1 for r in results if not r.success)
    if dry_run:
        print(f"  {linked} would link  |  {skipped} skipped  |  {failed} failed")
    else:
        print(f"  {linked} linked  |  {skipped} skipped  |  {failed} failed")
    print()
