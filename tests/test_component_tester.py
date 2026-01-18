"""
Example tests using ComponentTester

Demonstrates how to use the AgentUI testing framework to test
UI components in isolation.
"""

import pytest
from agentui.testing import ComponentTester, ANSIAsserter
from agentui.primitives import UICode, UITable


# Initialize tester (shared across tests)
tester = ComponentTester(theme="charm-dark")
asserter = ANSIAsserter()


class TestCodeRendering:
    """Test UICode component rendering with syntax highlighting"""

    def test_python_syntax_highlighting(self):
        """Python code should be syntax highlighted with CharmDark theme"""
        result = tester.render_code(
            language="python",
            code='def hello():\n    print("world")',
            title="Python Example"
        )

        # Verify rendering succeeded
        assert result.success
        assert result.has_ansi_codes()

        # Verify CharmDark theme colors
        asserter.assert_has_pink_keywords(result.output)  # def keyword
        asserter.assert_has_teal_strings(result.output)   # "world" string

        # Verify styling
        asserter.assert_has_bold_text(result.output)      # keywords bold
        asserter.assert_has_borders(result.output)        # box drawing

        # Verify content
        asserter.assert_contains_text(result.output, "hello")
        asserter.assert_contains_text(result.output, "Python Example")

    def test_go_syntax_highlighting(self):
        """Go code should be syntax highlighted"""
        result = tester.render_code(
            language="go",
            code='func main() {\n    fmt.Println("hello")\n}',
            title="Go Example"
        )

        assert result.success
        assert result.has_ansi_codes()
        asserter.assert_has_pink_keywords(result.output)  # func keyword
        asserter.assert_contains_text(result.output, "main")

    def test_highlighting_increases_size(self):
        """Syntax highlighting should significantly increase output size"""
        plain_code = "def hello(): pass"

        result = tester.render_code("python", plain_code)

        # Highlighted code should be 2-8x larger due to ANSI codes
        asserter.assert_larger_than_plain(
            result.output,
            plain_code,
            min_ratio=2.0
        )

    def test_multiline_code(self):
        """Should handle multiline code with proper line numbers"""
        code = '''import asyncio

async def fetch_data(url: str) -> dict:
    """Fetch data asynchronously."""
    # Simulate API call
    await asyncio.sleep(0.1)
    return {"status": "success"}

result = await fetch_data("https://api.example.com")
print(f"Result: {result}")'''

        result = tester.render_code("python", code)

        assert result.success
        asserter.assert_has_pink_keywords(result.output)    # async, def, await
        asserter.assert_has_teal_strings(result.output)     # Strings
        asserter.assert_has_gray_comments(result.output)    # Comment
        asserter.assert_contains_text(result.output, "fetch_data")


class TestTableRendering:
    """Test UITable component rendering"""

    def test_table_basic_rendering(self):
        """Table should render with headers and rows"""
        result = tester.render_table(
            columns=["Name", "Age", "City"],
            rows=[
                ["Alice", "30", "NYC"],
                ["Bob", "25", "SF"],
            ],
            title="User Table"
        )

        assert result.success

        # Verify content
        asserter.assert_contains_text(result.output, "Name")
        asserter.assert_contains_text(result.output, "Alice")
        asserter.assert_contains_text(result.output, "User Table")

        # Verify borders (tables use box drawing characters)
        assert any(c in result.output for c in ["┌", "├", "│", "└"])

    def test_empty_table(self):
        """Empty table should render without errors"""
        result = tester.render_table(
            columns=["Column"],
            rows=[],
            title="Empty Table"
        )

        assert result.success
        asserter.assert_contains_text(result.output, "Column")


class TestSnapshotTesting:
    """Test snapshot testing functionality"""

    def test_snapshot_baseline(self):
        """Should create and compare snapshots"""
        from agentui.testing import ANSISnapshotter

        snapshotter = ANSISnapshotter()

        code = "def fibonacci(n):\n    if n <= 1:\n        return n"
        result = tester.render_code("python", code)

        # Save baseline
        snapshotter.save_baseline("test-fibonacci", result.output, overwrite=True)

        # Compare (should match)
        diff = snapshotter.compare("test-fibonacci", result.output)
        assert diff.matched

        # Different output (should not match)
        different_code = "def fibonacci(n):\n    return n"  # Changed
        different_result = tester.render_code("python", different_code)

        diff = snapshotter.compare("test-fibonacci", different_result.output)
        assert not diff.matched
        assert len(diff.changes) > 0


class TestThemeSupport:
    """Test different theme rendering"""

    def test_charm_light_theme(self):
        """Should support CharmLight theme"""
        light_tester = ComponentTester(theme="charm-light")

        result = light_tester.render_code("python", "def hello(): pass")

        assert result.success
        assert result.has_ansi_codes()

    def test_default_theme(self):
        """Should use CharmDark as default theme"""
        default_tester = ComponentTester()  # No theme specified

        result = default_tester.render_code("python", "x = 42")

        assert result.success
        # Should still have CharmDark colors
        asserter.assert_has_pink_keywords(result.output)


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_unknown_language(self):
        """Unknown language should fallback gracefully"""
        result = tester.render_code("unknown-lang", "some code")

        # Should render but without syntax highlighting
        assert result.success
        asserter.assert_contains_text(result.output, "some code")

    def test_empty_code(self):
        """Empty code should render without errors"""
        result = tester.render_code("python", "")

        assert result.success

    def test_special_characters(self):
        """Should handle special characters in code"""
        code = 'print("Hello 你好 🎨")'
        result = tester.render_code("python", code)

        assert result.success
        asserter.assert_contains_text(result.output, "你好")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
