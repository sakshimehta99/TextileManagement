import streamlit as st
import pandas as pd

# Initialize session state for storing data and current page
if 'data' not in st.session_state:
    st.session_state['data'] = []

if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

# Function to add data to the session state
def add_data(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight):
    # Check for duplicate SR No.
    existing_sr_no = [record['SR No.'] for record in st.session_state['data']]
    if sr_no in existing_sr_no:
        st.error(f'SR No. {sr_no} already exists. Please use a unique SR No.')
    else:
        st.session_state['data'].insert(0, {
            'SR No.': sr_no,
            'ID1': id1, 'METRE1': metre1,
            'ID2': id2, 'METRE2': metre2,
            'ID3': id3, 'METRE3': metre3,
            'ID4': id4, 'METRE4': metre4,
            'ID5': id5, 'METRE5': metre5,
            'WEIGHT': weight
        })
        st.success('Data added successfully!')

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

# Render navigation bar
render_navbar()

# Render content based on the current page
page = st.session_state['page']

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
        add_data(sr_no, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight)

    # Display the data below the form
    if st.session_state['data']:
        st.header('Production Data')
        df = pd.DataFrame(st.session_state['data'])
        st.dataframe(df)

elif page == 'view_data':
    st.header('View Data')
    if st.session_state['data']:
        df = pd.DataFrame(st.session_state['data'])
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
