#!/usr/bin/env python3
import os
import asyncio
from typing import Optional
from contextlib import AsyncExitStack
from dotenv import load_dotenv
import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

genai.configure(api_key=GEMINI_API_KEY)

class MCPAgent:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.chat = None
        self.system_instruction = """You are a network automation expert using pyATS and Arista devices.
Rules:
- For config changes: Ask clarification first, then confirm before applying
- For show commands: Execute confidently
- Explain actions briefly before calling tools
- Interpret results in simple terms for junior engineers
- Use multiple tools when needed for complex tasks
Be clear, answer to the fact and safety-conscious."""
        
    async def connect_to_server(self, server_script: str):
        """Connect to MCP server."""
        server_params = StdioServerParameters(
            command="python3",
            args=[server_script],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        stdio, write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(stdio, write)
        )
        
        await self.session.initialize()
        response = await self.session.list_tools()
        print(f"\n✓ Connected! Available tools: {[t.name for t in response.tools]}\n")
        
    async def process_query(self, query: str) -> str:
        """Process user query with Gemini + MCP tools."""
        # Get available tools
        response = await self.session.list_tools()
        tools = response.tools
        
        # Convert MCP tools to Gemini function declarations
        gemini_tools = []
        for tool in tools:
            schema = tool.inputSchema
            gemini_tools.append(
                genai.protos.Tool(
                    function_declarations=[
                        genai.protos.FunctionDeclaration(
                            name=tool.name,
                            description=tool.description or "",
                            parameters=genai.protos.Schema(
                                type=genai.protos.Type.OBJECT,
                                properties={
                                    k: genai.protos.Schema(
                                        type=genai.protos.Type.STRING,
                                        description=v.get("description", "")
                                    )
                                    for k, v in schema.get("properties", {}).items()
                                },
                                required=schema.get("required", [])
                            )
                        )
                    ]
                )
            )
        
        # Start chat if not exists
        if not self.chat:
            self.chat = self.model.start_chat(enable_automatic_function_calling=False)
        
        # Send query with tools
        response = self.chat.send_message(query, tools=gemini_tools)
        
        # Handle function calls
        while any(hasattr(p, 'function_call') and p.function_call for p in response.candidates[0].content.parts):
            function_responses = []
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    tool_name = part.function_call.name
                    tool_args = dict(part.function_call.args)
                    print(f"🔧 Calling tool: {tool_name}({tool_args})")
                    
                    result = await self.session.call_tool(tool_name, tool_args)
                    result_text = result.content[0].text if isinstance(result.content, list) else str(result.content)
                    
                    function_responses.append(genai.protos.Part(
                        function_response=genai.protos.FunctionResponse(name=tool_name, response={"result": result_text})
                    ))
            
            response = self.chat.send_message(genai.protos.Content(parts=function_responses), tools=gemini_tools)
        
        return response.text
    
    async def chat_loop(self):
        """Interactive chat loop."""
        print("🤖 Gemini Network Agent Ready!")
        print("Ask me anything about your network, or type 'quit' to exit.\n")
        
        while True:
            try:
                query = input("You: ").strip()
                if query.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye! 👋")
                    break
                
                if not query:
                    continue
                
                response = await self.process_query(query)
                print(f"\n🤖 Agent: {response}\n")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}\n")
    
    async def cleanup(self):
        """Clean up resources."""
        await self.exit_stack.aclose()

async def main():
    agent = MCPAgent()
    try:
        await agent.connect_to_server("server.py")
        await agent.chat_loop()
    finally:
        await agent.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

