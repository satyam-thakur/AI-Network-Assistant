import os
import re
import sys
import json
import time
import logging
import textwrap
from pyats.topology import loader
from dotenv import load_dotenv
import asyncio
from functools import partial
from fastmcp import FastMCP

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ContainerlabMCPServer")

# --- Load Environment Variables ---
load_dotenv()
TESTBED_PATH = os.getenv("PYATS_TESTBED_PATH")

if not TESTBED_PATH or not os.path.exists(TESTBED_PATH):
    logger.critical(f"CRITICAL: PYATS_TESTBED_PATH environment variable not set or file not found: {TESTBED_PATH}")
    sys.exit(1)

logger.info(f"Using testbed file: {TESTBED_PATH}")

# --- Core pyATS Helper Functions ---
def _get_device(device_name: str):
    """Load testbed and connect to device."""
    testbed = loader.load(TESTBED_PATH)
    device = testbed.devices.get(device_name)
    
    if not device:
        raise ValueError(f"Device '{device_name}' not found in testbed.")
    
    if not device.is_connected():
        logger.info(f"Connecting to {device_name}...")
        device.connect(
            connection_timeout=120,
            learn_hostname=True,
            log_stdout=False,
            mit=True
        )
        logger.info(f"Connected to {device_name}")
    
    return device

def _safe_disconnect(device):
    """Safely disconnect from device."""
    if device and device.is_connected():
        try:
            device.disconnect()
            logger.info(f"Disconnected from {device.name}")
        except Exception as e:
            logger.warning(f"Disconnect error: {e}")

def clean_output(output: str) -> str:
    """Clean ANSI escape sequences from output."""
    if not output:
        return ""
    
    if isinstance(output, bytes):
        output = output.decode("utf-8", errors="replace")
    
    # Remove ANSI escape sequences
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    output = ansi_escape.sub('', output)
    
    # Remove other common escape sequences
    output = re.sub(r'\[\?[\d;]+[hl]', '', output)
    output = re.sub(r'\[[\d;]*[A-Za-z]', '', output)
    
    return output

async def run_command_async(device_name: str, command: str, command_type: str = "any") -> dict:
    """Execute a command on a device."""
    try:
        # Validate show commands only if specified
        if command_type == "show":
            cmd = command.lower().strip()
            if not cmd.startswith("show"):
                return {"status": "error", "error": f"Command '{command}' is not a 'show' command."}
            if any(term in cmd.split() for term in ['|', 'include', 'exclude', 'begin', 'redirect', '>', '<', 'config', 'copy', 'delete', 'erase', 'reload', 'write']):
                return {"status": "error", "error": "Command contains disallowed terms."}
        
        # Execute command asynchronously to avoid blocking
        return await asyncio.get_event_loop().run_in_executor(None, partial(_execute_command, device_name, command))
        
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return {"status": "error", "error": str(e)}

def _execute_command(device_name: str, command: str) -> dict:
    """Execute command on device using sendline/expect (avoids regex errors)."""
    device = None
    try:
        device = _get_device(device_name)
        logger.info(f"Executing '{command}' on {device_name}")
        
        # Enter enable mode
        device.sendline("enable")
        time.sleep(0.5)
        
        # Disable pagination for commands that produce large output
        if "running-config" in command.lower() or "startup-config" in command.lower():
            device.sendline("terminal length 0")
            time.sleep(0.5)
            timeout = 60
        else:
            timeout = 20
        
        # Use sendline/expect directly (simpler and avoids bad character range errors)
        device.sendline(command)
        time.sleep(1)
        
        # Try to get output with simple pattern
        try:
            result = device.expect([r'.*[>#]'], timeout=timeout)
            raw_output = result.match_output
        except Exception as expect_err:
            logger.warning(f"Expect timed out, reading buffer: {expect_err}")
            time.sleep(1)
            raw_output = str(device.spawn.buffer)
        
        # Clean output
        cleaned_output = clean_output(raw_output)
        
        # Remove command echo and prompt
        lines = cleaned_output.split('\n')
        if len(lines) > 2:
            output = '\n'.join(lines[1:-1])
        elif len(lines) > 1:
            output = '\n'.join(lines[1:])
        else:
            output = cleaned_output
            
        logger.info(f"Successfully executed '{command}' on {device_name}")
        return {"status": "completed", "device": device_name, "output": output.strip()}
            
    except Exception as e:
        logger.error(f"Command error: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        _safe_disconnect(device)

async def apply_device_configuration_async(device_name: str, config_commands: str) -> dict:
    """Apply configuration to a device."""
    try:
        if "erase" in config_commands.lower():
            return {"status": "error", "error": "Dangerous 'erase' command detected."}
        return await asyncio.get_event_loop().run_in_executor(None, partial(_execute_config, device_name, config_commands))
    except Exception as e:
        return {"status": "error", "error": str(e)}

def _execute_config(device_name: str, config_commands: str) -> dict:
    """Apply configuration to device using sendline (avoids state machine issues)."""
    device = None
    try:
        device = _get_device(device_name)
        cleaned_config = textwrap.dedent(config_commands.strip())
        if not cleaned_config:
            return {"status": "error", "error": "Empty configuration provided."}
        
        logger.info(f"Applying configuration on {device_name}:\n{cleaned_config}")
        
        # Manually enter enable mode using sendline
        device.sendline("enable")
        time.sleep(0.5)
        
        # Enter config mode
        device.sendline("configure")
        time.sleep(0.5)
        
        # Apply each config line
        config_lines = cleaned_config.split('\n')
        for line in config_lines:
            line = line.strip()
            if line:  # Skip empty lines
                device.sendline(line)
                time.sleep(0.3)
        
        # Exit config mode
        device.sendline("exit")
        time.sleep(0.5)
        
        # Get final output
        try:
            result = device.expect([r'.*[>#]'], timeout=5)
            output = clean_output(result.match_output)
        except:
            output = "Configuration commands sent"
        
        logger.info(f"Configuration applied successfully on {device_name}")
        return {"status": "success", "message": f"Configuration applied on {device_name}.", "output": output}
    except Exception as e:
        logger.error(f"Error applying configuration: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        _safe_disconnect(device)

# --- Initialize FastMCP ---
mcp = FastMCP("pyATS Network Automation Server")

# --- Define MCP Tools ---
@mcp.tool()
async def list_devices() -> str:
    """List all devices in the testbed with their IPs."""
    try:
        testbed = loader.load(TESTBED_PATH)
        devices = []
        for name, device in testbed.devices.items():
            ip = device.connections.cli.ip if hasattr(device.connections, 'cli') else "unknown"
            devices.append({"name": name, "ip": str(ip)})
        return json.dumps({"devices": devices}, indent=2)
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)}, indent=2)

@mcp.tool()
async def run_show_command(device_name: str, command: str) -> str:
    """Execute a 'show' command on a network device."""
    result = await run_command_async(device_name, command, "show")
    return json.dumps(result, indent=2)

@mcp.tool()
async def configure_device(device_name: str, config_commands: str) -> str:
    """Apply configuration to network device."""
    result = await apply_device_configuration_async(device_name, config_commands)
    return json.dumps(result, indent=2)

@mcp.tool()
async def pyats_show_running_config(device_name: str) -> str:
    """Get device running configuration."""
    result = await run_command_async(device_name, "show running-config")
    return json.dumps(result, indent=2)

@mcp.tool()
async def pyats_show_logging(device_name: str) -> str:
    """Get recent device logs."""
    result = await run_command_async(device_name, "show logging last 250")
    return json.dumps(result, indent=2)

@mcp.tool()
async def pyats_ping_from_network_device(device_name: str, command: str) -> str:
    """Execute ping command from network device."""
    if not command.lower().strip().startswith("ping"):
        return json.dumps({"status": "error", "error": "Not a ping command"}, indent=2)
    result = await run_command_async(device_name, command)
    return json.dumps(result, indent=2)

@mcp.tool()
async def pyats_run_linux_command(device_name: str, command: str) -> str:
    """Execute Linux command on device."""
    result = await run_command_async(device_name, command)
    return json.dumps(result, indent=2)

# --- Main Function ---
if __name__ == "__main__":
    # port = int(os.environ.get("PORT", 8000))
    # host = "0.0.0.0"

    # logger.info(f"Starting MCP Server on {host}:{port} with testbed: {TESTBED_PATH}")
    
    # mcp.run(
    #     transport="http",
    #     host=host,
    #     port=port,
    #     stateless_http=True
    # )
    logger.info(f"Starting MCP Server (stdio) with testbed: {TESTBED_PATH}")
    mcp.run(transport="stdio")
