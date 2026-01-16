#!/usr/bin/env python3
"""
End-to-End Test - Tests Python ↔ Go communication.

This script tests the full communication pipeline:
1. Python sends UI commands to Go TUI
2. Go TUI renders them
3. Go TUI sends user events back to Python

Run:
    # First build the TUI
    make build-tui
    
    # Then run this test
    python examples/e2e_test.py
"""

import asyncio
import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from agentui.bridge import TUIBridge, TUIConfig, BridgeError
from agentui.protocol import MessageType

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def test_basic_communication():
    """Test basic message sending."""
    logger.info("=== Test: Basic Communication ===")
    
    config = TUIConfig(
        app_name="E2E Test",
        tagline="Testing communication",
        theme="catppuccin-mocha",
        debug=True,
    )
    
    bridge = TUIBridge(config)
    
    try:
        await bridge.start()
        logger.info("✓ Bridge started")
        
        # Send some messages
        await bridge.send_status("Testing connection...")
        logger.info("✓ Sent status message")
        
        await asyncio.sleep(0.5)
        
        # Send text
        await bridge.send_text("Hello from Python! ", done=False)
        await bridge.send_text("This is streaming text.", done=True)
        logger.info("✓ Sent text messages")
        
        await asyncio.sleep(0.5)
        
        # Send markdown
        await bridge.send_markdown("""
## Test Markdown

This is a **bold** test with:
- Bullet 1
- Bullet 2
- Bullet 3

```python
print("Hello, World!")
```
""", title="Markdown Test")
        logger.info("✓ Sent markdown")
        
        await asyncio.sleep(0.5)
        
        # Send table
        await bridge.send_table(
            columns=["Name", "Value", "Status"],
            rows=[
                ["Test 1", "100", "✓"],
                ["Test 2", "200", "✓"],
                ["Test 3", "300", "✓"],
            ],
            title="Test Table",
            footer="All tests passed!"
        )
        logger.info("✓ Sent table")
        
        await asyncio.sleep(0.5)
        
        # Send code
        await bridge.send_code(
            code='''async def main():
    bridge = TUIBridge()
    await bridge.start()
    await bridge.send_text("Hello!")
    await bridge.stop()''',
            language="python",
            title="example.py"
        )
        logger.info("✓ Sent code block")
        
        await asyncio.sleep(0.5)
        
        # Send progress
        await bridge.send_progress(
            message="Running tests...",
            percent=75,
            steps=[
                {"label": "Initialize", "status": "complete"},
                {"label": "Send messages", "status": "complete"},
                {"label": "Test forms", "status": "running"},
                {"label": "Cleanup", "status": "pending"},
            ]
        )
        logger.info("✓ Sent progress")
        
        await asyncio.sleep(0.5)
        
        # Send alerts
        await bridge.send_alert("Information message", severity="info")
        await bridge.send_alert("Success message", severity="success")
        await bridge.send_alert("Warning message", severity="warning")
        await bridge.send_alert("Error message", severity="error")
        logger.info("✓ Sent alerts")
        
        await asyncio.sleep(1)
        
        # Done
        await bridge.send_done("Test completed successfully!")
        logger.info("✓ Sent done")
        
        await asyncio.sleep(2)
        
    except BridgeError as e:
        logger.error(f"✗ Bridge error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        return False
    finally:
        await bridge.stop()
        logger.info("✓ Bridge stopped")
    
    return True


async def test_interactive_forms():
    """Test form interactions."""
    logger.info("\n=== Test: Interactive Forms ===")
    
    config = TUIConfig(
        app_name="Form Test",
        tagline="Testing forms",
        debug=True,
    )
    
    bridge = TUIBridge(config)
    
    try:
        await bridge.start()
        
        await bridge.send_text("Testing form interaction...", done=True)
        await asyncio.sleep(0.5)
        
        # Request form
        logger.info("Requesting form...")
        result = await bridge.request_form(
            fields=[
                {"name": "name", "label": "Your Name", "type": "text", "required": True},
                {"name": "language", "label": "Favorite Language", "type": "select", 
                 "options": ["Python", "Go", "Rust", "TypeScript"]},
                {"name": "agree", "label": "I agree to the terms", "type": "checkbox"},
            ],
            title="Test Form",
            description="Please fill in this form to test the communication.",
        )
        
        if result:
            logger.info(f"✓ Form submitted: {result}")
            await bridge.send_alert(f"Received: {result}", severity="success")
        else:
            logger.info("✓ Form cancelled")
            await bridge.send_alert("Form was cancelled", severity="info")
        
        await asyncio.sleep(1)
        
        # Test confirmation
        logger.info("Requesting confirmation...")
        confirmed = await bridge.request_confirm(
            "Do you want to continue?",
            title="Confirm Action",
            destructive=False,
        )
        logger.info(f"✓ Confirmed: {confirmed}")
        
        await asyncio.sleep(0.5)
        
        # Test selection
        logger.info("Requesting selection...")
        selected = await bridge.request_select(
            "Choose your theme:",
            ["Catppuccin Mocha", "Dracula", "Nord", "Tokyo Night"],
            default="Catppuccin Mocha",
        )
        logger.info(f"✓ Selected: {selected}")
        
        await asyncio.sleep(1)
        
        await bridge.send_done("Form tests completed!")
        await asyncio.sleep(2)
        
    except BridgeError as e:
        logger.error(f"✗ Bridge error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await bridge.stop()
    
    return True


async def test_chat_loop():
    """Test interactive chat loop."""
    logger.info("\n=== Test: Chat Loop ===")
    
    config = TUIConfig(
        app_name="Chat Test",
        tagline="Testing chat interaction",
        debug=True,
    )
    
    bridge = TUIBridge(config)
    
    try:
        await bridge.start()
        
        await bridge.send_text(
            "Welcome to the chat test! Type messages and I'll echo them back. "
            "Type 'quit' to exit.",
            done=True
        )
        await bridge.send_status("Ready for input")
        
        message_count = 0
        max_messages = 5
        
        async for event in bridge.events():
            logger.info(f"Received event: {event.type}")
            
            if event.type == MessageType.INPUT.value:
                content = event.payload.get("content", "")
                message_count += 1
                
                if content.lower() == "quit":
                    await bridge.send_text("Goodbye!", done=True)
                    break
                
                # Echo back
                await bridge.send_spinner("Processing...")
                await asyncio.sleep(0.5)
                
                response = f"You said: '{content}' (message #{message_count})"
                await bridge.send_text(response, done=True)
                
                await bridge.send_status(f"Messages: {message_count}/{max_messages}")
                
                if message_count >= max_messages:
                    await bridge.send_alert(
                        f"Reached {max_messages} messages, ending test",
                        severity="info"
                    )
                    break
            
            elif event.type == MessageType.QUIT.value:
                logger.info("User requested quit")
                break
        
        await bridge.send_done(f"Chat test completed with {message_count} messages")
        await asyncio.sleep(1)
        
    except BridgeError as e:
        logger.error(f"✗ Bridge error: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await bridge.stop()
    
    return True


async def main():
    """Run all tests."""
    print("=" * 60)
    print("AgentUI End-to-End Tests")
    print("=" * 60)
    print()
    print("These tests require the Go TUI to be built:")
    print("  make build-tui")
    print()
    print("Tests will run interactively - follow the prompts.")
    print("=" * 60)
    print()
    
    # Check if TUI binary exists
    tui_path = Path(__file__).parent.parent / "bin" / "agentui-tui"
    if not tui_path.exists():
        print(f"ERROR: TUI binary not found at {tui_path}")
        print("Please run 'make build-tui' first.")
        return 1
    
    tests = [
        ("Basic Communication", test_basic_communication),
        ("Interactive Forms", test_interactive_forms),
        ("Chat Loop", test_chat_loop),
    ]
    
    results = []
    
    for name, test_func in tests:
        print(f"\n{'=' * 40}")
        print(f"Running: {name}")
        print("=" * 40)
        
        try:
            result = await test_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\nTest interrupted by user")
            results.append((name, False))
            break
        except Exception as e:
            print(f"\nTest failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n  Total: {passed}/{total} passed")
    
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
