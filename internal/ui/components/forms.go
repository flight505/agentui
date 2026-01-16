// Package components contains reusable UI components.
package components

import (
	"strings"

	"github.com/charmbracelet/bubbles/textinput"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/flight505/agentui/internal/protocol"
	"github.com/flight505/agentui/internal/theme"
)

// FormField represents a single form field.
type FormField struct {
	Name        string
	Label       string
	Type        string // "text", "select", "checkbox", "number", "password", "textarea"
	Options     []string
	Required    bool
	Description string
	Placeholder string
	Default     any

	// Runtime state
	textInput   textinput.Model
	selectIndex int
	checked     bool
	value       any
}

// Form is a complete form component with multiple fields.
type Form struct {
	Title       string
	Description string
	Fields      []FormField
	SubmitLabel string
	CancelLabel string

	focusIndex int
	width      int
	submitted  bool
	cancelled  bool
}

// NewForm creates a new form from a protocol payload.
func NewForm(payload *protocol.FormPayload) *Form {
	fields := make([]FormField, len(payload.Fields))

	for i, f := range payload.Fields {
		field := FormField{
			Name:        f.Name,
			Label:       f.Label,
			Type:        f.Type,
			Options:     f.Options,
			Required:    f.Required,
			Description: f.Description,
			Placeholder: f.Placeholder,
			Default:     f.Default,
		}

		// Initialize text input for text-based fields
		if field.Type == "" || field.Type == "text" || field.Type == "password" || field.Type == "number" {
			ti := textinput.New()
			ti.Placeholder = field.Placeholder
			ti.CharLimit = 256

			if field.Type == "password" {
				ti.EchoMode = textinput.EchoPassword
			}

			// Set default value
			if field.Default != nil {
				if s, ok := field.Default.(string); ok {
					ti.SetValue(s)
				}
			}

			field.textInput = ti
		}

		// Initialize select index
		if field.Type == "select" && field.Default != nil {
			if s, ok := field.Default.(string); ok {
				for j, opt := range field.Options {
					if opt == s {
						field.selectIndex = j
						break
					}
				}
			}
		}

		// Initialize checkbox
		if field.Type == "checkbox" {
			if b, ok := field.Default.(bool); ok {
				field.checked = b
			}
		}

		fields[i] = field
	}

	submitLabel := payload.SubmitLabel
	if submitLabel == "" {
		submitLabel = "Submit"
	}
	cancelLabel := payload.CancelLabel
	if cancelLabel == "" {
		cancelLabel = "Cancel"
	}

	form := &Form{
		Title:       payload.Title,
		Description: payload.Description,
		Fields:      fields,
		SubmitLabel: submitLabel,
		CancelLabel: cancelLabel,
		focusIndex:  0,
	}

	// Focus first text input
	form.updateFocus()

	return form
}

// SetWidth sets the form width.
func (f *Form) SetWidth(width int) {
	f.width = width
	for i := range f.Fields {
		f.Fields[i].textInput.Width = width - 10
	}
}

// Update handles input for the form.
func (f *Form) Update(msg tea.Msg) tea.Cmd {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "tab", "down":
			f.nextField()
			return nil

		case "shift+tab", "up":
			f.prevField()
			return nil

		case "enter":
			// If on submit button
			if f.focusIndex == len(f.Fields) {
				f.submitted = true
				return nil
			}
			// If on cancel button
			if f.focusIndex == len(f.Fields)+1 {
				f.cancelled = true
				return nil
			}
			// If on select field, cycle options
			if f.focusIndex < len(f.Fields) {
				field := &f.Fields[f.focusIndex]
				if field.Type == "select" && len(field.Options) > 0 {
					field.selectIndex = (field.selectIndex + 1) % len(field.Options)
				} else if field.Type == "checkbox" {
					field.checked = !field.checked
				}
			}
			return nil

		case "left", "right":
			// For select fields, cycle options
			if f.focusIndex < len(f.Fields) {
				field := &f.Fields[f.focusIndex]
				if field.Type == "select" && len(field.Options) > 0 {
					if msg.String() == "right" {
						field.selectIndex = (field.selectIndex + 1) % len(field.Options)
					} else {
						field.selectIndex--
						if field.selectIndex < 0 {
							field.selectIndex = len(field.Options) - 1
						}
					}
				}
			}
			// Toggle checkbox
			if f.focusIndex < len(f.Fields) && f.Fields[f.focusIndex].Type == "checkbox" {
				f.Fields[f.focusIndex].checked = !f.Fields[f.focusIndex].checked
			}
			// Toggle between submit/cancel buttons
			if f.focusIndex >= len(f.Fields) {
				if f.focusIndex == len(f.Fields) {
					f.focusIndex = len(f.Fields) + 1
				} else {
					f.focusIndex = len(f.Fields)
				}
			}
			return nil

		case " ":
			// Toggle checkbox with space
			if f.focusIndex < len(f.Fields) && f.Fields[f.focusIndex].Type == "checkbox" {
				f.Fields[f.focusIndex].checked = !f.Fields[f.focusIndex].checked
			}
			return nil

		case "esc":
			f.cancelled = true
			return nil
		}
	}

	// Update focused text input
	if f.focusIndex < len(f.Fields) {
		field := &f.Fields[f.focusIndex]
		if field.Type == "" || field.Type == "text" || field.Type == "password" || field.Type == "number" {
			var cmd tea.Cmd
			field.textInput, cmd = field.textInput.Update(msg)
			cmds = append(cmds, cmd)
		}
	}

	return tea.Batch(cmds...)
}

func (f *Form) nextField() {
	f.focusIndex++
	if f.focusIndex > len(f.Fields)+1 {
		f.focusIndex = 0
	}
	f.updateFocus()
}

func (f *Form) prevField() {
	f.focusIndex--
	if f.focusIndex < 0 {
		f.focusIndex = len(f.Fields) + 1
	}
	f.updateFocus()
}

func (f *Form) updateFocus() {
	for i := range f.Fields {
		if i == f.focusIndex {
			f.Fields[i].textInput.Focus()
		} else {
			f.Fields[i].textInput.Blur()
		}
	}
}

// IsSubmitted returns true if the form was submitted.
func (f *Form) IsSubmitted() bool {
	return f.submitted
}

// IsCancelled returns true if the form was cancelled.
func (f *Form) IsCancelled() bool {
	return f.cancelled
}

// GetValues returns the form values.
func (f *Form) GetValues() map[string]any {
	values := make(map[string]any)

	for _, field := range f.Fields {
		switch field.Type {
		case "select":
			if len(field.Options) > 0 && field.selectIndex < len(field.Options) {
				values[field.Name] = field.Options[field.selectIndex]
			}
		case "checkbox":
			values[field.Name] = field.checked
		default:
			values[field.Name] = field.textInput.Value()
		}
	}

	return values
}

// View renders the form.
func (f *Form) View() string {
	styles := theme.Current.Styles
	colors := theme.Current.Colors
	var sb strings.Builder

	// Title
	if f.Title != "" {
		sb.WriteString(styles.FormTitle.Render(f.Title))
		sb.WriteString("\n\n")
	}

	// Description
	if f.Description != "" {
		descStyle := lipgloss.NewStyle().Foreground(colors.TextMuted)
		sb.WriteString(descStyle.Render(f.Description))
		sb.WriteString("\n\n")
	}

	// Fields
	for i, field := range f.Fields {
		focused := i == f.focusIndex

		// Label
		label := field.Label
		if field.Required {
			label += " *"
		}

		labelStyle := styles.FormLabel
		if focused {
			labelStyle = labelStyle.Foreground(colors.Primary).Bold(true)
		}
		sb.WriteString(labelStyle.Render(label))

		// Description
		if field.Description != "" {
			descStyle := lipgloss.NewStyle().Foreground(colors.TextDim).Italic(true)
			sb.WriteString(" ")
			sb.WriteString(descStyle.Render(field.Description))
		}
		sb.WriteString("\n")

		// Input
		switch field.Type {
		case "select":
			sb.WriteString(f.renderSelect(field, focused))
		case "checkbox":
			sb.WriteString(f.renderCheckbox(field, focused))
		default:
			sb.WriteString(f.renderTextInput(field, focused))
		}
		sb.WriteString("\n\n")
	}

	// Buttons
	submitFocused := f.focusIndex == len(f.Fields)
	cancelFocused := f.focusIndex == len(f.Fields)+1

	submitStyle := styles.FormButton
	if submitFocused {
		submitStyle = styles.FormButtonFocus
	}

	cancelStyle := styles.FormButton
	if cancelFocused {
		cancelStyle = styles.FormButtonFocus
	}

	sb.WriteString(submitStyle.Render(f.SubmitLabel))
	sb.WriteString("  ")
	sb.WriteString(cancelStyle.Render(f.CancelLabel))

	// Wrap in container
	containerStyle := styles.FormContainer
	if f.width > 0 {
		containerStyle = containerStyle.Width(f.width - 4)
	}

	return containerStyle.Render(sb.String())
}

func (f *Form) renderTextInput(field FormField, focused bool) string {
	colors := theme.Current.Colors

	inputStyle := lipgloss.NewStyle().
		Background(colors.Surface).
		Foreground(colors.Text).
		Padding(0, 1)

	if focused {
		inputStyle = inputStyle.
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colors.Primary)
	} else {
		inputStyle = inputStyle.
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colors.TextDim)
	}

	return inputStyle.Render(field.textInput.View())
}

func (f *Form) renderSelect(field FormField, focused bool) string {
	colors := theme.Current.Colors
	var sb strings.Builder

	for i, opt := range field.Options {
		selected := i == field.selectIndex

		var prefix string
		var style lipgloss.Style

		if selected {
			prefix = "● "
			style = lipgloss.NewStyle().Foreground(colors.Primary).Bold(true)
		} else {
			prefix = "○ "
			style = lipgloss.NewStyle().Foreground(colors.TextMuted)
		}

		if focused && selected {
			style = style.Background(colors.Surface)
		}

		sb.WriteString(style.Render(prefix + opt))
		if i < len(field.Options)-1 {
			sb.WriteString("  ")
		}
	}

	return sb.String()
}

func (f *Form) renderCheckbox(field FormField, focused bool) string {
	colors := theme.Current.Colors

	var box string
	var style lipgloss.Style

	if field.checked {
		box = "[✓]"
		style = lipgloss.NewStyle().Foreground(colors.Success)
	} else {
		box = "[ ]"
		style = lipgloss.NewStyle().Foreground(colors.TextMuted)
	}

	if focused {
		style = style.Bold(true)
		if !field.checked {
			style = style.Foreground(colors.Primary)
		}
	}

	return style.Render(box)
}

// ConfirmDialog is a yes/no confirmation dialog.
type ConfirmDialog struct {
	Title        string
	Message      string
	ConfirmLabel string
	CancelLabel  string
	Destructive  bool

	focusConfirm bool
	confirmed    bool
	responded    bool
	width        int
}

// NewConfirmDialog creates a new confirmation dialog.
func NewConfirmDialog(payload *protocol.ConfirmPayload) *ConfirmDialog {
	confirmLabel := payload.ConfirmLabel
	if confirmLabel == "" {
		confirmLabel = "Yes"
	}
	cancelLabel := payload.CancelLabel
	if cancelLabel == "" {
		cancelLabel = "No"
	}

	return &ConfirmDialog{
		Title:        payload.Title,
		Message:      payload.Message,
		ConfirmLabel: confirmLabel,
		CancelLabel:  cancelLabel,
		Destructive:  payload.Destructive,
		focusConfirm: true,
	}
}

// SetWidth sets the dialog width.
func (c *ConfirmDialog) SetWidth(width int) {
	c.width = width
}

// Update handles input for the dialog.
func (c *ConfirmDialog) Update(msg tea.Msg) tea.Cmd {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "left", "right", "tab", "h", "l":
			c.focusConfirm = !c.focusConfirm
		case "y":
			c.confirmed = true
			c.responded = true
		case "n", "esc":
			c.confirmed = false
			c.responded = true
		case "enter":
			c.confirmed = c.focusConfirm
			c.responded = true
		}
	}
	return nil
}

// HasResponded returns true if the user has responded.
func (c *ConfirmDialog) HasResponded() bool {
	return c.responded
}

// IsConfirmed returns true if the user confirmed.
func (c *ConfirmDialog) IsConfirmed() bool {
	return c.confirmed
}

// View renders the dialog.
func (c *ConfirmDialog) View() string {
	styles := theme.Current.Styles
	colors := theme.Current.Colors
	var sb strings.Builder

	// Title
	if c.Title != "" {
		titleStyle := styles.FormTitle
		if c.Destructive {
			titleStyle = titleStyle.Foreground(colors.Warning)
		}
		sb.WriteString(titleStyle.Render(c.Title))
		sb.WriteString("\n\n")
	}

	// Message
	msgStyle := lipgloss.NewStyle().Foreground(colors.Text)
	sb.WriteString(msgStyle.Render(c.Message))
	sb.WriteString("\n\n")

	// Hint
	hintStyle := lipgloss.NewStyle().Foreground(colors.TextDim).Italic(true)
	sb.WriteString(hintStyle.Render("Press Y for yes, N for no, or use arrow keys"))
	sb.WriteString("\n\n")

	// Buttons
	confirmStyle := styles.FormButton
	cancelStyle := styles.FormButton

	if c.focusConfirm {
		confirmStyle = styles.FormButtonFocus
		if c.Destructive {
			confirmStyle = confirmStyle.Background(colors.Warning)
		}
	} else {
		cancelStyle = styles.FormButtonFocus
	}

	sb.WriteString(confirmStyle.Render(c.ConfirmLabel))
	sb.WriteString("  ")
	sb.WriteString(cancelStyle.Render(c.CancelLabel))

	// Container
	containerStyle := styles.FormContainer
	if c.Destructive {
		containerStyle = containerStyle.BorderForeground(colors.Warning)
	}
	if c.width > 0 {
		containerStyle = containerStyle.Width(min(60, c.width-4))
	} else {
		containerStyle = containerStyle.Width(60)
	}

	return containerStyle.Render(sb.String())
}

// SelectMenu is a selection menu component.
type SelectMenu struct {
	Label   string
	Options []string
	Default string

	selectedIndex int
	responded     bool
	cancelled     bool
	width         int
}

// NewSelectMenu creates a new select menu.
func NewSelectMenu(payload *protocol.SelectPayload) *SelectMenu {
	menu := &SelectMenu{
		Label:   payload.Label,
		Options: payload.Options,
		Default: payload.Default,
	}

	// Find default index
	if menu.Default != "" {
		for i, opt := range menu.Options {
			if opt == menu.Default {
				menu.selectedIndex = i
				break
			}
		}
	}

	return menu
}

// SetWidth sets the menu width.
func (s *SelectMenu) SetWidth(width int) {
	s.width = width
}

// Update handles input for the menu.
func (s *SelectMenu) Update(msg tea.Msg) tea.Cmd {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "up", "k":
			if s.selectedIndex > 0 {
				s.selectedIndex--
			}
		case "down", "j":
			if s.selectedIndex < len(s.Options)-1 {
				s.selectedIndex++
			}
		case "enter":
			s.responded = true
		case "esc":
			s.cancelled = true
			s.responded = true
		}
	}
	return nil
}

// HasResponded returns true if the user has responded.
func (s *SelectMenu) HasResponded() bool {
	return s.responded
}

// IsCancelled returns true if the user cancelled.
func (s *SelectMenu) IsCancelled() bool {
	return s.cancelled
}

// GetSelected returns the selected option.
func (s *SelectMenu) GetSelected() string {
	if s.cancelled || len(s.Options) == 0 {
		return ""
	}
	return s.Options[s.selectedIndex]
}

// View renders the menu.
func (s *SelectMenu) View() string {
	styles := theme.Current.Styles
	colors := theme.Current.Colors
	var sb strings.Builder

	// Label
	sb.WriteString(styles.FormTitle.Render(s.Label))
	sb.WriteString("\n\n")

	// Options
	for i, opt := range s.Options {
		selected := i == s.selectedIndex

		var prefix string
		var style lipgloss.Style

		if selected {
			prefix = "▸ "
			style = lipgloss.NewStyle().
				Foreground(colors.Primary).
				Bold(true).
				Background(colors.Surface).
				Padding(0, 1)
		} else {
			prefix = "  "
			style = lipgloss.NewStyle().
				Foreground(colors.Text).
				Padding(0, 1)
		}

		sb.WriteString(style.Render(prefix + opt))
		sb.WriteString("\n")
	}

	// Hint
	sb.WriteString("\n")
	hintStyle := lipgloss.NewStyle().Foreground(colors.TextDim).Italic(true)
	sb.WriteString(hintStyle.Render("↑↓ to move, Enter to select, Esc to cancel"))

	// Container
	containerStyle := styles.FormContainer
	if s.width > 0 {
		containerStyle = containerStyle.Width(min(50, s.width-4))
	} else {
		containerStyle = containerStyle.Width(50)
	}

	return containerStyle.Render(sb.String())
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
