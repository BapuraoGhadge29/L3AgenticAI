import asyncio
import traceback

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

# Remote Tavily MCP server
TAVILY_MCP_URL = "https://mcp.tavily.com/mcp/"


async def main():

    print("Connecting to Tavily Remote MCP Server...")

    try:

        # Step 1: Connect to remote MCP server
        async with streamable_http_client(
            TAVILY_MCP_URL
        ) as (read_stream, write_stream):

            print("HTTP connection established.")

            # Step 2: Create MCP client session
            async with ClientSession(
                read_stream,
                write_stream
            ) as session:

                # Step 3: Initialize MCP connection
                await session.initialize()

                print("MCP initialization successful!")

                # Step 4: Discover available remote tools
                print("\nAvailable Remote Tools:")

                tools = await session.list_tools()

                for tool in tools.tools:

                    print(f"\nTool Name: {tool.name}")
                    print(f"Description: {tool.description}")

                # Step 5: Find Tavily search tool
                tool_name = "tavily_search"

                tavily_tool = next(
                    (
                        tool for tool in tools.tools
                        if tool.name == tool_name
                    ),
                    None
                )

                if tavily_tool is None:

                    print("\ntavily_search tool not found!")
                    return

                print("\nCalling remote tool: tavily_search")

                # Step 6: Prepare search query
                search_query = "Latest developments in Generative AI"

                # Step 7: Invoke remote Tavily tool
                result = await session.call_tool(
                    "tavily_search",
                    arguments={
                        "query": search_query
                    }
                )

                # Step 8: Display search results
                print("\nTavily Search Results")
                print("=" * 60)

                for content in result.content:

                    if hasattr(content, "text"):

                        print(content.text)

                if result.isError:

                    print("\nRemote tool returned an error.")

                else:

                    print("\nSearch completed successfully!")

    except Exception as error:

        print("\nError connecting to Tavily MCP Server:")

        traceback.print_exception(error)


# Application entry point
if __name__ == "__main__":

    asyncio.run(main())