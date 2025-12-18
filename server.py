# server.py
from firestore_service import get_edges
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("ptu-sheet-generator")

@mcp.tool()
def getEdges():
    """Returns all edges for the user."""
    return get_edges()



if __name__ == "__main__":
    mcp.run(transport="stdio")
