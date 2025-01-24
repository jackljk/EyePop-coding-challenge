import streamlit as st
import pandas as pd
from io import StringIO
from dotenv import load_dotenv
from eyepop import EyePopSdk
import os

load_dotenv()

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    # create 2 columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("Original Image")
        st.image(uploaded_file, caption="Uploaded PNG")
    
    # save the uploaded file to /assests/uploads/uploaded_image.png
    filepath = 'assets/uploads/uploaded_image.png'
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getvalue())
    
    # send file to eyepop api to get the result
    with EyePopSdk.endpoint() as endpoint:
        result = endpoint.upload(filepath).predict()
        print(result)
        st.write(result)
        
    with col2:
        st.write("Result")
        st.write(result)