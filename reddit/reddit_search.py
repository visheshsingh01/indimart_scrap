import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def initialize_driver():
    """Set up the Chrome WebDriver with options."""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Run in headless mode if desired

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def search_reddit(query):
    """Open Reddit and search for the specified query."""
    driver = initialize_driver()
    try:
        driver.get("https://www.reddit.com")
        time.sleep(5)  # Allow the page to load

        # Find the search box and enter the query
        search_box = driver.find_element("class name", "search-input")

        search_box.send_keys(query)
        search_box.submit()  # Submit the search

        time.sleep(5)  # Allow the search results to load

        # Print the page title to confirm the search
        print("Page Title:", driver.title)

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

# Example usage
if __name__ == "__main__":
    search_reddit("caterpillar")
