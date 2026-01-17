# AgentUI Implementation Plans

> **For Claude Code:** Read THIS file first. Only follow the ACTIVE plan.

## Active Plan

**`2026-01-17-charm-aesthetic-implementation.md`** - Current implementation plan

## Archived Plans

Files prefixed with `_archived_` are **SUPERSEDED** and should NOT be followed.

## Key Direction

**DO:**
- Focus on Charm aesthetic (pink/purple/teal from Charmbracelet)
- Use simple `lipgloss.Color` for most cases
- Use `lipgloss.AdaptiveColor` for light/dark auto-detection
- Make themes extensible via JSON loader
- Get CharmDark/CharmLight working perfectly first

**DO NOT:**
- Implement Sage, Obsidian, Zephyr, Ember themes (archived direction)
- Bundle many community themes by default
- Use `CompleteAdaptiveColor` everywhere (overkill for most cases)
- Follow any plan in `_archived_*` files
