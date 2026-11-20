# Local MCP stdio client
 
from fastmcp import Client
import asyncio 
 
client = Client("mcp_stdio_server.py")
 
async def call_greet(name: str):
    async with client:
        response = await client.call_tool("greet", {"name": name})
        print(response)

        result = await client.call_tool("add",{"x": 10, "y": 20})
        print("Addition result:", result.data) 

async def call_add(x: int,y:int):
    async with client:
        response = await client.call_tool("add", {"x": x,"y":y})
        print(response)
 
if __name__ == "__main__":
    asyncio.run(call_greet('Tom'))
    asyncio.run(call_add(50,50))