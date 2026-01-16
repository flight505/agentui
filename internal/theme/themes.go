package theme

import "github.com/charmbracelet/lipgloss"

// Catppuccin Mocha - dark theme
var catppuccinMochaColors = Colors{
	// Core
	Primary:    lipgloss.Color("#cba6f7"), // Mauve
	Secondary:  lipgloss.Color("#f5c2e7"), // Pink
	Background: lipgloss.Color("#1e1e2e"), // Base
	Surface:    lipgloss.Color("#313244"), // Surface0
	Overlay:    lipgloss.Color("#45475a"), // Surface1

	// Text
	Text:      lipgloss.Color("#cdd6f4"), // Text
	TextMuted: lipgloss.Color("#a6adc8"), // Subtext0
	TextDim:   lipgloss.Color("#6c7086"), // Overlay0

	// Semantic
	Success: lipgloss.Color("#a6e3a1"), // Green
	Warning: lipgloss.Color("#f9e2af"), // Yellow
	Error:   lipgloss.Color("#f38ba8"), // Red
	Info:    lipgloss.Color("#89b4fa"), // Blue

	// Accents
	Accent1: lipgloss.Color("#94e2d5"), // Teal
	Accent2: lipgloss.Color("#fab387"), // Peach
	Accent3: lipgloss.Color("#89dceb"), // Sky
}

// CatppuccinMocha is the dark Catppuccin theme.
var CatppuccinMocha = Theme{
	Name:   "Catppuccin Mocha",
	Colors: catppuccinMochaColors,
	Styles: BuildStyles(catppuccinMochaColors),
}

// Catppuccin Latte - light theme
var catppuccinLatteColors = Colors{
	// Core
	Primary:    lipgloss.Color("#8839ef"), // Mauve
	Secondary:  lipgloss.Color("#ea76cb"), // Pink
	Background: lipgloss.Color("#eff1f5"), // Base
	Surface:    lipgloss.Color("#e6e9ef"), // Surface0
	Overlay:    lipgloss.Color("#ccd0da"), // Surface1

	// Text
	Text:      lipgloss.Color("#4c4f69"), // Text
	TextMuted: lipgloss.Color("#6c6f85"), // Subtext0
	TextDim:   lipgloss.Color("#9ca0b0"), // Overlay0

	// Semantic
	Success: lipgloss.Color("#40a02b"), // Green
	Warning: lipgloss.Color("#df8e1d"), // Yellow
	Error:   lipgloss.Color("#d20f39"), // Red
	Info:    lipgloss.Color("#1e66f5"), // Blue

	// Accents
	Accent1: lipgloss.Color("#179299"), // Teal
	Accent2: lipgloss.Color("#fe640b"), // Peach
	Accent3: lipgloss.Color("#04a5e5"), // Sky
}

// CatppuccinLatte is the light Catppuccin theme.
var CatppuccinLatte = Theme{
	Name:   "Catppuccin Latte",
	Colors: catppuccinLatteColors,
	Styles: BuildStyles(catppuccinLatteColors),
}

// Dracula theme
var draculaColors = Colors{
	Primary:    lipgloss.Color("#bd93f9"), // Purple
	Secondary:  lipgloss.Color("#ff79c6"), // Pink
	Background: lipgloss.Color("#282a36"), // Background
	Surface:    lipgloss.Color("#44475a"), // Current Line
	Overlay:    lipgloss.Color("#6272a4"), // Comment

	Text:      lipgloss.Color("#f8f8f2"), // Foreground
	TextMuted: lipgloss.Color("#6272a4"), // Comment
	TextDim:   lipgloss.Color("#44475a"), // Current Line

	Success: lipgloss.Color("#50fa7b"), // Green
	Warning: lipgloss.Color("#f1fa8c"), // Yellow
	Error:   lipgloss.Color("#ff5555"), // Red
	Info:    lipgloss.Color("#8be9fd"), // Cyan

	Accent1: lipgloss.Color("#8be9fd"), // Cyan
	Accent2: lipgloss.Color("#ffb86c"), // Orange
	Accent3: lipgloss.Color("#ff79c6"), // Pink
}

// Dracula is the Dracula theme.
var Dracula = Theme{
	Name:   "Dracula",
	Colors: draculaColors,
	Styles: BuildStyles(draculaColors),
}

// Nord theme
var nordColors = Colors{
	Primary:    lipgloss.Color("#88c0d0"), // Nord8
	Secondary:  lipgloss.Color("#81a1c1"), // Nord9
	Background: lipgloss.Color("#2e3440"), // Nord0
	Surface:    lipgloss.Color("#3b4252"), // Nord1
	Overlay:    lipgloss.Color("#434c5e"), // Nord2

	Text:      lipgloss.Color("#eceff4"), // Nord6
	TextMuted: lipgloss.Color("#d8dee9"), // Nord4
	TextDim:   lipgloss.Color("#4c566a"), // Nord3

	Success: lipgloss.Color("#a3be8c"), // Nord14
	Warning: lipgloss.Color("#ebcb8b"), // Nord13
	Error:   lipgloss.Color("#bf616a"), // Nord11
	Info:    lipgloss.Color("#5e81ac"), // Nord10

	Accent1: lipgloss.Color("#8fbcbb"), // Nord7
	Accent2: lipgloss.Color("#d08770"), // Nord12
	Accent3: lipgloss.Color("#b48ead"), // Nord15
}

// Nord is the Nord theme.
var Nord = Theme{
	Name:   "Nord",
	Colors: nordColors,
	Styles: BuildStyles(nordColors),
}

// Tokyo Night theme
var tokyoNightColors = Colors{
	Primary:    lipgloss.Color("#7aa2f7"), // Blue
	Secondary:  lipgloss.Color("#bb9af7"), // Purple
	Background: lipgloss.Color("#1a1b26"), // Background
	Surface:    lipgloss.Color("#24283b"), // Background highlight
	Overlay:    lipgloss.Color("#414868"), // Terminal black

	Text:      lipgloss.Color("#c0caf5"), // Foreground
	TextMuted: lipgloss.Color("#a9b1d6"), // Foreground dark
	TextDim:   lipgloss.Color("#565f89"), // Comment

	Success: lipgloss.Color("#9ece6a"), // Green
	Warning: lipgloss.Color("#e0af68"), // Yellow
	Error:   lipgloss.Color("#f7768e"), // Red
	Info:    lipgloss.Color("#7dcfff"), // Cyan

	Accent1: lipgloss.Color("#73daca"), // Teal
	Accent2: lipgloss.Color("#ff9e64"), // Orange
	Accent3: lipgloss.Color("#f7768e"), // Magenta
}

// TokyoNight is the Tokyo Night theme.
var TokyoNight = Theme{
	Name:   "Tokyo Night",
	Colors: tokyoNightColors,
	Styles: BuildStyles(tokyoNightColors),
}
