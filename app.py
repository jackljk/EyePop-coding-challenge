import streamlit as st
from dotenv import load_dotenv
from helpers import call_eye_pop, update_state_vars
import os

# for deployment
try:
    # set environment variables using os by getting from the st.secrets
    os.environ['EYEPOP_SECRET_KEY'] = st.secrets['keys']['EYEPOP_SECRET_KEY']
    os.environ['EYEPOP_POP_ID'] = st.secrets['keys']['EYEPOP_POP_ID']
except:
    pass

# for local testing
load_dotenv()



if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None   
    st.session_state.nutrition_data = None
    st.session_state.raw_response = None




st.title("Nutrition Label Reader")

format_option = st.selectbox("Select format", ["json", "dataframe (editable)"])
st.slider("Confidence threshold", 0.0, 1.0, 0.5, key="confidence_threshold")
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    st.session_state.uploaded_file = uploaded_file
    response = call_eye_pop(uploaded_file)
    update_state_vars(response)
    
col1, col2 = st.columns(2)

with col1:
    if st.session_state.uploaded_file is not None or st.session_state.nutrition_data is not None:
        st.write("Original Image")
        st.image(st.session_state.uploaded_file, caption="Uploaded PNG")
    else:
        st.write("Upload an image to get the result")
        
with col2:
    if st.session_state.uploaded_file is not None or st.session_state.nutrition_data is not None:
        st.write("Result")        
        # Create containers for both formats
        json_container = st.empty()
        dataframe_container = st.empty()
        
        # Populate both containers
        with json_container:
            st.json(st.session_state.nutrition_data)
        
        with dataframe_container:
            st.data_editor(st.session_state.nutrition_data)
        
        # Show/hide based on selection
        if format_option == "json":
            dataframe_container.empty()
        else:
            json_container.empty()
            
if st.session_state.uploaded_file is not None or st.session_state.raw_response is not None:            
    st.write("Raw Response")
    st.json(st.session_state.raw_response, expanded=False)