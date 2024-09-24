# -*- coding: utf-8 -*-
"""
@Time: 2024/9/22 下午3:27
@Auth: Bacchos
@File: wsj_crawler.py
@IDE: PyCharm
@Motto: ABC(Always Be Coding)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import random
from datetime import datetime
from db.db_config import connect_to_database, insert_to_db

# Configure proxy settings for the browser
proxy = "http://127.0.0.1:7890"
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server={}".format(proxy))


# Function to parse cookies from a file and convert them into a format usable by the browser
def parse_cookies_from_file(file_path):
    """
    Parse cookies string from a text file.

    :param file_path: Path to the cookies file
    :return: List of dictionaries representing cookies
    """
    cookies = []
    # Read the contents of the file
    with open(file_path, 'r') as file:
        cookie_str = file.read().strip()
    # Split the cookie string into individual cookie pairs
    cookie_pairs = cookie_str.split('; ')
    for pair in cookie_pairs:
        # Split each pair into name and value
        name, value = pair.split('=', 1)
        cookies.append({'name': name, 'value': value, 'domain': '.wsj.com', 'path': '/'})
    return cookies


# Function to extract news articles from WSJ using Selenium
def extract_news_from_wsj(cookies):
    # Initialize the WebDriver with configured options
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)

    # Establish a connection to the database
    db_connection = connect_to_database()
    if not db_connection or not db_connection.is_connected():
        print("Database connection is unavailable. Please check the database configuration.")
        return

    # Step 1: Open the page, add cookies, and refresh the page
    try:
        driver.get("https://www.wsj.com/pro/venture-capital/topics/fin-tech")
        time.sleep(5)  # Wait for the page to fully load

        # Refresh the page to apply cookies
        driver.refresh()
        time.sleep(5)  # Wait again after refreshing

    except Exception as e:
        print(f"Error while loading the page: {e}")

    # Step 2: Start extracting content from the page
    try:
        # Click the "LOAD MORE" button up to 10 times to load more content
        click_count = 0
        max_clicks = 10
        while click_count < max_clicks:
            try:
                # Locate and click the "LOAD MORE" button
                load_more_button = wait.until(
                    EC.element_to_be_clickable(
                        (By.CSS_SELECTOR, '.style--load-more--33JcjVhT .style--primary-button--K1rns8Qg'))
                )
                load_more_button.click()
                click_count += 1
                print(f"Click {click_count} successful")
                # Random wait between 1 to 5 seconds to avoid clicking too fast
                time.sleep(random.uniform(1, 5))
            except TimeoutException:
                print("Failed to find or click the 'LOAD MORE' button")
                break

        # Get all date elements from the page
        date_elements = driver.find_elements(By.CSS_SELECTOR, '.WSJProTheme--timestamp--3qWxDquR')
        dates = [date_element.text for date_element in date_elements]
        print(f"Retrieved {len(dates)} dates.")

        # Get all link elements from the page
        link_elements = driver.find_elements(By.CSS_SELECTOR, '.WSJProTheme--headline--3o49YRww a')
        links = [link_element.get_attribute('href') for link_element in link_elements]
        print(f"Retrieved {len(links)} links.")

        # Step 3: Extract content from each link
        for date, link in zip(dates, links):
            try:
                # Convert the date format from "Month Day, Year" to "YYYY-MM-DD"
                formatted_date = datetime.strptime(date, '%B %d, %Y').strftime('%Y-%m-%d')
                # Open the link
                driver.get(link)
                print(f"Opening link: {link}")

                # Add cookies to the current page
                for cookie in cookies:
                    driver.add_cookie(cookie)

                driver.refresh()
                # Random wait between 2 to 5 seconds after opening each link
                time.sleep(random.uniform(2, 5))

                # Locate and extract the first paragraph content
                caption_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.e1m33gv80.css-426zcb-CaptionSpan.e1m33gv81'))
                )
                caption_text = caption_element.text
                print(f"First paragraph: {caption_text}")

                # Locate and extract the second paragraph content
                paragraph1_element = driver.find_element(By.CSS_SELECTOR, '.css-k3zb6l-Paragraph.e1e4oisd0')
                paragraph1_text = paragraph1_element.text
                print(f"Second paragraph: {paragraph1_text}")

                # Locate and extract the third paragraph content
                paragraph2_element = driver.find_elements(By.CSS_SELECTOR, '.css-k3zb6l-Paragraph.e1e4oisd0')[1]
                paragraph2_text = paragraph2_element.text
                print(f"Third paragraph: {paragraph2_text}")
                caption_text = caption_element.text
                print(f"Content: {caption_text}")

                # Combine the extracted content
                content = f"{paragraph1_text} {paragraph2_text}"

                # Insert the extracted data into the database
                insert_to_db(db_connection, formatted_date, link, caption_text, content)

            except NoSuchElementException as e:
                print(f"Unable to find the specified element: {e}")
            except Exception as e:
                print(f"Error extracting content from {link}: {e}")

    except Exception as e:
        print(f"Error during execution: {e}")

    finally:
        # Close the browser
        driver.quit()
        print("Browser has been closed.")


# Main function
def main():
    # Load cookies from a file
    cookies = parse_cookies_from_file('../cookies/wsj_cookies')  # Update the filename to the actual cookies file path
    # Start extracting news data
    extract_news_from_wsj(cookies)


# Execute the main function
if __name__ == "__main__":
    main()
