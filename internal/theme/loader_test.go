package theme

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadThemeFromJSON(t *testing.T) {
	jsonData := []byte(`{
  "id": "test-json-theme",
  "name": "Test JSON Theme",
  "description": "A theme loaded from JSON",
  "author": "Test Author",
  "version": "1.0.0",
  "colors": {
    "primary": "#FF0000",
    "secondary": "#00FF00",
    "background": "#000000",
    "surface": "#111111",
    "overlay": "#222222",
    "text": "#FFFFFF",
    "textMuted": "#AAAAAA",
    "textDim": "#555555",
    "success": "#00FF00",
    "warning": "#FFFF00",
    "error": "#FF0000",
    "info": "#00FFFF",
    "accent1": "#FF00FF",
    "accent2": "#00FFFF",
    "accent3": "#FFFF00"
  }
}`)

	theme, err := LoadThemeFromJSON(jsonData)
	if err != nil {
		t.Fatalf("LoadThemeFromJSON failed: %v", err)
	}

	// Verify metadata
	if theme.ID != "test-json-theme" {
		t.Errorf("Theme ID = %s, want 'test-json-theme'", theme.ID)
	}

	if theme.Name != "Test JSON Theme" {
		t.Errorf("Theme Name = %s, want 'Test JSON Theme'", theme.Name)
	}

	if theme.Description != "A theme loaded from JSON" {
		t.Errorf("Theme Description = %s, want 'A theme loaded from JSON'", theme.Description)
	}

	if theme.Author != "Test Author" {
		t.Errorf("Theme Author = %s, want 'Test Author'", theme.Author)
	}

	if theme.Version != "1.0.0" {
		t.Errorf("Theme Version = %s, want '1.0.0'", theme.Version)
	}

	// Verify colors are parsed
	if theme.Colors.Primary == nil {
		t.Error("Primary color should be set")
	}

	if theme.Colors.Text == nil {
		t.Error("Text color should be set")
	}

	// Verify styles are built
	if theme.Styles.Header.GetForeground() == nil {
		t.Error("Styles should be built automatically")
	}
}

func TestLoadThemeFromFile(t *testing.T) {
	// Create a temporary JSON file
	tmpDir := t.TempDir()
	themeFile := filepath.Join(tmpDir, "test-theme.json")

	jsonData := []byte(`{
  "id": "file-theme",
  "name": "File Theme",
  "colors": {
    "primary": "#7D56F4",
    "secondary": "#d946ef",
    "background": "#1a1a2e",
    "surface": "#252538",
    "overlay": "#2f2f45",
    "text": "#FAFAFA",
    "textMuted": "#a9b1d6",
    "textDim": "#565f89",
    "success": "#04B575",
    "warning": "#ffb86c",
    "error": "#ff6b6b",
    "info": "#7dcfff",
    "accent1": "212",
    "accent2": "#7D56F4",
    "accent3": "35"
  }
}`)

	if err := os.WriteFile(themeFile, jsonData, 0644); err != nil {
		t.Fatalf("Failed to write test theme file: %v", err)
	}

	// Load the theme
	theme, err := LoadThemeFromFile(themeFile)
	if err != nil {
		t.Fatalf("LoadThemeFromFile failed: %v", err)
	}

	// Verify it loaded correctly
	if theme.ID != "file-theme" {
		t.Errorf("Theme ID = %s, want 'file-theme'", theme.ID)
	}

	if theme.Name != "File Theme" {
		t.Errorf("Theme Name = %s, want 'File Theme'", theme.Name)
	}
}

func TestLoadInvalidJSON(t *testing.T) {
	invalidJSON := []byte(`{invalid json}`)

	_, err := LoadThemeFromJSON(invalidJSON)
	if err == nil {
		t.Error("LoadThemeFromJSON should fail with invalid JSON")
	}
}

func TestLoadThemeFromNonexistentFile(t *testing.T) {
	_, err := LoadThemeFromFile("/nonexistent/path/theme.json")
	if err == nil {
		t.Error("LoadThemeFromFile should fail with nonexistent file")
	}
}

func TestParseColor(t *testing.T) {
	tests := []struct {
		name     string
		input    string
		wantType string
	}{
		{"hex color", "#FF0000", "lipgloss.Color"},
		{"ANSI color", "212", "lipgloss.Color"},
		{"named color", "red", "lipgloss.Color"},
		{"empty string", "", "lipgloss.Color"},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			color := parseColor(tt.input)
			if color == nil {
				t.Error("parseColor should never return nil")
			}
		})
	}
}

func TestLoadThemesFromDirectory(t *testing.T) {
	// Create a temporary directory with test themes
	tmpDir := t.TempDir()

	// Create valid theme file
	validTheme := []byte(`{
  "id": "valid-theme",
  "name": "Valid Theme",
  "colors": {
    "primary": "#FF0000",
    "secondary": "#00FF00",
    "background": "#000000",
    "surface": "#111111",
    "overlay": "#222222",
    "text": "#FFFFFF",
    "textMuted": "#AAAAAA",
    "textDim": "#555555",
    "success": "#00FF00",
    "warning": "#FFFF00",
    "error": "#FF0000",
    "info": "#00FFFF",
    "accent1": "#FF00FF",
    "accent2": "#00FFFF",
    "accent3": "#FFFF00"
  }
}`)

	if err := os.WriteFile(filepath.Join(tmpDir, "valid.json"), validTheme, 0644); err != nil {
		t.Fatalf("Failed to write valid theme: %v", err)
	}

	// Create invalid theme file
	invalidTheme := []byte(`{invalid}`)
	if err := os.WriteFile(filepath.Join(tmpDir, "invalid.json"), invalidTheme, 0644); err != nil {
		t.Fatalf("Failed to write invalid theme: %v", err)
	}

	// Create non-JSON file (should be skipped)
	if err := os.WriteFile(filepath.Join(tmpDir, "readme.txt"), []byte("not a theme"), 0644); err != nil {
		t.Fatalf("Failed to write readme: %v", err)
	}

	// Load themes from directory
	count, errs := LoadThemesFromDirectory(tmpDir)

	// Should load 1 valid theme
	if count != 1 {
		t.Errorf("LoadThemesFromDirectory loaded %d themes, want 1", count)
	}

	// Should have 1 error (from invalid.json)
	if len(errs) != 1 {
		t.Errorf("LoadThemesFromDirectory returned %d errors, want 1", len(errs))
	}

	// Verify the valid theme was registered
	if _, ok := Available["valid-theme"]; !ok {
		t.Error("Valid theme should be registered")
	}

	// Cleanup
	delete(Available, "valid-theme")
}
