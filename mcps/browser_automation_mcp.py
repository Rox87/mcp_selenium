import os
import sqlite3
import time
from typing import Optional, Dict, Any, List
from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Initialize FastMCP server
mcp = FastMCP("Selenium Profiler MCP")

DB_PATH = os.path.join(os.path.dirname(__file__), "backend", "profiles.db")

# Global state for the browser
active_driver: Optional[webdriver.Chrome] = None
current_profile_id: Optional[str] = None

def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE id=?", (profile_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def get_profile_by_name(name: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM profiles WHERE name=?", (name,))
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

@mcp.tool()
def list_profiles() -> List[Dict[str, Any]]:
    """List all available browser profiles configured in the UI."""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, name, headless FROM profiles")
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

@mcp.tool()
def start_browser(profile_id: Optional[str] = None) -> str:
    """
    Start the browser using a specific profile ID.
    If no profile_id is provided, it defaults to the profile named 'Default'.
    If a browser is already running, it will be closed first.
    """
    global active_driver, current_profile_id
    
    profile = None
    if profile_id:
        profile = get_profile(profile_id)
        if not profile:
            return f"Error: Profile with ID '{profile_id}' not found."
    else:
        profile = get_profile_by_name("Rodrigo")
        if not profile:
            return "Error: No profile_id provided and no profile named 'Rodrigo' found."
    
    profile_id = profile['id'] # Ensure we have the actual ID

    if active_driver:
        try:
            active_driver.quit()
        except:
            pass
        active_driver = None

    options = ChromeOptions()
    
    if profile.get('headless'):
        options.add_argument("--headless=new")
    
    if profile.get('disable_images'):
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
        
    user_data_dir = profile.get('user_data_dir')
    if user_data_dir:
        # Convert to absolute path if relative, or leave if absolute
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
    user_agent = profile.get('user_agent')
    if user_agent:
        options.add_argument(f"--user-agent={user_agent}")
        
    proxy = profile.get('proxy')
    if proxy:
        options.add_argument(f"--proxy-server={proxy}")

    # Additional standard options for stability
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        service = ChromeService(ChromeDriverManager().install())
        active_driver = webdriver.Chrome(service=service, options=options)
        active_driver.implicitly_wait(5)
        current_profile_id = profile_id
        return f"Successfully started browser with profile '{profile.get('name')}' ({profile_id})."
    except Exception as e:
        return f"Failed to start browser: {str(e)}"

@mcp.tool()
def navigate(url: str) -> str:
    """Navigate the active browser to a specific URL."""
    global active_driver
    if not active_driver:
        return "Error: No active browser. Please run start_browser first."
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
        
    try:
        active_driver.get(url)
        return f"Successfully navigated to {url}. Current title: {active_driver.title}"
    except Exception as e:
        return f"Failed to navigate: {str(e)}"

@mcp.tool()
def get_page_source() -> str:
    """Get the HTML source code of the current page."""
    global active_driver
    if not active_driver:
        return "Error: No active browser."
    return active_driver.page_source

@mcp.tool()
def get_page_info() -> Dict[str, str]:
    """Get basic info about the current page (URL, title)."""
    global active_driver
    if not active_driver:
        return {"error": "No active browser."}
    return {
        "url": active_driver.current_url,
        "title": active_driver.title
    }

def _get_by(by_type: str):
    by_map = {
        "css": By.CSS_SELECTOR,
        "xpath": By.XPATH,
        "id": By.ID,
        "name": By.NAME,
        "class": By.CLASS_NAME,
        "tag": By.TAG_NAME
    }
    return by_map.get(by_type.lower(), By.CSS_SELECTOR)

@mcp.tool()
def click_element(selector: str, by: str = "css", timeout: int = 10) -> str:
    """Click an element on the page."""
    global active_driver
    if not active_driver:
        return "Error: No active browser."
        
    try:
        locator = (_get_by(by), selector)
        element = WebDriverWait(active_driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
        element.click()
        return f"Successfully clicked element: {selector}"
    except TimeoutException:
        return f"Error: Element '{selector}' not clickable after {timeout} seconds."
    except Exception as e:
        return f"Error clicking element: {str(e)}"

@mcp.tool()
def type_text(selector: str, text: str, by: str = "css", clear_first: bool = True, timeout: int = 10) -> str:
    """Type text into an input field on the page."""
    global active_driver
    if not active_driver:
        return "Error: No active browser."
        
    try:
        locator = (_get_by(by), selector)
        element = WebDriverWait(active_driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
        if clear_first:
            element.clear()
        element.send_keys(text)
        return f"Successfully typed text into element: {selector}"
    except TimeoutException:
        return f"Error: Element '{selector}' not found after {timeout} seconds."
    except Exception as e:
        return f"Error typing text: {str(e)}"

@mcp.tool()
def execute_script(script: str) -> Any:
    """Execute arbitrary JavaScript in the context of the current page."""
    global active_driver
    if not active_driver:
        return "Error: No active browser."
        
    try:
        result = active_driver.execute_script(script)
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@mcp.tool()
def stop_browser() -> str:
    """Close the active browser."""
    global active_driver, current_profile_id
    if not active_driver:
        return "Browser is not running."
        
    try:
        active_driver.quit()
        active_driver = None
        current_profile_id = None
        return "Browser stopped successfully."
    except Exception as e:
        return f"Error stopping browser: {str(e)}"

@mcp.tool()
def take_screenshot(filename: str = "screenshot.png") -> str:
    """Take a screenshot of the current browser page and save it."""
    global active_driver
    if not active_driver:
        return "Error: No active browser."
        
    try:
        # Create screenshots directory if it doesn't exist
        os.makedirs("screenshots", exist_ok=True)
        path = os.path.join("screenshots", filename)
        active_driver.save_screenshot(path)
        return f"Screenshot saved to: {os.path.abspath(path)}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

@mcp.tool()
def wait(seconds: int) -> str:
    """Wait for a specified number of seconds before continuing."""
    try:
        time.sleep(seconds)
        return f"Waited for {seconds} seconds."
    except Exception as e:
        return f"Error during wait: {str(e)}"

if __name__ == "__main__":
    # Start the FastMCP server
    print("Starting Selenium Profiler MCP server...")
    mcp.run()
