"""
ANSI Snapshot Testing

Snapshot testing for terminal output, similar to Jest snapshots for web.
Captures ANSI-formatted output and compares against baselines.
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SnapshotDiff:
    """Result of comparing output to snapshot"""
    matched: bool
    baseline: str | None = None
    current: str | None = None
    changes: list[str] | None = None

    def render(self) -> str:
        """Render diff in human-readable format"""
        if self.matched:
            return "✅ Snapshot matched"

        lines = ["❌ Snapshot mismatch", ""]

        if self.changes:
            lines.append("Changes detected:")
            for change in self.changes:
                lines.append(f"  {change}")
        else:
            lines.append("Files differ but detailed diff unavailable")

        return "\n".join(lines)


class ANSISnapshotter:
    """
    Snapshot testing for ANSI terminal output

    Saves baseline output and compares future runs against it,
    similar to Jest snapshot testing for web components.

    Examples:
        >>> snapshotter = ANSISnapshotter()
        >>>
        >>> # First run: create baseline
        >>> output = tester.render_code("python", "def hello(): pass")
        >>> snapshotter.save_baseline("python-hello", output.output)
        >>>
        >>> # Later: compare against baseline
        >>> new_output = tester.render_code("python", "def hello(): pass")
        >>> diff = snapshotter.compare("python-hello", new_output.output)
        >>> assert diff.matched
    """

    def __init__(self, snapshot_dir: Path | None = None):
        """
        Initialize snapshotter

        Args:
            snapshot_dir: Directory to store snapshots
                         (default: tests/__snapshots__)
        """
        if snapshot_dir is None:
            snapshot_dir = Path("tests") / "__snapshots__"

        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def save_baseline(self, name: str, output: str, overwrite: bool = False):
        """
        Save ANSI output as baseline snapshot

        Args:
            name: Snapshot name (e.g., "python-fibonacci")
            output: ANSI output to save
            overwrite: If True, overwrite existing baseline

        Raises:
            FileExistsError: If baseline exists and overwrite=False
        """
        ansi_file = self.snapshot_dir / f"{name}.ansi"
        text_file = self.snapshot_dir / f"{name}.txt"

        if ansi_file.exists() and not overwrite:
            raise FileExistsError(
                f"Baseline already exists: {ansi_file}. "
                f"Use overwrite=True to replace."
            )

        # Save raw ANSI output
        ansi_file.write_text(output, encoding='utf-8')

        # Save human-readable version (ANSI codes stripped)
        plain_text = self._strip_ansi(output)
        text_file.write_text(plain_text, encoding='utf-8')

    def compare(self, name: str, current: str) -> SnapshotDiff:
        """
        Compare current output to baseline

        Args:
            name: Snapshot name
            current: Current ANSI output to compare

        Returns:
            SnapshotDiff with comparison result

        Raises:
            FileNotFoundError: If baseline doesn't exist
        """
        baseline_file = self.snapshot_dir / f"{name}.ansi"

        if not baseline_file.exists():
            raise FileNotFoundError(
                f"No baseline snapshot for '{name}'. "
                f"Create one with save_baseline() first."
            )

        baseline = baseline_file.read_text(encoding='utf-8')

        # Exact match?
        if baseline == current:
            return SnapshotDiff(matched=True)

        # Find differences
        changes = self._diff_ansi(baseline, current)

        return SnapshotDiff(
            matched=False,
            baseline=baseline,
            current=current,
            changes=changes
        )

    def update(self, name: str, new_output: str):
        """
        Update baseline snapshot (after intentional changes)

        Args:
            name: Snapshot name
            new_output: New output to use as baseline
        """
        self.save_baseline(name, new_output, overwrite=True)

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape sequences"""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)

    def _diff_ansi(self, baseline: str, current: str) -> list[str]:
        """
        Find differences between two ANSI outputs

        Returns list of human-readable change descriptions
        """
        changes = []

        # Line-by-line comparison
        baseline_lines = baseline.splitlines()
        current_lines = current.splitlines()

        if len(baseline_lines) != len(current_lines):
            changes.append(
                f"Line count changed: {len(baseline_lines)} → {len(current_lines)}"
            )

        # Compare each line
        for i, (base_line, curr_line) in enumerate(zip(baseline_lines, current_lines)):
            if base_line != curr_line:
                # Check if it's just ANSI code differences
                base_plain = self._strip_ansi(base_line)
                curr_plain = self._strip_ansi(curr_line)

                if base_plain == curr_plain:
                    # Text same, colors different
                    changes.append(f"Line {i+1}: Color/style changed")
                else:
                    # Text content changed
                    changes.append(f"Line {i+1}: Text changed")

        return changes

    def list_snapshots(self) -> list[str]:
        """List all available snapshots"""
        ansi_files = self.snapshot_dir.glob("*.ansi")
        return [f.stem for f in ansi_files]

    def delete(self, name: str):
        """Delete a snapshot"""
        ansi_file = self.snapshot_dir / f"{name}.ansi"
        text_file = self.snapshot_dir / f"{name}.txt"

        ansi_file.unlink(missing_ok=True)
        text_file.unlink(missing_ok=True)
