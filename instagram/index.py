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
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    # Extract profile name
    try:
        name_element = soup.find('span', class_="x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xvs91rp x1s688f x5n08af x10wh9bi x1wdrske x8viiok x18hxmgj")
        user_data['name'] = name_element.get_text(strip=True) if name_element else "Not found"
    except Exception as e:
        print("Error",e)

    # Extract profile bio
    try:
        bio_element = soup.find('span', class_="_ap3a _aaco _aacu _aacx _aad7 _aade")
        user_data['bio'] = bio_element.get_text(strip=True) if bio_element else "Not found"
    except Exception as e:
        print("Error",e)

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
    
    #Extract links from the profile 
    try:
    # Find all buttons matching this class
        buttons = driver.find_elements(By.CLASS_NAME, "_acan")

        if len(buttons) > 0:
            for button in buttons:
            # Check if this button has the "Link icon" inside it
                if "Link icon" in button.get_attribute("innerHTML"):
                    button.click()
                    time.sleep(5)
                    print("Button clicked successfully!")
                    break  # Stop after clicking the first valid button
                else:
                    print("No link button found on this profile.")
        else:
            print("No buttons found on this profile.")
        
        try:
            modal = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='dialog']"))
            )
            # Find all anchor tags within the modal
            modal_links = modal.find_elements(By.TAG_NAME, "a")
            extracted_links = [link.get_attribute("href") for link in modal_links if link.get_attribute("href")]
            user_data['bio_links'] = extracted_links
            print("Extracted links from modal:", extracted_links)
        except Exception as e:
            print("Error extracting links from modal:", e)
            user_data['bio_links'] = []


        try:
            close_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Close']"))
            )
            close_button.click()
            print("Modal closed successfully!")
        except Exception as e:
            print("Error closing modal:", e)

    except Exception as e:
        print("Error clicking the button:", e)

     # Count highlights: We are only counting the number of highlight items, not going inside them.

    try:
        # Wait for the highlights section to be present
        highlights_section = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//section[contains(@class, 'xc3tme8') and contains(@class, 'xcrlgei')]"))
        )
        # Locate the unordered list (ul) that holds the highlights
        highlights_ul = highlights_section.find_element(By.XPATH, ".//ul[contains(@class, '_acay')]")
        
        # Find all list items (li) within the highlights list
        highlight_items = highlights_ul.find_elements(By.XPATH, ".//li[contains(@class, '_acaz')]")

        highlights_count = len(highlight_items)
        user_data['highlights_count'] = highlights_count
        print("Highlights count:", highlights_count)

        # for i in range(highlights_count):
        #     # Re-fetch highlight items in case the DOM updates
        #     highlight_items = highlights_section.find_elements(By.XPATH, ".//ul[contains(@class, '_acay')]/li[contains(@class, '_acaz')]")
        #     if i < len(highlight_items):
        #         current_highlight = highlight_items[i]
        #         driver.execute_script("arguments[0].scrollIntoView();", current_highlight)
        #         time.sleep(1)  # Optional: allow scrolling to complete
        #         current_highlight.click()
        #         print(f"Clicked highlight {i+1}")
        #         time.sleep(5)  # Wait for the highlight modal to open and play briefly
                
        #         # Click the close button within the highlight modal
        #        # Click the close button within the highlight modal using an XPath that targets the SVG with title "Close"
        #         try:
        #             # Wait for the close button inside the container to be clickable
        #             close_highlight_btn = WebDriverWait(driver, 10).until(
        #                 EC.element_to_be_clickable((By.CSS_SELECTOR, ".x1n2onr6.x1vjfegm svg[aria-label='Close']"))
        #             )
        #             driver.execute_script("""
        #                 var evt = new MouseEvent('click', {bubbles: true, cancelable: true});
        #                 arguments[0].dispatchEvent(evt);
        #             """, close_highlight_btn)
        #             print(f"Highlight {i+1} closed successfully!")
        #             print(f"Highlight {i+1} closed successfully!")
        #         except Exception as e:
        #             print(f"Error closing highlight {i+1}:", e)

        #         time.sleep(1)  # Wait a moment before processing the next highlight
        #     else:
        #         print("Highlight index out of range.")

    except Exception as e:
        print("Error extracting highlights count:", e)
        user_data['highlights_count'] = "Not found"

    # try:
    #     # Locate the container with role="tablist"
    #     tablist = WebDriverWait(driver, 10).until(
    #         EC.presence_of_element_located((By.XPATH, "//div[@role='tablist']"))
    #     )
    #     # Find all <a> tags within the tablist
    #     tabs = tablist.find_elements(By.TAG_NAME, "a")
    #     print(f"Found {len(tabs)} tabs in the tablist.")
    
    # # Loop through each tab and click it
    #     for index, tab in enumerate(tabs):
    #         try:
    #             href = tab.get_attribute("href")
    #             print(f"Clicking tab {index+1}: {href}")
    #             # Use JavaScript click to bypass any potential click issues
    #             driver.execute_script("arguments[0].click();", tab)
    #             time.sleep(3)  # Wait for the tab content to load
    #         except Exception as inner_e:
    #             print(f"Error clicking tab {index+1}: {inner_e}")
    # except Exception as e:
    #     print("Error finding tablist:", e)

    # Locate the posts container and count the posts using the specific classes
    try:
        # Locate the container that holds the posts
        posts_container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xg7h5cd') and contains(@class, 'x1n2onr6')]"))
        )
        # Find all <a> tags within the container having the specified post classes.
        # (The XPath below ensures the <a> has the class _a6hd which seems unique for posts.)
        post_links = posts_container.find_elements(By.XPATH, ".//a[contains(@class, '_a6hd')]")
        posts_count = len(post_links)
        print(f"Found {posts_count} posts.")
    except Exception as e:
        print("Error locating posts container or post links:", e)
        return

    # Loop through each post
    for i in range(posts_count):
        try:
            # Re-fetch the posts container and post links to avoid stale element issues
            posts_container = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'xg7h5cd') and contains(@class, 'x1n2onr6')]"))
            )
            post_links = posts_container.find_elements(By.XPATH, ".//a[contains(@class, '_a6hd')]")
            if i < len(post_links):
                current_post = post_links[i]
                # Scroll the post into view
                driver.execute_script("arguments[0].scrollIntoView(true);", current_post)
                time.sleep(1)
                # Click the post using JavaScript to avoid click interception issues
                driver.execute_script("arguments[0].click();", current_post)
                print(f"Clicked post {i+1}")
                time.sleep(5)  # Wait for the modal to open
                
                # Attempt to close the modal
                try:
                    # Try to locate the close button within the modal. Adjust the XPath if needed.
                    #  Wait for the close button inside the container to be clickable
                    close_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x160vmok.x10l6tqk.x1eu8d0j.x1vjfegm"))
                    )

                    driver.execute_script("""
                        var evt = new MouseEvent('click', {
                            bubbles: true,
                            cancelable: true,
                            view: window
                        });
                        arguments[0].dispatchEvent(evt);
                    """, close_btn)
                    time.sleep(3)

                    print("Close button clicked using MouseEvent!")

                    

                  
                except Exception as close_e:
                    print(f"Error closing post {i+1} with close button: {close_e}")
                    
                time.sleep(2)  # Pause before processing the next post
            else:
                print("Post index out of range.")
        except Exception as inner_e:
            print(f"Error processing post {i+1}: {inner_e}")


    
        


    print(f"Scraped Data: {user_data}")
    return user_data

def main():
    usernames = ['chrishemsworth']
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
        with open('instagram.json', 'w', encoding='utf-8') as json_file:
            json.dump(scraped_data, json_file, indent=4,ensure_ascii=False)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
