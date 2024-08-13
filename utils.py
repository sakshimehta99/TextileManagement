import streamlit as st
import mysql.connector
from mysql.connector import errorcode
import datetime
import pdfkit
import os

# Function to connect to the MySQL database
def connect_db():
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",  # Replace with your MySQL host
            user="root",  # Replace with your MySQL username
            password="root",  # Replace with your MySQL password
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
                          quality VARCHAR(50),
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
                          weight VARCHAR(50),
                          category VARCHAR(50),
                        remarks VARCHAR(50),
                       today_date DATE)''')
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
                          quality VARCHAR(50),
                          metre INT,
                          weight VARCHAR(50),
                          date VARCHAR(10),
                          machine_no VARCHAR(10),
                          category VARCHAR(50),
                          remarks VARCHAR(50),
                          today_date DATE
                          )''')
        conn.close()

# Function to add data to the database
def add_data_to_db(sr_no, quality, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight, category, remarks,today_date):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        try:
            cursor.execute('''INSERT INTO production_data (sr_no, quality, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight, category, remarks, today_date)
                              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)''', 
                           (sr_no, quality, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight, category, remarks, today_date))
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
        st.session_state['data'].insert(0, [sr_no, quality, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight, category, remarks, today_date])

# Function to transform and insert data into the long format table
def transform_and_insert_data_long(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight   ):
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

# # Function to transform and store daily stock data using PARTITION BY and ORDER BY
# def transform_and_store_daily_stock_data():
#     conn = connect_db()
#     if conn is not None:
#         cursor = conn.cursor()

#         # Use window function to get the last record for each sr_no
#         cursor.execute('''
#             SELECT DISTINCT
#                 sr_no,
#                 FIRST_VALUE(metre) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS metre,
#                 FIRST_VALUE(weight) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS weight,
#                 FIRST_VALUE(date) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS date,
#                 FIRST_VALUE(machine_no) OVER (PARTITION BY sr_no ORDER BY metre DESC) AS machine_no
#             FROM production_data_long
#         ''')
#         data = cursor.fetchall()
#         cursor.close()

#         insert_query = ("INSERT INTO daily_stock_data (sr_no, metre, weight, date, machine_no) "
#                         "VALUES (%s, %s, %s, %s, %s) "
#                         "ON DUPLICATE KEY UPDATE metre=%s, weight=%s, date=%s, machine_no=%s")

#         for row in data:
#             sr_no, metre, weight, date, machine_no = row
#             cursor = conn.cursor()
#             cursor.execute(insert_query, (sr_no, metre, weight, date, machine_no, metre, weight, date, machine_no))
#             conn.commit()
#             cursor.close()
#         conn.close()



def transform_and_store_daily_stock_data():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()

        # Use window function to get the last record for each sr_no
        cursor.execute('''
            SELECT DISTINCT
                p.sr_no,
                FIRST_VALUE(p.quality) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS quality,
                FIRST_VALUE(pd.metre) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS metre,
                FIRST_VALUE(pd.weight) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS weight,
                FIRST_VALUE(pd.date) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS date,
                FIRST_VALUE(pd.machine_no) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS machine_no,
                FIRST_VALUE(p.category) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS category,
                FIRST_VALUE(p.remarks) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS remarks,
                FIRST_VALUE(p.today_date) OVER (PARTITION BY p.sr_no ORDER BY pd.metre DESC) AS today_date
            FROM production_data_long pd
            JOIN production_data p ON pd.sr_no = p.sr_no
        ''')
        data = cursor.fetchall()
        cursor.close()

        insert_query = ("INSERT INTO daily_stock_data (sr_no, quality, metre, weight, date, machine_no, category, remarks, today_date) "
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s) "
                        "ON DUPLICATE KEY UPDATE quality=%s, metre=%s, weight=%s, date=%s, machine_no=%s, category=%s, remarks=%s, today_date=%s")

        for row in data:
            sr_no, quality, metre, weight, date, machine_no, category, remarks, today_date = row
            cursor = conn.cursor()
            cursor.execute(insert_query, (sr_no, quality, metre, weight, date, machine_no, category, remarks, today_date, quality, metre, weight, date, machine_no, category, remarks, today_date))
            conn.commit()
            cursor.close()
        conn.close()
# Function to get daily stock data from the database
def get_daily_stock_data():
    return fetch_data_from_db('SELECT * FROM daily_stock_data')


def group_and_aggregate_data(date, quality):
    quality_table_map = {
        '60 gm Plain': 'aggregated_60gm_plain',
        'Chiffon': 'aggregated_chiffon'
    }
    table_name = quality_table_map.get(quality)
    
    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            date DATE,
            quality VARCHAR(50),
            sr_no_count INT,
            metre_sum INT,
            total_stock INT,
            sales INT DEFAULT 0,
            PRIMARY KEY (date, quality)
        );
    '''

    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute(create_table_query)
        conn.commit()

        # Aggregate data
        cursor.execute('''
            SELECT quality, today_date, COUNT(sr_no) as sr_no_count, SUM(metre) as metre_sum
            FROM daily_stock_data
            WHERE today_date = %s AND quality = %s
            GROUP BY quality, today_date
        ''', (date, quality))
        result = cursor.fetchone()
        if result:
            insert_or_update_aggregated_data(result[1], result[0], result[2], result[3], table_name)
        
        else:
            insert_or_update_aggregated_data(date, quality, 0, 0, table_name)
        conn.close()

def insert_or_update_aggregated_data(date, quality, sr_no_count, metre_sum, table_name):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()

        # Fetch previous total_stock and sales from the database
        cursor.execute(f'''
            SELECT total_stock, sales FROM {table_name}
            WHERE date < %s AND quality = %s
            ORDER BY date DESC LIMIT 1
        ''', (date, quality))
        previous_data = cursor.fetchone()
        
        previous_total_stock = previous_data[0] if previous_data else 0
        previous_sales = previous_data[1] if previous_data else 0
        # Calculate new total_stock
        new_total_stock = previous_total_stock + sr_no_count - previous_sales
        
        cursor.execute(f'''
            INSERT INTO {table_name} (date, quality, sr_no_count, metre_sum, total_stock, sales)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE sr_no_count = VALUES(sr_no_count), metre_sum = VALUES(metre_sum), total_stock = {new_total_stock}
        ''', (date, quality, sr_no_count, metre_sum, new_total_stock, 0))  # Sales default to 0 initially
        conn.commit()
        conn.close()



def get_aggregated_data(table_name):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        
        # Get data for the specified table
        cursor.execute(f'''
            SELECT date, quality, sr_no_count, metre_sum, total_stock, sales
            FROM {table_name}
        ''')
        aggregated_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return aggregated_data


def create_company_table():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS client_details (
                company_code INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100),
                address VARCHAR(100),
                contact_number VARCHAR(15)
            );
        ''')
        conn.commit()
        conn.close()

# Function to add company details to the database
def add_company_to_db(name, address, contact_number):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO client_details (name, address, contact_number)
            VALUES (%s, %s, %s)
        ''', (name, address, contact_number))
        conn.commit()
        conn.close()
        st.success(f'Company {name} added successfully!')


def create_order_table():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_requests (
                order_id INT AUTO_INCREMENT PRIMARY KEY,
                company_code INT,
                quantity INT,
                completed_quantity INT DEFAULT 0,
                quality VARCHAR(50),
                status ENUM('pending', 'completed') DEFAULT 'pending',
                FOREIGN KEY (company_code) REFERENCES client_details(company_code)
            );
        ''')
        conn.commit()
        conn.close()
        return


# Function to fetch company details for the dropdown list
def get_company_details():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT company_code, name FROM client_details')
        companies = cursor.fetchall()
        conn.close()
        return companies
    return []


def get_company_address(company_code):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT address FROM client_details WHERE company_code = %s', (company_code,))
    address = cursor.fetchone()
    conn.close()
    return address[0] if address else ''



# Function to add order request to the database
def add_order_to_db(today_date, company_code, quantity, quality):
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO order_requests (today_date,company_code, quantity, quality)
            VALUES (%s,%s, %s, %s)
        ''', (today_date, company_code, quantity, quality))
        conn.commit()   
        conn.close()
        st.success('Order request added successfully!')


# Function to fetch pending orders from the database
def get_pending_orders():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT o.order_id, c.name, o.quality, o.completed_quantity, o.quantity
            FROM order_requests o
            JOIN client_details c ON o.company_code = c.company_code
            WHERE o.completed_quantity < o.quantity
        ''')
        pending_orders = cursor.fetchall()
        conn.close()
        return pending_orders
    return []


def create_invoice_table():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_header (
    challan_number INT AUTO_INCREMENT PRIMARY KEY,
    date DATE,
    company_code INT,
    company_name VARCHAR(100),
    address TEXT,
    broker VARCHAR(100),
    quality VARCHAR(50),
    total_taka INT,
    FOREIGN KEY (company_code) REFERENCES client_details(company_code)
);
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoice_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challan_number INT,
    sr_no VARCHAR(50),
    quality VARCHAR(50),                   
    metre INT,
    weight INT,
    machine_no VARCHAR(10),
    FOREIGN KEY (challan_number) REFERENCES invoice_header(challan_number)
);

        ''')
        conn.commit()
        conn.close()
        return

def get_stock_details(sr_no):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT metre, weight, machine_no FROM daily_stock_data WHERE sr_no = %s', (sr_no,))
    stock = cursor.fetchone()
    conn.close()
    return stock if stock else ('Product not found', 'Product not found', 'Product not found')


def update_order_status(company_code, quality, sr_no_count):
    conn = connect_db()
    cursor = conn.cursor(buffered=True)

    # Get the corresponding order based on company code, quality, and status
    cursor.execute('''
        SELECT order_id, quantity, completed_quantity FROM order_requests
        WHERE company_code = %s AND quality = %s AND status = 'pending'
        ORDER BY order_id ASC LIMIT 1
    ''', (company_code, quality))
    order = cursor.fetchone()

    if order:
        order_id, quantity, completed_quantity = order  
        completed_quantity += sr_no_count  # Update the completed quantity

        if completed_quantity > quantity:
            st.error('there is some error, completed quantity > quantity.')

        # Check if the completed quantity exceeds or matches the total quantity
        if completed_quantity == quantity:
            # completed_quantity = quantity  # Cap the completed quantity
            # Mark the order as completed
            cursor.execute('UPDATE order_requests SET completed_quantity = %s, status = %s WHERE order_id = %s', 
                           (completed_quantity, 'completed', order_id))
        else:
            # Just update the completed quantity
            cursor.execute('UPDATE order_requests SET completed_quantity = %s WHERE order_id = %s', 
                           (completed_quantity, order_id))
        
        conn.commit()

    conn.close()


# Function to update sales count
def update_sales_count(date, quality, sr_no_count):
    quality_table_map = {
        '60 gm Plain': 'aggregated_60gm_plain',
        'Chiffon': 'aggregated_chiffon'
    }
    table_name = quality_table_map.get(quality)
    

    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(f'''
        UPDATE {table_name}
        SET sales = sales + %s
        WHERE date = %s
    ''', (sr_no_count, date))
    
    conn.commit()
    conn.close()
    return


def add_invoice_to_db(challan_number, date, company_code, company_name, address, broker, quality, sr_no_list):
    sr_no_count = len(sr_no_list)
    conn = connect_db()
    cursor = conn.cursor()


    # Insert data into the invoice_header table
    cursor.execute('''
        INSERT INTO invoice_header (challan_number, date, company_code, company_name, address, broker, quality, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (challan_number, date, company_code, company_name, address, broker, quality, sr_no_count))


    for sr_no in sr_no_list:    
        metre, weight, machine_no = get_stock_details(sr_no)
        if metre is not None and weight is not None:
            cursor.execute('''
                INSERT INTO invoice_details (challan_number, sr_no,quality, metre, weight, machine_no)
                VALUES (%s, %s, %s, %s, %s,%s)
            ''', (challan_number, sr_no, quality, metre, weight, machine_no))    
    conn.commit()
    conn.close()
    
    # Update order status
    update_order_status(company_code, quality, sr_no_count)
    # Reduce stock, update sales
    update_sales_count(date, quality, sr_no_count)
    return  


def show_invoice_details(challan_number):
    conn = connect_db()
    cursor = conn.cursor()

    # Fetch header details
    cursor.execute('''
        SELECT challan_number, date, company_code, company_name, address, broker, quality, quantity
        FROM invoice_header
        WHERE challan_number = %s
    ''', (challan_number,))
    header = cursor.fetchone()

    # Fetch invoice details
    cursor.execute('''
        SELECT sr_no, quality, metre, weight, machine_no
        FROM invoice_details
        WHERE challan_number = %s
    ''', (challan_number,))
    details = cursor.fetchall()
    conn.close()

    # Display the dialog box (using expander)
    with st.expander(f"Invoice Details for {challan_number}", expanded=True):
        if header and details:
            st.markdown(f"### Invoice Details for Challan Number: {header[0]}")
            st.write(f"**Date:** {header[1]}")
            st.write(f"**Company Code:** {header[2]}")
            st.write(f"**Company Name:** {header[3]}")
            st.write(f"**Address:** {header[4]}")
            st.write(f"**Broker:** {header[5]}")
            st.write(f"**Quality:** {header[6]}")
            st.write(f"**Quantity:** {header[7]}")

            st.write("**SR No. Details:**")
            st.table(details)

            # Handle Print button click
            if st.button("Print", key=f"print_{challan_number}"):
                st.session_state[f'print_triggered_{challan_number}'] = True

        # Check if print was triggered
        if st.session_state.get(f'print_triggered_{challan_number}', False):
            st.write(f"Printing invoice for Challan Number: {challan_number}")
            st.write('<script>window.print();</script>', unsafe_allow_html=True)
            st.session_state[f'print_triggered_{challan_number}'] = False  # Reset after printing

    


    

# Function to handle page navigation
def navigate_to(page):
    st.session_state['page'] = page


# Function to render the navigation bar
def render_navbar():
    st.sidebar.title("Navigation")
    pages = ['Home', 'ADD PRODUCTION', 'VIEW DATA', 'PRODUCT DATA', 'DAILY STOCK DATA','DAILY REPORT','Add Client Details','ADD ORDER','Pending Orders','MAKE INVOICE','VIEW INVOICE']
    for page in pages:
        st.sidebar.button(page, on_click= navigate_to, args=(page.lower().replace(' ', '_'),))
