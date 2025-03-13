import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

def initialize_driver():
    """Set up the Chrome WebDriver with options."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode if desired
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def scrape_reddit_posts(subreddit_url):
    """Scrape posts from the specified subreddit."""
    driver = initialize_driver()
    try:
        driver.get(subreddit_url)
        time.sleep(5)  # Allow the page to load

        # Scroll down a few times to load more posts
        for _ in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # Get the page source and parse it with BeautifulSoup
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract post titles
        posts = soup.find_all("div", class_="_1oQyIsiPHYt6nx7VOmd1sz")
        titles = []
        for post in posts:
            title_elem = post.find("h3")
            if title_elem:
                title = title_elem.get_text(strip=True)
                titles.append(title)
    for title in titles:
        print("Title:", title)
    print("Scraped Titles:")

    for title in titles:
        print("Title:", title)

    for title in titles:
        print("Title:", title)
    # Save the scraped titles to a text file
    with open("scraped_titles.txt", "w") as file:
        for title in titles:
            file.write(title + "\n")
    return titles


    finally:
        driver.quit()


    except Exception as e:
        print(f"An error occurred: {e}")

        print(f"An error occurred: {e}")

        print(f"An error occurred: {e}")
    finally:
    finally:
        driver.quit()


# Example usage
if __name__ == "__main__":
    subreddit_url = "https://www.reddit.com/r/learnpython/"  # Change to your target subreddit
    post_titles = scrape_reddit_posts(subreddit_url)
    for title in post_titles:
        print("Title:", title)
