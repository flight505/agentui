#!/usr/bin/env python3
"""
Generative UI Demo

Demonstrates all the UI primitives that agents can generate.
The LLM can return these primitives from tools to create rich, interactive UIs.

Run:
    python examples/generative_ui_demo.py
"""

import asyncio
from agentui import (
    AgentApp,
    UIForm,
    UIFormField,
    UIProgress,
    UIProgressStep,
    UITable,
    UICode,
    UIConfirm,
    UISelect,
)
from agentui.primitives import text_field, select_field, checkbox_field


app = AgentApp(
    name="ui-demo",
    provider="claude",
    system_prompt="""You are a demo assistant that showcases beautiful UI elements.

You have several tools that return rich UI elements:
- show_project_form: Show a form to configure a project
- show_progress: Show a progress indicator with steps
- show_data_table: Show a data table
- show_code_example: Show a code snippet
- confirm_action: Ask for confirmation
- select_option: Show a selection menu

Use these tools when the user asks to see demos of the UI elements.
Be creative and show off the beautiful interfaces!""",
    theme="catppuccin-mocha",
    tagline="UI Primitives Demo",
)


@app.ui_tool(
    name="show_project_form",
    description="Show a beautiful form to configure a new project",
    parameters={
        "type": "object",
        "properties": {
            "project_type": {
                "type": "string",
                "description": "Type of project (web, api, cli)"
            }
        }
    }
)
def show_project_form(project_type: str = "web") -> UIForm:
    """Return a form for project configuration."""
    tech_options = {
        "web": ["React", "Vue", "Svelte", "HTMX"],
        "api": ["FastAPI", "Express", "Go Gin", "Rails"],
        "cli": ["Python", "Go", "Rust", "Node"],
    }.get(project_type, ["Python", "Go", "Node"])
    
    return UIForm(
        title=f"Configure {project_type.title()} Project",
        description="Fill in the details for your new project.",
        fields=[
            text_field("name", "Project Name", required=True, placeholder="my-awesome-project"),
            select_field("framework", "Framework", tech_options, required=True),
            select_field("database", "Database", ["PostgreSQL", "MySQL", "SQLite", "MongoDB"]),
            checkbox_field("docker", "Include Docker setup", default=True),
            checkbox_field("ci", "Add CI/CD pipeline", default=True),
        ],
        submit_label="Create Project",
        cancel_label="Cancel",
    )


@app.ui_tool(
    name="show_progress",
    description="Show a multi-step progress indicator",
    parameters={
        "type": "object",
        "properties": {
            "task": {
                "type": "string",
                "description": "What task to show progress for"
            }
        }
    }
)
def show_progress(task: str = "deployment") -> UIProgress:
    """Return a progress indicator."""
    steps_by_task = {
        "deployment": [
            UIProgressStep("Build", "complete", "Compiled in 2.3s"),
            UIProgressStep("Test", "complete", "42 tests passed"),
            UIProgressStep("Deploy", "running", "Uploading to production..."),
            UIProgressStep("Verify", "pending"),
        ],
        "research": [
            UIProgressStep("Market Analysis", "complete"),
            UIProgressStep("Competitor Review", "complete"),
            UIProgressStep("Architecture Design", "running"),
            UIProgressStep("Cost Estimation", "pending"),
            UIProgressStep("Sprint Planning", "pending"),
        ],
    }
    
    steps = steps_by_task.get(task, [
        UIProgressStep("Step 1", "complete"),
        UIProgressStep("Step 2", "running"),
        UIProgressStep("Step 3", "pending"),
    ])
    
    return UIProgress(
        message=f"Running {task}...",
        percent=60.0,
        steps=steps,
    )


@app.ui_tool(
    name="show_data_table",
    description="Show a formatted data table",
    parameters={
        "type": "object",
        "properties": {
            "data_type": {
                "type": "string",
                "description": "Type of data to show (costs, metrics, comparison)"
            }
        }
    }
)
def show_data_table(data_type: str = "costs") -> UITable:
    """Return a data table."""
    tables = {
        "costs": UITable(
            title="Monthly Cloud Costs",
            columns=["Service", "Tier", "Monthly Cost", "Annual"],
            rows=[
                ["EC2", "t3.medium", "$30.00", "$360"],
                ["RDS", "db.t3.small", "$25.00", "$300"],
                ["S3", "Standard", "$5.00", "$60"],
                ["Lambda", "1M requests", "$2.00", "$24"],
                ["CloudFront", "100GB", "$8.50", "$102"],
            ],
            footer="Total: $70.50/month · $846/year",
        ),
        "metrics": UITable(
            title="Application Metrics",
            columns=["Metric", "Current", "Target", "Status"],
            rows=[
                ["Response Time", "45ms", "<100ms", "✓"],
                ["Error Rate", "0.1%", "<1%", "✓"],
                ["Uptime", "99.9%", "99.5%", "✓"],
                ["Throughput", "1.2k/s", "1k/s", "✓"],
            ],
        ),
        "comparison": UITable(
            title="Framework Comparison",
            columns=["Feature", "React", "Vue", "Svelte"],
            rows=[
                ["Learning Curve", "Medium", "Easy", "Easy"],
                ["Performance", "Good", "Good", "Excellent"],
                ["Bundle Size", "Large", "Medium", "Small"],
                ["Ecosystem", "Huge", "Large", "Growing"],
                ["TypeScript", "Excellent", "Good", "Good"],
            ],
        ),
    }
    
    return tables.get(data_type, tables["costs"])


@app.ui_tool(
    name="show_code_example",
    description="Show a syntax-highlighted code example",
    parameters={
        "type": "object",
        "properties": {
            "language": {
                "type": "string",
                "description": "Programming language"
            }
        }
    }
)
def show_code_example(language: str = "python") -> UICode:
    """Return a code block."""
    examples = {
        "python": UICode(
            title="FastAPI Example",
            language="python",
            code='''from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}''',
        ),
        "go": UICode(
            title="Go HTTP Server",
            language="go",
            code='''package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, World!")
    })
    
    http.ListenAndServe(":8080", nil)
}''',
        ),
        "typescript": UICode(
            title="React Component",
            language="typescript",
            code='''interface Props {
  name: string;
  count: number;
}

export function Counter({ name, count }: Props) {
  const [value, setValue] = useState(count);
  
  return (
    <div className="counter">
      <h2>{name}</h2>
      <button onClick={() => setValue(v => v + 1)}>
        Count: {value}
      </button>
    </div>
  );
}''',
        ),
    }
    
    return examples.get(language, examples["python"])


@app.ui_tool(
    name="confirm_action",
    description="Ask for confirmation before an action",
    parameters={
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to confirm"
            },
            "destructive": {
                "type": "boolean",
                "description": "Whether the action is destructive"
            }
        }
    }
)
def confirm_action(action: str = "deploy", destructive: bool = False) -> UIConfirm:
    """Return a confirmation dialog."""
    messages = {
        "deploy": "Deploy to production? This will affect live users.",
        "delete": "Delete this project? This action cannot be undone.",
        "reset": "Reset all settings to defaults?",
    }
    
    return UIConfirm(
        title="Confirm Action",
        message=messages.get(action, f"Proceed with {action}?"),
        confirm_label="Yes, proceed",
        cancel_label="Cancel",
        destructive=destructive or action == "delete",
    )


@app.ui_tool(
    name="select_option",
    description="Show a selection menu",
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Category of options"
            }
        }
    }
)
def select_option(category: str = "theme") -> UISelect:
    """Return a selection menu."""
    options = {
        "theme": UISelect(
            label="Select Theme",
            options=[
                "Catppuccin Mocha",
                "Catppuccin Latte",
                "Dracula",
                "Nord",
                "Tokyo Night",
            ],
            default="Catppuccin Mocha",
        ),
        "model": UISelect(
            label="Select AI Model",
            options=[
                "Claude Opus 4.5",
                "Claude Sonnet 4.5",
                "GPT-4o",
                "Gemini Pro",
            ],
        ),
        "provider": UISelect(
            label="Select Cloud Provider",
            options=["AWS", "Google Cloud", "Azure", "DigitalOcean"],
        ),
    }
    
    return options.get(category, options["theme"])


async def main():
    """Run the demo."""
    print("🎨 AgentUI - Generative UI Demo")
    print()
    print("Ask me to show you different UI elements:")
    print("  • 'Show me a project form'")
    print("  • 'Show progress for deployment'")
    print("  • 'Show cloud cost table'")
    print("  • 'Show Python code example'")
    print("  • 'Ask me to confirm deletion'")
    print()
    
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
