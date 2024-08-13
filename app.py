import streamlit as st
import pandas as pd
from utils import init_db, render_navbar, navigate_to, add_data_to_db, get_data_from_db, get_long_format_data, get_daily_stock_data

# Initialize the database
init_db()

# Render navigation bar
render_navbar()

# Render content based on the current page
page = st.session_state.get('page', 'home')

if page == 'home':
    st.title('Home Page')
    st.write('Welcome to the Textile Management System!')
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
    if 'data' not in st.session_state:
        st.session_state['data'] = get_data_from_db()
    
    if st.session_state['data']:
        st.header('Production Data')
        df = pd.DataFrame(st.session_state['data'], columns=['SR No.', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT'])
        st.dataframe(df)

elif page == 'view_data':
    st.title('View Data')
    data = get_data_from_db()
    df = pd.DataFrame(data, columns=['SR No.', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT'])
    st.dataframe(df)
elif page == 'product_data':
    st.title('Product Data')
    data = get_long_format_data()
    df = pd.DataFrame(data, columns=['SR No.', 'ID', 'Metre', 'Weight', 'Date', 'Machine No.', 'Worker ID', 'Metre Count'])
    st.dataframe(df)
elif page == 'daily_stock_data':
    st.title('Daily Stock Data')
    data = get_daily_stock_data()
    df = pd.DataFrame(data, columns=['SR No.', 'Metre', 'Weight', 'Date', 'Machine No.'])
    st.dataframe(df)
# Additional pages can be added here

# Ensure the current page is set in session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

