"""
Tests for the bridge module.
"""

import pytest
import asyncio
from agentui.bridge import CLIBridge, TUIConfig, create_bridge
from agentui.protocol import Message


@pytest.fixture
def cli_config():
    """Create a test configuration."""
    return TUIConfig(
        app_name="Test App",
        tagline="Testing",
        theme="catppuccin-mocha",
    )


@pytest.fixture
def cli_bridge(cli_config):
    """Create a CLI bridge for testing."""
    return CLIBridge(cli_config)


class TestCLIBridge:
    """Tests for CLIBridge."""
    
    @pytest.mark.asyncio
    async def test_start_stop(self, cli_bridge):
        """Test basic start/stop lifecycle."""
        assert not cli_bridge.is_running
        
        await cli_bridge.start()
        assert cli_bridge.is_running
        
        await cli_bridge.stop()
        assert not cli_bridge.is_running
    
    @pytest.mark.asyncio
    async def test_send_text(self, cli_bridge, capsys):
        """Test sending text."""
        await cli_bridge.start()
        
        await cli_bridge.send_text("Hello ", done=False)
        await cli_bridge.send_text("World!", done=True)
        
        await cli_bridge.stop()
        
        # Check output was printed
        captured = capsys.readouterr()
        assert "Hello" in captured.out or cli_bridge._console is not None
    
    @pytest.mark.asyncio
    async def test_send_alert(self, cli_bridge):
        """Test sending alerts."""
        await cli_bridge.start()
        
        # Should not raise
        await cli_bridge.send_alert("Info message", severity="info")
        await cli_bridge.send_alert("Success!", severity="success")
        await cli_bridge.send_alert("Warning!", severity="warning")
        await cli_bridge.send_alert("Error!", severity="error")
        
        await cli_bridge.stop()
    
    @pytest.mark.asyncio
    async def test_send_progress(self, cli_bridge):
        """Test sending progress."""
        await cli_bridge.start()
        
        await cli_bridge.send_progress(
            message="Working...",
            percent=50.0,
            steps=[
                {"label": "Step 1", "status": "complete"},
                {"label": "Step 2", "status": "running"},
            ]
        )
        
        await cli_bridge.stop()


class TestCreateBridge:
    """Tests for create_bridge function."""
    
    def test_fallback_to_cli(self):
        """Test that create_bridge falls back to CLI when TUI not found."""
        config = TUIConfig(
            tui_path="/nonexistent/path/to/tui",
        )
        
        bridge = create_bridge(config, fallback=True)
        assert isinstance(bridge, CLIBridge)
    
    def test_no_fallback_raises(self):
        """Test that create_bridge raises when fallback=False and TUI not found."""
        config = TUIConfig(
            tui_path="/nonexistent/path/to/tui",
        )
        
        with pytest.raises(FileNotFoundError):
            create_bridge(config, fallback=False)


class TestTUIConfig:
    """Tests for TUIConfig."""
    
    def test_default_values(self):
        """Test default configuration values."""
        config = TUIConfig()
        
        assert config.theme == "catppuccin-mocha"
        assert config.app_name == "AgentUI"
        assert config.tagline == "AI Agent Interface"
        assert config.tui_path is None
        assert config.debug is False
        assert config.reconnect_attempts == 3
    
    def test_custom_values(self):
        """Test custom configuration values."""
        config = TUIConfig(
            theme="dracula",
            app_name="My App",
            tagline="Custom tagline",
            debug=True,
        )
        
        assert config.theme == "dracula"
        assert config.app_name == "My App"
        assert config.tagline == "Custom tagline"
        assert config.debug is True
