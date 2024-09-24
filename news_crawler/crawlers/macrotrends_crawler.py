# -*- coding: utf-8 -*-
"""
@Time: 2024/9/22 下午3:34
@Auth: Bacchos
@File: macrotrends_crawler.py
@IDE: PyCharm
@Motto: ABC(Always Be Coding)

"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
from db.db_config import connect_to_database, insert_financial_data

# Configure WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=http://127.0.0.1:7890")  # Set proxy if needed
chrome_options.add_argument("--window-size=1920,1080")  # Set the browser window size

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Visit the target webpage
url = "https://www.macrotrends.net/stocks/charts/KO/cocacola/income-statement"
driver.get(url)

# Set wait time for element loading
wait = WebDriverWait(driver, 5)

# Hide ads on the page by executing JavaScript
try:
    driver.execute_script("""
        var ads = document.getElementById('IC_D_Adhesion_1__ayManagerEnv__1_580c7453');
        if (ads) {
            ads.style.display = 'none';
        }
    """)
    print("Ads have been hidden.")
except Exception as e:
    print(f"Error hiding ads: {e}")


# Define a function to format strings into floats, removing symbols like $, commas, and parentheses
def format_to_float(value):
    """
    Formats a string to a float, removing $, commas, and other symbols.
    :param value: String value such as "$36,212" or "-"
    :return: Float value or None if the input is '-'
    """
    try:
        if value == '-':
            return None
        return float(value.replace('$', '').replace(',', '').replace('(', '-').replace(')', ''))
    except ValueError:
        print(f"Unable to convert to number: {value}")
        return None


# Define a function to move the horizontal scrollbar
def move_scrollbar():
    try:
        # Locate the scrollbar using XPath
        scrollbar = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="jqxScrollThumbhorizontalScrollBarjqxgrid"]')))
        ActionChains(driver).drag_and_drop_by_offset(scrollbar, 370, 0).perform()  # Move scrollbar to the right by 370 pixels
        print("Scrollbar has been moved.")
        time.sleep(2)  # Wait for the scrollbar to move
    except Exception as e:
        print(f"Error moving scrollbar: {e}")


# Function to extract data from the page
def extract_data(xpath1_range, xpath2_y_range, trigger_scroll=False):
    # Scroll to a specific vertical position on the page
    scroll_position = 624  # Adjust as needed
    driver.execute_script(f"window.scrollTo(0, {scroll_position});")
    time.sleep(2)  # Wait for the page to scroll
    print(f"Page scrolled to position: {scroll_position}px.")

    data_dict = {}  # Initialize a dictionary to store all extracted data

    # Extract data from the first XPath structure, mapping each x to a report_date
    for x in xpath1_range:
        xpath1 = f'/html/body/div[3]/div[3]/div[3]/div/div/div[4]/div[1]/div/div[{x}]/div/div[1]/span'
        try:
            element1 = wait.until(EC.presence_of_element_located((By.XPATH, xpath1)))
            report_date = element1.text
            print(f"Extracted data XPath1 (x={x}): {report_date}")
            data_dict[x] = {'report_date': report_date}  # Use x as the key to store the date
        except Exception as e:
            print(f"Error extracting data from XPath1 index x={x}: {e}")

    # Extract data from the second XPath structure, mapping y and z values to corresponding financial fields
    for y in xpath2_y_range:
        for z in xpath1_range:  # Ensure z matches x
            xpath2 = f'/html/body/div[3]/div[3]/div[3]/div/div/div[4]/div[2]/div/div[{y}]/div[{z}]/div'
            try:
                element2 = wait.until(EC.presence_of_element_located((By.XPATH, xpath2)))
                data2 = format_to_float(element2.text)  # Format the data
                print(f"Extracted data XPath2 (y={y}, z={z}): {data2}")

                # Map the y value to the appropriate financial field
                field_mapping = {
                    1: 'revenue', 2: 'cost_of_goods_sold', 3: 'gross_profit',
                    4: 'research_and_dev_expenses', 5: 'sg_and_a_expenses',
                    6: 'other_op_income_expenses', 7: 'operating_expenses',
                    8: 'operating_income', 9: 'non_operating_income', 10: 'pre_tax_income',
                    11: 'income_taxes', 12: 'income_after_taxes', 13: 'other_income',
                    14: 'income_from_cont_ops', 15: 'income_from_disc_ops', 16: 'net_income',
                    17: 'ebitda', 18: 'ebit', 19: 'basic_shares_outstanding',
                    20: 'shares_outstanding', 21: 'basic_eps', 22: 'eps_earnings_per_share'
                }

                # Only add data to the corresponding date's dictionary if z matches x
                if z in data_dict:
                    data_dict[z][field_mapping.get(y, 'unknown_field')] = data2

                # Trigger scrollbar movement if conditions are met
                if trigger_scroll and y == max(xpath2_y_range) and z == max(xpath1_range):
                    print(f"Triggering scrollbar movement condition: (y={y}, z={z})")
                    move_scrollbar()
            except Exception as e:
                print(f"Error extracting data from XPath2 index (y={y}, z={z}): {e}")

    # Return all collected data as a list of dictionaries
    return list(data_dict.values())


# Main function to run the data extraction and insertion process
def main():
    # Connect to the MySQL database
    connection = connect_to_database()
    if not connection:
        print("Unable to connect to the database, terminating program.")
        return

    try:
        # Step 1: Extract data from xpath1 (x=3-10) and xpath2 (y=1-22, z=3-10)
        data = extract_data(range(3, 10), range(1, 23), trigger_scroll=True)
        time.sleep(2)

        # Step 2: Extract data from xpath1 (x=11-15) and xpath2 (y=1-22, z=11-15)
        data.extend(extract_data(range(10, 16), range(1, 23), trigger_scroll=True))
        time.sleep(2)

        # Step 3: Extract data from xpath1 (x=16-17) and xpath2 (y=1-22, z=16-17)
        data.extend(extract_data(range(16, 18), range(1, 23)))

        # Insert the collected data into the database
        for record in data:
            if 'report_date' in record:
                insert_financial_data(connection, record['report_date'], record)

    except Exception as e:
        print(f"Error during execution: {e}")

    finally:
        # Close the database connection
        if connection.is_connected():
            connection.close()
            print("Database connection closed.")

        # Close the browser
        driver.quit()
        print("Browser closed.")


# Execute the main function
if __name__ == "__main__":
    main()
