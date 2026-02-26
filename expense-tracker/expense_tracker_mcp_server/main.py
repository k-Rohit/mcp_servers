# main.py
from mcp_init import mcp
import tools.tools  # registers all @mcp.tool() decorators

if __name__ == "__main__":
    mcp.run()