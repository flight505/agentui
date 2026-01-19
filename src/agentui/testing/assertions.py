"""
ANSI Assertions

Assertion helpers for verifying ANSI codes, colors, and styling
in terminal output.
"""

import re


class ANSIAsserter:
    """
    Assertion helpers for ANSI terminal output

    Provides pytest-style assertions for verifying syntax highlighting,
    colors, and styling in rendered output.

    Examples:
        >>> asserter = ANSIAsserter()
        >>>
        >>> result = tester.render_code("python", "def hello(): pass")
        >>>
        >>> # Verify ANSI codes present
        >>> asserter.has_ansi_codes(result.output)
        >>>
        >>> # Verify specific colors
        >>> asserter.has_pink_keywords(result.output)  # CharmDark theme
        >>> asserter.has_teal_strings(result.output)
        >>>
        >>> # Verify styling
        >>> asserter.has_bold_text(result.output)
        >>> asserter.has_italic_text(result.output)
    """

    # ANSI color code mappings (CharmDark theme)
    CHARM_PINK = "212"      # Keywords
    CHARM_TEAL = "35"       # Strings, types
    CHARM_PURPLE = "99"     # Functions
    CHARM_VIOLET = "63"     # Indigo
    CHARM_GRAY = "60"       # Comments

    # ANSI style codes
    BOLD = "\x1b[1m"
    ITALIC = "\x1b[3m"
    RESET = "\x1b[0m"

    def has_ansi_codes(self, output: str) -> bool:
        """Check if output contains any ANSI escape sequences"""
        return '\x1b[' in output

    def assert_has_ansi_codes(self, output: str, message: str | None = None) -> None:
        """Assert that output contains ANSI codes"""
        if not self.has_ansi_codes(output):
            msg = message or "Output does not contain ANSI escape sequences"
            raise AssertionError(msg)

    def has_color_code(self, output: str, ansi_code: str) -> bool:
        """Check if specific ANSI color code is present"""
        # 256-color format: \x1b[38;5;{code}m
        pattern = f"\x1b[38;5;{ansi_code}m"
        return pattern in output

    def assert_has_color_code(
        self,
        output: str,
        ansi_code: str,
        message: str | None = None
    ) -> None:
        """Assert that specific ANSI color code is present"""
        if not self.has_color_code(output, ansi_code):
            msg = message or f"Output does not contain ANSI color code {ansi_code}"
            raise AssertionError(msg)

    # CharmDark theme specific assertions
    def has_pink_keywords(self, output: str) -> bool:
        """Check if output has pink-colored text (keywords in CharmDark)"""
        return self.has_color_code(output, self.CHARM_PINK)

    def assert_has_pink_keywords(self, output: str) -> None:
        """Assert pink keywords present (CharmDark theme)"""
        self.assert_has_color_code(
            output,
            self.CHARM_PINK,
            "Output does not contain pink keywords (ANSI 212)"
        )

    def has_teal_strings(self, output: str) -> bool:
        """Check if output has teal-colored text (strings in CharmDark)"""
        return self.has_color_code(output, self.CHARM_TEAL)

    def assert_has_teal_strings(self, output: str) -> None:
        """Assert teal strings present (CharmDark theme)"""
        self.assert_has_color_code(
            output,
            self.CHARM_TEAL,
            "Output does not contain teal strings (ANSI 35)"
        )

    def has_purple_functions(self, output: str) -> bool:
        """Check if output has purple-colored text (functions in CharmDark)"""
        return self.has_color_code(output, self.CHARM_PURPLE)

    def assert_has_purple_functions(self, output: str) -> None:
        """Assert purple functions present (CharmDark theme)"""
        self.assert_has_color_code(
            output,
            self.CHARM_PURPLE,
            "Output does not contain purple functions (ANSI 99)"
        )

    def has_gray_comments(self, output: str) -> bool:
        """Check if output has gray-colored text (comments in CharmDark)"""
        return self.has_color_code(output, self.CHARM_GRAY)

    def assert_has_gray_comments(self, output: str) -> None:
        """Assert gray comments present (CharmDark theme)"""
        self.assert_has_color_code(
            output,
            self.CHARM_GRAY,
            "Output does not contain gray comments (ANSI 60)"
        )

    # Style assertions
    def has_bold_text(self, output: str) -> bool:
        """Check if output contains bold text"""
        return self.BOLD in output

    def assert_has_bold_text(self, output: str) -> None:
        """Assert that output contains bold styling"""
        if not self.has_bold_text(output):
            raise AssertionError("Output does not contain bold text (\\x1b[1m)")

    def has_italic_text(self, output: str) -> bool:
        """Check if output contains italic text"""
        return self.ITALIC in output

    def assert_has_italic_text(self, output: str) -> None:
        """Assert that output contains italic styling"""
        if not self.has_italic_text(output):
            raise AssertionError("Output does not contain italic text (\\x1b[3m)")

    # Box drawing characters
    def has_borders(self, output: str) -> bool:
        """Check if output contains box-drawing border characters"""
        borders = ["╭", "╮", "╰", "╯", "─", "│"]
        return any(char in output for char in borders)

    def assert_has_borders(self, output: str) -> None:
        """Assert that output contains box-drawing borders"""
        if not self.has_borders(output):
            raise AssertionError(
                "Output does not contain box-drawing border characters"
            )

    # Content assertions
    def contains_text(self, output: str, text: str) -> bool:
        """Check if text is present (ignoring ANSI codes)"""
        # Strip ANSI codes for comparison
        plain = self._strip_ansi(output)
        return text in plain

    def assert_contains_text(self, output: str, text: str) -> None:
        """Assert that specific text is present"""
        if not self.contains_text(output, text):
            raise AssertionError(f"Output does not contain text: '{text}'")

    def _strip_ansi(self, text: str) -> str:
        """Remove ANSI escape sequences"""
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', text)

    # Size assertions
    def assert_min_size(self, output: str, min_bytes: int) -> None:
        """Assert output is at least min_bytes (indicates highlighting)"""
        actual_size = len(output)
        if actual_size < min_bytes:
            raise AssertionError(
                f"Output too small: {actual_size} bytes < {min_bytes} bytes. "
                f"May indicate missing syntax highlighting."
            )

    def assert_larger_than_plain(
        self,
        highlighted: str,
        plain: str,
        min_ratio: float = 2.0
    ) -> None:
        """
        Assert highlighted code is significantly larger than plain text

        ANSI codes make highlighted code 2-8x larger than plain text.
        This helps verify syntax highlighting was applied.

        Args:
            highlighted: Output with ANSI codes
            plain: Plain text without highlighting
            min_ratio: Minimum size ratio (default: 2.0)
        """
        highlighted_size = len(highlighted)
        plain_size = len(plain)

        if plain_size == 0:
            raise ValueError("Plain text is empty")

        ratio = highlighted_size / plain_size

        if ratio < min_ratio:
            raise AssertionError(
                f"Highlighted output not significantly larger than plain text.\n"
                f"Highlighted: {highlighted_size} bytes\n"
                f"Plain: {plain_size} bytes\n"
                f"Ratio: {ratio:.2f}x (expected >= {min_ratio}x)\n"
                f"This may indicate syntax highlighting was not applied."
            )
