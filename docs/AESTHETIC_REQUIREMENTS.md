# AgentUI Aesthetic Requirements

> **Critical:** This document defines the visual design philosophy to avoid generic "AI slop" TUI aesthetics. All Go TUI implementation MUST follow these principles.

Based on comprehensive research into Charm/Bubbletea, Lip Gloss, terminal color theory, and TUI animation patterns.

---

## Core Aesthetic Philosophy

**"Intentional Restraint with Strategic Flourish"**

- Use 3-4 colors intentionally, not 8+ colors generically
- Typography hierarchy (bold, faint, italic) > color saturation
- Animation timing 100-500ms (responsive, not sluggish)
- Cultural/thematic coherence over "modern developer theme #47"

---

## 1. Color Palette Requirements

### Current State (To Evolve)
✅ 5 themes implemented (Catppuccin, Dracula, Nord, Tokyo Night, Gruvbox)
❌ All follow "safe modern developer theme" patterns
❌ Missing distinctive, culturally-inspired alternatives

### Required Additions

**Distinctive Palette #1: "Sage" (Minimalist Warm)**
- Philosophy: Japanese MA (negative space), warm minimalism
- Base: Warm grays (#2a2827, #e8e6e3)
- Accent: Forest green (#799a77) for interactive elements
- Secondary: Clay (#a0826d) for emphasis
- Semantic: Sage for success, terracotta for warnings

**Distinctive Palette #2: "Obsidian" (Modern Technical)**
- Philosophy: High-contrast technical, cyberpunk-lite
- Base: Deep charcoal (#0a0a0a, #1a1a1a)
- Accent: Vibrant cyan (#00d9ff) for primary actions
- Secondary: Neon green (#39ff14) for success states
- Use: Data-heavy UIs, developer tools

**Distinctive Palette #3: "Zephyr" (Light Calm)**
- Philosophy: Productivity-focused light theme
- Base: Cream (#faf9f6, #fffef9)
- Accent: Cool blue (#4a90e2) for interactive
- Secondary: Teal (#88c9d1) for supporting elements
- Use: Extended reading, documentation viewing

**Distinctive Palette #4: "Ember" (Premium Warmth)**
- Philosophy: Inviting, premium feel
- Base: Deep navy (#1e293b, #0f172a)
- Accent: Warm amber (#f59e0b) for interactive
- Secondary: Coral (#ff6b6b) for emphasis
- Use: Consumer-facing AI agents

### Color System Architecture

```go
type ColorPalette struct {
    // Base hierarchy (3 levels minimum)
    Background  lipgloss.Color
    Surface     lipgloss.Color  // Elevated elements
    Text        lipgloss.Color
    TextMuted   lipgloss.Color
    TextDim     lipgloss.Color  // Least emphasis

    // Interaction (single primary + 1-2 accents max)
    Primary     lipgloss.Color  // Focused/interactive
    Accent1     lipgloss.Color  // Tool calls, special states
    Accent2     lipgloss.Color  // Secondary actions

    // Semantic (4 standard)
    Success     lipgloss.Color
    Warning     lipgloss.Color
    Error       lipgloss.Color
    Info        lipgloss.Color
}
```

**Mandatory**: All colors MUST use `AdaptiveColor` or `CompleteAdaptiveColor` for terminal compatibility:

```go
Primary: lipgloss.CompleteAdaptiveColor{
    Light: lipgloss.CompleteColor{
        TrueColor: "#4a90e2",
        ANSI256:   "68",
        ANSI:      "4",
    },
    Dark: lipgloss.CompleteColor{
        TrueColor: "#5eadf7",
        ANSI256:   "75",
        ANSI:      "12",
    },
}
```

---

## 2. Typography & Hierarchy

### Hierarchy Through Text Treatment (Not Just Color)

**Level 1 - Critical Information:**
```go
Bold(true).Foreground(Primary).MarginBottom(1)
```
Example: Section headers, active form titles

**Level 2 - Important Content:**
```go
Foreground(Text).MarginBottom(1)
```
Example: User messages, main content

**Level 3 - Supporting Information:**
```go
Foreground(TextMuted).Faint(true)
```
Example: Timestamps, helper text, metadata

**Level 4 - Disabled/Archived:**
```go
Foreground(TextDim).Strikethrough(true).Faint(true)
```
Example: Completed steps, old messages

### Text Formatting Guidelines

- **Bold**: Titles, active elements, focus states
- **Italic**: Quotes, citations, system messages
- **Faint**: Metadata, timestamps, secondary info
- **Underline**: Links (if applicable), active selections
- **Strikethrough**: Completed items, disabled options
- **Reverse**: Selection state, keyboard shortcuts

**Anti-pattern**: Don't use color alone for hierarchy—combine with weight/style.

---

## 3. Borders & Composition

### Border Style Philosophy

**Current**: Uses `RoundedBorder()` everywhere (modern but generic)

**Required Diversity**:

1. **Rounded** - Casual, friendly interfaces
   ```go
   Border(lipgloss.RoundedBorder())
   ```

2. **Double** - Important containers, modal dialogs
   ```go
   Border(lipgloss.DoubleBorder())
   ```

3. **Half-Block** - Modern, sophisticated (DISTINCTIVE)
   ```go
   Border(lipgloss.OuterHalfBlockBorder())
   ```

4. **Asymmetric** - Visual flow, quotes, sidebars
   ```go
   Border(lipgloss.NormalBorder(), false, false, false, true)  // Left only
   ```

### Per-Side Border Coloring (LEVERAGE THIS)

```go
// Different colors create visual hierarchy
style := NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderLeftForeground(colors.Primary).      // Accent left
    BorderTopForeground(colors.Surface).       // Subtle top/right/bottom
    BorderRightForeground(colors.Surface).
    BorderBottomForeground(colors.Surface)
```

Use cases:
- **Left accent**: Quote blocks, sidebars, nested content
- **Top accent**: Section dividers
- **Full accent**: Active/focused elements
- **No border top/bottom**: Stacked list items

### Advanced Composition Patterns

**Layered Containers** (creates depth without shadows):
```go
outer := NewStyle().
    Border(lipgloss.ThickBorder()).
    BorderForeground(colors.Primary).
    Padding(1)

inner := NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderForeground(colors.Surface).
    Padding(2)

result := outer.Render(inner.Render(content))
```

**Textured Backgrounds** (UNIQUE TO LIPGLOSS):
```go
lipgloss.Place(
    width, height,
    lipgloss.Center, lipgloss.Center,
    content,
    lipgloss.WithWhitespaceChars("▔▁"),  // Creates pattern
    lipgloss.WithWhitespaceForeground(colors.Surface),
)
```

**ColorWhitespace for Card Effect**:
```go
cardStyle := NewStyle().
    Background(colors.Surface).
    ColorWhitespace(true).  // Extends background to padding
    Padding(2, 4).
    Border(lipgloss.RoundedBorder())
```

---

## 4. Animation & Motion Requirements

### Timing Standards

| Duration | Use Case | Feel |
|----------|----------|------|
| **100ms** | Button clicks, toggles, micro-interactions | Instantaneous |
| **200-300ms** | Modal appearance, form reveals, state changes | Smooth |
| **300-500ms** | Layout transitions, multi-element reveals | Deliberate |
| **> 500ms** | Only for indeterminate spinners (never for transitions) | Sluggish |

### Required Animation Capabilities

**1. Spinner Variations (Already Implemented)**
```go
// Fast (urgent operations)
spinner.Dot     // 10 FPS - energetic
spinner.MiniDot // 12 FPS - snappy

// Medium (standard operations)
spinner.Points  // 7 FPS - rhythmic
spinner.Meter   // 7 FPS - progress-like

// Slow (background operations)
spinner.Globe   // 4 FPS - leisurely
spinner.Moon    // 8 FPS - steady
```

**2. Staggered Reveals (IMPLEMENT THIS)**

Progress steps should animate in with 100ms delays:
```go
// Frame 0ms:   ○ Step 1
// Frame 100ms: ○ Step 1, ○ Step 2
// Frame 200ms: ○ Step 1, ○ Step 2, ● Step 3 (running)
// Frame 300ms: ○ Step 1, ○ Step 2, ● Step 3, ○ Step 4
```

Implementation pattern:
```go
type Model struct {
    visibleSteps int
    stepDelay    time.Duration
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {
    case tea.TickMsg:
        if m.visibleSteps < len(m.allSteps) {
            m.visibleSteps++
            return m, tea.Tick(100*time.Millisecond, func(t time.Time) tea.Msg {
                return tea.TickMsg(t)
            })
        }
    }
}
```

**3. Harmonica Spring Physics (NEW REQUIREMENT)**

Add dependency:
```bash
go get github.com/charmbracelet/harmonica
```

Use for smooth modal/dialog positioning:
```go
import "github.com/charmbracelet/harmonica"

const (
    FPS       = 60
    Frequency = 7.0   // Higher = faster
    Damping   = 0.15  // Lower = bouncier
)

type Model struct {
    spring harmonica.Spring
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    // Smooth easing to target position
    m.spring.Update(currentPos, currentVel, targetPos)

    if m.spring.Done() {
        return m, nil
    }
    return m, tea.Tick(time.Second/FPS, ...)
}
```

**4. Progress Bar Fill Animation**

Don't jump 0% → 50% → 100%, animate smoothly:
```go
type ProgressModel struct {
    currentPercent float64
    targetPercent  float64
}

// Smooth interpolation (200ms total)
func (m Model) Update(msg tea.Msg) {
    diff := m.targetPercent - m.currentPercent
    m.currentPercent += diff * 0.1  // Exponential easing
}
```

### Animation Anti-Patterns

❌ **Don't**: Instant state changes (0ms)
✅ **Do**: 100-200ms transitions

❌ **Don't**: Linear motion (looks robotic)
✅ **Do**: Easing curves (accelerate in, decelerate out)

❌ **Don't**: All elements animate simultaneously
✅ **Do**: Stagger by 50-100ms

❌ **Don't**: Animate everything (visual noise)
✅ **Do**: Animate high-impact moments (page load, major state changes)

---

## 5. Component-Specific Aesthetic Rules

### Forms

**Visual Hierarchy**:
1. **Title**: Bold + Primary color + DoubleBorder
2. **Field labels**: Text color, normal weight
3. **Helper text**: TextMuted + Faint
4. **Required markers**: Error color (*)
5. **Focused field**: Primary border + Background(Surface)

**Border Treatment**:
```go
formContainer := NewStyle().
    Border(lipgloss.DoubleBorder()).
    BorderForeground(colors.Primary).
    Padding(2, 4)

focusedField := NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderForeground(colors.Primary).
    Background(colors.Surface).
    Padding(0, 1)

blurredField := NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderForeground(colors.TextMuted).
    Padding(0, 1)
```

### Tables

**Alternating Row Pattern** (prevents monotony):
```go
StyleFunc(func(row, col int) lipgloss.Style {
    if row == table.HeaderRow {
        return headerStyle.Bold(true).Foreground(colors.Primary)
    }
    if row%2 == 0 {
        return evenStyle.Background(colors.Surface)
    }
    return oddStyle  // No background
})
```

**Column-Specific Colors** (semantic meaning):
```go
// Status column uses semantic colors
if col == statusColumnIndex {
    switch value {
    case "success":
        return baseStyle.Foreground(colors.Success)
    case "error":
        return baseStyle.Foreground(colors.Error)
    }
}
```

### Code Blocks

**Syntax Highlighting** (via Chroma):
```go
import "github.com/alecthomas/chroma/v2/styles"

// Use terminal-appropriate styles
style := styles.Get("monokai")  // High contrast
// OR
style := styles.Get("paraiso-dark")  // Softer, more readable
```

**Border Treatment**:
```go
// Hidden border with colored background
codeStyle := NewStyle().
    Border(lipgloss.HiddenBorder()).
    Background(colors.Surface).
    Padding(1, 2).
    Width(termWidth - 4)
```

### Progress Indicators

**Step Icons** (Unicode symbols):
```go
func getStepIcon(status string) string {
    switch status {
    case "complete":
        return "✓"  // Success color
    case "running":
        return "●"  // Primary color
    case "error":
        return "✗"  // Error color
    default:
        return "○"  // TextMuted color
    }
}
```

**Progress Bar Styling**:
```go
// Use block characters for density
filled := strings.Repeat("█", filledWidth)
empty := strings.Repeat("░", emptyWidth)

bar := lipgloss.NewStyle().
    Foreground(colors.Primary).
    Render(filled + empty)
```

### Chat Messages

**Role-Based Styling**:
```go
// User messages: Left-aligned, subtle border
userStyle := NewStyle().
    Border(lipgloss.RoundedBorder()).
    BorderForeground(colors.Accent1).
    Padding(1, 2).
    MaxWidth(termWidth * 0.8).
    AlignHorizontal(lipgloss.Left)

// Assistant messages: Full-width, primary accent
assistantStyle := NewStyle().
    Border(lipgloss.RoundedBorder(), true, false, true, true).  // No left border
    BorderLeftForeground(colors.Primary).
    BorderForeground(colors.Surface).
    Padding(1, 2).
    MaxWidth(termWidth)

// System messages: Italic, muted, no border
systemStyle := NewStyle().
    Foreground(colors.TextMuted).
    Italic(true).
    Padding(1, 0)
```

---

## 6. Implementation Checklist

### Phase 1: Color Palettes
- [ ] Implement "Sage" theme (minimalist warm)
- [ ] Implement "Obsidian" theme (modern technical)
- [ ] Implement "Zephyr" theme (light calm)
- [ ] Implement "Ember" theme (premium warmth)
- [ ] Use `CompleteAdaptiveColor` for all palette colors
- [ ] Test all themes in 16-color, 256-color, true-color terminals

### Phase 2: Advanced Borders
- [ ] Add `DoubleBorder()` for modal dialogs
- [ ] Add `OuterHalfBlockBorder()` for modern containers
- [ ] Implement asymmetric borders (left-only for quotes)
- [ ] Use per-side border coloring for hierarchy
- [ ] Add textured backgrounds with `WithWhitespaceChars()`

### Phase 3: Typography Hierarchy
- [ ] Define 4 levels of text hierarchy (critical, important, supporting, disabled)
- [ ] Use Bold + Primary for level 1
- [ ] Use Faint + TextMuted for level 3
- [ ] Use Strikethrough + TextDim for level 4
- [ ] Never rely on color alone—combine with weight/style

### Phase 4: Animation System
- [ ] Add Harmonica dependency for spring physics
- [ ] Implement staggered step reveals (100ms delays)
- [ ] Add smooth progress bar interpolation (200ms)
- [ ] Configure spinner FPS based on operation urgency
- [ ] Test all animations stay within 100-500ms range

### Phase 5: Component Refinement
- [ ] Forms: DoubleBorder containers, focused field styling
- [ ] Tables: Alternating row backgrounds, semantic column colors
- [ ] Code: Chroma syntax highlighting, subtle borders
- [ ] Progress: Unicode step icons with semantic colors
- [ ] Chat: Role-based asymmetric borders, width constraints

---

## 7. Testing & Validation

### Visual Testing Checklist
- [ ] View in 16-color terminal (check ANSI fallbacks)
- [ ] View in 256-color terminal (check ANSI256 mapping)
- [ ] View in true-color terminal (check TrueColor rendering)
- [ ] Test light background terminal (adaptive color switch)
- [ ] Test dark background terminal (adaptive color switch)
- [ ] Verify contrast ratios (WCAG AA: 4.5:1 minimum)
- [ ] Check animation frame rates (60 FPS smooth, no stuttering)

### Aesthetic Quality Criteria
- [ ] **Distinctiveness**: Not immediately recognizable as "generic Catppuccin-style TUI"
- [ ] **Cohesion**: All colors relate thematically, not random assortment
- [ ] **Hierarchy**: Clear visual importance levels without ambiguity
- [ ] **Restraint**: Uses 3-4 colors intentionally, not 8+ colors
- [ ] **Motion**: Animations feel responsive (100-300ms), not sluggish
- [ ] **Surprise**: At least 2 unique visual patterns (textured backgrounds, asymmetric borders, etc.)

---

## 8. Anti-Patterns to Avoid

❌ **Generic Modern Developer Theme**
- Catppuccin/Dracula/Nord as the only options
- Purple/pink gradients everywhere
- No cultural or thematic identity

❌ **Color Overload**
- 8+ colors fighting for attention
- Every element has different color
- No visual hierarchy

❌ **Monotone Boredom**
- All text same color/weight
- No use of bold, italic, faint
- Flat, lifeless appearance

❌ **Animation Abuse**
- Everything animates (visual noise)
- Slow animations (> 500ms)
- Linear motion (robotic feel)

❌ **Accessibility Neglect**
- Poor contrast ratios (< 4.5:1)
- Color-only differentiation
- No ANSI/ANSI256 fallbacks

---

## Summary

**Distinctive AgentUI Aesthetics = Intentional Restraint + Strategic Flourish**

- **4 new distinctive themes** beyond Catppuccin/Dracula
- **Advanced Lip Gloss features** (textured backgrounds, asymmetric borders, per-side colors)
- **Typography hierarchy** (bold, faint, italic) over color saturation
- **100-500ms animation timing** with staggered reveals and spring physics
- **Component-specific styling** with semantic meaning and visual consistency

This creates a TUI that feels **designed**, not **generated**.
