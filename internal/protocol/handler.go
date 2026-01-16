package protocol

import (
	"bufio"
	"encoding/json"
	"io"
	"sync"
)

// Handler manages JSON protocol communication over streams.
type Handler struct {
	reader  *bufio.Reader
	writer  io.Writer
	writeMu sync.Mutex

	// Channels for async message handling
	incoming chan *Message
	outgoing chan *Message
	errors   chan error
	done     chan struct{}
}

// NewHandler creates a new protocol handler.
func NewHandler(r io.Reader, w io.Writer) *Handler {
	return &Handler{
		reader:   bufio.NewReader(r),
		writer:   w,
		incoming: make(chan *Message, 100),
		outgoing: make(chan *Message, 100),
		errors:   make(chan error, 10),
		done:     make(chan struct{}),
	}
}

// Start begins async read/write loops.
func (h *Handler) Start() {
	go h.readLoop()
	go h.writeLoop()
}

// Stop terminates the handler.
func (h *Handler) Stop() {
	close(h.done)
}

// Incoming returns the channel of incoming messages from Python.
func (h *Handler) Incoming() <-chan *Message {
	return h.incoming
}

// Errors returns the channel of errors.
func (h *Handler) Errors() <-chan error {
	return h.errors
}

// Send queues a message to be sent to Python.
func (h *Handler) Send(msg *Message) {
	select {
	case h.outgoing <- msg:
	case <-h.done:
	}
}

// SendSync sends a message synchronously.
func (h *Handler) SendSync(msg *Message) error {
	h.writeMu.Lock()
	defer h.writeMu.Unlock()

	data, err := json.Marshal(msg)
	if err != nil {
		return err
	}

	data = append(data, '\n')
	_, err = h.writer.Write(data)
	return err
}

// readLoop continuously reads messages from stdin.
func (h *Handler) readLoop() {
	defer close(h.incoming)

	for {
		select {
		case <-h.done:
			return
		default:
		}

		line, err := h.reader.ReadBytes('\n')
		if err != nil {
			if err != io.EOF {
				select {
				case h.errors <- err:
				case <-h.done:
				}
			}
			return
		}

		if len(line) == 0 || (len(line) == 1 && line[0] == '\n') {
			continue
		}

		var msg Message
		if err := json.Unmarshal(line, &msg); err != nil {
			select {
			case h.errors <- err:
			case <-h.done:
			}
			continue
		}

		select {
		case h.incoming <- &msg:
		case <-h.done:
			return
		}
	}
}

// writeLoop continuously writes messages to stdout.
func (h *Handler) writeLoop() {
	for {
		select {
		case <-h.done:
			return
		case msg := <-h.outgoing:
			if err := h.SendSync(msg); err != nil {
				select {
				case h.errors <- err:
				case <-h.done:
				}
			}
		}
	}
}

// Convenience methods for sending common messages

// SendInput sends a user input message.
func (h *Handler) SendInput(content string) error {
	msg, err := NewMessage(TypeInput, InputPayload{Content: content})
	if err != nil {
		return err
	}
	return h.SendSync(msg)
}

// SendFormResponse sends form response.
func (h *Handler) SendFormResponse(id string, values map[string]any) error {
	msg, err := NewMessageWithID(TypeFormResponse, id, FormResponsePayload{Values: values})
	if err != nil {
		return err
	}
	return h.SendSync(msg)
}

// SendConfirmResponse sends confirmation response.
func (h *Handler) SendConfirmResponse(id string, confirmed bool) error {
	msg, err := NewMessageWithID(TypeConfirmResponse, id, ConfirmResponsePayload{Confirmed: confirmed})
	if err != nil {
		return err
	}
	return h.SendSync(msg)
}

// SendSelectResponse sends selection response.
func (h *Handler) SendSelectResponse(id string, value string) error {
	msg, err := NewMessageWithID(TypeSelectResponse, id, SelectResponsePayload{Value: value})
	if err != nil {
		return err
	}
	return h.SendSync(msg)
}

// SendQuit sends quit message.
func (h *Handler) SendQuit() error {
	msg, _ := NewMessage(TypeQuit, nil)
	return h.SendSync(msg)
}

// SendResize sends terminal resize notification.
func (h *Handler) SendResize(width, height int) error {
	msg, err := NewMessage(TypeResize, ResizePayload{Width: width, Height: height})
	if err != nil {
		return err
	}
	return h.SendSync(msg)
}
