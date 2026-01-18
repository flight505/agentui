// AgentUI TUI - Beautiful terminal interface for AI agents
package main

import (
	"bufio"
	"encoding/json"
	"flag"
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/flight505/agentui/internal/app"
	"github.com/flight505/agentui/internal/protocol"
	"github.com/flight505/agentui/internal/theme"
	"github.com/flight505/agentui/internal/ui/views"
)

var (
	version = "0.1.0"
)

func main() {
	// Command line flags
	themeName := flag.String("theme", "catppuccin-mocha", "Color theme")
	appName := flag.String("name", "AgentUI", "Application name")
	tagline := flag.String("tagline", "AI Agent Interface", "Application tagline")
	showVersion := flag.Bool("version", false, "Show version")
	listThemes := flag.Bool("list-themes", false, "List available themes")
	headless := flag.Bool("headless", false, "Run in headless mode for testing")
	flag.Parse()

	if *showVersion {
		fmt.Printf("agentui-tui v%s\n", version)
		os.Exit(0)
	}

	if *listThemes {
		fmt.Println("Available themes:")
		for name := range theme.Available {
			marker := "  "
			if name == "catppuccin-mocha" {
				marker = "* "
			}
			fmt.Printf("%s%s\n", marker, name)
		}
		os.Exit(0)
	}

	// Set theme
	if !theme.SetTheme(*themeName) {
		fmt.Fprintf(os.Stderr, "Unknown theme: %s\n", *themeName)
		fmt.Fprintln(os.Stderr, "Use --list-themes to see available options")
		os.Exit(1)
	}

	// Headless mode for testing
	if *headless {
		if err := runHeadless(); err != nil {
			fmt.Fprintf(os.Stderr, "Error in headless mode: %v\n", err)
			os.Exit(1)
		}
		os.Exit(0)
	}

	// Create protocol handler for stdin/stdout
	handler := protocol.NewHandler(os.Stdin, os.Stdout)
	handler.Start()
	defer handler.Stop()

	// Create and run the TUI
	model := app.NewModel(handler, *appName, *tagline)

	p := tea.NewProgram(
		model,
		tea.WithAltScreen(),
		tea.WithMouseCellMotion(),
	)

	if _, err := p.Run(); err != nil {
		fmt.Fprintf(os.Stderr, "Error running TUI: %v\n", err)
		os.Exit(1)
	}
}

// runHeadless runs in non-interactive mode for testing.
// Reads a single JSON message from stdin, renders it, and writes output to stdout.
func runHeadless() error {
	// Read JSON message from stdin
	reader := bufio.NewReader(os.Stdin)
	line, err := reader.ReadBytes('\n')
	if err != nil {
		return fmt.Errorf("failed to read stdin: %w", err)
	}

	// Parse protocol message
	var msg protocol.Message
	if err := json.Unmarshal(line, &msg); err != nil {
		return fmt.Errorf("failed to parse JSON: %w", err)
	}

	// Render based on message type
	var output string

	switch msg.Type {
	case protocol.TypeCode:
		var payload protocol.CodePayload
		if err := msg.ParsePayload(&payload); err != nil {
			return fmt.Errorf("failed to parse code payload: %w", err)
		}

		view := views.NewCodeView()
		view.SetCode(payload.Code)
		view.SetLanguage(payload.Language)
		if payload.Title != "" {
			view.SetTitle(payload.Title)
		}
		view.SetLineNumbers(payload.LineNumbers)
		view.SetWidth(80)

		output = view.View()

	case protocol.TypeTable:
		var payload protocol.TablePayload
		if err := msg.ParsePayload(&payload); err != nil {
			return fmt.Errorf("failed to parse table payload: %w", err)
		}

		view := views.NewTableView()
		if payload.Title != "" {
			view.SetTitle(payload.Title)
		}

		// Convert columns from []any to []string
		columns := make([]string, len(payload.Columns))
		for i, col := range payload.Columns {
			columns[i] = fmt.Sprintf("%v", col)
		}
		view.SetColumns(columns)
		view.SetRows(payload.Rows)
		view.SetWidth(80)

		output = view.View()

	case protocol.TypeMarkdown:
		var payload protocol.MarkdownPayload
		if err := msg.ParsePayload(&payload); err != nil {
			return fmt.Errorf("failed to parse markdown payload: %w", err)
		}

		view := views.NewMarkdownView()
		view.SetContent(payload.Content)
		if payload.Title != "" {
			view.SetTitle(payload.Title)
		}
		view.SetWidth(80)

		output = view.View()

	case protocol.TypeProgress:
		// For progress, just output a simple representation
		var payload protocol.ProgressPayload
		if err := msg.ParsePayload(&payload); err != nil {
			return fmt.Errorf("failed to parse progress payload: %w", err)
		}

		output = fmt.Sprintf("Progress: %s", payload.Message)
		if payload.Percent != nil {
			output += fmt.Sprintf(" (%.0f%%)", *payload.Percent)
		}
		output += "\n"

	default:
		return fmt.Errorf("unsupported message type in headless mode: %s", msg.Type)
	}

	// Write rendered output to stdout
	fmt.Print(output)

	return nil
}
