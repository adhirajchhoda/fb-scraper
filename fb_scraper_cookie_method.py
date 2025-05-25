from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    StaleElementReferenceException,
    InvalidSessionIdException,
    WebDriverException,
    NoSuchElementException
)
import time
import json
import pandas as pd

FB_GROUP_URL = "https://www.facebook.com/groups/tjhsst"
SCROLL_PAUSE_TIME = 2.5
NUM_SCROLLS = 100

options = Options()
options.add_argument("--disable-notifications")
options.add_argument("--start-maximized")

service = Service("C:/Users/achom/Downloads/fb scraper/chromedriver.exe")
driver = None

post_data = []
collected_post_texts = set()

try:
    driver = webdriver.Chrome(service=service, options=options)

    with open("facebook_cookies.json", "r") as f:
        cookies = json.load(f)

    driver.get("https://www.facebook.com")
    time.sleep(3)
    driver.delete_all_cookies()
    for cookie in cookies:
        try:
            if 'name' in cookie and 'value' in cookie:
                if 'sameSite' in cookie:
                    del cookie['sameSite']
                driver.add_cookie(cookie)
        except WebDriverException:
            continue

    driver.get(FB_GROUP_URL)
    print(f"Navigated to group: {FB_GROUP_URL}")
    time.sleep(5)

    def click_all_see_more(driver_instance):
        if not driver_instance or not driver_instance.session_id:
            return
        try:
            buttons = driver_instance.find_elements(By.XPATH, '//div[@role="button"][.//span[contains(text(),"See more")]]')
            if buttons:
                print(f"Found {len(buttons)} 'See more' buttons to click.")
            for btn_idx, btn in enumerate(buttons):
                try:
                    driver_instance.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(0.1)
                    driver_instance.execute_script("arguments[0].click();", btn)
                    time.sleep(0.3)
                except (ElementClickInterceptedException, StaleElementReferenceException):
                    continue
                except WebDriverException:
                    print("Browser closed during 'See more' click.")
                    return
        except WebDriverException:
            print("Browser closed while finding 'See more' buttons.")
            return

    def scrape_current_posts(driver_instance, existing_texts_set, target_data_list):
        if not driver_instance or not driver_instance.session_id:
            return 0
        new_posts_found_this_round = 0
        selectors = [
            'div[data-ad-comet-preview="message"]',
            'div[data-testid="post_message"]',
            'div[dir="auto"][style*="text-align: start"]',
        ]
        current_texts_on_page = set()
        for selector_idx, selector in enumerate(selectors):
            if not driver_instance.session_id:
                break
            try:
                post_elements = driver_instance.find_elements(By.CSS_SELECTOR, selector)
                for element_idx, post_element in enumerate(post_elements):
                    try:
                        text = post_element.text.strip()
                        if text and text not in current_texts_on_page:
                            current_texts_on_page.add(text)
                            if text not in existing_texts_set:
                                existing_texts_set.add(text)
                                target_data_list.append(text)
                                new_posts_found_this_round += 1
                                print(f"Collected new post ({len(target_data_list)} total): {text[:70]}...")
                    except StaleElementReferenceException:
                        continue
                    except WebDriverException:
                        if not driver_instance.session_id:
                            return new_posts_found_this_round
                        continue
            except NoSuchElementException:
                continue
            except WebDriverException:
                if not driver_instance.session_id:
                    return new_posts_found_this_round
                continue
        return new_posts_found_this_round

    last_height = driver.execute_script("return document.body.scrollHeight")
    consecutive_scrolls_with_no_new_posts = 0

    for i in range(NUM_SCROLLS):
        if not driver or not driver.session_id:
            print("Browser session ended. Stopping scroll.")
            break
        print(f"Scroll attempt {i+1}/{NUM_SCROLLS}, Total collected: {len(post_data)}")
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(SCROLL_PAUSE_TIME)
            if not driver.session_id:
                break
            click_all_see_more(driver)
            if not driver.session_id:
                break
            new_posts_this_cycle = scrape_current_posts(driver, collected_post_texts, post_data)
            if not driver.session_id:
                break
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                if new_posts_this_cycle == 0:
                    consecutive_scrolls_with_no_new_posts += 1
                    print(f"No change in page height or new posts. Count: {consecutive_scrolls_with_no_new_posts}")
                else:
                    consecutive_scrolls_with_no_new_posts = 0
                if consecutive_scrolls_with_no_new_posts >= 3:
                    print("Reached end of page or no new content for 3 consecutive scrolls. Stopping.")
                    break
            else:
                consecutive_scrolls_with_no_new_posts = 0
            last_height = new_height
        except WebDriverException as e:
            print(f"WebDriverException during scroll loop (attempt {i+1}): {e}")
            if not driver or not driver.session_id:
                print("Session lost. Breaking scroll loop.")
            break

except Exception as e:
    print(f"An unexpected error occurred: {e}")

finally:
    if post_data:
        try:
            df = pd.DataFrame(post_data, columns=["PostText"])
            df.to_csv("facebook_group_posts.csv", index=False, encoding="utf-8-sig")
            print(f"--- FINAL: Scraped {len(df)} unique posts. Saved to facebook_group_posts.csv ---")
        except Exception as e_csv:
            print(f"Error saving to CSV: {e_csv}")
    else:
        print("--- FINAL: No posts were collected. CSV not updated/created. ---")

    if driver and driver.session_id:
        try:
            driver.quit()
            print("Browser closed successfully.")
        except WebDriverException as e_quit:
            print(f"Error quitting driver: {e_quit}")
    elif driver:
        print("Driver existed but session was already lost or invalid prior to quit.")
    else:
        print("Driver was not initialized.")
    print("Script finished.")
