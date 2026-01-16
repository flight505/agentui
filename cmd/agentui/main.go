// AgentUI TUI - Beautiful terminal interface for AI agents
package main

import (
	"flag"
	"fmt"
	"os"

	tea "github.com/charmbracelet/bubbletea"

	"github.com/flight505/agentui/internal/app"
	"github.com/flight505/agentui/internal/protocol"
	"github.com/flight505/agentui/internal/theme"
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
