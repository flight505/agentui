// Package protocol defines the JSON message types for Python-Go communication.
package protocol

import (
	"encoding/json"
)

// MessageType identifies the type of message.
type MessageType string

// Message types from Python → Go (render commands)
const (
	TypeText     MessageType = "text"
	TypeMarkdown MessageType = "markdown"
	TypeProgress MessageType = "progress"
	TypeForm     MessageType = "form"
	TypeTable    MessageType = "table"
	TypeCode     MessageType = "code"
	TypeConfirm  MessageType = "confirm"
	TypeSelect   MessageType = "select"
	TypeAlert    MessageType = "alert"
	TypeSpinner  MessageType = "spinner"
	TypeStatus   MessageType = "status"
	TypeClear    MessageType = "clear"
	TypeDone     MessageType = "done"
	TypeUpdate   MessageType = "update" // Phase 3: Progressive streaming
)

// Message types from Go → Python (user events)
const (
	TypeInput           MessageType = "input"
	TypeFormResponse    MessageType = "form_response"
	TypeConfirmResponse MessageType = "confirm_response"
	TypeSelectResponse  MessageType = "select_response"
	TypeCancel          MessageType = "cancel"
	TypeQuit            MessageType = "quit"
	TypeResize          MessageType = "resize"
)

// Message is the base message structure for all protocol communication.
type Message struct {
	Type    MessageType     `json:"type"`
	ID      string          `json:"id,omitempty"`
	Payload json.RawMessage `json:"payload,omitempty"`
}

// --- Payload types from Python → Go ---

// TextPayload contains streamed text content.
type TextPayload struct {
	Content string `json:"content"`
	Done    bool   `json:"done,omitempty"`
}

// MarkdownPayload contains markdown content to render.
type MarkdownPayload struct {
	Content string `json:"content"`
	Title   string `json:"title,omitempty"`
}

// ProgressStep represents a step in a multi-step progress.
type ProgressStep struct {
	Label  string `json:"label"`
	Status string `json:"status"` // "pending", "running", "complete", "error"
	Detail string `json:"detail,omitempty"`
}

// ProgressPayload shows progress indicators.
type ProgressPayload struct {
	Message string         `json:"message"`
	Percent *float64       `json:"percent,omitempty"`
	Steps   []ProgressStep `json:"steps,omitempty"`
}

// FormField defines a single form field.
type FormField struct {
	Name        string   `json:"name"`
	Label       string   `json:"label"`
	Type        string   `json:"type"`
	Options     []string `json:"options,omitempty"`
	Default     any      `json:"default,omitempty"`
	Required    bool     `json:"required,omitempty"`
	Description string   `json:"description,omitempty"`
	Placeholder string   `json:"placeholder,omitempty"`
}

// FormPayload requests user input via form.
type FormPayload struct {
	Title       string      `json:"title,omitempty"`
	Description string      `json:"description,omitempty"`
	Fields      []FormField `json:"fields"`
	SubmitLabel string      `json:"submit_label,omitempty"`
	CancelLabel string      `json:"cancel_label,omitempty"`
}

// TablePayload displays a data table.
type TablePayload struct {
	Title   string     `json:"title,omitempty"`
	Columns []any      `json:"columns"`
	Rows    [][]string `json:"rows"`
	Footer  string     `json:"footer,omitempty"`
}

// CodePayload displays syntax-highlighted code.
type CodePayload struct {
	Code        string `json:"code"`
	Language    string `json:"language,omitempty"`
	Title       string `json:"title,omitempty"`
	LineNumbers bool   `json:"line_numbers,omitempty"`
}

// ConfirmPayload requests yes/no confirmation.
type ConfirmPayload struct {
	Message      string `json:"message"`
	Title        string `json:"title,omitempty"`
	ConfirmLabel string `json:"confirm_label,omitempty"`
	CancelLabel  string `json:"cancel_label,omitempty"`
	Destructive  bool   `json:"destructive,omitempty"`
}

// SelectPayload requests selection from options.
type SelectPayload struct {
	Label   string   `json:"label"`
	Options []string `json:"options"`
	Default string   `json:"default,omitempty"`
}

// AlertPayload shows a notification.
type AlertPayload struct {
	Message  string `json:"message"`
	Title    string `json:"title,omitempty"`
	Severity string `json:"severity,omitempty"`
}

// SpinnerPayload shows a loading spinner.
type SpinnerPayload struct {
	Message string `json:"message"`
}

// StatusPayload updates the status bar.
type StatusPayload struct {
	Message string     `json:"message"`
	Tokens  *TokenInfo `json:"tokens,omitempty"`
}

// TokenInfo shows token usage.
type TokenInfo struct {
	Input  int `json:"input"`
	Output int `json:"output"`
}

// ClearPayload clears part of the UI.
type ClearPayload struct {
	Scope string `json:"scope"`
}

// DonePayload indicates agent completion.
type DonePayload struct {
	Summary string `json:"summary,omitempty"`
}

// UpdatePayload updates an existing component by ID (Phase 3: Progressive streaming).
// Contains the component ID and fields to update.
type UpdatePayload struct {
	ID string `json:"id"`
	// Dynamically typed fields - can contain any component updates
	Fields map[string]any `json:"-"`
}

// UnmarshalJSON custom unmarshaller to handle dynamic fields.
func (u *UpdatePayload) UnmarshalJSON(data []byte) error {
	// First unmarshal into temporary map
	var temp map[string]any
	if err := json.Unmarshal(data, &temp); err != nil {
		return err
	}

	// Extract ID
	if id, ok := temp["id"].(string); ok {
		u.ID = id
	}

	// Store remaining fields
	u.Fields = make(map[string]any)
	for k, v := range temp {
		if k != "id" {
			u.Fields[k] = v
		}
	}

	return nil
}

// --- Payload types from Go → Python ---

// InputPayload sends user text input.
type InputPayload struct {
	Content string `json:"content"`
}

// FormResponsePayload returns form values.
type FormResponsePayload struct {
	Values map[string]any `json:"values"`
}

// ConfirmResponsePayload returns confirmation result.
type ConfirmResponsePayload struct {
	Confirmed bool `json:"confirmed"`
}

// SelectResponsePayload returns selection result.
type SelectResponsePayload struct {
	Value string `json:"value"`
}

// ResizePayload notifies of terminal resize.
type ResizePayload struct {
	Width  int `json:"width"`
	Height int `json:"height"`
}

// NewMessage creates a new message with the given type and payload.
func NewMessage(msgType MessageType, payload any) (*Message, error) {
	payloadBytes, err := json.Marshal(payload)
	if err != nil {
		return nil, err
	}
	return &Message{
		Type:    msgType,
		Payload: payloadBytes,
	}, nil
}

// NewMessageWithID creates a new message with ID for request/response correlation.
func NewMessageWithID(msgType MessageType, id string, payload any) (*Message, error) {
	msg, err := NewMessage(msgType, payload)
	if err != nil {
		return nil, err
	}
	msg.ID = id
	return msg, nil
}

// ParsePayload unmarshals the payload into the given type.
func (m *Message) ParsePayload(v any) error {
	return json.Unmarshal(m.Payload, v)
}
