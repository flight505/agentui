# Creating Skills

Skills extend agent capabilities with custom tools. Each skill MUST have both YAML definitions and Python implementations.

## Requirements

Every skill requires:
1. **skill.yaml** - Tool definitions and metadata
2. **skill.py** - Python implementations for all tools
3. **SKILL.md** (optional) - Instructions for the LLM

**IMPORTANT:** Skills without skill.py will raise `ValueError` at load time. This ensures production readiness.

## Directory Structure

```
my_skill/
├── SKILL.md      # Optional: LLM instructions
├── skill.yaml    # Required: Tool definitions
└── skill.py      # Required: Tool implementations
```

## Minimal Example

### skill.yaml
```yaml
name: greeter
description: Greeting tools
version: 1.0.0

tools:
  - name: greet
    description: Greet a user by name
    parameters:
      type: object
      properties:
        name:
          type: string
          description: User's name
      required:
        - name
```

### skill.py
```python
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"
```

### SKILL.md (optional)
```markdown
# Greeter Skill

Use the `greet` tool to welcome users.

Be friendly and personable in your greetings.
```

## Loading Skills

```python
from agentui import AgentApp

app = AgentApp(
    name="My Agent",
    skills=["./skills/greeter"]
)

# Skills are automatically loaded and tools registered
```

## Tool Definition Format

Each tool in skill.yaml must define:

- **name**: Function name in skill.py (must match exactly)
- **description**: What the tool does (shown to LLM)
- **parameters**: JSON Schema for parameters

```yaml
tools:
  - name: calculate_sum
    description: Add two numbers together
    parameters:
      type: object
      properties:
        a:
          type: number
          description: First number
        b:
          type: number
          description: Second number
      required:
        - a
        - b
```

## Python Implementation

Handler functions in skill.py can:

- Accept parameters matching the YAML schema
- Return any JSON-serializable data
- Be async (use `async def`)
- Raise exceptions (caught by framework)

```python
def calculate_sum(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

# Async handlers are supported
async def fetch_data(url: str) -> dict:
    """Fetch data from URL."""
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

## Multiple Tools

Skills can define multiple tools:

```yaml
tools:
  - name: add
    description: Add numbers
    parameters:
      type: object
      properties:
        a: {type: number}
        b: {type: number}

  - name: multiply
    description: Multiply numbers
    parameters:
      type: object
      properties:
        a: {type: number}
        b: {type: number}
```

```python
def add(a: float, b: float) -> float:
    return a + b

def multiply(a: float, b: float) -> float:
    return a * b
```

## Error Handling

If skill.py is missing or incomplete:

```
ValueError: Skill 'greeter' defines tool 'greet' in YAML but has no skill.py
with handler implementation. Create ./skills/greeter/skill.py with a function
named 'greet'
```

If function name doesn't match:

```
ValueError: Tool 'greet' defined in YAML but function not found in skill.py.
Add a function named 'greet' to skill.py
```

If handler is not callable:

```
ValueError: Tool 'greet' in skill.py is not callable. It must be a function.
```

## Advanced: Configuration

Skills can include custom configuration:

```yaml
name: weather
tools:
  - name: get_weather
    description: Get current weather
    parameters:
      type: object
      properties:
        city: {type: string}

config:
  api_key_env: WEATHER_API_KEY
  cache_ttl: 300
  units: celsius
```

Access configuration in skill.py:

```python
# Configuration is NOT automatically injected
# Instead, load it in your app and pass to handlers as needed

from agentui.skills import load_skill

skill = load_skill("./skills/weather")
api_key = skill.config.get("api_key_env")  # "WEATHER_API_KEY"
cache_ttl = skill.config.get("cache_ttl")  # 300
```

## SKILL.md Instructions

The SKILL.md file provides context to the LLM about when and how to use tools:

```markdown
# Weather Skill

Use these tools to help users with weather information.

## Guidelines

1. Always ask for the city if not provided
2. Default to celsius unless user specifies fahrenheit
3. Mention that data may be delayed by a few minutes
4. For forecasts, ask how many days (1-7)

## Response Format

When reporting weather:
- Include temperature, conditions, and humidity
- Add relevant warnings (heat advisories, storms, etc.)
- Be concise but informative
```

## Best Practices

1. **Validation**: Validate inputs in your Python handlers
2. **Error Messages**: Return helpful error information
3. **Type Hints**: Use type hints for better IDE support
4. **Documentation**: Add docstrings to handler functions
5. **Testing**: Test handlers independently before integration

## Example: Weather Skill

See `examples/skills/weather/` for a complete example with:
- Multiple tools (get_weather, get_forecast)
- Parameter validation
- Structured return values
- LLM instructions in SKILL.md

## Troubleshooting

**Problem:** `ValueError: has no skill.py`
- **Solution:** Create skill.py with handler functions

**Problem:** `function not found in skill.py`
- **Solution:** Ensure function name in skill.py matches tool name in YAML exactly

**Problem:** Tool not being called by agent
- **Solution:** Check that description in YAML is clear and specific

**Problem:** Parameters not being passed correctly
- **Solution:** Verify YAML schema matches Python function signature
