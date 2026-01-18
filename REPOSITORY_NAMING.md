# Repository Naming

## Current Situation

**GitHub Repository Name:** `agent-ui-framework`
**Project Name:** `AgentUI` (pronounced "Agent TUI")
**Package Name:** `agentui`

## Recommended Change

The repository should be renamed to match the project name for consistency:

**From:** `https://github.com/flight505/agent-ui-framework`
**To:** `https://github.com/flight505/agentui`

## Why Rename?

1. **Consistency** — Package is `agentui`, project is `AgentUI`, but repo is `agent-ui-framework`
2. **Clarity** — "AgentUI" (Agent TUI) clearly indicates it's a Terminal UI framework
3. **Branding** — All documentation refers to "AgentUI", not "Agent UI Framework"
4. **Simplicity** — Shorter, cleaner URL

## How to Rename on GitHub

1. Go to: `https://github.com/flight505/agent-ui-framework/settings`
2. Scroll to "Repository name"
3. Change from: `agent-ui-framework`
4. Change to: `agentui`
5. Click "Rename"

**GitHub automatically sets up redirects**, so old links won't break immediately.

## After Renaming

Update local repository remote:

```bash
# Check current remote
git remote -v

# Update remote URL
git remote set-url origin https://github.com/flight505/agentui.git

# Verify
git remote -v
```

## Documentation to Update

After renaming, update these references:

- ✅ `README.md` — Already uses correct `agentui` name
- ✅ `CLAUDE.md` — Already references project as `AgentUI`
- ✅ `pyproject.toml` — Package name already `agentui`
- ⚠️ Any external links or bookmarks
- ⚠️ CI/CD configurations (if any)
- ⚠️ npm/pip package references

## Current README

The README already uses the correct repository name:

```bash
git clone https://github.com/flight505/agentui
```

**Note:** This URL currently redirects to `agent-ui-framework`, but will work directly after rename.

## Impact

**Minimal impact:**
- GitHub provides automatic redirects
- Local git remotes continue working
- Can update remotes at leisure

**Best practice:**
- Rename sooner rather than later
- Less external documentation to update
- Cleaner before project gains wider adoption

## Pronunciation

**AgentUI** = **"Agent TUI"** (Terminal User Interface)

Not "Agent U-I" — the "UI" should be pronounced as one syllable: "TUI" (T-U-I).

This emphasizes that it's a **terminal** interface framework, not a generic UI framework.
