"""
AgentUI Testing Framework

Provides utilities for testing AgentUI components in isolation,
similar to how Storybook tests web components.

Main classes:
    ComponentTester: Test UI primitives (UICode, UITable, etc.) in isolation
    ANSISnapshotter: Snapshot testing for terminal output
    ANSIAsserter: Assertions for ANSI codes and styling
"""

from .component_tester import ComponentTester
from .snapshot import ANSISnapshotter
from .assertions import ANSIAsserter

__all__ = [
    "ComponentTester",
    "ANSISnapshotter",
    "ANSIAsserter",
]
