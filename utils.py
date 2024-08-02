import streamlit as st
import mysql.connector
from mysql.connector import errorcode

# Function to connect to the MySQL database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",  # Replace with your MySQL host
            user="root",  # Replace with your MySQL username
            password="S@kshi27",  # Replace with your MySQL password
            database="textile_db"  # Replace with your database name
        )
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            st.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            st.error("Database does not exist")
        else:
            st.error(err)
    return None

# Function to initialize the database (create tables if they don't exist)
def init_db():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS production_data (
                          sr_no VARCHAR(50) PRIMARY KEY,
                          id1 VARCHAR(50),
                          metre1 VARCHAR(50),
                          id2 VARCHAR(50),
                          metre2 VARCHAR(50),
                          id3 VARCHAR(50),
                          metre3 VARCHAR(50),
                          id4 VARCHAR(50),
                          metre4 VARCHAR(50),
                          id5 VARCHAR(50),
                          metre5 VARCHAR(50),
                          weight VARCHAR(50))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS production_data_long (
                          sr_no VARCHAR(50),
                          id VARCHAR(50),
                          metre INT,
                          weight VARCHAR(50),
                          date VARCHAR(10),
                          machine_no VARCHAR(10),
                          worker_id VARCHAR(10),
                          metre_count INT)''')  # Added metre_count column
        cursor.execute('''CREATE TABLE IF NOT EXISTS daily_stock_data (
                          sr_no VARCHAR(50) PRIMARY KEY,
                          metre INT,
                          weight VARCHAR(50),
                          date VARCHAR(10),
                          machine_no VARCHAR(10))''')
        conn.close()

# Function to add data to the database
def add_data_to_db(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO production_data (sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', 
                           (sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight))
            conn.commit()
            st.success('Data added successfully!')
            transform_and_insert_data_long(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight)
            transform_and_store_daily_stock_data()
        except mysql.connector.IntegrityError:
            st.error(f'SR No. {sr_no} already exists. Please use a unique SR No.')
        conn.close()
        # Update session state with new data
        if 'data' not in st.session_state:
            st.session_state['data'] = []
        st.session_state['data'].insert(0, [sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight])

# Function to transform and insert data into the long format table
def transform_and_insert_data_long(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight):
    def parse_id(id_value):
        date_part = id_value[:8]
        machine_no_part = id_value[8:11]
        worker_id_part = id_value[-4:]
        
        # Convert date_part from YYYYMMDD to DD-MM-YYYY
        date_converted = f"{date_part[:2]}-{date_part[2:4]}-{date_part[4:8]}"
        
        return date_converted, machine_no_part, worker_id_part

    transformed_data = [
        (sr_no, id1, metre1, weight, *parse_id(id1)),
        (sr_no, id2, metre2, weight, *parse_id(id2)),
        (sr_no, id3, metre3, weight, *parse_id(id3)),
        (sr_no, id4, metre4, weight, *parse_id(id4)),
        (sr_no, id5, metre5, weight, *parse_id(id5)),
    ]
    
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        insert_query = ("INSERT INTO production_data_long (sr_no, id, metre, weight, date, machine_no, worker_id, metre_count) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)")
        
        # Get the existing data for the given sr_no to compute metre_count
        cursor.execute('SELECT sr_no, metre FROM production_data_long WHERE sr_no = %s', (sr_no,))
        existing_metre_data = cursor.fetchall()
        
        previous_metre = 0.0
        for row in transformed_data:
            metre = float(row[2])
            if not existing_metre_data and previous_metre == 0:
                metre_count = metre  # First entry for the sr_no
            else:
                metre_count = metre - previous_metre
            previous_metre = metre
            cursor.execute(insert_query, row + (metre_count,))
        
        conn.commit()
        cursor.close()
        conn.close()

# Function to get data from the database
def get_data_from_db():
    return fetch_data_from_db('SELECT * FROM production_data')

# Function to get long format data from the database
def get_long_format_data():
    return fetch_data_from_db('SELECT * FROM production_data_long')

# General function to fetch data from the database
def fetch_data_from_db(query):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()
    return []

# Function to transform and store daily stock data using PARTITION BY and ORDER BY
def transform_and_store_daily_stock_data():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()

        # Use window function to get the last record for each sr_no
        cursor.execute('''
            SELECT DISTINCT
                sr_no,
                FIRST_VALUE(metre) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS metre,
                FIRST_VALUE(weight) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS weight,
                FIRST_VALUE(date) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS date,
                FIRST_VALUE(machine_no) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS machine_no
            FROM production_data_long
        ''')
        data = cursor.fetchall()
        cursor.close()

        insert_query = ("INSERT INTO daily_stock_data (sr_no, metre, weight, date, machine_no) "
                        "VALUES (%s, %s, %s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE metre=%s, weight=%s, date=%s, machine_no=%s")

        for row in data:
            sr_no, metre, weight, date, machine_no = row
            cursor = conn.cursor()
            cursor.execute(insert_query, (sr_no, metre, weight, date, machine_no, metre, weight, date, machine_no))
            conn.commit()
            cursor.close()
        conn.close()

# Function to get daily stock data from the database
def get_daily_stock_data():
    return fetch_data_from_db('SELECT * FROM daily_stock_data')

# Function to handle page navigation
def navigate_to(page):
    st.session_state['page'] = page

# Function to render the navigation bar
def render_navbar():
    st.sidebar.title("Navigation")
    pages = ['Home', 'ADD PRODUCTION', 'VIEW DATA', 'MAKE BILL', 'DELIVERY REPORT', 'MANIPULATION', 'PRODUCT DATA', 'DAILY STOCK DATA']
    for page in pages:
        st.sidebar.button(page, on_click=navigate_to, args=(page.lower().replace(' ', '_'),))
