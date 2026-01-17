package main

import (
	"fmt"
	"strings"

	"github.com/flight505/agentui/internal/theme"
	"github.com/flight505/agentui/internal/ui/views"
)

func main() {
	// Set CharmDark theme
	theme.SetTheme("charm-dark")

	// Sample Python code
	pythonCode := `def hello(name: str) -> str:
    """Greet someone."""
    return f"Hello, {name}!"  # Return greeting

# Usage
message = hello("World")
print(message)`

	// Create code view
	view := views.NewCodeView()
	view.SetTitle("Python Example")
	view.SetLanguage("python")
	view.SetCode(pythonCode)
	view.SetLineNumbers(true)
	view.SetWidth(80)

	// Render it
	output := view.View()

	fmt.Println("========================================================================")
	fmt.Println("🎨 Syntax Highlighting - ANSI Color Codes Demo")
	fmt.Println("========================================================================")
	fmt.Println()
	fmt.Println("Here's the rendered output with syntax highlighting:")
	fmt.Println()
	fmt.Println(output)
	fmt.Println()
	fmt.Println("========================================================================")
	fmt.Println("📊 Raw ANSI Codes")
	fmt.Println("========================================================================")
	fmt.Println()
	fmt.Println("Here's a snippet showing the actual ANSI escape sequences:")
	fmt.Println()

	// Show first 200 characters with visible escape codes
	snippet := output
	if len(snippet) > 400 {
		snippet = snippet[:400]
	}

	// Replace escape codes with visible representation
	visible := strings.ReplaceAll(snippet, "\x1b", "\\x1b")
	fmt.Println(visible)

	fmt.Println()
	fmt.Println("...")
	fmt.Println()
	fmt.Println("Color code meanings:")
	fmt.Println("  \\x1b[38;2;255;135;215m = Pink (keywords)")
	fmt.Println("  \\x1b[38;2;0;175;95m    = Teal (strings)")
	fmt.Println("  \\x1b[38;2;125;86;244m  = Purple (functions)")
	fmt.Println("  \\x1b[1m                 = Bold")
	fmt.Println("  \\x1b[3m                 = Italic")
	fmt.Println("  \\x1b[0m                 = Reset")
	fmt.Println()
}
