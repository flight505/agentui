# AgentUI Animation System

AgentUI uses **Harmonica** spring physics for smooth, natural animations that match the Charm aesthetic.

---

## Overview

The animation system provides:
- **Spring-based motion** (no linear easing)
- **60 FPS animation loops** for fluid motion
- **Automatic settling** (stops when motion completes)
- **Three timing presets** (Fast, Default, Slow)
- **Position and opacity springs** for modals/forms

---

## Architecture

### Core Components

```
internal/ui/animations/
├── spring.go          # Spring physics implementation
```

### Integration Points

```
internal/app/app.go    # Bubbletea model with animation state
├── modalOpacity       # OpacitySpring for fade effects
├── modalPosition      # PositionSpring for slide effects
└── animating bool     # Track if any animation is active
```

---

## Spring Physics

### What is a Spring?

Springs create natural motion based on physics. Unlike linear easing (start slow, move fast, end slow), springs:
- **Overshoot** slightly (feels responsive)
- **Settle smoothly** (no abrupt stops)
- **Adapt** to changing targets mid-motion

### Spring Parameters

```go
type SpringConfig struct {
    FPS       int     // Frames per second (60 recommended)
    Stiffness float64 // How "tight" the spring is (1-20)
    Damping   float64 // How much the spring resists motion (0.05-1.0)
}
```

**Stiffness**: Higher = faster, snappier motion
**Damping**: Higher = less overshoot, more resistance

---

## Timing Presets

### Fast (100ms) - Micro-interactions

```go
config := animations.FastSpringConfig()
// Stiffness: 12.0
// Damping: 0.25
```

**Use for**:
- Button clicks
- Toggle switches
- Hover effects
- Checkbox animations

### Default (200-300ms) - Charm Standard

```go
config := animations.DefaultSpringConfig()
// Stiffness: 7.0
// Damping: 0.15
```

**Use for**:
- Modal fade-in/out
- Form transitions
- State changes
- Component reveals

**This is the Charm aesthetic standard**: smooth, responsive, not too fast.

### Slow (500ms) - Deliberate Transitions

```go
config := animations.SlowSpringConfig()
// Stiffness: 4.0
// Damping: 0.1
```

**Use for**:
- Page transitions
- Large layout changes
- Multi-element choreography
- Attention-grabbing effects

---

## Animation Types

### 1. Opacity Spring (Fade Effects)

```go
opacity := animations.NewOpacitySpring(animations.DefaultSpringConfig())

// Fade in (0.0 → 1.0)
opacity.FadeIn()

// Fade out (current → 0.0)
opacity.FadeOut()

// Set specific opacity
opacity.SetOpacity(0.5)

// In your Update loop:
if opacity.Update() {
    // Still animating, schedule next frame
    cmds = append(cmds, animations.TickCmd())
}

// Get current value (0.0 - 1.0)
alpha := opacity.Opacity()
```

### 2. Position Spring (Movement)

```go
position := animations.NewPositionSpring(animations.DefaultSpringConfig())

// Set target position
position.SetTarget(100, 50)  // x=100, y=50

// Jump immediately (no animation)
position.SetCurrent(0, 0)

// In your Update loop:
if position.Update() {
    cmds = append(cmds, animations.TickCmd())
}

// Get current position
x, y := position.Position()  // Returns (int, int)
```

### 3. Generic Spring (Custom Values)

```go
spring := animations.NewSpring(animations.DefaultSpringConfig())

// Animate to target value
spring.SetTarget(100.0)

// In your Update loop:
if spring.Update() {
    cmds = append(cmds, animations.TickCmd())
}

// Get current value
value := spring.Value()  // float64
```

---

## Integration with Bubbletea

### 1. Add Spring to Model

```go
type Model struct {
    // ... other fields

    // Animation springs
    modalOpacity  *animations.OpacitySpring
    modalPosition *animations.PositionSpring
    animating     bool
}
```

### 2. Initialize in Constructor

```go
func NewModel() Model {
    config := animations.DefaultSpringConfig()

    return Model{
        modalOpacity:  animations.NewOpacitySpring(config),
        modalPosition: animations.NewPositionSpring(config),
        animating:     false,
    }
}
```

### 3. Handle Animation Ticks

```go
func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
    switch msg := msg.(type) {

    case animations.TickMsg:
        // Update all springs
        opacityActive := m.modalOpacity.Update()
        positionActive := m.modalPosition.Update()

        // Continue if any spring is still moving
        if opacityActive || positionActive {
            m.animating = true
            return m, animations.TickCmd()
        } else {
            m.animating = false
        }

    // ... other message handlers
    }

    return m, nil
}
```

### 4. Trigger Animations

```go
// When showing a modal/form
case ShowModal:
    m.modalOpacity.FadeIn()
    m.modalPosition.SetTarget(0, float64(m.height/6))
    return m, animations.TickCmd()  // Start animation loop

// When hiding a modal
case HideModal:
    m.modalOpacity.FadeOut()
    m.modalPosition.SetTarget(0, -100)  // Slide up
    return m, animations.TickCmd()
```

### 5. Use in View

```go
func (m Model) View() string {
    // Apply opacity to modal
    opacity := m.modalOpacity.Opacity()

    // Apply position to modal
    x, y := m.modalPosition.Position()

    // Render modal with animations
    modal := lipgloss.NewStyle().
        MarginTop(y).
        MarginLeft(x).
        // Note: lipgloss doesn't support opacity directly,
        // but you can use it to control visibility thresholds
        Render(modalContent)

    if opacity < 0.01 {
        return ""  // Don't render if essentially invisible
    }

    return modal
}
```

---

## Real-World Example

### Animated Form Appearance

```go
// In Update handler
case protocol.TypeForm:
    // Create form component
    m.currentForm = components.NewForm(&payload)
    m.state = StateForm

    // Animate in
    m.modalOpacity.SetCurrent(0.0)  // Start invisible
    m.modalOpacity.FadeIn()          // Animate to visible

    // Slide down from above
    m.modalPosition.SetCurrent(0, -50)        // Start above
    m.modalPosition.SetTarget(0, m.height/6)  // Move to center

    return m, animations.TickCmd()  // Start animation

// In View
func (m Model) renderForm() string {
    if m.currentForm == nil {
        return ""
    }

    opacity := m.modalOpacity.Opacity()
    _, y := m.modalPosition.Position()

    // Don't render if nearly invisible
    if opacity < 0.01 {
        return ""
    }

    // Apply position
    formStyle := lipgloss.NewStyle().
        MarginTop(y).
        Align(lipgloss.Center)

    return formStyle.Render(m.currentForm.View())
}
```

---

## Timing Guidelines

| Duration | Use Case | Config |
|----------|----------|--------|
| **100ms** | Button feedback, toggles | `FastSpringConfig()` |
| **200-300ms** | Modals, forms, state transitions | `DefaultSpringConfig()` ✨ |
| **500ms+** | Page transitions, complex choreography | `SlowSpringConfig()` |

**Charm Aesthetic**: Default (200-300ms) is the sweet spot for responsive yet smooth UX.

---

## Performance Considerations

### Automatic Settling

Springs automatically stop when motion completes:

```go
func isSettled(current, velocity, target, threshold float64) bool {
    positionDelta := abs(current - target)
    absVelocity := abs(velocity)

    // Stop if position is close and velocity is low
    return positionDelta < threshold && absVelocity < threshold
}
```

**Default threshold**: 0.5 units (configurable)

### 60 FPS Animation Loop

```go
func TickCmd() tea.Cmd {
    return tea.Tick(time.Second/60, func(t time.Time) tea.Msg {
        return TickMsg(t)
    })
}
```

- **Frame time**: ~16.67ms (1000ms / 60)
- **CPU usage**: Only active while animating
- **Auto-stops**: No wasted cycles when settled

---

## Best Practices

### 1. Use Appropriate Timing

```go
// ❌ Too fast (jarring)
config := SpringConfig{FPS: 60, Stiffness: 20.0, Damping: 0.5}

// ✅ Charm aesthetic (smooth)
config := animations.DefaultSpringConfig()

// ❌ Too slow (sluggish)
config := SpringConfig{FPS: 60, Stiffness: 2.0, Damping: 0.05}
```

### 2. Coordinate Related Animations

```go
// ✅ Fade and slide together
m.modalOpacity.FadeIn()
m.modalPosition.SetTarget(0, centerY)

// ❌ Don't start separately with delays
// (springs handle timing naturally)
```

### 3. Respect User Preferences

Consider adding a flag to disable animations:

```go
if !m.animationsEnabled {
    // Jump immediately
    m.modalOpacity.SetCurrent(1.0)
    m.modalPosition.SetCurrent(0, centerY)
    return m, nil
}

// Otherwise, animate
m.modalOpacity.FadeIn()
m.modalPosition.SetTarget(0, centerY)
return m, animations.TickCmd()
```

### 4. Batch Animation Starts

```go
// ✅ Start all animations at once
m.modalOpacity.FadeIn()
m.modalPosition.SetTarget(x, y)
m.contentOpacity.FadeIn()
return m, animations.TickCmd()  // One tick starts all

// ❌ Don't chain separate ticks
```

---

## Debugging Animations

### Log Spring State

```go
case animations.TickMsg:
    fmt.Fprintf(os.Stderr, "Opacity: %.2f, Position: %d,%d\n",
        m.modalOpacity.Opacity(),
        m.modalPosition.Position())

    m.modalOpacity.Update()
    // ...
```

### Visualize Spring Motion

Test springs in isolation:

```go
spring := animations.NewSpring(animations.DefaultSpringConfig())
spring.SetTarget(100.0)

for i := 0; i < 60; i++ {  // 1 second at 60fps
    spring.Update()
    fmt.Printf("Frame %d: %.2f\n", i, spring.Value())
}
```

---

## Future Enhancements

Potential additions to the animation system:

- **Staggered animations**: Delay start of multiple springs
- **Easing curves**: Pre-defined spring configs (elastic, bounce)
- **Animation sequences**: Chain animations programmatically
- **Gesture-based springs**: Drag to dismiss with velocity
- **Progress bar smoothing**: Animate progress changes

---

## References

- **Harmonica**: https://github.com/charmbracelet/harmonica
- **Spring Physics**: https://en.wikipedia.org/wiki/Hooke%27s_law
- **Charm Aesthetic**: Smooth, responsive motion (200-300ms default)

---

**Remember**: Great animations are *felt, not seen*. The best animations enhance UX without being distracting. Keep it smooth, keep it Charm. ✨
