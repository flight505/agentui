// Package views contains reusable UI view components.
package views

import (
	"strings"

	"github.com/charmbracelet/glamour"
	"github.com/charmbracelet/lipgloss"

	"github.com/flight505/agentui/internal/theme"
)

// MarkdownView renders markdown content.
type MarkdownView struct {
	content  string
	title    string
	width    int
	renderer *glamour.TermRenderer
}

// NewMarkdownView creates a new markdown view.
func NewMarkdownView() *MarkdownView {
	return &MarkdownView{}
}

// SetContent sets the markdown content.
func (m *MarkdownView) SetContent(content string) {
	m.content = content
}

// SetTitle sets an optional title.
func (m *MarkdownView) SetTitle(title string) {
	m.title = title
}

// SetWidth sets the rendering width.
func (m *MarkdownView) SetWidth(width int) {
	m.width = width
	m.renderer = nil // Reset renderer to rebuild with new width
}

func (m *MarkdownView) getRenderer() *glamour.TermRenderer {
	if m.renderer != nil {
		return m.renderer
	}

	width := m.width
	if width <= 0 {
		width = 80
	}

	// Create renderer with theme-appropriate style
	style := glamour.DarkStyleConfig
	colors := theme.Current.Colors

	// Customize some colors
	style.Document.Color = (*string)(nil)
	style.H1.Color = stringPtr(string(colors.Primary))
	style.H2.Color = stringPtr(string(colors.Primary))
	style.H3.Color = stringPtr(string(colors.Secondary))
	style.Link.Color = stringPtr(string(colors.Info))
	style.Code.Color = stringPtr(string(colors.Accent1))
	style.CodeBlock.Chroma.Text.Color = stringPtr(string(colors.Text))

	r, err := glamour.NewTermRenderer(
		glamour.WithStyles(style),
		glamour.WithWordWrap(width-4),
	)
	if err != nil {
		// Fallback to default
		r, _ = glamour.NewTermRenderer(
			glamour.WithAutoStyle(),
			glamour.WithWordWrap(width-4),
		)
	}

	m.renderer = r
	return r
}

// View renders the markdown.
func (m *MarkdownView) View() string {
	var sb strings.Builder
	styles := theme.Current.Styles

	if m.title != "" {
		sb.WriteString(styles.FormTitle.Render(m.title))
		sb.WriteString("\n\n")
	}

	if m.content == "" {
		return sb.String()
	}

	renderer := m.getRenderer()
	rendered, err := renderer.Render(m.content)
	if err != nil {
		// Fallback to plain text
		sb.WriteString(m.content)
	} else {
		sb.WriteString(strings.TrimSpace(rendered))
	}

	return sb.String()
}

func stringPtr(s string) *string {
	return &s
}

// TableView renders a data table.
type TableView struct {
	title      string
	columns    []string
	rows       [][]string
	footer     string
	width      int
	selected   int
	selectable bool
}

// NewTableView creates a new table view.
func NewTableView() *TableView {
	return &TableView{
		selected: -1,
	}
}

// SetTitle sets the table title.
func (t *TableView) SetTitle(title string) {
	t.title = title
}

// SetColumns sets the column headers.
func (t *TableView) SetColumns(columns []string) {
	t.columns = columns
}

// SetRows sets the table data.
func (t *TableView) SetRows(rows [][]string) {
	t.rows = rows
}

// SetFooter sets the table footer.
func (t *TableView) SetFooter(footer string) {
	t.footer = footer
}

// SetWidth sets the table width.
func (t *TableView) SetWidth(width int) {
	t.width = width
}

// SetSelectable enables row selection.
func (t *TableView) SetSelectable(selectable bool) {
	t.selectable = selectable
}

// SetSelected sets the selected row index.
func (t *TableView) SetSelected(index int) {
	t.selected = index
}

// GetSelected returns the selected row index.
func (t *TableView) GetSelected() int {
	return t.selected
}

// View renders the table.
func (t *TableView) View() string {
	if len(t.columns) == 0 {
		return ""
	}

	styles := theme.Current.Styles
	colors := theme.Current.Colors
	var sb strings.Builder

	// Calculate column widths
	colWidths := t.calculateColumnWidths()
	totalWidth := 0
	for _, w := range colWidths {
		totalWidth += w + 3 // padding + border
	}

	// Title
	if t.title != "" {
		titleStyle := lipgloss.NewStyle().
			Foreground(colors.Primary).
			Bold(true).
			Width(totalWidth).
			Align(lipgloss.Center)
		sb.WriteString(titleStyle.Render(t.title))
		sb.WriteString("\n")
	}

	// Top border
	sb.WriteString(t.renderBorder("┌", "┬", "┐", "─", colWidths))
	sb.WriteString("\n")

	// Header
	headerStyle := styles.TableHeader
	sb.WriteString("│")
	for i, col := range t.columns {
		cell := lipgloss.NewStyle().
			Width(colWidths[i]).
			Align(lipgloss.Center).
			Inherit(headerStyle).
			Render(truncate(col, colWidths[i]))
		sb.WriteString(" ")
		sb.WriteString(cell)
		sb.WriteString(" │")
	}
	sb.WriteString("\n")

	// Header/body separator
	sb.WriteString(t.renderBorder("├", "┼", "┤", "─", colWidths))
	sb.WriteString("\n")

	// Rows
	for rowIdx, row := range t.rows {
		isSelected := t.selectable && rowIdx == t.selected
		isAlt := rowIdx%2 == 1

		rowStyle := styles.TableRow
		if isAlt {
			rowStyle = styles.TableRowAlt
		}
		if isSelected {
			rowStyle = styles.TableSelected
		}

		sb.WriteString("│")
		for i, cell := range row {
			if i >= len(colWidths) {
				break
			}
			cellStyle := lipgloss.NewStyle().
				Width(colWidths[i]).
				Inherit(rowStyle)
			sb.WriteString(" ")
			sb.WriteString(cellStyle.Render(truncate(cell, colWidths[i])))
			sb.WriteString(" │")
		}
		// Fill missing columns
		for i := len(row); i < len(colWidths); i++ {
			sb.WriteString(" ")
			sb.WriteString(strings.Repeat(" ", colWidths[i]))
			sb.WriteString(" │")
		}
		sb.WriteString("\n")
	}

	// Bottom border
	sb.WriteString(t.renderBorder("└", "┴", "┘", "─", colWidths))
	sb.WriteString("\n")

	// Footer
	if t.footer != "" {
		footerStyle := lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Width(totalWidth).
			Align(lipgloss.Right).
			Italic(true)
		sb.WriteString(footerStyle.Render(t.footer))
	}

	return sb.String()
}

func (t *TableView) calculateColumnWidths() []int {
	if len(t.columns) == 0 {
		return nil
	}

	widths := make([]int, len(t.columns))

	// Start with header widths
	for i, col := range t.columns {
		widths[i] = len(col)
	}

	// Check row data
	for _, row := range t.rows {
		for i, cell := range row {
			if i < len(widths) && len(cell) > widths[i] {
				widths[i] = len(cell)
			}
		}
	}

	// Apply max width constraints
	maxColWidth := 40
	if t.width > 0 {
		maxColWidth = (t.width - len(t.columns)*3 - 1) / len(t.columns)
		if maxColWidth < 10 {
			maxColWidth = 10
		}
	}

	for i := range widths {
		if widths[i] > maxColWidth {
			widths[i] = maxColWidth
		}
		if widths[i] < 5 {
			widths[i] = 5
		}
	}

	return widths
}

func (t *TableView) renderBorder(left, mid, right, line string, widths []int) string {
	var sb strings.Builder
	sb.WriteString(left)
	for i, w := range widths {
		sb.WriteString(strings.Repeat(line, w+2))
		if i < len(widths)-1 {
			sb.WriteString(mid)
		}
	}
	sb.WriteString(right)
	return sb.String()
}

func truncate(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	if maxLen <= 3 {
		return s[:maxLen]
	}
	return s[:maxLen-3] + "..."
}

// CodeView renders syntax-highlighted code.
type CodeView struct {
	code        string
	language    string
	title       string
	lineNumbers bool
	width       int
}

// NewCodeView creates a new code view.
func NewCodeView() *CodeView {
	return &CodeView{
		lineNumbers: true,
	}
}

// SetCode sets the code content.
func (c *CodeView) SetCode(code string) {
	c.code = code
}

// SetLanguage sets the syntax highlighting language.
func (c *CodeView) SetLanguage(language string) {
	c.language = language
}

// SetTitle sets an optional title.
func (c *CodeView) SetTitle(title string) {
	c.title = title
}

// SetLineNumbers enables/disables line numbers.
func (c *CodeView) SetLineNumbers(enabled bool) {
	c.lineNumbers = enabled
}

// SetWidth sets the rendering width.
func (c *CodeView) SetWidth(width int) {
	c.width = width
}

// View renders the code block.
func (c *CodeView) View() string {
	styles := theme.Current.Styles
	colors := theme.Current.Colors
	var sb strings.Builder

	// Title
	if c.title != "" {
		sb.WriteString(styles.CodeTitle.Render(c.title))
		sb.WriteString("\n")
	}

	// Code content with line numbers
	lines := strings.Split(c.code, "\n")
	maxLineNum := len(lines)
	lineNumWidth := len(strings.Itoa(maxLineNum))

	lineNumStyle := lipgloss.NewStyle().
		Foreground(colors.TextDim).
		Width(lineNumWidth).
		Align(lipgloss.Right)

	codeStyle := lipgloss.NewStyle().
		Foreground(colors.Text)

	var codeContent strings.Builder
	for i, line := range lines {
		if c.lineNumbers {
			codeContent.WriteString(lineNumStyle.Render(strings.Itoa(i + 1)))
			codeContent.WriteString(" │ ")
		}
		codeContent.WriteString(codeStyle.Render(line))
		if i < len(lines)-1 {
			codeContent.WriteString("\n")
		}
	}

	// Wrap in container
	containerStyle := styles.CodeContainer
	if c.width > 0 {
		containerStyle = containerStyle.Width(c.width - 4)
	}

	sb.WriteString(containerStyle.Render(codeContent.String()))

	return sb.String()
}

// ProgressView renders a progress indicator.
type ProgressView struct {
	message string
	percent float64
	steps   []ProgressStep
	width   int
}

// ProgressStep represents a step in multi-step progress.
type ProgressStep struct {
	Label  string
	Status string // "pending", "running", "complete", "error"
	Detail string
}

// NewProgressView creates a new progress view.
func NewProgressView() *ProgressView {
	return &ProgressView{
		percent: -1, // Indeterminate by default
	}
}

// SetMessage sets the progress message.
func (p *ProgressView) SetMessage(message string) {
	p.message = message
}

// SetPercent sets the progress percentage (0-100, or -1 for indeterminate).
func (p *ProgressView) SetPercent(percent float64) {
	p.percent = percent
}

// SetSteps sets the progress steps.
func (p *ProgressView) SetSteps(steps []ProgressStep) {
	p.steps = steps
}

// SetWidth sets the rendering width.
func (p *ProgressView) SetWidth(width int) {
	p.width = width
}

// View renders the progress indicator.
func (p *ProgressView) View() string {
	colors := theme.Current.Colors
	var sb strings.Builder

	// Message
	if p.message != "" {
		msgStyle := lipgloss.NewStyle().
			Foreground(colors.Text).
			Bold(true)
		sb.WriteString(msgStyle.Render(p.message))
		sb.WriteString("\n\n")
	}

	// Progress bar
	if p.percent >= 0 {
		barWidth := 40
		if p.width > 0 && p.width < 50 {
			barWidth = p.width - 10
		}

		filled := int(float64(barWidth) * p.percent / 100)
		if filled > barWidth {
			filled = barWidth
		}

		barStyle := lipgloss.NewStyle().Foreground(colors.Primary)
		emptyStyle := lipgloss.NewStyle().Foreground(colors.TextDim)
		percentStyle := lipgloss.NewStyle().Foreground(colors.TextMuted)

		bar := barStyle.Render(strings.Repeat("█", filled)) +
			emptyStyle.Render(strings.Repeat("░", barWidth-filled))

		sb.WriteString(bar)
		sb.WriteString(" ")
		sb.WriteString(percentStyle.Render(strings.Itoa(int(p.percent)) + "%"))
		sb.WriteString("\n")
	}

	// Steps
	if len(p.steps) > 0 {
		sb.WriteString("\n")
		for _, step := range p.steps {
			var icon string
			var style lipgloss.Style

			switch step.Status {
			case "complete":
				icon = "✓"
				style = lipgloss.NewStyle().Foreground(colors.Success)
			case "running":
				icon = "●"
				style = lipgloss.NewStyle().Foreground(colors.Primary).Bold(true)
			case "error":
				icon = "✗"
				style = lipgloss.NewStyle().Foreground(colors.Error)
			default: // pending
				icon = "○"
				style = lipgloss.NewStyle().Foreground(colors.TextDim)
			}

			sb.WriteString(style.Render(icon + " " + step.Label))
			if step.Detail != "" {
				detailStyle := lipgloss.NewStyle().Foreground(colors.TextMuted).Italic(true)
				sb.WriteString(" ")
				sb.WriteString(detailStyle.Render(step.Detail))
			}
			sb.WriteString("\n")
		}
	}

	return sb.String()
}

// AlertView renders an alert/notification.
type AlertView struct {
	message  string
	title    string
	severity string // "info", "success", "warning", "error"
	width    int
}

// NewAlertView creates a new alert view.
func NewAlertView() *AlertView {
	return &AlertView{
		severity: "info",
	}
}

// SetMessage sets the alert message.
func (a *AlertView) SetMessage(message string) {
	a.message = message
}

// SetTitle sets the alert title.
func (a *AlertView) SetTitle(title string) {
	a.title = title
}

// SetSeverity sets the alert severity.
func (a *AlertView) SetSeverity(severity string) {
	a.severity = severity
}

// SetWidth sets the rendering width.
func (a *AlertView) SetWidth(width int) {
	a.width = width
}

// View renders the alert.
func (a *AlertView) View() string {
	styles := theme.Current.Styles
	colors := theme.Current.Colors

	var style lipgloss.Style
	var icon string

	switch a.severity {
	case "success":
		style = styles.AlertSuccess
		icon = "✓"
	case "warning":
		style = styles.AlertWarning
		icon = "⚠"
	case "error":
		style = styles.AlertError
		icon = "✗"
	default: // info
		style = styles.AlertInfo
		icon = "ℹ"
	}

	if a.width > 0 {
		style = style.Width(a.width - 4)
	}

	var content strings.Builder
	if a.title != "" {
		titleStyle := lipgloss.NewStyle().Bold(true)
		content.WriteString(titleStyle.Render(icon + " " + a.title))
		content.WriteString("\n")
		content.WriteString(a.message)
	} else {
		iconStyle := lipgloss.NewStyle().Foreground(colors.Text)
		content.WriteString(iconStyle.Render(icon + " " + a.message))
	}

	return style.Render(content.String())
}
