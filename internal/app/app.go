// Package app contains the main Bubbletea application model.
package app

import (
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	"github.com/charmbracelet/bubbles/textarea"
	"github.com/charmbracelet/bubbles/viewport"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/flight505/agentui/internal/protocol"
	"github.com/flight505/agentui/internal/theme"
	"github.com/flight505/agentui/internal/ui/components"
	"github.com/flight505/agentui/internal/ui/views"
)

// State represents the current UI state.
type State int

const (
	StateChat State = iota
	StateForm
	StateConfirm
	StateSelect
	StateError
)

// Message represents a chat message.
type Message struct {
	Role      string // "user", "assistant", "system"
	Content   string
	Timestamp time.Time
	IsCode    bool
	Language  string
}

// ErrorInfo holds error state.
type ErrorInfo struct {
	Message   string
	Details   string
	Timestamp time.Time
	Retryable bool
}

// Model is the main application model.
type Model struct {
	// Protocol handler
	handler *protocol.Handler

	// UI state
	state    State
	ready    bool
	width    int
	height   int
	quitting bool

	// Components
	viewport viewport.Model
	input    textarea.Model
	spinner  spinner.Model

	// Views
	markdownView *views.MarkdownView
	tableView    *views.TableView
	codeView     *views.CodeView
	progressView *views.ProgressView
	alertView    *views.AlertView

	// Chat state
	messages      []Message
	streamingText string
	isStreaming   bool

	// Form state (using new component)
	currentForm   *components.Form
	currentFormID string

	// Confirm state (using new component)
	currentConfirm   *components.ConfirmDialog
	currentConfirmID string

	// Select state (using new component)
	currentSelect   *components.SelectMenu
	currentSelectID string

	// Progress state
	currentProgress *views.ProgressView

	// Error state
	lastError *ErrorInfo

	// Status
	statusMessage string
	tokenInfo     *protocol.TokenInfo

	// App info
	appName    string
	appTagline string

	// Debug mode
	debugMode bool
}

// NewModel creates a new application model.
func NewModel(handler *protocol.Handler, appName, tagline string) Model {
	// Input area
	ti := textarea.New()
	ti.Placeholder = "Type a message..."
	ti.Focus()
	ti.CharLimit = 4096
	ti.SetWidth(80)
	ti.SetHeight(3)
	ti.ShowLineNumbers = false
	ti.KeyMap.InsertNewline.SetEnabled(false) // Enter sends, not newline

	// Spinner for loading states
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = theme.Current.Styles.Spinner

	return Model{
		handler:      handler,
		state:        StateChat,
		input:        ti,
		spinner:      s,
		messages:     []Message{},
		appName:      appName,
		appTagline:   tagline,
		markdownView: views.NewMarkdownView(),
		tableView:    views.NewTableView(),
		codeView:     views.NewCodeView(),
		progressView: views.NewProgressView(),
		alertView:    views.NewAlertView(),
	}
}

// Init initializes the model.
func (m Model) Init() tea.Cmd {
	return tea.Batch(
		textarea.Blink,
		m.spinner.Tick,
		m.listenForMessages(),
	)
}

// listenForMessages creates a command that listens for protocol messages.
func (m Model) listenForMessages() tea.Cmd {
	return func() tea.Msg {
		select {
		case msg, ok := <-m.handler.Incoming():
			if !ok {
				return connectionClosedMsg{}
			}
			if msg == nil {
				return nil
			}
			return protocolMsg{msg}
		case err := <-m.handler.Errors():
			return protocolErrorMsg{err}
		}
	}
}

// Message types for tea.Cmd
type protocolMsg struct {
	msg *protocol.Message
}

type protocolErrorMsg struct {
	err error
}

type connectionClosedMsg struct{}

type clearErrorMsg struct{}

// Update handles messages and updates the model.
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	var cmds []tea.Cmd

	switch msg := msg.(type) {
	case tea.KeyMsg:
		// Global keys
		if msg.String() == "ctrl+c" {
			m.quitting = true
			m.handler.SendQuit()
			return m, tea.Quit
		}

		// Clear error on any key
		if m.state == StateError && msg.String() != "" {
			m.state = StateChat
			m.lastError = nil
		}

		return m.handleKeyMsg(msg)

	case tea.WindowSizeMsg:
		m.width = msg.Width
		m.height = msg.Height
		m.ready = true

		// Update viewport size
		headerHeight := 3
		footerHeight := 1
		inputHeight := 5
		m.viewport = viewport.New(msg.Width, msg.Height-headerHeight-footerHeight-inputHeight)
		m.viewport.SetContent(m.renderMessages())

		// Update input width
		m.input.SetWidth(msg.Width - 4)

		// Update view widths
		m.markdownView.SetWidth(msg.Width - 4)
		m.tableView.SetWidth(msg.Width - 4)
		m.codeView.SetWidth(msg.Width - 4)
		m.progressView.SetWidth(msg.Width - 4)
		m.alertView.SetWidth(msg.Width - 4)

		// Update form width if present
		if m.currentForm != nil {
			m.currentForm.SetWidth(msg.Width)
		}
		if m.currentConfirm != nil {
			m.currentConfirm.SetWidth(msg.Width)
		}
		if m.currentSelect != nil {
			m.currentSelect.SetWidth(msg.Width)
		}

		// Notify Python of resize
		if err := m.handler.SendResize(msg.Width, msg.Height); err != nil {
			m.setError("Failed to send resize", err.Error(), false)
		}

		return m, nil

	case protocolMsg:
		return m.handleProtocolMsg(msg.msg)

	case protocolErrorMsg:
		m.setError("Protocol error", msg.err.Error(), true)
		return m, m.listenForMessages()

	case connectionClosedMsg:
		m.setError("Connection closed", "The Python process has disconnected", false)
		return m, nil

	case clearErrorMsg:
		if m.state == StateError {
			m.state = StateChat
			m.lastError = nil
		}
		return m, nil

	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		cmds = append(cmds, cmd)
	}

	// Update components based on state
	switch m.state {
	case StateChat:
		var cmd tea.Cmd
		m.input, cmd = m.input.Update(msg)
		cmds = append(cmds, cmd)

	case StateForm:
		if m.currentForm != nil {
			cmd := m.currentForm.Update(msg)
			cmds = append(cmds, cmd)

			// Check if form is done
			if m.currentForm.IsSubmitted() {
				if err := m.handler.SendFormResponse(m.currentFormID, m.currentForm.GetValues()); err != nil {
					m.setError("Failed to send form", err.Error(), false)
				}
				m.state = StateChat
				m.currentForm = nil
			} else if m.currentForm.IsCancelled() {
				if err := m.handler.SendFormResponse(m.currentFormID, nil); err != nil {
					m.setError("Failed to send form", err.Error(), false)
				}
				m.state = StateChat
				m.currentForm = nil
			}
		}

	case StateConfirm:
		if m.currentConfirm != nil {
			cmd := m.currentConfirm.Update(msg)
			cmds = append(cmds, cmd)

			if m.currentConfirm.HasResponded() {
				if err := m.handler.SendConfirmResponse(m.currentConfirmID, m.currentConfirm.IsConfirmed()); err != nil {
					m.setError("Failed to send confirmation", err.Error(), false)
				}
				m.state = StateChat
				m.currentConfirm = nil
			}
		}

	case StateSelect:
		if m.currentSelect != nil {
			cmd := m.currentSelect.Update(msg)
			cmds = append(cmds, cmd)

			if m.currentSelect.HasResponded() {
				if err := m.handler.SendSelectResponse(m.currentSelectID, m.currentSelect.GetSelected()); err != nil {
					m.setError("Failed to send selection", err.Error(), false)
				}
				m.state = StateChat
				m.currentSelect = nil
			}
		}
	}

	return m, tea.Batch(cmds...)
}

func (m *Model) setError(message, details string, retryable bool) {
	m.lastError = &ErrorInfo{
		Message:   message,
		Details:   details,
		Timestamp: time.Now(),
		Retryable: retryable,
	}
	m.state = StateError
}

// handleKeyMsg processes keyboard input.
func (m Model) handleKeyMsg(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch m.state {
	case StateChat:
		return m.handleChatKeys(msg)
	}
	return m, nil
}

// handleChatKeys handles keys in chat mode.
func (m Model) handleChatKeys(msg tea.KeyMsg) (tea.Model, tea.Cmd) {
	switch msg.String() {
	case "esc":
		if m.isStreaming {
			// Cancel streaming (send cancel to Python)
			m.handler.SendSync(&protocol.Message{Type: protocol.TypeCancel})
			m.isStreaming = false
			m.statusMessage = "Cancelled"
		}
		return m, nil

	case "ctrl+l":
		// Clear chat
		m.messages = []Message{}
		m.viewport.SetContent("")
		return m, nil

	case "ctrl+d":
		// Toggle debug mode
		m.debugMode = !m.debugMode
		return m, nil

	case "pgup":
		m.viewport.LineUp(10)
		return m, nil

	case "pgdown":
		m.viewport.LineDown(10)
		return m, nil

	case "enter":
		// Send message if not empty and not streaming
		if m.isStreaming {
			return m, nil
		}

		content := strings.TrimSpace(m.input.Value())
		if content != "" {
			// Add user message to chat
			m.messages = append(m.messages, Message{
				Role:      "user",
				Content:   content,
				Timestamp: time.Now(),
			})
			m.viewport.SetContent(m.renderMessages())
			m.viewport.GotoBottom()

			// Send to Python
			if err := m.handler.SendInput(content); err != nil {
				m.setError("Failed to send message", err.Error(), true)
				return m, nil
			}

			// Clear input
			m.input.Reset()

			// Start streaming state
			m.isStreaming = true
			m.statusMessage = "Thinking..."
		}
		return m, nil
	}

	// Pass to textarea
	var cmd tea.Cmd
	m.input, cmd = m.input.Update(msg)
	return m, cmd
}

// handleProtocolMsg processes messages from Python.
func (m Model) handleProtocolMsg(msg *protocol.Message) (tea.Model, tea.Cmd) {
	if msg == nil {
		return m, m.listenForMessages()
	}

	switch msg.Type {
	case protocol.TypeText:
		var payload protocol.TextPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid text payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.streamingText += payload.Content
		if payload.Done {
			m.messages = append(m.messages, Message{
				Role:      "assistant",
				Content:   m.streamingText,
				Timestamp: time.Now(),
			})
			m.streamingText = ""
			m.isStreaming = false
		}
		m.viewport.SetContent(m.renderMessages())
		m.viewport.GotoBottom()

	case protocol.TypeMarkdown:
		var payload protocol.MarkdownPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid markdown payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.messages = append(m.messages, Message{
			Role:      "assistant",
			Content:   payload.Content,
			Timestamp: time.Now(),
		})
		m.viewport.SetContent(m.renderMessages())
		m.viewport.GotoBottom()

	case protocol.TypeCode:
		var payload protocol.CodePayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid code payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.messages = append(m.messages, Message{
			Role:      "assistant",
			Content:   payload.Code,
			Timestamp: time.Now(),
			IsCode:    true,
			Language:  payload.Language,
		})
		m.viewport.SetContent(m.renderMessages())
		m.viewport.GotoBottom()

	case protocol.TypeTable:
		var payload protocol.TablePayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid table payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		// Convert columns to strings
		cols := make([]string, len(payload.Columns))
		for i, c := range payload.Columns {
			if s, ok := c.(string); ok {
				cols[i] = s
			} else {
				cols[i] = fmt.Sprintf("%v", c)
			}
		}
		m.tableView.SetTitle(payload.Title)
		m.tableView.SetColumns(cols)
		m.tableView.SetRows(payload.Rows)
		m.tableView.SetFooter(payload.Footer)
		// Add rendered table as message
		m.messages = append(m.messages, Message{
			Role:      "system",
			Content:   m.tableView.View(),
			Timestamp: time.Now(),
		})
		m.viewport.SetContent(m.renderMessages())
		m.viewport.GotoBottom()

	case protocol.TypeForm:
		var payload protocol.FormPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid form payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.currentForm = components.NewForm(&payload)
		m.currentForm.SetWidth(m.width)
		m.currentFormID = msg.ID
		m.state = StateForm

	case protocol.TypeConfirm:
		var payload protocol.ConfirmPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid confirm payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.currentConfirm = components.NewConfirmDialog(&payload)
		m.currentConfirm.SetWidth(m.width)
		m.currentConfirmID = msg.ID
		m.state = StateConfirm

	case protocol.TypeSelect:
		var payload protocol.SelectPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid select payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.currentSelect = components.NewSelectMenu(&payload)
		m.currentSelect.SetWidth(m.width)
		m.currentSelectID = msg.ID
		m.state = StateSelect

	case protocol.TypeProgress:
		var payload protocol.ProgressPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid progress payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.progressView.SetMessage(payload.Message)
		if payload.Percent != nil {
			m.progressView.SetPercent(*payload.Percent)
		} else {
			m.progressView.SetPercent(-1)
		}
		if len(payload.Steps) > 0 {
			steps := make([]views.ProgressStep, len(payload.Steps))
			for i, s := range payload.Steps {
				steps[i] = views.ProgressStep{
					Label:  s.Label,
					Status: s.Status,
					Detail: s.Detail,
				}
			}
			m.progressView.SetSteps(steps)
		}
		m.currentProgress = m.progressView
		m.statusMessage = payload.Message

	case protocol.TypeAlert:
		var payload protocol.AlertPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid alert payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.alertView.SetMessage(payload.Message)
		m.alertView.SetTitle(payload.Title)
		m.alertView.SetSeverity(payload.Severity)
		// Add alert as message
		m.messages = append(m.messages, Message{
			Role:      "system",
			Content:   m.alertView.View(),
			Timestamp: time.Now(),
		})
		m.viewport.SetContent(m.renderMessages())
		m.viewport.GotoBottom()

	case protocol.TypeStatus:
		var payload protocol.StatusPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid status payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.statusMessage = payload.Message
		m.tokenInfo = payload.Tokens

	case protocol.TypeSpinner:
		var payload protocol.SpinnerPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid spinner payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		m.statusMessage = payload.Message
		m.isStreaming = true

	case protocol.TypeClear:
		var payload protocol.ClearPayload
		if err := msg.ParsePayload(&payload); err != nil {
			m.setError("Invalid clear payload", err.Error(), false)
			return m, m.listenForMessages()
		}
		if payload.Scope == "chat" || payload.Scope == "all" {
			m.messages = []Message{}
			m.viewport.SetContent("")
		}
		if payload.Scope == "progress" || payload.Scope == "all" {
			m.currentProgress = nil
		}

	case protocol.TypeDone:
		var payload protocol.DonePayload
		msg.ParsePayload(&payload) // Ignore error, summary is optional
		m.isStreaming = false
		m.currentProgress = nil
		if payload.Summary != "" {
			m.statusMessage = payload.Summary
		} else {
			m.statusMessage = "Ready"
		}
	}

	return m, m.listenForMessages()
}

// renderMessages renders all chat messages.
func (m Model) renderMessages() string {
	var sb strings.Builder
	styles := theme.Current.Styles
	colors := theme.Current.Colors

	for _, msg := range m.messages {
		var content string

		switch msg.Role {
		case "user":
			prefix := "👤 "
			style := styles.UserMessage
			if m.width > 0 {
				style = style.Width(m.width - 4)
			}
			content = style.Render(prefix + msg.Content)

		case "assistant":
			prefix := "🤖 "
			if msg.IsCode {
				// Render as code block
				m.codeView.SetCode(msg.Content)
				m.codeView.SetLanguage(msg.Language)
				content = m.codeView.View()
			} else {
				// Render markdown
				m.markdownView.SetContent(msg.Content)
				rendered := m.markdownView.View()
				// Add prefix to first line
				lines := strings.SplitN(rendered, "\n", 2)
				if len(lines) > 1 {
					content = prefix + lines[0] + "\n" + lines[1]
				} else {
					content = prefix + rendered
				}
			}

		case "system":
			// System messages are pre-rendered (tables, alerts, etc.)
			content = msg.Content
		}

		sb.WriteString(content)
		sb.WriteString("\n")
	}

	// Render streaming text
	if m.streamingText != "" {
		style := lipgloss.NewStyle().Foreground(colors.Text)
		if m.width > 0 {
			style = style.Width(m.width - 4)
		}
		sb.WriteString(style.Render("🤖 " + m.streamingText + "▌"))
		sb.WriteString("\n")
	}

	// Render current progress if any
	if m.currentProgress != nil {
		sb.WriteString("\n")
		sb.WriteString(m.currentProgress.View())
	}

	return sb.String()
}

// View renders the UI.
func (m Model) View() string {
	if !m.ready {
		return m.spinner.View() + " Initializing..."
	}

	if m.quitting {
		return "Goodbye! 👋\n"
	}

	styles := theme.Current.Styles
	colors := theme.Current.Colors

	// Header
	headerStyle := styles.Header.Width(m.width)
	headerContent := m.appName
	if m.appTagline != "" {
		headerContent += " · " + m.appTagline
	}
	header := headerStyle.Render(headerContent)

	// Main content depends on state
	var content string
	switch m.state {
	case StateChat:
		content = m.viewport.View()
	case StateForm:
		if m.currentForm != nil {
			content = m.centerVertically(m.currentForm.View())
		}
	case StateConfirm:
		if m.currentConfirm != nil {
			content = m.centerVertically(m.currentConfirm.View())
		}
	case StateSelect:
		if m.currentSelect != nil {
			content = m.centerVertically(m.currentSelect.View())
		}
	case StateError:
		content = m.centerVertically(m.renderError())
	}

	// Input area (only in chat mode)
	var inputArea string
	if m.state == StateChat {
		inputStyle := styles.InputFieldFocus.Width(m.width - 4)
		if m.isStreaming {
			inputStyle = styles.InputField.Width(m.width - 4)
		}
		inputArea = inputStyle.Render(m.input.View())
	}

	// Status bar
	statusStyle := styles.StatusBar.Width(m.width)
	statusContent := m.statusMessage
	if m.isStreaming {
		statusContent = m.spinner.View() + " " + statusContent
	}

	// Token info on right side
	if m.tokenInfo != nil && m.tokenInfo.Input > 0 {
		tokenStr := fmt.Sprintf("↑%d ↓%d", m.tokenInfo.Input, m.tokenInfo.Output)
		padding := m.width - lipgloss.Width(statusContent) - lipgloss.Width(tokenStr) - 4
		if padding > 0 {
			statusContent += strings.Repeat(" ", padding)
			statusContent += lipgloss.NewStyle().Foreground(colors.TextMuted).Render(tokenStr)
		}
	}

	// Debug info
	if m.debugMode {
		debugInfo := fmt.Sprintf(" | State: %d | Msgs: %d", m.state, len(m.messages))
		statusContent += lipgloss.NewStyle().Foreground(colors.Warning).Render(debugInfo)
	}

	statusBar := statusStyle.Render(statusContent)

	// Combine
	return lipgloss.JoinVertical(
		lipgloss.Left,
		header,
		content,
		inputArea,
		statusBar,
	)
}

func (m Model) centerVertically(content string) string {
	contentHeight := lipgloss.Height(content)
	viewportHeight := m.height - 9 // header + input + status

	if contentHeight >= viewportHeight {
		return content
	}

	padding := (viewportHeight - contentHeight) / 2
	return strings.Repeat("\n", padding) + content
}

func (m Model) renderError() string {
	if m.lastError == nil {
		return ""
	}

	colors := theme.Current.Colors
	styles := theme.Current.Styles

	var sb strings.Builder

	// Error icon and title
	titleStyle := lipgloss.NewStyle().
		Foreground(colors.Error).
		Bold(true)
	sb.WriteString(titleStyle.Render("⚠ " + m.lastError.Message))
	sb.WriteString("\n\n")

	// Details
	if m.lastError.Details != "" {
		detailStyle := lipgloss.NewStyle().Foreground(colors.TextMuted)
		sb.WriteString(detailStyle.Render(m.lastError.Details))
		sb.WriteString("\n\n")
	}

	// Hint
	hintStyle := lipgloss.NewStyle().Foreground(colors.TextDim).Italic(true)
	if m.lastError.Retryable {
		sb.WriteString(hintStyle.Render("Press any key to continue, or Ctrl+C to quit"))
	} else {
		sb.WriteString(hintStyle.Render("Press any key to continue"))
	}

	// Container
	containerStyle := styles.AlertError.Width(60)
	return containerStyle.Render(sb.String())
}
