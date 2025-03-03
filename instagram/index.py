from selenium import webdriver 
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import json

# Instagram credentials
USERNAME = "vishesh@brancosoft.com"
PASSWORD = "123456789@1234"

if not USERNAME or not PASSWORD:
    raise ValueError("Instagram credentials are missing! Set them in environment variables.")

def login_to_instagram(driver):
    """Logs in to Instagram using the provided driver."""
    driver.get('https://www.instagram.com/accounts/login/')
    
    # Wait for login fields
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, 'username')))

    # Enter username and password
    driver.find_element(By.NAME, 'username').send_keys(USERNAME)
    driver.find_element(By.NAME, 'password').send_keys(PASSWORD)
    driver.find_element(By.NAME, 'password').send_keys(Keys.ENTER)

    # Wait for homepage to load
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, "//nav")))
        print("Login successful!")
    except:
        print("Login may have failed. Please check credentials.")

    # Handle pop-ups
    popups = ["//button[contains(text(), 'Not Now')]"]
    for popup_xpath in popups:
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, popup_xpath))).click()
            print(f"Closed pop-up: {popup_xpath}")
        except:
            pass

def scrape_instagram_profile(driver, target_username):
    """Scrapes Instagram profile data."""
    url = f'https://www.instagram.com/{target_username}/'
    driver.get(url)

    time.sleep(5)  # Allow page to load

    user_data = {"username": target_username}

    # Extract profile bio
    try:
        bio_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, '-vDIg')]/span"))
        )
        user_data['bio'] = bio_element.text
    except:
        user_data['bio'] = "Not found"

    # Extract posts, followers, and following counts
    try:
        stats = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//ul[contains(@class, 'x78zum5')]//span[contains(@class, 'x5n08af')]"))
        )
        if len(stats) >= 3:
            user_data['posts'] = stats[0].text
            user_data['followers'] = stats[1].text
            user_data['following'] = stats[2].text
        else:
            user_data.update({'posts': "Not found", 'followers': "Not found", 'following': "Not found"})
    except:
        user_data.update({'posts': "Not found", 'followers': "Not found", 'following': "Not found"})

    # Extract profile image URL
    try:
        profile_image_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//img[contains(@alt, 'profile picture')]"))
        )
        user_data['profile_image_url'] = profile_image_element.get_attribute('src')
    except:
        user_data['profile_image_url'] = "Not found"

    print(f"Scraped Data: {user_data}")
    return user_data

def main():
    usernames = ['iamdkjha']
    scraped_data = []

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    try:
        login_to_instagram(driver)

        for user in usernames:
            data = scrape_instagram_profile(driver, user)
            if data:
                scraped_data.append(data)

        # Save data to JSON file
        with open('instagram.json', 'w') as json_file:
            json.dump(scraped_data, json_file, indent=4)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
