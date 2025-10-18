# Source Code - AI Network Assistant

Core implementation of the AI Network Assistant using MCP (Model Context Protocol).

---

## Architecture

```
User ──► agent.py ◄─MCP(stdio)─► server.py ◄─SSH(pyATS)─► Network Devices
         (Gemini)                 (FastMCP)                (Arista cEOS)
```

---

## Files

### `agent.py` - AI Agent
Interactive chat client powered by Google Gemini.

- Loads Gemini API and connects to MCP server
- Converts MCP tools to Gemini function declarations
- Handles user queries and tool execution
- Provides interactive chat loop

**Requires:** `GEMINI_API_KEY` environment variable

### `server.py` - MCP Server
FastMCP server exposing network automation tools via pyATS.

- Loads pyATS testbed from `PYATS_TESTBED_PATH`
- Connects to devices via SSH on-demand
- Validates inputs and cleans output
- Auto-disconnects after operations

**Requires:** `PYATS_TESTBED_PATH` environment variable

---

## MCP Tools

| Tool | Parameters | Description |
|------|------------|-------------|
| `list_devices()` | - | List all devices in testbed |
| `run_show_command()` | device_name, command | Execute show commands (validated) |
| `configure_device()` | device_name, config_commands | Apply configuration (blocks "erase") |
| `pyats_show_running_config()` | device_name | Get running configuration |
| `pyats_show_logging()` | device_name | Get last 250 log entries |
| `pyats_ping_from_network_device()` | device_name, command | Execute ping from device |
| `pyats_run_linux_command()` | device_name, command | Execute Linux commands (cEOS only) |

---

## Getting Started

1. **Setup environment** (from project root):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure `.env`** (project root):
   ```bash
   GEMINI_API_KEY=your_gemini_api_key_here
   PYATS_TESTBED_PATH=./containerlab/testbed_containerlab.yaml
   ```

3. **Deploy lab**:
   ```bash
   sudo containerlab deploy -t containerlab/topology.clab.yaml
   ```

4. **Run agent**:
   ```bash
   python3 src/agent.py
   ```

---

## Usage Examples

```
You: List all devices
Agent: [Shows 3 devices with IPs]

You: Show IP routes on ceos1
Agent: [Executes run_show_command and displays routing table]

You: Configure Ethernet1 on ceos2 with description "Uplink"
Agent: [Applies configuration and confirms]
```

---

## How It Works

```
User Query → Gemini (intent) → MCP Tool Call → pyATS (SSH) → Device
         ← Gemini (response) ← Tool Result ← Clean Output ← Device
```

**Safety:** Input validation blocks dangerous commands (erase, pipes, redirects)

---

## Adding Custom Tools

In `server.py`:

```python
@mcp.tool()
async def my_tool(device_name: str) -> str:
    """Tool description."""
    result = await custom_operation(device_name)
    return json.dumps(result, indent=2)
```

Tool is automatically exposed to agent via MCP.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not found | Create `.env` with `GEMINI_API_KEY` |
| Testbed path error | Verify `PYATS_TESTBED_PATH` points to valid YAML |
| Connection failure | Check lab is running: `sudo containerlab inspect` |
| Timeout errors | Increase timeout in `server.py` or check device SSH |

---

