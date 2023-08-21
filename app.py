import os
import streamlit as st
import pandas as pd

VALID_USERNAME = 'admin'
VALID_PASSWORD = 'admin'
UPLOAD_FOLDER = "C:/Users/virajhumbre/Desktop/S3/"

# In-memory template storage (for demonstration purposes)
if 'TEMPLATES' not in st.session_state:
    st.session_state.TEMPLATES = {}

DATA_TYPE_MAPPING = {
    'object': 'object',
    'integer': 'int64',
    'float': 'float64',
    'date': 'datetime64'
}

DATA_TYPE_OPTIONS = ['object', 'int64', 'float64', 'datetime64']


def create_or_edit_template(folder_name):
    st.write(f"Create/Edit template for '{folder_name}'")
    template = st.session_state.TEMPLATES.get(folder_name, {'columns': [], 'data_types': []})

    num_columns = st.number_input("Number of Columns", min_value=1, value=len(template['columns']) or 1)

    while len(template['columns']) < num_columns:
        template['columns'].append('')
        template['data_types'].append('object')  # Default data type to 'object'

    new_columns = []  # Store new column names for the template
    new_data_types = []  # Store new data type strings for the template columns

    for i, column in enumerate(template['columns']):
        col_name = st.text_input(f"Column {i+1} Name", column)
        col_data_type = st.text_area(f"Column {i+1} Data Type", template['data_types'][i].strip())  # Remove extra whitespace

        new_columns.append(col_name)
        new_data_types.append(col_data_type)

    template['columns'] = new_columns  # Update column names in the template
    template['data_types'] = new_data_types  # Update data types in the template

    st.session_state.TEMPLATES[folder_name] = {'columns': template['columns'], 'data_types': template['data_types']}





def append_data_to_folder_file(folder_path, data_to_append):
    file_path = os.path.join(folder_path, "combined_data_1.csv")

    if os.path.exists(file_path):
        existing_data = pd.read_csv(file_path)
        combined_data = pd.concat([existing_data, data_to_append], ignore_index=True)
    else:
        combined_data = data_to_append

    combined_data.to_csv(file_path, index=False)

def overwrite_data_in_folder_file(folder_path, data_to_overwrite):
    file_path = os.path.join(folder_path, "combined_data.csv")
    data_to_overwrite.to_csv(file_path, index=False)

def validate_uploaded_columns_and_data_types(uploaded_df, template):
    uploaded_columns = list(uploaded_df.columns)
    uploaded_data_types = uploaded_df.dtypes.map(lambda x: x.name).tolist()  # Convert to string representation

    template_columns = template['columns']
    template_data_types = template['data_types']

    st.write("Uploaded Columns:", uploaded_columns)
    st.write("Uploaded Data Types:", uploaded_data_types)
    st.write("Template Columns:", template_columns)
    st.write("Template Data Types:", template_data_types)
    st.write("Converted Uploaded Data Types:", uploaded_data_types)

    mismatched_columns = set(uploaded_columns) - set(template_columns)
    mismatched_data_types = set(uploaded_data_types) - set(template_data_types)

    st.write("Mismatched Columns:", mismatched_columns)
    st.write("Mismatched Data Types:", mismatched_data_types)

    return not (mismatched_columns or mismatched_data_types)

def validate_credentials(username, password):
    return username == VALID_USERNAME and password == VALID_PASSWORD

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'txt', 'csv', 'xlsx'}

def get_upload_folders():
    return [name for name in os.listdir(UPLOAD_FOLDER) if os.path.isdir(os.path.join(UPLOAD_FOLDER, name))]

def main():
    st.title('File Upload and Dashboard')

    # Login Section
    st.subheader('Login')
    username = st.text_input('Username')
    password = st.text_input('Password', type='password')
    login_button = st.button('Login')

    if login_button:
        if validate_credentials(username, password):
            st.success('Login successful!')
            st.session_state.logged_in = True
        else:
            st.error('Invalid credentials')

    # Template Management Section
    if st.session_state.get('logged_in'):
        st.subheader('Template Management')
        selected_folder = st.selectbox('Select a folder', get_upload_folders())

        with st.form("template_form"):
            edit_template_button = st.form_submit_button('Create/Edit Template')
            if edit_template_button:
                create_or_edit_template(selected_folder)

    # Dashboard Section
    if st.session_state.get('logged_in'):
        st.subheader('Dashboard')
        selected_option = st.selectbox('Select an option', get_upload_folders())

        # File Upload Section
        st.subheader('File Upload')
        uploaded_file = st.file_uploader('Upload a file', type=['xlsx', 'csv'])

        if uploaded_file is not None:
            if allowed_file(uploaded_file.name):
                file_extension = uploaded_file.name.split('.')[-1].lower()

                if file_extension == 'xlsx':
                    uploaded_df = pd.read_excel(uploaded_file, engine='openpyxl')
                elif file_extension == 'csv':
                    uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8')

                template = st.session_state.TEMPLATES.get(selected_option, {'columns': [], 'data_types': []})

                if validate_uploaded_columns_and_data_types(uploaded_df, template):
                    with open(os.path.join(UPLOAD_FOLDER, selected_option, uploaded_file.name), 'wb') as f:
                        f.write(uploaded_file.read())
                    # Append data to the respective folder's combined file
                    folder_path = os.path.join(UPLOAD_FOLDER, selected_option)
                    append_data_to_folder_file(folder_path, uploaded_df)

                    # Overwrite data in the sales data folder's combined file
                    folder_path = os.path.join(UPLOAD_FOLDER, selected_option)
                    overwrite_data_in_folder_file(folder_path, uploaded_df)
                    st.success('File uploaded successfully')
                else:
                    st.error("Column names and/or data types of the uploaded file do not match the template.")
            else:
                st.error('Invalid file format. Allowed formats are xlsx and csv.')

if __name__ == '__main__':
    main()
