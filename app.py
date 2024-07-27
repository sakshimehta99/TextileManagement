import streamlit as st
import pandas as pd
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
                          id INT,
                          metre INT,
                          weight VARCHAR(50))''')
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
        except mysql.connector.IntegrityError:
            st.error(f'SR No. {sr_no} already exists. Please use a unique SR No.')
        conn.close()

# Function to transform and insert data into the long format table
def transform_and_insert_data_long(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight):
    transformed_data = [
        (sr_no, id1, metre1, weight),
        (sr_no, id2, metre2, weight),
        (sr_no, id3, metre3, weight),
        (sr_no, id4, metre4, weight),
        (sr_no, id5, metre5, weight),
    ]
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        insert_query = ("INSERT INTO production_data_long (sr_no, id, metre, weight) "
                        "VALUES (%s, %s, %s, %s)")
        for row in transformed_data:
            cursor.execute(insert_query, row)
        conn.commit()
        cursor.close()
        conn.close()

# Function to get data from the database
def get_data_from_db():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM production_data ORDER BY sr_no DESC')
        data = cursor.fetchall()
        conn.close()
        return data
    return []

# Function to get long format data from the database
def get_long_format_data():
    conn = connect_db()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM production_data_long ORDER BY sr_no DESC')
        data = cursor.fetchall()
        conn.close()
        return data
    return []

# Function to handle page navigation
def navigate_to(page):
    st.session_state['page'] = page

# Function to render the navigation bar
def render_navbar():
    st.sidebar.title("Navigation")
    st.sidebar.button('Home', on_click=navigate_to, args=('home',))
    st.sidebar.button('ADD PRODUCTION', on_click=navigate_to, args=('add_production',))
    st.sidebar.button('VIEW DATA', on_click=navigate_to, args=('view_data',))
    st.sidebar.button('MAKE BILL', on_click=navigate_to, args=('make_bill',))
    st.sidebar.button('DELIVERY REPORT', on_click=navigate_to, args=('delivery_report',))
    st.sidebar.button('MANIPULATION', on_click=navigate_to, args=('manipulation',))
    st.sidebar.button('PRODUCT DATA', on_click=navigate_to, args=('product_data',))

# Initialize the database
init_db()

# Render navigation bar
render_navbar()

# Render content based on the current page
page = st.session_state.get('page', 'home')

if page == 'home':
    st.title('Home Page')
    st.write('Welcome to the home page. Use the sidebar to navigate.')

elif page == 'add_production':
    st.header('Add Production')
    sr_no = st.text_input('SR No.')
    col1, col2 = st.columns(2)
    with col1:
        id1 = st.text_input('ID1')
        id2 = st.text_input('ID2')
        id3 = st.text_input('ID3')
        id4 = st.text_input('ID4')
        id5 = st.text_input('ID5')
    with col2:
        metre1 = st.text_input('METRE1')
        metre2 = st.text_input('METRE2')
        metre3 = st.text_input('METRE3')
        metre4 = st.text_input('METRE4')
        metre5 = st.text_input('METRE5')
    weight = st.text_input('WEIGHT')
    if st.button('SUBMIT'):
        add_data_to_db(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight)

    # Display the data below the form
    data = get_data_from_db()
    if data:
        st.header('Production Data')
        df = pd.DataFrame(data, columns=['SR No.', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT'])
        st.dataframe(df)

elif page == 'view_data':
    st.header('View Data')
    data = get_data_from_db()
    if data:
        df = pd.DataFrame(data, columns=['SR No.', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT'])
        st.dataframe(df)
    else:
        st.write('No data available.')

elif page == 'make_bill':
    st.header('Make Bill')
    # Implement functionality for Make Bill

elif page == 'delivery_report':
    st.header('Delivery Report')
    # Implement functionality for Delivery Report

elif page == 'manipulation':
    st.header('Manipulation')
    # Implement functionality for Manipulation

elif page == 'product_data':
    st.header('Product Data')
    df = pd.DataFrame(get_long_format_data(), columns=['SR No.', 'ID', 'METRE', 'WEIGHT'])
    st.dataframe(df)


