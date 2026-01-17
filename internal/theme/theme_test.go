package theme

import (
	"testing"

	"github.com/charmbracelet/lipgloss"
)

func TestThemeRegistration(t *testing.T) {
	// CharmDark, CharmLight, CharmAuto should be registered by init()
	themes := []string{"charm-dark", "charm-light", "charm-auto"}

	for _, name := range themes {
		if _, ok := Available[name]; !ok {
			t.Errorf("Theme %s should be registered but wasn't found", name)
		}
	}
}

func TestSetTheme(t *testing.T) {
	// Test setting a valid theme
	if !SetTheme("charm-dark") {
		t.Error("SetTheme failed for valid theme 'charm-dark'")
	}

	if Current.ID != "charm-dark" {
		t.Errorf("Current theme ID = %s, want 'charm-dark'", Current.ID)
	}

	// Test setting an invalid theme
	if SetTheme("nonexistent-theme") {
		t.Error("SetTheme should return false for nonexistent theme")
	}
}

func TestRegister(t *testing.T) {
	// Create a test theme
	testTheme := &Theme{
		ID:          "test-theme",
		Name:        "Test Theme",
		Description: "A test theme",
		Author:      "Test",
		Version:     "1.0.0",
		Colors: Colors{
			Primary:    lipgloss.Color("#FF0000"),
			Secondary:  lipgloss.Color("#00FF00"),
			Background: lipgloss.Color("#000000"),
			Surface:    lipgloss.Color("#111111"),
			Overlay:    lipgloss.Color("#222222"),
			Text:       lipgloss.Color("#FFFFFF"),
			TextMuted:  lipgloss.Color("#AAAAAA"),
			TextDim:    lipgloss.Color("#555555"),
			Success:    lipgloss.Color("#00FF00"),
			Warning:    lipgloss.Color("#FFFF00"),
			Error:      lipgloss.Color("#FF0000"),
			Info:       lipgloss.Color("#00FFFF"),
			Accent1:    lipgloss.Color("#FF00FF"),
			Accent2:    lipgloss.Color("#00FFFF"),
			Accent3:    lipgloss.Color("#FFFF00"),
		},
	}

	// Register the test theme
	Register(testTheme)

	// Verify it was registered
	if _, ok := Available["test-theme"]; !ok {
		t.Error("Registered theme 'test-theme' not found in Available map")
	}

	// Verify we can set it as current
	if !SetTheme("test-theme") {
		t.Error("Failed to set registered test theme")
	}

	if Current.ID != "test-theme" {
		t.Errorf("Current theme ID = %s, want 'test-theme'", Current.ID)
	}

	// Cleanup
	delete(Available, "test-theme")
	SetTheme("charm-dark")
}

func TestBuildStyles(t *testing.T) {
	// Test that BuildStyles creates all required styles
	colors := CharmDark.Colors
	styles := BuildStyles(colors)

	// Check that key styles are created (non-nil check)
	if styles.Header.GetForeground() == nil {
		t.Error("Header style should have foreground color")
	}

	// Check border styles are not the default normal border
	if styles.UserMessage.GetBorderStyle() == lipgloss.NormalBorder() {
		t.Error("UserMessage should have a border style set")
	}

	if styles.CodeContainer.GetBorderStyle() == lipgloss.NormalBorder() {
		t.Error("CodeContainer should have a border style set")
	}
}

func TestCharmThemeColors(t *testing.T) {
	// Verify Charm signature colors are defined
	tests := []struct {
		name  string
		theme Theme
	}{
		{"CharmDark", CharmDark},
		{"CharmLight", CharmLight},
		{"CharmAuto", CharmAuto},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Verify theme has metadata
			if tt.theme.ID == "" {
				t.Error("Theme should have an ID")
			}
			if tt.theme.Name == "" {
				t.Error("Theme should have a name")
			}

			// Verify all color fields are set
			colors := tt.theme.Colors
			if colors.Primary == nil {
				t.Error("Primary color should be set")
			}
			if colors.Background == nil {
				t.Error("Background color should be set")
			}
			if colors.Text == nil {
				t.Error("Text color should be set")
			}
		})
	}
}

func TestThemeMetadata(t *testing.T) {
	// Test CharmDark metadata
	if CharmDark.ID != "charm-dark" {
		t.Errorf("CharmDark ID = %s, want 'charm-dark'", CharmDark.ID)
	}

	if CharmDark.Name != "Charm Dark" {
		t.Errorf("CharmDark Name = %s, want 'Charm Dark'", CharmDark.Name)
	}

	if CharmDark.Version == "" {
		t.Error("CharmDark should have a version")
	}

	if CharmDark.Author == "" {
		t.Error("CharmDark should have an author")
	}

	// Test CharmLight metadata
	if CharmLight.ID != "charm-light" {
		t.Errorf("CharmLight ID = %s, want 'charm-light'", CharmLight.ID)
	}

	// Test CharmAuto metadata
	if CharmAuto.ID != "charm-auto" {
		t.Errorf("CharmAuto ID = %s, want 'charm-auto'", CharmAuto.ID)
	}
}
