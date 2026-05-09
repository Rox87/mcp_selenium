# Selenium MCP Server

This is an MCP Server exposing Selenium tools to LLMs for Web Scraping.

## Structure
- `api.py`: FastAPI server that handles configurations and exposes the UI data
- `server.py`: FastMCP server exposing functions to LLMs (the core logic)
- `scraper.py`: Core Selenium driver setup and basic actions wrapper
- `ui`: Vite + React UI to configure browser profiles for MCP tools to use.
