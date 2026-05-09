from mcp.server.fastmcp import FastMCP
from scraper import Scraper

mcp = FastMCP("Selenium Web Scraper Server")

def _run_scraper_action(profile_id: str, action: callable):
    with Scraper(profile_id) as scraper:
        return action(scraper)

@mcp.tool()
def navigate_and_get_html(url: str, profile_id: str = "default") -> str:
    """Navigates to a URL and returns the page HTML source."""
    def action(scraper: Scraper):
        scraper.navigate(url)
        return scraper.export_html()
    return _run_scraper_action(profile_id, action)

@mcp.tool()
def get_element_text(url: str, selector: str, by: str = "css", profile_id: str = "default") -> str:
    """Gets the text of an element on a webpage."""
    def action(scraper: Scraper):
        scraper.navigate(url)
        scraper.wait_for_element(selector, by)
        return scraper.get_text(selector, by)
    return _run_scraper_action(profile_id, action)

@mcp.tool()
def interact_and_extract(
    url: str,
    interactions: list[dict],
    extract_selector: str,
    extract_by: str = "css",
    profile_id: str = "default"
) -> str:
    """Performs sequence of interactions and extracts text."""
    def action(scraper: Scraper):
        scraper.navigate(url)
        for interaction in interactions:
            act = interaction.get("action")
            sel = interaction.get("selector")
            b = interaction.get("by", "css")
            scraper.wait_for_element(sel, b)
            if act == "click":
                scraper.click(sel, b)
            elif act == "type":
                text = interaction.get("text", "")
                scraper.type_text(sel, text, b)
        scraper.wait_for_element(extract_selector, extract_by)
        return scraper.get_text(extract_selector, extract_by)
    return _run_scraper_action(profile_id, action)

@mcp.tool()
def execute_javascript(url: str, script: str, profile_id: str = "default") -> str:
    """Executes arbitrary JavaScript on a webpage and returns the result."""
    def action(scraper: Scraper):
        scraper.navigate(url)
        result = scraper.execute_js(script)
        return str(result)
    return _run_scraper_action(profile_id, action)

@mcp.tool()
def take_screenshot_tool(url: str, profile_id: str = "default") -> str:
    """Takes a screenshot of the webpage and returns it as a base64 string."""
    def action(scraper: Scraper):
        scraper.navigate(url)
        return scraper.take_screenshot()
    return _run_scraper_action(profile_id, action)

if __name__ == "__main__":
    mcp.run()
