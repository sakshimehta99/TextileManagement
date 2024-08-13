import streamlit as st
import pandas as pd
import datetime
from utils import init_db,connect_db, render_navbar, navigate_to, add_data_to_db, get_data_from_db, get_long_format_data, get_daily_stock_data,group_and_aggregate_data
from utils import get_aggregated_data, create_company_table, add_company_to_db, create_order_table, get_company_details, add_order_to_db, get_pending_orders,create_invoice_table, get_company_address, add_invoice_to_db, get_stock_details
from utils import show_invoice_details





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
    quality = st.selectbox('Quality', ['60 gm Plain', 'Chiffon'])
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
    category = st.text_input('Category')
    remarks = st.text_input('Remarks')
    if st.button('SUBMIT'):
        today_date = datetime.datetime.today().strftime('%Y-%m-%d')  # Get today's date
        add_data_to_db(sr_no, quality, id1, metre1, id2, metre2, id3, metre3, id4, metre4, id5, metre5, weight, category, remarks, today_date)
    # Display the data below the form
    if 'data' not in st.session_state:
        st.session_state['data'] = get_data_from_db()
    
    if st.session_state['data']:
        st.header('Production Data')
        df = pd.DataFrame(st.session_state['data'], columns=['SR No.','Quality', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT','Category', 'Remarks', 'Today_date'])
        st.dataframe(df)

elif page == 'view_data':
    st.title('View Data')
    data = get_data_from_db()
    df = pd.DataFrame(data, columns=['SR No.','QUALITY', 'ID1', 'METRE1', 'ID2', 'METRE2', 'ID3', 'METRE3', 'ID4', 'METRE4', 'ID5', 'METRE5', 'WEIGHT', 'CATEGORY', 'REMARKS','today_date'])
    st.dataframe(df)
elif page == 'product_data':
    st.title('Product Data')
    data = get_long_format_data()
    df = pd.DataFrame(data, columns=['SR No.', 'ID', 'Metre', 'Weight', 'Date', 'Machine No.', 'Worker ID', 'Metre Count'])
    st.dataframe(df)
elif page == 'daily_stock_data':
    st.title('Daily Stock Data')
    data = get_daily_stock_data()
    df = pd.DataFrame(data, columns=['SR No.', 'QUALITY','Metre', 'Weight', 'Date', 'Machine No.','CATEGORY', 'REMARKS','Today_date'])
    st.dataframe(df)
# Additional pages can be added here


elif page == 'daily_report':

    st.title('Aggregate Daily Stock Data')

    # Date input
    date = st.text_input('Date (YYYY-MM-DD)')

    # Quality dropdown
    quality = st.selectbox('Quality', ['60 gm Plain', 'Chiffon'])

    if st.button('Submit'):
        if date:
            group_and_aggregate_data(date, quality)
            st.success(f'Data aggregated and stored for {quality} on {date}.')
        else:
            st.error('Please enter a date.')


    st.header('Aggregated Daily Stock Data - 60 gm Plain')
    aggregated_data_60gm_plain = get_aggregated_data('aggregated_60gm_plain')
    df_60gm_plain = pd.DataFrame(aggregated_data_60gm_plain, columns=['Date', 'Quality', 'SR No. Count', 'Metre Sum', 'Total Stock', 'Sales'])
    st.dataframe(df_60gm_plain)
    
    st.header('Aggregated Daily Stock Data - Chiffon')
    aggregated_data_chiffon = get_aggregated_data('aggregated_chiffon')
    df_chiffon = pd.DataFrame(aggregated_data_chiffon, columns=['Date', 'Quality', 'SR No. Count', 'Metre Sum', 'Total Stock', 'Sales'])
    st.dataframe(df_chiffon)
    
    # st.header('Update Sales')
    # update_date = st.text_input('Date to Update Sales (YYYY-MM-DD)')
    # update_quality = st.selectbox('Quality to Update', ['60 gm Plain', 'Chiffon'])
    # sales_input = st.number_input('Sales', min_value=0)

    # if st.button('Update Sales'):
    #     update_sales(update_date, update_quality, sales_input)
    #     st.success(f'Sales updated for {update_quality} on {update_date}.')


# Initialize the database and create the company_details table
# create_company_table()

elif page == 'add_client_details': 
    create_company_table()

    st.title('Add Company Details')

    with st.form(key='company_form'):
        name = st.text_input('Name')
        address = st.text_area('Address')
        contact_number = st.text_input('Contact Number')
        submit_button = st.form_submit_button(label='Submit')

    if submit_button:
        if name and address and contact_number:
            add_company_to_db(name, address, contact_number)
        else:
            st.error('Please fill in all fields.')



elif page == 'add_order':

    # Initialize the database and create the order_requests table
    create_order_table()

    # Create the Streamlit form for order requests
    st.title('Add Order Request')

    # Fetch company details for the dropdown list
    companies = get_company_details()
    company_dict = {name: code for code, name in companies}

    company_name = st.selectbox('Company Name', list(company_dict.keys()))
    company_code = company_dict[company_name]
    quantity = st.number_input('Quantity', min_value=1, step=1)
    quality = st.selectbox('Quality', ['60 gm Plain', 'Chiffon'])

    if st.button('Submit'):
        if company_name and quantity and quality:
            today_date = datetime.datetime.today().strftime('%Y-%m-%d')
            add_order_to_db(today_date, company_code, quantity, quality)
        else:
            st.error('Please fill in all fields.')


# Create a Streamlit page to display pending orders
elif page == 'pending_orders':
    st.title('Pending Orders')
    
    pending_orders = get_pending_orders()
    
    if pending_orders:
        order_data = []
        for order in pending_orders:
            order_id, company_name, quality, completed_quantity, quantity = order
            progress = f"{completed_quantity}/{quantity}"
            order_data.append([company_name, quality, progress])
        
        df = pd.DataFrame(order_data, columns=['Company Name', 'Quality', 'Quantity'])
        st.dataframe(df)
    else:
        st.write('No pending orders.')



elif page == 'make_invoice':
    
    create_invoice_table()
    # Initialize the form
    st.title('Create Challan')
    # create_invoice_table()

    # Auto-incremented challan number
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT MAX(challan_number) FROM invoice_details')
    result = cursor.fetchone()
    conn.close()
    challan_number = result[0] + 1 if result[0] else 1
    st.write(f'Challan Number: {challan_number}')

    # Date input
    date = datetime.datetime.today().strftime('%Y-%m-%d')
    st.write(f'Date: {date}')

    # Company details
    companies = get_company_details()
    company_dict = {name: code for code, name in companies}
    company_name = st.selectbox('Company Name', list(company_dict.keys()))
    company_code = company_dict[company_name]
    address = get_company_address(company_code)
    st.write(f'Address: {address}')

    # Broker and Quality
    broker = st.text_input('Broker')
    quality = st.selectbox('Quality', ['60 gm Plain', 'Chiffon'])

    # SR No. inputs
    sr_no_list = []
    metre_list = []
    weight_list = []
    total_metre = 0 
    for i in range(28):
        col1, col2, col3 = st.columns(3)
        with col1:
            sr_no = st.text_input(f'SR No. {i + 1}', key=f'sr_no_{i}')
            if sr_no:
                sr_no_list.append(sr_no)
                metre, weight, machine_no = get_stock_details(sr_no)
                metre_list.append(metre)
                weight_list.append(weight)
                # Handle None or invalid metre values
                if metre is not None and isinstance(metre, (int, float)):
                    total_metre += metre
                else:
                    metre_list[-1] = 'N/A'  # Replace invalid metre with 'N/A'


        with col2:
            st.write(f'Metre: {metre_list[-1]}' if sr_no else 'Metre: N/A')
            
        with col3:
            st.write(f'Weight: {weight_list[-1]}' if sr_no else 'Weight: N/A')
        
        # Display totals
    sr_no_count = 0
    sr_no_count =len(sr_no_list)
    st.write(f"Total SR No. Count: {len(sr_no_list)}")
    st.write(f"Total Metre: {total_metre}")

    # Form submission logic here
    if st.button('Submit'):
        if company_name and broker and quality and sr_no_list:
            valid = True  # Flag to track if all SR numbers are valid
            
            for sr_no in sr_no_list:
                metre, weight, machine_no = get_stock_details(sr_no)
                if metre == 'Product not found':
                    valid = False  # Mark as invalid if any SR number is not found
                    break  # Exit the loop immediately when an invalid SR number is found

            if valid:
            # Fetch the order details to check the remaining quantity
                conn = connect_db()
                cursor = conn.cursor(buffered=True)
                cursor.execute('''SELECT quantity, completed_quantity FROM order_requests WHERE company_code = %s AND quality = %s AND status = 'pending'ORDER BY order_id ASC LIMIT 1''', 
                           (company_code, quality))
                order = cursor.fetchone()
                conn.close()

                if order:
                    quantity, completed_quantity = order
                    remaining_quantity = quantity - completed_quantity
                    print('abc',sr_no_count)
                    print('rem',remaining_quantity)
                    print('com',completed_quantity)
                    print('qua',quantity)
                    
                    if sr_no_count <= remaining_quantity:
                        # Proceed with adding the invoice and updating completed orders
                        add_invoice_to_db(challan_number, date, company_code, company_name, address, broker, quality, sr_no_list)
                        st.success('Challan created successfully!')
                    else:
                        st.error('Challan creation failed: Insufficient remaining quantity to fulfill the order.')
                else:
                    st.error('No matching order found for the provided company and quality.')
            else:
                st.error('Challan creation failed due to an invalid SR number.')
        else:
            st.error('Please fill in all required fields.')


elif page == 'view_invoice':
    st.title("View Invoices")

    # Fetch latest 20 invoices
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT challan_number, date, company_name, quality, quantity FROM invoice_header ORDER BY date DESC LIMIT 20')
    invoices = cursor.fetchall()
    conn.close()

    st.subheader("Latest 20 Invoices")
    headers = ["Challan Nos", "Date", "Company", "Quality", "Quantity", "Actions"]
    st.write("_______".join(headers))

    for invoice in invoices:
        col1, col2, col3, col4, col5, col6 = st.columns([1, 1, 1, 1, 1, 1])
        col1.write(invoice[0])  # Challan Number
        col2.write(invoice[1])  # Date
        col3.write(invoice[2])  # Company Name
        col4.write(invoice[3])  # Quality
        col5.write(invoice[4])  # Quantity
        
        if col6.button(f"View Invoice ", key=invoice[0]):
            st.session_state['show_invoice'] = invoice[0]
            show_invoice_details(invoice[0])
            # st.experimental_rerun()

# if 'show_invoice' in st.session_state:
#     challan_number = st.session_state['show_invoice']
#     show_invoice_details(challan_number)


# Ensure the current page is set in session state
if 'page' not in st.session_state:
    st.session_state['page'] = 'home'

