**macrotrend_crawler.py**
Descrption：
The webpage data at https://www.macrotrends.net/stocks/charts/KO/cocacola/income-statement is of the report type and features a draggable bar, indicating it is dynamically loaded. Therefore, the current script's WebDriver is set to a resolution of 2560x1440; if your monitor resolution changes, adjustments will need to be made.

Usage：
1. Configure WebDriver: The code first configures the Chrome browser's WebDriver, including settings for proxy servers, window size, and other parameters.
2. Access the Target Webpage: The WebDriver is used to open the target webpage, which is Coca-Cola Company’s (KO) financial report page.
3. Ad Blocking: JavaScript code is executed to hide ad elements on the page to reduce distractions.
4. Data Extraction Function:
    extract_data() function extracts financial data through two different XPath ranges. It first scrolls the page to a specific position and then retrieves the report date and corresponding financial data fields sequentially.
    The extracted data is formatted (e.g., removing $ symbols and commas) and converted into floating-point numbers.
    The data is stored in a dictionary, where the report date serves as the key and the associated financial data as the value.
5. Scrollbar Operation: To ensure all financial data is visible, the code automatically moves the horizontal scrollbar to load more data when certain conditions are met.
6. Data Insertion: The extracted financial data is collected into a list and then inserted into a MySQL database one by one.
7. Error Handling: The code employs a try-except structure to catch and handle potential exceptions, such as data extraction failures or database connection errors.
8.Resource Cleanup: At the end of execution or in the event of an error, the code ensures that database connections and the browser are closed to free up resources.

********************************************************************************

**wsj_crawler.py**
Description:
1. The webpage data at https://www.wsj.com/pro/venture-capital/topics/fin-tech is classified as news and information.
2. The website has strong anti-scraping mechanisms (device verification, human verification, IP blocking).
3. The current solution is to use cookies to bypass verification; the first run requires manually obtaining cookies and placing them in the directory news_crawler/cookies/wsj_cookies.
4. Cookies can be obtained using the Chrome browser extension "Cookies Tool."

Usage:
1. Configure Browser and Proxy: The code first sets up the Chrome browser's WebDriver and configures a proxy server to address potential regional restrictions or speed issues.
2. Parse Cookie File: The parse_cookies_from_file() function reads cookies from a specified file and parses them into a format usable by the browser. These cookies are used for authentication during web access to bypass certain restrictions.
3. Initialize WebDriver and Connect to Database: The extract_news_from_wsj() function launches the browser, sets up waiting mechanisms, and attempts to connect to the database. Once the database connection is successful, data extraction begins.
4. Access Target Webpage: The script uses the WebDriver to access a specific page on The Wall Street Journal and refreshes the page after loading cookies to ensure access to protected content.
5. Dynamically Load More Content: By simulating clicks on the “LOAD MORE” button, the script can click up to 10 times to gradually load more news articles, mimicking user actions to gather additional data.
6. Extract Article Dates and Links: The script extracts all date and link elements from the page and stores them in a list for subsequent data extraction.
7. Access Each Article and Extract Content:
    The script opens each extracted article link and refreshes the page after adding cookies.
    It uses specified CSS selectors to extract the title, first paragraph, and second paragraph of each article.
    These contents are formatted to a specified date format and the extracted data is inserted into the database.
8. Error Handling and Resource Cleanup: The script includes error handling mechanisms at each step to capture and log potential errors, ensuring that the program does not crash even if issues arise. After completing tasks, it closes the browser and database connection to free up resources.

