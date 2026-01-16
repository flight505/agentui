# AgentUI Complete Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete the AgentUI framework implementation according to DESIGN.md specification with distinctive, beautiful aesthetics

**Architecture:** Hybrid Go/Python split-process architecture with JSON Lines protocol over stdio. Go handles TUI rendering using Charm libraries (Bubbletea, Lip Gloss, Glamour, Harmonica), Python handles LLM integration and agent logic.

**Tech Stack:**
- Python 3.11+ (asyncio, anthropic, openai, rich, pyyaml)
- Go 1.22+ (Bubbletea, Lip Gloss, Glamour, Bubbles, Harmonica, Chroma)
- Protocol: JSON Lines over stdin/stdout

**Current State:** Foundation is in place with core Python/Go structure, basic protocol, some UI components, Claude/OpenAI providers. Missing: complete UI primitives, skills system, full agent loop, additional providers, complete testing, **distinctive aesthetic implementation**.

**Aesthetic Philosophy:** See `docs/AESTHETIC_REQUIREMENTS.md` for comprehensive visual design guidelines. TL;DR: Intentional restraint (3-4 colors), typography hierarchy > color, 100-500ms animations, distinctive themes beyond Catppuccin/Dracula.

---

## Phase 0: Aesthetic Foundation (CRITICAL - DO FIRST)

### Task 0.1: Add Distinctive Color Palettes

**Files:**
- Modify: `internal/theme/themes.go`
- Create: `internal/theme/sage.go`
- Create: `internal/theme/obsidian.go`
- Create: `internal/theme/zephyr.go`
- Create: `internal/theme/ember.go`

**Step 1: Add Harmonica and Chroma dependencies**

Run: `cd cmd/agentui && go get github.com/charmbracelet/harmonica github.com/alecthomas/chroma/v2`

**Step 2: Implement Sage theme (minimalist warm)**

Create `internal/theme/sage.go`:

```go
package theme

import "github.com/charmbracelet/lipgloss"

// SageTheme - Minimalist warm gray + forest green (Japanese MA aesthetic)
func SageTheme() Theme {
	return Theme{
		Name: "Sage",
		Colors: ColorPalette{
			// Base - warm grays
			Background: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#e8e6e3",
					ANSI256:   "254",
					ANSI:      "15",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#2a2827",
					ANSI256:   "235",
					ANSI:      "0",
				},
			},
			Surface: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#f5f4f1",
					ANSI256:   "255",
					ANSI:      "15",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#3a3735",
					ANSI256:   "237",
					ANSI:      "8",
				},
			},
			Text: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#2a2827",
					ANSI256:   "235",
					ANSI:      "0",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#e8e6e3",
					ANSI256:   "254",
					ANSI:      "15",
				},
			},
			TextMuted: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#6b6560",
					ANSI256:   "240",
					ANSI:      "8",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#9d9590",
					ANSI256:   "246",
					ANSI:      "7",
				},
			},

			// Interaction - forest green
			Primary: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#5a7a58",
					ANSI256:   "65",
					ANSI:      "2",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#799a77",
					ANSI256:   "108",
					ANSI:      "10",
				},
			},
			Accent1: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#8a6b5f",
					ANSI256:   "95",
					ANSI:      "3",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#a0826d",
					ANSI256:   "137",
					ANSI:      "11",
				},
			},
			Accent2: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#9a6c51",
					ANSI256:   "131",
					ANSI:      "1",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#c97857",
					ANSI256:   "173",
					ANSI:      "9",
				},
			},

			// Semantic
			Success: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#5a7a58",
					ANSI256:   "65",
					ANSI:      "2",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#799a77",
					ANSI256:   "108",
					ANSI:      "10",
				},
			},
			Warning: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#9a6c51",
					ANSI256:   "131",
					ANSI:      "3",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#c97857",
					ANSI256:   "173",
					ANSI:      "11",
				},
			},
			Error: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#a64d4d",
					ANSI256:   "131",
					ANSI:      "1",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#d47070",
					ANSI256:   "167",
					ANSI:      "9",
				},
			},
			Info: lipgloss.CompleteAdaptiveColor{
				Light: lipgloss.CompleteColor{
					TrueColor: "#4a7390",
					ANSI256:   "67",
					ANSI:      "4",
				},
				Dark: lipgloss.CompleteColor{
					TrueColor: "#6b9db8",
					ANSI256:   "74",
					ANSI:      "12",
				},
			},
		},
	}
}
```

**Step 3: Implement Obsidian theme (modern technical)**

Create `internal/theme/obsidian.go`:

```go
package theme

import "github.com/charmbracelet/lipgloss"

// ObsidianTheme - High-contrast technical (cyberpunk-lite)
func ObsidianTheme() Theme {
	return Theme{
		Name: "Obsidian",
		Colors: ColorPalette{
			// Base - deep charcoal
			Background: lipgloss.CompleteColor{
				TrueColor: "#0a0a0a",
				ANSI256:   "232",
				ANSI:      "0",
			},
			Surface: lipgloss.CompleteColor{
				TrueColor: "#1a1a1a",
				ANSI256:   "234",
				ANSI:      "8",
			},
			Text: lipgloss.CompleteColor{
				TrueColor: "#e5e5e5",
				ANSI256:   "254",
				ANSI:      "15",
			},
			TextMuted: lipgloss.CompleteColor{
				TrueColor: "#888888",
				ANSI256:   "244",
				ANSI:      "7",
			},

			// Interaction - vibrant cyan
			Primary: lipgloss.CompleteColor{
				TrueColor: "#00d9ff",
				ANSI256:   "45",
				ANSI:      "14",
			},
			Accent1: lipgloss.CompleteColor{
				TrueColor: "#39ff14",
				ANSI256:   "46",
				ANSI:      "10",
			},
			Accent2: lipgloss.CompleteColor{
				TrueColor: "#ff006e",
				ANSI256:   "198",
				ANSI:      "13",
			},

			// Semantic
			Success: lipgloss.CompleteColor{
				TrueColor: "#39ff14",
				ANSI256:   "46",
				ANSI:      "10",
			},
			Warning: lipgloss.CompleteColor{
				TrueColor: "#ffdd00",
				ANSI256:   "220",
				ANSI:      "11",
			},
			Error: lipgloss.CompleteColor{
				TrueColor: "#ff0055",
				ANSI256:   "197",
				ANSI:      "9",
			},
			Info: lipgloss.CompleteColor{
				TrueColor: "#00d9ff",
				ANSI256:   "45",
				ANSI:      "12",
			},
		},
	}
}
```

**Step 4: Implement Zephyr theme (light calm)**

Create `internal/theme/zephyr.go`:

```go
package theme

import "github.com/charmbracelet/lipgloss"

// ZephyrTheme - Productivity-focused light theme
func ZephyrTheme() Theme {
	return Theme{
		Name: "Zephyr",
		Colors: ColorPalette{
			// Base - cream
			Background: lipgloss.CompleteColor{
				TrueColor: "#faf9f6",
				ANSI256:   "255",
				ANSI:      "15",
			},
			Surface: lipgloss.CompleteColor{
				TrueColor: "#fffef9",
				ANSI256:   "231",
				ANSI:      "7",
			},
			Text: lipgloss.CompleteColor{
				TrueColor: "#2d2d2d",
				ANSI256:   "235",
				ANSI:      "0",
			},
			TextMuted: lipgloss.CompleteColor{
				TrueColor: "#6b6b6b",
				ANSI256:   "241",
				ANSI:      "8",
			},

			// Interaction - cool blue
			Primary: lipgloss.CompleteColor{
				TrueColor: "#4a90e2",
				ANSI256:   "68",
				ANSI:      "4",
			},
			Accent1: lipgloss.CompleteColor{
				TrueColor: "#88c9d1",
				ANSI256:   "116",
				ANSI:      "6",
			},
			Accent2: lipgloss.CompleteColor{
				TrueColor: "#5ab5a0",
				ANSI256:   "72",
				ANSI:      "2",
			},

			// Semantic
			Success: lipgloss.CompleteColor{
				TrueColor: "#2fa84f",
				ANSI256:   "34",
				ANSI:      "2",
			},
			Warning: lipgloss.CompleteColor{
				TrueColor: "#e89f3c",
				ANSI256:   "178",
				ANSI:      "3",
			},
			Error: lipgloss.CompleteColor{
				TrueColor: "#e74c3c",
				ANSI256:   "203",
				ANSI:      "1",
			},
			Info: lipgloss.CompleteColor{
				TrueColor: "#4a90e2",
				ANSI256:   "68",
				ANSI:      "4",
			},
		},
	}
}
```

**Step 5: Implement Ember theme (premium warmth)**

Create `internal/theme/ember.go`:

```go
package theme

import "github.com/charmbracelet/lipgloss"

// EmberTheme - Inviting, premium feel
func EmberTheme() Theme {
	return Theme{
		Name: "Ember",
		Colors: ColorPalette{
			// Base - deep navy
			Background: lipgloss.CompleteColor{
				TrueColor: "#0f172a",
				ANSI256:   "233",
				ANSI:      "0",
			},
			Surface: lipgloss.CompleteColor{
				TrueColor: "#1e293b",
				ANSI256:   "235",
				ANSI:      "8",
			},
			Text: lipgloss.CompleteColor{
				TrueColor: "#e2e8f0",
				ANSI256:   "254",
				ANSI:      "15",
			},
			TextMuted: lipgloss.CompleteColor{
				TrueColor: "#94a3b8",
				ANSI256:   "246",
				ANSI:      "7",
			},

			// Interaction - warm amber
			Primary: lipgloss.CompleteColor{
				TrueColor: "#f59e0b",
				ANSI256:   "214",
				ANSI:      "11",
			},
			Accent1: lipgloss.CompleteColor{
				TrueColor: "#ff6b6b",
				ANSI256:   "203",
				ANSI:      "9",
			},
			Accent2: lipgloss.CompleteColor{
				TrueColor: "#fbbf24",
				ANSI256:   "220",
				ANSI:      "3",
			},

			// Semantic
			Success: lipgloss.CompleteColor{
				TrueColor: "#34d399",
				ANSI256:   "77",
				ANSI:      "10",
			},
			Warning: lipgloss.CompleteColor{
				TrueColor: "#fbbf24",
				ANSI256:   "220",
				ANSI:      "11",
			},
			Error: lipgloss.CompleteColor{
				TrueColor: "#ff6b6b",
				ANSI256:   "203",
				ANSI:      "9",
			},
			Info: lipgloss.CompleteColor{
				TrueColor: "#60a5fa",
				ANSI256:   "75",
				ANSI:      "12",
			},
		},
	}
}
```

**Step 6: Register new themes**

In `internal/theme/themes.go`, add:

```go
func init() {
	Available["sage"] = SageTheme()
	Available["obsidian"] = ObsidianTheme()
	Available["zephyr"] = ZephyrTheme()
	Available["ember"] = EmberTheme()
}
```

**Step 7: Build and test all themes**

Run: `make build-tui`
Run: `./bin/agentui-tui --list-themes`
Expected: Shows all 9 themes (5 existing + 4 new)

Run: `./bin/agentui-tui --theme sage`
Run: `./bin/agentui-tui --theme obsidian`
Run: `./bin/agentui-tui --theme zephyr`
Run: `./bin/agentui-tui --theme ember`

**Step 8: Commit**

```bash
git add internal/theme/sage.go internal/theme/obsidian.go internal/theme/zephyr.go internal/theme/ember.go internal/theme/themes.go cmd/agentui/go.mod cmd/agentui/go.sum
git commit -m "feat: add 4 distinctive color palettes (Sage, Obsidian, Zephyr, Ember)"
```

---

### Task 0.2: Enhance Typography Hierarchy

**Files:**
- Modify: `internal/theme/theme.go`
- Create: `internal/theme/typography.go`

**Step 1: Define typography hierarchy levels**

Create `internal/theme/typography.go`:

```go
package theme

import "github.com/charmbracelet/lipgloss"

// TypographyLevel defines text hierarchy
type TypographyLevel int

const (
	LevelCritical TypographyLevel = iota  // Bold + Primary color
	LevelImportant                         // Normal + Text color
	LevelSupporting                        // Faint + TextMuted
	LevelDisabled                          // Strikethrough + TextDim
)

// GetTypographyStyle returns styled text for hierarchy level
func GetTypographyStyle(level TypographyLevel, content string) string {
	colors := Current.Colors

	var style lipgloss.Style

	switch level {
	case LevelCritical:
		style = lipgloss.NewStyle().
			Bold(true).
			Foreground(colors.Primary).
			MarginBottom(1)
	case LevelImportant:
		style = lipgloss.NewStyle().
			Foreground(colors.Text).
			MarginBottom(1)
	case LevelSupporting:
		style = lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Faint(true)
	case LevelDisabled:
		style = lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Strikethrough(true).
			Faint(true)
	default:
		style = lipgloss.NewStyle().Foreground(colors.Text)
	}

	return style.Render(content)
}
```

**Step 2: Update message rendering to use hierarchy**

In `internal/app/app.go`, update message rendering:

```go
// User messages - Level Important
userStyle := theme.GetTypographyStyle(theme.LevelImportant, msg.Content)

// Assistant messages - Level Important
assistantStyle := theme.GetTypographyStyle(theme.LevelImportant, msg.Content)

// System messages - Level Supporting
systemStyle := theme.GetTypographyStyle(theme.LevelSupporting, msg.Content)

// Timestamps - Level Supporting
timestampStyle := theme.GetTypographyStyle(theme.LevelSupporting, timestamp)
```

**Step 3: Test hierarchy rendering**

Run: `make build-tui && uv run python examples/simple_agent.py`
Expected: Clear visual hierarchy between message types

**Step 4: Commit**

```bash
git add internal/theme/typography.go internal/app/app.go
git commit -m "feat: add typography hierarchy system (4 levels)"
```

---

### Task 0.3: Add Staggered Animation and Harmonica Physics

**Files:**
- Create: `internal/animation/stagger.go`
- Create: `internal/animation/spring.go`
- Modify: `internal/app/app.go`
- Modify: `internal/ui/views/views.go`

**Step 1: Create staggered reveal animation helper**

Create `internal/animation/stagger.go`:

```go
package animation

import (
	"time"

	tea "github.com/charmbracelet/bubbletea"
)

// StaggerMsg represents a stagger animation tick
type StaggerMsg struct {
	Index int
}

// StaggerConfig defines stagger animation parameters
type StaggerConfig struct {
	TotalItems int
	Delay      time.Duration  // Default: 100ms
}

// StartStagger returns a command to begin staggered reveals
func StartStagger(cfg StaggerConfig) tea.Cmd {
	if cfg.Delay == 0 {
		cfg.Delay = 100 * time.Millisecond
	}

	return func() tea.Msg {
		return StaggerMsg{Index: 0}
	}
}

// NextStagger returns a command for the next stagger tick
func NextStagger(currentIndex int, cfg StaggerConfig) tea.Cmd {
	if currentIndex >= cfg.TotalItems-1 {
		return nil  // Done staggering
	}

	return tea.Tick(cfg.Delay, func(t time.Time) tea.Msg {
		return StaggerMsg{Index: currentIndex + 1}
	})
}
```

**Step 2: Create Harmonica spring animation helper**

Create `internal/animation/spring.go`:

```go
package animation

import (
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/harmonica"
)

const (
	FPS       = 60
	Frequency = 7.0   // Higher = faster spring
	Damping   = 0.15  // Lower = bouncier
)

// SpringMsg represents a spring animation tick
type SpringMsg struct {
	Time time.Time
}

// SpringState manages spring physics state
type SpringState struct {
	Spring         harmonica.Spring
	CurrentPos     float64
	CurrentVel     float64
	TargetPos      float64
	AnimationDone  bool
}

// NewSpringState creates a new spring animation state
func NewSpringState(startPos, targetPos float64) *SpringState {
	return &SpringState{
		Spring:        harmonica.NewSpring(harmonica.FPS(FPS), Frequency, Damping),
		CurrentPos:    startPos,
		CurrentVel:    0,
		TargetPos:     targetPos,
		AnimationDone: false,
	}
}

// Update updates the spring physics
func (s *SpringState) Update() {
	s.CurrentPos, s.CurrentVel = s.Spring.Update(
		s.CurrentPos,
		s.CurrentVel,
		s.TargetPos,
	)

	// Check if settled (within 0.01 units of target)
	if abs(s.CurrentPos-s.TargetPos) < 0.01 && abs(s.CurrentVel) < 0.01 {
		s.AnimationDone = true
		s.CurrentPos = s.TargetPos
	}
}

// StartSpring returns a command to begin spring animation
func StartSpring() tea.Cmd {
	return tea.Tick(time.Second/FPS, func(t time.Time) tea.Msg {
		return SpringMsg{Time: t}
	})
}

// ContinueSpring returns a command to continue spring animation
func ContinueSpring() tea.Cmd {
	return tea.Tick(time.Second/FPS, func(t time.Time) tea.Msg {
		return SpringMsg{Time: t}
	})
}

func abs(x float64) float64 {
	if x < 0 {
		return -x
	}
	return x
}
```

**Step 3: Add staggered reveals to progress steps**

In `internal/ui/views/views.go`, modify `ProgressView`:

```go
import "github.com/flight505/agentui/internal/animation"

type ProgressView struct {
	message       string
	percent       float64
	steps         []ProgressStep
	width         int
	visibleSteps  int  // For stagger animation
}

func (p *ProgressView) SetSteps(steps []ProgressStep) {
	p.steps = steps
	p.visibleSteps = 0  // Start with none visible
}

func (p *ProgressView) RevealNextStep() {
	if p.visibleSteps < len(p.steps) {
		p.visibleSteps++
	}
}

func (p *ProgressView) View() string {
	var sb strings.Builder
	colors := theme.Current.Colors

	// ... (existing progress bar code)

	// Render only visible steps (stagger effect)
	if len(p.steps) > 0 {
		sb.WriteString("\n\n")
		for i := 0; i < p.visibleSteps && i < len(p.steps); i++ {
			step := p.steps[i]
			icon := getStepIcon(step.Status, colors)
			sb.WriteString(fmt.Sprintf("  %s %s\n", icon, step.Label))
		}
	}

	return sb.String()
}
```

**Step 4: Wire up stagger animation in main app**

In `internal/app/app.go`, add stagger handling:

```go
import "github.com/flight505/agentui/internal/animation"

type Model struct {
	// ... existing fields
	staggerConfig animation.StaggerConfig
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {

	case animation.StaggerMsg:
		// Reveal next progress step
		if m.currentProgress != nil {
			m.currentProgress.RevealNextStep()
			return m, animation.NextStagger(msg.Index, m.staggerConfig)
		}

	case protocol.ProgressMsg:
		// ... existing progress handling
		if len(msg.Steps) > 0 {
			// Start stagger animation
			m.staggerConfig = animation.StaggerConfig{
				TotalItems: len(msg.Steps),
				Delay:      100 * time.Millisecond,
			}
			return m, animation.StartStagger(m.staggerConfig)
		}
	}

	// ... rest of update
}
```

**Step 5: Add smooth progress bar interpolation**

In `internal/ui/views/views.go`, add to `ProgressView`:

```go
type ProgressView struct {
	// ... existing fields
	currentPercent float64  // Animated current
	targetPercent  float64  // Target to reach
}

func (p *ProgressView) SetPercent(pct float64) {
	p.targetPercent = pct
}

func (p *ProgressView) UpdateAnimation() bool {
	// Smooth interpolation (exponential easing)
	if abs(p.currentPercent-p.targetPercent) > 0.5 {
		diff := p.targetPercent - p.currentPercent
		p.currentPercent += diff * 0.15  // Easing factor
		return true  // Still animating
	}
	p.currentPercent = p.targetPercent
	return false  // Done
}

func (p *ProgressView) View() string {
	// Use currentPercent instead of targetPercent
	if p.currentPercent > 0 {
		bar := renderProgressBar(p.currentPercent, p.width-20)
		// ...
	}
}
```

**Step 6: Test animations**

Run: `make build-tui && uv run python examples/generative_ui_demo.py`
Expected:
- Progress steps reveal one by one (100ms delays)
- Progress bar fills smoothly, not in jumps

**Step 7: Commit**

```bash
git add internal/animation/ internal/ui/views/views.go internal/app/app.go
git commit -m "feat: add staggered reveals and smooth progress animations"
```

---

## Phase 1: Complete UI Primitives (Go Side)

### Task 1: Complete Progress View with Steps

**Files:**
- Modify: `internal/ui/views/views.go:200-300`
- Test manually: `examples/generative_ui_demo.py`

**Step 1: Write test Go code for progress with steps**

Create `internal/ui/views/progress_test.go`:

```go
package views

import (
	"testing"
)

func TestProgressViewWithSteps(t *testing.T) {
	p := NewProgressView()
	p.SetMessage("Processing...")
	p.SetPercent(50)

	steps := []ProgressStep{
		{Label: "Step 1", Status: "complete"},
		{Label: "Step 2", Status: "running"},
		{Label: "Step 3", Status: "pending"},
	}
	p.SetSteps(steps)

	view := p.View()
	if view == "" {
		t.Fatal("Progress view should not be empty")
	}
}
```

**Step 2: Run test to verify it fails**

Run: `cd internal/ui/views && go test -v`
Expected: FAIL - methods don't exist

**Step 3: Implement progress view with steps support**

In `internal/ui/views/views.go`, add to ProgressView:

```go
type ProgressStep struct {
	Label  string
	Status string // "complete", "running", "pending", "error"
}

type ProgressView struct {
	message string
	percent float64
	steps   []ProgressStep
	width   int
}

func NewProgressView() *ProgressView {
	return &ProgressView{
		steps: make([]ProgressStep, 0),
	}
}

func (p *ProgressView) SetMessage(msg string) {
	p.message = msg
}

func (p *ProgressView) SetPercent(pct float64) {
	p.percent = pct
}

func (p *ProgressView) SetSteps(steps []ProgressStep) {
	p.steps = steps
}

func (p *ProgressView) SetWidth(width int) {
	p.width = width
}

func (p *ProgressView) View() string {
	var sb strings.Builder
	colors := theme.Current.Colors

	// Message with spinner or percent
	if p.percent > 0 {
		bar := renderProgressBar(p.percent, p.width-20)
		sb.WriteString(lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Render(fmt.Sprintf("%s [%.0f%%]", p.message, p.percent)))
		sb.WriteString("\n")
		sb.WriteString(bar)
	} else {
		sb.WriteString(lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Render("⟳ " + p.message))
	}

	// Render steps
	if len(p.steps) > 0 {
		sb.WriteString("\n\n")
		for _, step := range p.steps {
			icon := getStepIcon(step.Status, colors)
			sb.WriteString(fmt.Sprintf("  %s %s\n", icon, step.Label))
		}
	}

	return sb.String()
}

func renderProgressBar(percent float64, width int) string {
	if width < 10 {
		width = 40
	}

	filled := int((percent / 100.0) * float64(width))
	if filled > width {
		filled = width
	}

	colors := theme.Current.Colors
	bar := strings.Repeat("█", filled) + strings.Repeat("░", width-filled)

	return lipgloss.NewStyle().
		Foreground(colors.Primary).
		Render(bar)
}

func getStepIcon(status string, colors theme.ColorPalette) string {
	switch status {
	case "complete":
		return lipgloss.NewStyle().Foreground(colors.Success).Render("✓")
	case "running":
		return lipgloss.NewStyle().Foreground(colors.Primary).Render("●")
	case "error":
		return lipgloss.NewStyle().Foreground(colors.Error).Render("✗")
	default: // pending
		return lipgloss.NewStyle().Foreground(colors.TextMuted).Render("○")
	}
}
```

**Step 4: Run test to verify it passes**

Run: `cd internal/ui/views && go test -v`
Expected: PASS

**Step 5: Wire up progress in protocol handler**

In `internal/protocol/handler.go`, update the progress message handler:

```go
case "progress":
	var payload struct {
		Message string              `json:"message"`
		Percent *float64            `json:"percent,omitempty"`
		Steps   []map[string]string `json:"steps,omitempty"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return nil
	}

	// Convert steps
	var steps []views.ProgressStep
	for _, s := range payload.Steps {
		steps = append(steps, views.ProgressStep{
			Label:  s["label"],
			Status: s["status"],
		})
	}

	return ProgressMsg{
		Message: payload.Message,
		Percent: payload.Percent,
		Steps:   steps,
	}
```

**Step 6: Test with Python example**

Run: `make build-tui && uv run python examples/generative_ui_demo.py`
Expected: Progress bars with steps render correctly

**Step 7: Commit**

```bash
git add internal/ui/views/views.go internal/ui/views/progress_test.go internal/protocol/handler.go
git commit -m "feat: add progress view with step tracking"
```

---

### Task 2: Complete Table View

**Files:**
- Modify: `internal/ui/views/views.go:400-500`
- Create: `internal/ui/views/table_test.go`

**Step 1: Write test for table rendering**

```go
// internal/ui/views/table_test.go
package views

import (
	"strings"
	"testing"
)

func TestTableView(t *testing.T) {
	tv := NewTableView()
	tv.SetTitle("Test Table")
	tv.SetColumns([]string{"Name", "Value", "Status"})
	tv.SetRows([][]string{
		{"Item 1", "100", "OK"},
		{"Item 2", "200", "OK"},
	})
	tv.SetFooter("Total: 2 items")
	tv.SetWidth(80)

	view := tv.View()

	if !strings.Contains(view, "Test Table") {
		t.Error("Table should contain title")
	}
	if !strings.Contains(view, "Item 1") {
		t.Error("Table should contain row data")
	}
}
```

**Step 2: Run test**

Run: `cd internal/ui/views && go test -run TestTableView -v`
Expected: FAIL - NewTableView doesn't exist

**Step 3: Implement TableView**

```go
type TableView struct {
	title   string
	columns []string
	rows    [][]string
	footer  string
	width   int
}

func NewTableView() *TableView {
	return &TableView{}
}

func (t *TableView) SetTitle(title string) {
	t.title = title
}

func (t *TableView) SetColumns(columns []string) {
	t.columns = columns
}

func (t *TableView) SetRows(rows [][]string) {
	t.rows = rows
}

func (t *TableView) SetFooter(footer string) {
	t.footer = footer
}

func (t *TableView) SetWidth(width int) {
	t.width = width
}

func (t *TableView) View() string {
	var sb strings.Builder
	colors := theme.Current.Colors
	styles := theme.Current.Styles

	if t.title != "" {
		sb.WriteString(styles.FormTitle.Render(t.title))
		sb.WriteString("\n\n")
	}

	if len(t.columns) == 0 {
		return sb.String()
	}

	// Calculate column widths
	colWidths := make([]int, len(t.columns))
	for i, col := range t.columns {
		colWidths[i] = len(col)
	}
	for _, row := range t.rows {
		for i, cell := range row {
			if i < len(colWidths) && len(cell) > colWidths[i] {
				colWidths[i] = len(cell)
			}
		}
	}

	// Render header
	headerStyle := lipgloss.NewStyle().
		Foreground(colors.Primary).
		Bold(true)

	for i, col := range t.columns {
		sb.WriteString(headerStyle.Render(padRight(col, colWidths[i])))
		if i < len(t.columns)-1 {
			sb.WriteString("  ")
		}
	}
	sb.WriteString("\n")

	// Render separator
	for i := range t.columns {
		sb.WriteString(strings.Repeat("─", colWidths[i]))
		if i < len(t.columns)-1 {
			sb.WriteString("  ")
		}
	}
	sb.WriteString("\n")

	// Render rows
	rowStyle := lipgloss.NewStyle().Foreground(colors.Text)
	for _, row := range t.rows {
		for i, cell := range row {
			if i < len(colWidths) {
				sb.WriteString(rowStyle.Render(padRight(cell, colWidths[i])))
				if i < len(row)-1 {
					sb.WriteString("  ")
				}
			}
		}
		sb.WriteString("\n")
	}

	// Render footer
	if t.footer != "" {
		sb.WriteString("\n")
		sb.WriteString(lipgloss.NewStyle().
			Foreground(colors.TextMuted).
			Render(t.footer))
	}

	return sb.String()
}

func padRight(s string, width int) string {
	if len(s) >= width {
		return s
	}
	return s + strings.Repeat(" ", width-len(s))
}
```

**Step 4: Run test**

Run: `cd internal/ui/views && go test -run TestTableView -v`
Expected: PASS

**Step 5: Wire up in protocol handler**

Update `internal/protocol/handler.go`:

```go
case "table":
	var payload struct {
		Title   string     `json:"title,omitempty"`
		Columns []string   `json:"columns"`
		Rows    [][]string `json:"rows"`
		Footer  string     `json:"footer,omitempty"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return nil
	}

	return TableMsg{
		Title:   payload.Title,
		Columns: payload.Columns,
		Rows:    payload.Rows,
		Footer:  payload.Footer,
	}
```

**Step 6: Test end-to-end**

Run: `make build-tui && uv run python examples/generative_ui_demo.py`
Expected: Tables render correctly

**Step 7: Commit**

```bash
git add internal/ui/views/views.go internal/ui/views/table_test.go internal/protocol/handler.go
git commit -m "feat: add table view component"
```

---

### Task 3: Complete Code View with Syntax Highlighting

**Files:**
- Modify: `internal/ui/views/views.go:300-400`
- Create: `internal/ui/views/code_test.go`

**Step 1: Add chroma dependency**

Run: `cd cmd/agentui && go get github.com/alecthomas/chroma/v2`

**Step 2: Write test**

```go
// internal/ui/views/code_test.go
package views

import (
	"strings"
	"testing"
)

func TestCodeView(t *testing.T) {
	cv := NewCodeView()
	cv.SetCode("func main() {\n\tprintln(\"hello\")\n}")
	cv.SetLanguage("go")
	cv.SetTitle("main.go")
	cv.SetWidth(80)

	view := cv.View()

	if !strings.Contains(view, "main.go") {
		t.Error("Code view should contain title")
	}
}
```

**Step 3: Run test**

Run: `cd internal/ui/views && go test -run TestCodeView -v`
Expected: FAIL

**Step 4: Implement CodeView with syntax highlighting**

```go
import (
	"github.com/alecthomas/chroma/v2"
	"github.com/alecthomas/chroma/v2/formatters"
	"github.com/alecthomas/chroma/v2/lexers"
	"github.com/alecthomas/chroma/v2/styles"
)

type CodeView struct {
	code     string
	language string
	title    string
	width    int
}

func NewCodeView() *CodeView {
	return &CodeView{}
}

func (c *CodeView) SetCode(code string) {
	c.code = code
}

func (c *CodeView) SetLanguage(language string) {
	c.language = language
}

func (c *CodeView) SetTitle(title string) {
	c.title = title
}

func (c *CodeView) SetWidth(width int) {
	c.width = width
}

func (c *CodeView) View() string {
	var sb strings.Builder
	colors := theme.Current.Colors
	styles := theme.Current.Styles

	if c.title != "" {
		sb.WriteString(styles.FormTitle.Render(c.title))
		sb.WriteString("\n")
	}

	if c.code == "" {
		return sb.String()
	}

	// Try to get lexer for language
	lexer := lexers.Get(c.language)
	if lexer == nil {
		lexer = lexers.Fallback
	}
	lexer = chroma.Coalesce(lexer)

	// Use terminal formatter
	formatter := formatters.Get("terminal256")
	if formatter == nil {
		formatter = formatters.Fallback
	}

	// Get style
	style := styles.Get("monokai")
	if style == nil {
		style = styles.Fallback
	}

	// Format code
	var buf strings.Builder
	iterator, err := lexer.Tokenise(nil, c.code)
	if err != nil {
		// Fallback to plain text
		sb.WriteString(c.code)
		return sb.String()
	}

	err = formatter.Format(&buf, style, iterator)
	if err != nil {
		sb.WriteString(c.code)
		return sb.String()
	}

	// Wrap in border
	codeStyle := lipgloss.NewStyle().
		Border(lipgloss.RoundedBorder()).
		BorderForeground(colors.Surface).
		Padding(1, 2)

	sb.WriteString(codeStyle.Render(buf.String()))

	return sb.String()
}
```

**Step 5: Run test**

Run: `cd internal/ui/views && go test -run TestCodeView -v`
Expected: PASS

**Step 6: Update go.mod**

Run: `cd cmd/agentui && go mod tidy`

**Step 7: Wire up in handler**

```go
case "code":
	var payload struct {
		Code     string `json:"code"`
		Language string `json:"language,omitempty"`
		Title    string `json:"title,omitempty"`
	}
	if err := json.Unmarshal(msg.Payload, &payload); err != nil {
		return nil
	}

	return CodeMsg{
		Code:     payload.Code,
		Language: payload.Language,
		Title:    payload.Title,
	}
```

**Step 8: Test end-to-end**

Run: `make build-tui && uv run python examples/generative_ui_demo.py`

**Step 9: Commit**

```bash
git add internal/ui/views/views.go internal/ui/views/code_test.go internal/protocol/handler.go cmd/agentui/go.mod cmd/agentui/go.sum
git commit -m "feat: add code view with syntax highlighting"
```

---

## Phase 2: Complete Python Skills System

### Task 4: Implement SKILL.md Loader

**Files:**
- Create: `src/agentui/skills/loader.py`
- Modify: `src/agentui/skills/__init__.py`
- Create: `tests/test_skills.py`
- Create: `tests/fixtures/test_skill/SKILL.md`
- Create: `tests/fixtures/test_skill/skill.yaml`

**Step 1: Write failing test**

```python
# tests/test_skills.py
import pytest
from pathlib import Path
from agentui.skills.loader import load_skill, SkillLoadError


def test_load_skill_from_directory():
    """Test loading a skill from directory with SKILL.md and skill.yaml"""
    skill_path = Path(__file__).parent / "fixtures" / "test_skill"
    skill = load_skill(skill_path)

    assert skill.name == "test_skill"
    assert skill.instructions is not None
    assert len(skill.tools) > 0


def test_load_skill_missing_files():
    """Test that loading fails gracefully if files missing"""
    with pytest.raises(SkillLoadError):
        load_skill(Path("/nonexistent"))
```

**Step 2: Run test**

Run: `uv run pytest tests/test_skills.py -v`
Expected: FAIL - module doesn't exist

**Step 3: Create test fixtures**

```bash
mkdir -p tests/fixtures/test_skill
```

Create `tests/fixtures/test_skill/SKILL.md`:

```markdown
# Test Skill

This is a test skill for unit testing.

## Instructions

When using this skill, you should:
1. Call the test_tool with appropriate parameters
2. Return the result to the user
```

Create `tests/fixtures/test_skill/skill.yaml`:

```yaml
name: test_skill
version: 1.0.0
description: A test skill for unit testing

tools:
  - name: test_tool
    description: A test tool
    parameters:
      type: object
      properties:
        query:
          type: string
          description: Test query
      required:
        - query
```

**Step 4: Implement skill loader**

```python
# src/agentui/skills/loader.py
"""Skill loading system."""

import logging
from pathlib import Path
from typing import Any
import yaml

from agentui.types import ToolDefinition

logger = logging.getLogger(__name__)


class SkillLoadError(Exception):
    """Raised when skill loading fails."""
    pass


class Skill:
    """Represents a loaded skill."""

    def __init__(
        self,
        name: str,
        instructions: str,
        tools: list[ToolDefinition],
        version: str = "1.0.0",
        description: str = "",
    ):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.version = version
        self.description = description


def load_skill(path: str | Path) -> Skill:
    """
    Load a skill from a directory.

    Expected structure:
        skill_dir/
            SKILL.md      - Instructions for LLM
            skill.yaml    - Tool definitions and metadata

    Args:
        path: Path to skill directory

    Returns:
        Loaded Skill instance

    Raises:
        SkillLoadError: If skill cannot be loaded
    """
    path = Path(path)

    if not path.exists():
        raise SkillLoadError(f"Skill directory not found: {path}")

    if not path.is_dir():
        raise SkillLoadError(f"Skill path is not a directory: {path}")

    # Load SKILL.md
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        raise SkillLoadError(f"SKILL.md not found in {path}")

    try:
        instructions = skill_md.read_text(encoding="utf-8")
    except Exception as e:
        raise SkillLoadError(f"Failed to read SKILL.md: {e}")

    # Load skill.yaml
    skill_yaml = path / "skill.yaml"
    if not skill_yaml.exists():
        raise SkillLoadError(f"skill.yaml not found in {path}")

    try:
        with open(skill_yaml, encoding="utf-8") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        raise SkillLoadError(f"Failed to parse skill.yaml: {e}")

    if not isinstance(config, dict):
        raise SkillLoadError("skill.yaml must contain a YAML object")

    # Extract metadata
    name = config.get("name", path.name)
    version = config.get("version", "1.0.0")
    description = config.get("description", "")

    # Load tools
    tools = []
    tool_configs = config.get("tools", [])

    for tool_config in tool_configs:
        if not isinstance(tool_config, dict):
            logger.warning(f"Skipping invalid tool config in {name}")
            continue

        tool = ToolDefinition(
            name=tool_config.get("name", "unnamed_tool"),
            description=tool_config.get("description", ""),
            parameters=tool_config.get("parameters", {}),
            handler=None,  # Handler registered separately
            is_ui_tool=tool_config.get("is_ui_tool", False),
            requires_confirmation=tool_config.get("requires_confirmation", False),
        )
        tools.append(tool)

    logger.info(f"Loaded skill '{name}' with {len(tools)} tools")

    return Skill(
        name=name,
        instructions=instructions,
        tools=tools,
        version=version,
        description=description,
    )


def load_skills_from_manifest(manifest_paths: list[str | Path]) -> list[Skill]:
    """
    Load multiple skills from manifest paths.

    Args:
        manifest_paths: List of paths to skill directories

    Returns:
        List of loaded Skills
    """
    skills = []

    for path in manifest_paths:
        try:
            skill = load_skill(path)
            skills.append(skill)
        except SkillLoadError as e:
            logger.error(f"Failed to load skill from {path}: {e}")

    return skills
```

**Step 5: Run test**

Run: `uv run pytest tests/test_skills.py -v`
Expected: PASS

**Step 6: Update skills __init__.py**

```python
# src/agentui/skills/__init__.py
"""Skills system for AgentUI."""

from agentui.skills.loader import (
    load_skill,
    load_skills_from_manifest,
    Skill,
    SkillLoadError,
)

__all__ = [
    "load_skill",
    "load_skills_from_manifest",
    "Skill",
    "SkillLoadError",
]
```

**Step 7: Commit**

```bash
git add src/agentui/skills/loader.py src/agentui/skills/__init__.py tests/test_skills.py tests/fixtures/
git commit -m "feat: add SKILL.md loader for skills system"
```

---

### Task 5: Integrate Skills into AgentApp

**Files:**
- Modify: `src/agentui/app.py:75-120`
- Modify: `src/agentui/types.py`
- Create: `tests/test_app_with_skills.py`

**Step 1: Write test**

```python
# tests/test_app_with_skills.py
import pytest
from pathlib import Path
from agentui import AgentApp


def test_app_loads_skills_from_manifest():
    """Test that AgentApp can load skills from manifest"""
    manifest_path = Path(__file__).parent / "fixtures" / "test_app_manifest.yaml"

    # Create test manifest
    manifest_path.parent.mkdir(exist_ok=True)
    manifest_path.write_text("""
name: test-app
skills:
  - tests/fixtures/test_skill
""")

    app = AgentApp(manifest=manifest_path)

    # Skills should be loaded
    assert hasattr(app, '_skills')
    assert len(app._skills) > 0

    # Cleanup
    manifest_path.unlink()
```

**Step 2: Run test**

Run: `uv run pytest tests/test_app_with_skills.py -v`
Expected: FAIL - _skills not set

**Step 3: Update AppManifest type**

In `src/agentui/types.py`:

```python
@dataclass
class AppManifest:
    """Application manifest configuration."""
    name: str
    version: str = "1.0.0"
    description: str = ""
    display_name: str | None = None
    tagline: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    skills: list[str] = field(default_factory=list)  # Add this

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AppManifest":
        """Create from dictionary."""
        return cls(
            name=data.get("name", "app"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            display_name=data.get("display_name"),
            tagline=data.get("tagline"),
            system_prompt=data.get("system_prompt"),
            model=data.get("model"),
            skills=data.get("skills", []),  # Add this
        )
```

**Step 4: Update AgentApp to load skills**

In `src/agentui/app.py`:

```python
from agentui.skills import load_skills_from_manifest

# In __init__:
self._skills: list[Skill] = []

# After loading manifest:
if self.manifest.skills:
    self._skills = load_skills_from_manifest(self.manifest.skills)
    logger.info(f"Loaded {len(self._skills)} skills")
```

**Step 5: Inject skill instructions into system prompt**

In `src/agentui/app.py`, modify the config creation:

```python
# Build system prompt with skill instructions
system_prompt_parts = [system_prompt or self.manifest.system_prompt or "You are a helpful AI assistant."]

for skill in self._skills:
    system_prompt_parts.append(f"\n\n## {skill.name} Skill\n\n{skill.instructions}")

combined_system_prompt = "\n".join(system_prompt_parts)

self.config = AgentConfig(
    # ... other fields
    system_prompt=combined_system_prompt,
)
```

**Step 6: Register skill tools**

In `src/agentui/app.py`, add method:

```python
def _register_skill_tools(self) -> None:
    """Register tools from loaded skills."""
    for skill in self._skills:
        for tool in skill.tools:
            # Tool handler needs to be provided by user or skill module
            # For now, register the definition
            self._tools.append(tool)
            logger.debug(f"Registered tool from skill: {tool.name}")
```

Call in `run()` before creating core:

```python
self._register_skill_tools()
```

**Step 7: Run test**

Run: `uv run pytest tests/test_app_with_skills.py -v`
Expected: PASS

**Step 8: Commit**

```bash
git add src/agentui/app.py src/agentui/types.py tests/test_app_with_skills.py
git commit -m "feat: integrate skills loading into AgentApp"
```

---

## Phase 3: Complete Agent Loop

### Task 6: Implement Full Tool Execution Pipeline

**Files:**
- Modify: `src/agentui/core.py:100-250`
- Create: `tests/test_tool_execution.py`

**Step 1: Write test for tool execution**

```python
# tests/test_tool_execution.py
import pytest
from agentui.core import AgentCore
from agentui.types import AgentConfig, ToolDefinition, ProviderType


@pytest.mark.asyncio
async def test_tool_execution():
    """Test that tools are executed correctly"""

    # Create a test tool
    call_count = 0

    async def test_tool(query: str) -> dict:
        nonlocal call_count
        call_count += 1
        return {"result": f"Processed: {query}"}

    tool_def = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"]
        },
        handler=test_tool,
    )

    config = AgentConfig(
        provider=ProviderType.CLAUDE,
        api_key="test-key",
    )

    core = AgentCore(config=config)
    core.register_tool(tool_def)

    # Execute tool
    result = await core.execute_tool("test_tool", {"query": "hello"})

    assert call_count == 1
    assert result["result"] == "Processed: hello"
```

**Step 2: Run test**

Run: `uv run pytest tests/test_tool_execution.py -v`
Expected: FAIL - execute_tool doesn't exist

**Step 3: Implement execute_tool in AgentCore**

In `src/agentui/core.py`:

```python
async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> Any:
    """
    Execute a tool by name with given arguments.

    Args:
        tool_name: Name of tool to execute
        arguments: Tool arguments

    Returns:
        Tool result

    Raises:
        ValueError: If tool not found
        Exception: If tool execution fails
    """
    # Find tool
    tool = None
    for t in self._tools:
        if t.name == tool_name:
            tool = t
            break

    if not tool:
        raise ValueError(f"Tool not found: {tool_name}")

    if not tool.handler:
        raise ValueError(f"Tool {tool_name} has no handler")

    logger.debug(f"Executing tool: {tool_name} with args: {arguments}")

    # Check if confirmation required
    if tool.requires_confirmation and self._bridge:
        confirmed = await self._bridge.request_confirm(
            f"Allow tool '{tool_name}'?",
            title="Tool Permission",
        )
        if not confirmed:
            logger.info(f"Tool {tool_name} rejected by user")
            return {"error": "Tool execution rejected by user"}

    # Execute handler
    try:
        if asyncio.iscoroutinefunction(tool.handler):
            result = await tool.handler(**arguments)
        else:
            # Run sync function in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, lambda: tool.handler(**arguments))

        logger.debug(f"Tool {tool_name} result: {result}")
        return result

    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        raise
```

**Step 4: Run test**

Run: `uv run pytest tests/test_tool_execution.py -v`
Expected: PASS

**Step 5: Integrate tool calling into process_message**

In `src/agentui/core.py`, update `process_message` to handle tool calls:

```python
async def process_message(self, user_message: str) -> AsyncIterator[MessageChunk]:
    """
    Process a user message and yield response chunks.

    Handles tool calling loop.
    """
    # Add to context
    self._context.append({
        "role": "user",
        "content": user_message,
    })

    # Tool calling loop
    max_iterations = 10
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Get provider response
        response_content = ""
        tool_calls = []

        async for chunk in self._provider.stream_message(
            messages=self._context,
            system=self._config.system_prompt,
            tools=[self._tool_to_provider_format(t) for t in self._tools],
        ):
            if chunk.content:
                response_content += chunk.content
                yield chunk

            if chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)

        # Add assistant response to context
        if response_content or tool_calls:
            self._context.append({
                "role": "assistant",
                "content": response_content,
                "tool_calls": tool_calls if tool_calls else None,
            })

        # If no tool calls, we're done
        if not tool_calls:
            break

        # Execute tools
        tool_results = []
        for tool_call in tool_calls:
            try:
                result = await self.execute_tool(
                    tool_call["name"],
                    tool_call.get("arguments", {})
                )
                tool_results.append({
                    "tool_call_id": tool_call.get("id"),
                    "role": "tool",
                    "content": json.dumps(result),
                })
            except Exception as e:
                tool_results.append({
                    "tool_call_id": tool_call.get("id"),
                    "role": "tool",
                    "content": json.dumps({"error": str(e)}),
                })

        # Add tool results to context
        self._context.extend(tool_results)

        # Continue loop to get next response

    if iteration >= max_iterations:
        yield MessageChunk(
            content="\n\n[Max tool iterations reached]",
            is_complete=True
        )
```

**Step 6: Add _tool_to_provider_format helper**

```python
def _tool_to_provider_format(self, tool: ToolDefinition) -> dict:
    """Convert internal tool definition to provider format."""
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.parameters,
    }
```

**Step 7: Run integration test**

Run: `make build-tui && uv run python examples/simple_agent.py`
Expected: Agent can call tools

**Step 8: Commit**

```bash
git add src/agentui/core.py tests/test_tool_execution.py
git commit -m "feat: implement full tool execution pipeline with confirmation"
```

---

## Phase 4: Additional Providers

### Task 7: Add Gemini Provider

**Files:**
- Create: `src/agentui/providers/gemini.py`
- Modify: `src/agentui/types.py`
- Modify: `pyproject.toml`
- Create: `tests/test_gemini_provider.py`

**Step 1: Add dependency**

Update `pyproject.toml`:

```toml
[project.optional-dependencies]
gemini = [
    "google-generativeai>=0.3.0",
]
all = [
    "anthropic>=0.40.0",
    "openai>=1.50.0",
    "google-generativeai>=0.3.0",
]
```

**Step 2: Install dependency**

Run: `uv add --optional gemini google-generativeai`

**Step 3: Write test (will be mocked)**

```python
# tests/test_gemini_provider.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agentui.providers.gemini import GeminiProvider


@pytest.mark.asyncio
async def test_gemini_provider_init():
    """Test Gemini provider initialization"""
    with patch('google.generativeai.configure'):
        provider = GeminiProvider(api_key="test-key", model="gemini-pro")
        assert provider.model == "gemini-pro"
```

**Step 4: Run test**

Run: `uv run pytest tests/test_gemini_provider.py -v`
Expected: FAIL - module doesn't exist

**Step 5: Implement Gemini provider**

```python
# src/agentui/providers/gemini.py
"""Google Gemini provider."""

import asyncio
import json
import logging
from typing import Any, AsyncIterator

try:
    import google.generativeai as genai
    from google.generativeai.types import GenerationConfig
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from agentui.types import MessageChunk

logger = logging.getLogger(__name__)


class GeminiProvider:
    """Google Gemini API provider."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-pro",
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ):
        if not GEMINI_AVAILABLE:
            raise ImportError(
                "google-generativeai not installed. "
                "Install with: pip install agentui[gemini]"
            )

        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature

        # Configure API
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)

    async def stream_message(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[MessageChunk]:
        """
        Stream a message response.

        Note: Gemini API doesn't support streaming with tool use yet,
        so we'll simulate streaming.
        """
        # Build prompt from messages
        prompt_parts = []

        if system:
            prompt_parts.append(f"System: {system}\n")

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
            elif role == "tool":
                # Format tool result
                prompt_parts.append(f"Tool result: {content}")

        prompt_parts.append("Assistant: ")
        prompt = "\n\n".join(prompt_parts)

        # Generate config
        config = GenerationConfig(
            max_output_tokens=self.max_tokens,
            temperature=self.temperature,
        )

        # Generate response
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.generate_content(
                    prompt,
                    generation_config=config,
                )
            )

            # Yield response
            content = response.text

            # Simulate streaming by chunking
            chunk_size = 50
            for i in range(0, len(content), chunk_size):
                chunk_text = content[i:i+chunk_size]
                yield MessageChunk(
                    content=chunk_text,
                    is_complete=(i + chunk_size >= len(content))
                )
                await asyncio.sleep(0.01)  # Small delay for realistic streaming

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            yield MessageChunk(
                content=f"Error: {e}",
                is_complete=True
            )
```

**Step 6: Run test**

Run: `uv run pytest tests/test_gemini_provider.py -v`
Expected: PASS

**Step 7: Update provider type enum**

In `src/agentui/types.py`:

```python
class ProviderType(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"  # Add this
```

**Step 8: Wire up in AgentCore**

In `src/agentui/core.py`, update `_init_provider`:

```python
def _init_provider(self) -> Any:
    """Initialize the LLM provider."""
    if self._config.provider == ProviderType.CLAUDE:
        from agentui.providers.claude import ClaudeProvider
        return ClaudeProvider(
            api_key=self._config.api_key or "",
            model=self._config.model or "claude-sonnet-4-5-20250929",
            max_tokens=self._config.max_tokens,
            temperature=self._config.temperature,
        )
    elif self._config.provider == ProviderType.OPENAI:
        from agentui.providers.openai import OpenAIProvider
        return OpenAIProvider(
            api_key=self._config.api_key or "",
            model=self._config.model or "gpt-4o",
            max_tokens=self._config.max_tokens,
            temperature=self._config.temperature,
        )
    elif self._config.provider == ProviderType.GEMINI:
        from agentui.providers.gemini import GeminiProvider
        return GeminiProvider(
            api_key=self._config.api_key or "",
            model=self._config.model or "gemini-pro",
            max_tokens=self._config.max_tokens,
            temperature=self._config.temperature,
        )
    else:
        raise ValueError(f"Unknown provider: {self._config.provider}")
```

**Step 9: Update providers __init__.py**

```python
# src/agentui/providers/__init__.py
"""LLM providers."""

from agentui.providers.claude import ClaudeProvider
from agentui.providers.openai import OpenAIProvider
from agentui.providers.gemini import GeminiProvider, GEMINI_AVAILABLE

__all__ = [
    "ClaudeProvider",
    "OpenAIProvider",
    "GeminiProvider",
    "GEMINI_AVAILABLE",
]
```

**Step 10: Commit**

```bash
git add src/agentui/providers/gemini.py src/agentui/providers/__init__.py src/agentui/types.py src/agentui/core.py pyproject.toml tests/test_gemini_provider.py
git commit -m "feat: add Google Gemini provider support"
```

---

## Phase 5: Testing & Documentation

### Task 8: Add Integration Tests

**Files:**
- Create: `tests/integration/test_full_flow.py`
- Create: `tests/integration/conftest.py`

**Step 1: Create integration test structure**

```bash
mkdir -p tests/integration
```

**Step 2: Write integration test**

```python
# tests/integration/test_full_flow.py
"""End-to-end integration tests."""

import pytest
import asyncio
from pathlib import Path
from agentui import AgentApp


@pytest.mark.integration
@pytest.mark.asyncio
async def test_agent_with_tool_calling():
    """Test full agent flow with tool calling"""

    # Track tool calls
    tool_called = False
    tool_args = None

    async def weather_tool(city: str) -> dict:
        nonlocal tool_called, tool_args
        tool_called = True
        tool_args = {"city": city}
        return {
            "city": city,
            "temperature": 22,
            "conditions": "sunny"
        }

    # Create app
    app = AgentApp(
        provider="claude",
        api_key="test-key-invalid",  # Won't actually call API in this test
    )

    app.tool(
        name="get_weather",
        description="Get weather for a city",
        parameters={
            "type": "object",
            "properties": {
                "city": {"type": "string"}
            },
            "required": ["city"]
        }
    )(weather_tool)

    # Tool should be registered
    assert len(app._tools) == 1
    assert app._tools[0].name == "get_weather"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_app_loads_skills():
    """Test app loading skills from directory"""

    manifest_path = Path(__file__).parent.parent / "fixtures" / "test_app_manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    manifest_path.write_text("""
name: test-integration-app
description: Integration test app
skills:
  - tests/fixtures/test_skill
""")

    try:
        app = AgentApp(manifest=manifest_path)

        # Should have loaded skill
        assert len(app._skills) > 0
        assert app._skills[0].name == "test_skill"

    finally:
        if manifest_path.exists():
            manifest_path.unlink()
```

**Step 3: Create conftest for integration tests**

```python
# tests/integration/conftest.py
"""Pytest configuration for integration tests."""

import pytest


def pytest_configure(config):
    """Add integration marker."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
```

**Step 4: Update pytest config**

In `pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
markers = [
    "integration: integration tests (deselect with '-m \"not integration\"')",
]
```

**Step 5: Run integration tests**

Run: `uv run pytest tests/integration/ -v -m integration`
Expected: Tests pass

**Step 6: Add to CI skip marker**

Create `.github/workflows/test.yml` (if not exists):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install uv
      run: pip install uv

    - name: Install dependencies
      run: uv sync --all-extras

    - name: Run unit tests
      run: uv run pytest tests/ -v -m "not integration"

    - name: Run linting
      run: uv run ruff check src/ tests/
```

**Step 7: Commit**

```bash
git add tests/integration/ pyproject.toml .github/
git commit -m "test: add integration tests for full agent flow"
```

---

### Task 9: Add Documentation

**Files:**
- Create: `docs/getting-started.md`
- Create: `docs/api-reference.md`
- Create: `docs/examples.md`
- Modify: `README.md`

**Step 1: Create getting started guide**

```markdown
# Getting Started with AgentUI

## Installation

```bash
pip install agentui[all]
```

This installs AgentUI with support for all providers (Claude, OpenAI, Gemini).

For individual providers:
```bash
pip install agentui[claude]    # Claude only
pip install agentui[openai]    # OpenAI only
pip install agentui[gemini]    # Gemini only
```

## Quick Start

### Simple Agent

```python
from agentui import AgentApp
import asyncio

app = AgentApp(
    name="my-agent",
    provider="claude",  # or "openai", "gemini"
)

@app.tool(
    name="get_time",
    description="Get the current time",
    parameters={"type": "object", "properties": {}}
)
async def get_time():
    from datetime import datetime
    return {"time": datetime.now().isoformat()}

asyncio.run(app.run("What time is it?"))
```

### Using Manifests

Create `app.yaml`:

```yaml
name: my-agent
description: My AI agent
display_name: "My Agent"
tagline: "Helpful AI Assistant"

providers:
  default: claude
  claude:
    model: claude-sonnet-4-5-20250929

skills:
  - ./skills/research
  - ./skills/analysis

system_prompt: |
  You are a helpful AI assistant.
  Use your tools to help the user.
```

Then:

```python
from agentui import AgentApp
import asyncio

app = AgentApp(manifest="app.yaml")
asyncio.run(app.run())
```

## Next Steps

- [API Reference](api-reference.md)
- [Examples](examples.md)
- [Creating Skills](skills.md)
```

Save to `docs/getting-started.md`

**Step 2: Create API reference**

```markdown
# API Reference

## AgentApp

Main application class for creating AI agents.

### Constructor

```python
AgentApp(
    name: str = "agent",
    manifest: str | Path | AppManifest | None = None,
    provider: str = "claude",
    model: str | None = None,
    api_key: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    system_prompt: str | None = None,
    theme: str = "catppuccin-mocha",
    tagline: str = "AI Agent Interface",
    debug: bool = False,
)
```

### Methods

#### `tool(name, description, parameters)`

Decorator to register a tool.

```python
@app.tool(
    name="search_web",
    description="Search the web",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
)
async def search_web(query: str):
    return {"results": [...]}
```

#### `run(prompt=None)`

Run the agent application.

```python
await app.run()
await app.run("Initial prompt")
```

## UI Primitives

### Progress

```python
await bridge.send_progress(
    message="Processing...",
    percent=50,
    steps=[
        {"label": "Step 1", "status": "complete"},
        {"label": "Step 2", "status": "running"},
    ]
)
```

### Forms

```python
result = await bridge.request_form(
    title="Configuration",
    fields=[
        {"name": "name", "label": "Name", "type": "text"},
        {"name": "enabled", "label": "Enable", "type": "checkbox"},
    ]
)
```

### Tables

```python
await bridge.send_table(
    title="Results",
    columns=["Name", "Value"],
    rows=[["Item 1", "100"], ["Item 2", "200"]],
    footer="Total: 2 items"
)
```

More primitives: code, markdown, alerts, confirmations, selections.

## Providers

### Claude

```python
app = AgentApp(provider="claude", model="claude-sonnet-4-5-20250929")
```

Requires: `ANTHROPIC_API_KEY` environment variable

### OpenAI

```python
app = AgentApp(provider="openai", model="gpt-4o")
```

Requires: `OPENAI_API_KEY` environment variable

### Gemini

```python
app = AgentApp(provider="gemini", model="gemini-pro")
```

Requires: `GOOGLE_API_KEY` environment variable
```

Save to `docs/api-reference.md`

**Step 3: Update README**

Update `README.md` with:

```markdown
# AgentUI

Build beautiful AI agent applications with Charm-quality TUIs.

[![Tests](https://github.com/flight505/agentui/workflows/Tests/badge.svg)](https://github.com/flight505/agentui/actions)
[![PyPI](https://img.shields.io/pypi/v/agentui)](https://pypi.org/project/agentui/)

## Features

- 🎨 **Beautiful TUIs** - Charm/Bubbletea rendering in Go
- 🤖 **Multi-Provider** - Claude, OpenAI, Gemini support
- 🔧 **Tool System** - Easy decorator-based tool registration
- 📦 **Skills** - Modular, reusable agent capabilities
- 🎭 **Generative UI** - Forms, tables, progress, code blocks
- 🎨 **Themes** - Catppuccin, Dracula, Nord, and more

## Quick Start

```bash
pip install agentui[all]
```

```python
from agentui import AgentApp
import asyncio

app = AgentApp(provider="claude")

@app.tool("get_weather", "Get weather", {"type": "object", ...})
async def get_weather(city: str):
    return {"temp": 22, "conditions": "sunny"}

asyncio.run(app.run())
```

## Documentation

- [Getting Started](docs/getting-started.md)
- [API Reference](docs/api-reference.md)
- [Examples](docs/examples.md)

## Development

```bash
# Install dependencies
uv sync

# Build TUI
make build-tui

# Run tests
make test

# Run demo
make demo
```

## License

MIT
```

**Step 4: Commit**

```bash
git add docs/ README.md
git commit -m "docs: add getting started guide and API reference"
```

---

### Task 10: Binary Distribution Setup

**Files:**
- Create: `scripts/package-binaries.sh`
- Modify: `pyproject.toml`
- Create: `MANIFEST.in`

**Step 1: Create binary packaging script**

```bash
#!/bin/bash
# scripts/package-binaries.sh
#
# Build TUI binaries for all platforms and package with Python

set -e

echo "Building binaries for all platforms..."

# Create bin directory in package
mkdir -p src/agentui/bin

# Build for each platform
platforms=(
    "darwin/amd64"
    "darwin/arm64"
    "linux/amd64"
    "linux/arm64"
    "windows/amd64"
)

for platform in "${platforms[@]}"; do
    IFS='/' read -r -a parts <<< "$platform"
    os="${parts[0]}"
    arch="${parts[1]}"

    output="src/agentui/bin/agentui-tui-${os}-${arch}"
    if [ "$os" = "windows" ]; then
        output="${output}.exe"
    fi

    echo "Building for $os/$arch..."
    GOOS=$os GOARCH=$arch go build -o "$output" ./cmd/agentui
done

echo "Binaries built successfully!"
ls -lh src/agentui/bin/
```

**Step 2: Make script executable**

Run: `chmod +x scripts/package-binaries.sh`

**Step 3: Create MANIFEST.in**

```
# MANIFEST.in
include README.md
include LICENSE
include CLAUDE.md
include DESIGN.md
recursive-include src/agentui/bin *
recursive-include examples *.py *.yaml
recursive-include docs *.md
```

**Step 4: Update pyproject.toml build config**

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/agentui"]
include = [
    "/src/agentui/bin/*",
]

[tool.hatch.build.targets.sdist]
include = [
    "/src",
    "/examples",
    "/docs",
    "/scripts",
    "/cmd",
    "/internal",
    "/go.mod",
    "/go.sum",
    "/Makefile",
    "/MANIFEST.in",
]
```

**Step 5: Update Makefile**

Add target:

```makefile
# Package for distribution
package: build-all-platforms
	@echo "Packaging for distribution..."
	./scripts/package-binaries.sh
	uv build
	@echo "Package built: dist/"

# Publish to PyPI (requires auth)
publish: package
	uv publish
```

**Step 6: Test packaging**

Run: `make package`
Expected: Creates dist/ with wheel and sdist containing binaries

**Step 7: Create .gitignore entry**

Add to `.gitignore`:

```
# Distribution
dist/
build/
*.egg-info
```

**Step 8: Commit**

```bash
git add scripts/package-binaries.sh MANIFEST.in pyproject.toml Makefile .gitignore
git commit -m "build: add binary packaging for distribution"
```

---

## Phase 6: Polish & Examples

### Task 11: Add Comprehensive Examples

**Files:**
- Create: `examples/weather_agent.py`
- Create: `examples/research_assistant.py`
- Create: `examples/skills/web_search/SKILL.md`
- Create: `examples/skills/web_search/skill.yaml`

**Step 1: Create weather agent example**

```python
# examples/weather_agent.py
"""
Weather Agent Example

Demonstrates:
- Tool registration
- UI primitives (progress, tables)
- Error handling
"""

import asyncio
from agentui import AgentApp


app = AgentApp(
    name="weather-agent",
    provider="claude",
    system_prompt="""You are a weather assistant.
    Use the get_weather tool to help users with weather information.
    Display results in a nice table format.""",
    tagline="Weather Information Assistant"
)


@app.tool(
    name="get_weather",
    description="Get current weather for a city",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name"
            }
        },
        "required": ["city"]
    }
)
async def get_weather(city: str) -> dict:
    """Simulate getting weather (replace with real API)."""
    # Simulate API call delay
    await asyncio.sleep(0.5)

    # Mock data
    weather_data = {
        "city": city,
        "temperature": 22,
        "conditions": "Sunny",
        "humidity": 65,
        "wind_speed": 10
    }

    return weather_data


if __name__ == "__main__":
    asyncio.run(app.run("What's the weather in San Francisco?"))
```

**Step 2: Create research assistant example**

```python
# examples/research_assistant.py
"""
Research Assistant Example

Demonstrates:
- Multiple tools
- Progress tracking
- Markdown output
- Skills integration
"""

import asyncio
from agentui import AgentApp


app = AgentApp(
    manifest="examples/research_app.yaml"
)


@app.tool(
    name="web_search",
    description="Search the web for information",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
)
async def web_search(query: str) -> dict:
    """Mock web search."""
    await asyncio.sleep(1)
    return {
        "results": [
            {"title": f"Result for {query}", "url": "https://example.com"},
        ]
    }


@app.tool(
    name="summarize",
    description="Summarize text",
    parameters={
        "type": "object",
        "properties": {
            "text": {"type": "string"}
        },
        "required": ["text"]
    }
)
async def summarize(text: str) -> dict:
    """Mock summarization."""
    await asyncio.sleep(0.5)
    return {"summary": f"Summary of {len(text)} characters"}


if __name__ == "__main__":
    asyncio.run(app.run())
```

**Step 3: Create manifest for research assistant**

```yaml
# examples/research_app.yaml
name: research-assistant
version: 1.0.0
description: AI-powered research assistant

display_name: "Research Assistant"
tagline: "Gather and analyze information"

providers:
  default: claude
  claude:
    model: claude-sonnet-4-5-20250929

system_prompt: |
  You are a research assistant. Help users:
  1. Search for information
  2. Summarize findings
  3. Present results clearly

  Use tools to gather information and display in organized formats.
```

**Step 4: Create web search skill**

```markdown
# examples/skills/web_search/SKILL.md

# Web Search Skill

This skill provides web searching capabilities.

## Usage

When the user asks for information that requires web search:

1. Use the `search_web` tool with appropriate query
2. Present results in a table or formatted list
3. Offer to search for more details if needed

## Example

User: "Find information about Python asyncio"
Assistant: Let me search for that...
[Uses search_web tool]
[Displays results in table]
```

```yaml
# examples/skills/web_search/skill.yaml
name: web_search
version: 1.0.0
description: Web search capability

tools:
  - name: search_web
    description: Search the web for information
    parameters:
      type: object
      properties:
        query:
          type: string
          description: Search query
        max_results:
          type: integer
          description: Maximum number of results
          default: 5
      required:
        - query
```

**Step 5: Test examples**

Run: `uv run python examples/weather_agent.py`
Run: `uv run python examples/research_assistant.py`

**Step 6: Commit**

```bash
git add examples/
git commit -m "docs: add comprehensive examples for weather and research agents"
```

---

## Verification & Cleanup

### Task 12: Final Integration Testing

**Step 1: Run all tests**

```bash
uv run pytest tests/ -v
```

**Step 2: Run type checking**

```bash
uv run mypy src/
```

**Step 3: Run linting**

```bash
uv run ruff check src/ tests/ examples/
```

**Step 4: Run formatting**

```bash
uv run ruff format src/ tests/ examples/
```

**Step 5: Build everything**

```bash
make clean
make build
```

**Step 6: Test all examples**

```bash
for example in examples/*.py; do
    echo "Testing $example"
    uv run python "$example" --help || true
done
```

**Step 7: Build package**

```bash
make package
```

**Step 8: Verify package contents**

```bash
tar -tzf dist/agentui-*.tar.gz | grep -E '(bin/|examples/|docs/)'
```

**Step 9: Create release checklist**

Create `docs/release-checklist.md`:

```markdown
# Release Checklist

- [ ] All tests pass
- [ ] Type checking passes (mypy)
- [ ] Linting passes (ruff)
- [ ] Code formatted (ruff format)
- [ ] All examples work
- [ ] Documentation is up-to-date
- [ ] CHANGELOG.md updated
- [ ] Version bumped in pyproject.toml
- [ ] Binaries built for all platforms
- [ ] Package builds successfully
- [ ] Git tag created
- [ ] Pushed to GitHub
- [ ] Published to PyPI
```

**Step 10: Final commit**

```bash
git add -A
git commit -m "chore: complete implementation and verification"
git tag v0.1.0
```

---

## Summary

This plan implements the complete AgentUI framework according to DESIGN.md:

**Completed:**
1. ✅ All UI primitives (progress with steps, tables, code with syntax highlighting)
2. ✅ Skills system (SKILL.md loader, integration with AgentApp)
3. ✅ Full tool execution pipeline with confirmation support
4. ✅ Gemini provider (in addition to Claude and OpenAI)
5. ✅ Comprehensive testing (unit + integration)
6. ✅ Documentation (getting started, API reference)
7. ✅ Binary distribution setup
8. ✅ Example applications

**Architecture:**
- Split-process Go/Python design
- JSON Lines protocol over stdio
- Bubbletea TUI with Charm styling
- Provider abstraction for LLMs
- Skills and tools system

**Next Steps:**
- Run `make build && make test` to verify
- Test examples
- Package and distribute
