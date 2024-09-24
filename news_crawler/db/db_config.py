# -*- coding: utf-8 -*-
"""
@Time: 2024/9/23 上午12:23
@Auth: Bacchos
@File: db_config.py
@IDE: PyCharm
@Motto: ABC(Always Be Coding)
"""

import mysql.connector
from mysql.connector import Error


# Function to create and return a MySQL database connection object
def connect_to_database():
    """
    Creates and returns a MySQL database connection object.
    :return: MySQL connection object or None if the connection fails.
    """
    try:
        # Establish the connection with the database
        connection = mysql.connector.connect(
            host='localhost',  # Database host
            user='crawler',  # Database username
            password='123456',  # Database password
            database='news_data',  # Database name
            ssl_disabled=True  # Disable SSL
        )
        print("Successfully connected to the MySQL database")
        return connection
    except Error as e:
        # Handle connection errors
        print(f"Failed to connect to the MySQL database: {e}")
        return None


# Function to insert data into the wsj_news table
def insert_to_db(connection, date, link, title, content):
    """
    Inserts data into the wsj_news table in the MySQL database.

    :param connection: MySQL database connection object
    :param date: News date
    :param link: News link
    :param title: News title
    :param content: News content
    """
    # Check if the connection is valid and connected
    if not connection or not connection.is_connected():
        print("MySQL database connection is unavailable, please check the connection.")
        return

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query for data insertion
    insert_query = """
    INSERT INTO wsj_news (date, link, title, content)
    VALUES (%s, %s, %s, %s)
    """
    try:
        # Execute the insertion operation
        cursor.execute(insert_query, (date, link, title, content))
        connection.commit()  # Commit the transaction to save changes
        print(f"Successfully inserted data: Date: {date}, Link: {link}")
    except mysql.connector.Error as err:
        # Handle any errors that occur during the insert
        print(f"Error inserting data: {err}")
    finally:
        # Close the cursor
        cursor.close()


# Function to insert financial data into the financial_reports table
def insert_financial_data(connection, report_date, data_dict):
    """
    Inserts financial data into the financial_reports table in the MySQL database.

    :param connection: MySQL database connection object
    :param report_date: The report date
    :param data_dict: A dictionary containing financial fields and their corresponding values
    """
    # Check if the connection is valid and connected
    if not connection or not connection.is_connected():
        print("MySQL database connection is unavailable, please check the connection.")
        return

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL query for inserting financial data
    insert_query = """
    INSERT INTO finacial_data.financial_reports (report_date, revenue, cost_of_goods_sold, gross_profit, 
    research_and_dev_expenses, sg_and_a_expenses, other_op_income_expenses, operating_expenses, 
    operating_income, non_operating_income, pre_tax_income, income_taxes, income_after_taxes, 
    other_income, income_from_cont_ops, income_from_disc_ops, net_income, ebitda, ebit, 
    basic_shares_outstanding, shares_outstanding, basic_eps, eps_earnings_per_share)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    # Define the column names in the order they appear in the SQL query
    columns = [
        'revenue', 'cost_of_goods_sold', 'gross_profit', 'research_and_dev_expenses',
        'sg_and_a_expenses', 'other_op_income_expenses', 'operating_expenses', 'operating_income',
        'non_operating_income', 'pre_tax_income', 'income_taxes', 'income_after_taxes',
        'other_income', 'income_from_cont_ops', 'income_from_disc_ops', 'net_income',
        'ebitda', 'ebit', 'basic_shares_outstanding', 'shares_outstanding',
        'basic_eps', 'eps_earnings_per_share'
    ]

    # Prepare the values for insertion, ensuring they align with the columns
    values = [report_date] + [data_dict.get(col, None) for col in columns]

    try:
        # Execute the insert operation
        cursor.execute(insert_query, values)
        connection.commit()  # Commit the transaction to save changes
        print(f"Successfully inserted data: {report_date}")
    except mysql.connector.Error as err:
        # Handle any errors that occur during the insert
        print(f"Error inserting data: {err}")
    finally:
        # Close the cursor
        cursor.close()
