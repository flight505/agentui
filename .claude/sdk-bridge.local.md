---
# v1.4.0 Settings
enabled: true
model: claude-sonnet-4-5-20250929
max_sessions: 20
reserve_sessions: 2
progress_stall_threshold: 3
auto_handoff_after_plan: false
log_level: INFO
webhook_url:

# v2.0 Settings (Phases 1-3)
enable_v2_features: true
enable_semantic_memory: true
enable_adaptive_models: true
enable_approval_nodes: true
max_inner_loops: 5

# v2.0 Phase 3: Parallel Execution
enable_parallel_execution: true
max_parallel_workers: 3
---

# SDK Bridge Configuration

This project is configured for SDK bridge workflows.

## v1.4.0 Settings

- **model**: Claude model for SDK sessions
  - `claude-sonnet-4-5-20250929` (default, fast and capable)
  - `claude-opus-4-5-20251101` (most capable, slower and more expensive)

- **max_sessions**: Total sessions before giving up (default: 20)

- **reserve_sessions**: Keep N sessions for manual recovery (default: 2)

- **progress_stall_threshold**: Stop if no progress for N sessions (default: 3)

- **auto_handoff_after_plan**: Automatically handoff after /plan creates feature_list.json (default: false)

- **log_level**: Logging verbosity (DEBUG, INFO, WARNING, ERROR)

- **webhook_url**: Optional webhook for notifications

## Advanced Features

- **enable_v2_features**: Enable all advanced features (default: true)
  - Hybrid loops (same-session + multi-session)
  - Semantic memory (cross-project learning)
  - Adaptive model selection (Sonnet/Opus routing)
  - Approval workflow for high-risk changes

- **enable_semantic_memory**: Cross-project learning (default: true)
  - Learns from past implementations across projects
  - Suggests solutions based on similar features

- **enable_adaptive_models**: Smart model selection (default: true)
  - Routes complex/high-risk features to Opus
  - Uses Sonnet for standard features
  - Escalates to Opus on retry failures

- **enable_approval_nodes**: Human-in-the-loop approvals (default: true)
  - Pauses for high-risk operations
  - Presents alternatives and impact analysis
  - Non-blocking (other features continue)

- **max_inner_loops**: Same-session retries before starting new session (default: 5)
  - Self-healing pattern for quick fixes
  - Reduces API costs and time

- **enable_parallel_execution**: Enable parallel feature implementation (default: false)
  - Requires running `/sdk-bridge:plan` first to analyze dependencies
  - Launches multiple workers for independent features
  - Git-isolated branches per worker
  - Significant speedup for projects with many independent features
  - Enable with: `/sdk-bridge:enable-parallel`

- **max_parallel_workers**: Maximum concurrent workers (default: 3)
  - More workers = faster completion for independent features
  - Each worker uses API tokens and git branches
  - Recommended: 2-4 workers depending on feature independence

## Usage

After initialization:

1. Create feature_list.json (use `/plan` or manually)
2. (Optional) Run `/sdk-bridge:plan` to analyze dependencies for parallel execution
3. (Optional) Run `/sdk-bridge:enable-parallel` if plan recommends it
4. Run `/sdk-bridge:handoff` to start autonomous work
5. Monitor with `/sdk-bridge:status` or `/sdk-bridge:observe` (for parallel)
6. Resume with `/sdk-bridge:resume` when complete

## Parallel Execution Workflow

If you have many independent features:

1. `/sdk-bridge:plan` - Analyzes dependencies, creates execution plan
2. Review the dependency graph and estimated speedup
3. `/sdk-bridge:enable-parallel` - Enables parallel mode if beneficial
4. `/sdk-bridge:handoff` - Launches multiple workers automatically
5. `/sdk-bridge:observe` - Monitor all workers in real-time

## Configuration

After initialization:

1. Create feature_list.json (use `/plan` or manually)
2. Run `/sdk-bridge:handoff` to start autonomous work
3. Monitor with `/sdk-bridge:status`
4. Resume with `/sdk-bridge:resume` when complete

## Configuration

You can edit this file to customize settings for this project.
