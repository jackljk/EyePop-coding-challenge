import re
from eyepop import EyePopSdk
import streamlit as st
# variables
units = {'mg', 'g', '%', 'kg', 'lb', 'oz'}

NUTRITIONS = [
    'protein', 'fat', 'calories', 'sugar', 'sodium', 'fiber', 'carbohydrate', 'cholesterol', 'carbs'
]
THRESHOLD = 10

@st.cache_data
def call_eye_pop():
    if st.session_state.uploaded_file is None:
        return
    # save the uploaded file to /assests/uploads/uploaded_image.png
    filepath = 'assets/uploads/uploaded_image.png'
    with open(filepath, 'wb') as f:
        f.write(st.session_state.uploaded_file.getvalue())
    
    with st.spinner("Processing..."):
        # send file to eyepop api to get the result
        with EyePopSdk.endpoint() as endpoint:
            response = endpoint.upload(filepath).predict()
            
    return response

def update_state_vars(response):
    st.session_state.nutrition_data = get_nutrition_values(response, NUTRITIONS, THRESHOLD, st.session_state.confidence_threshold)
    st.session_state.raw_response = response
    
    



def get_nutrition_values(response, nutritions, threshold, confidence_threshold=0.5):
    """
    Extracts nutritional information from the response based on the given nutrition strings and threshold.

    Args:
        response (dict): A dictionary containing the response object from the EyePop API.
        nutritions (list): A list of strings representing the nutrition keywords to look for.
        threshold (int or float): The threshold value to determine proximity in 'y' values.

    Returns:
        dict: A dictionary with the nutritional information in a JSON format.
    """
    response_obj = response['objects']
    extracted_nutrition = parse_result(response_obj, nutritions, threshold, confidence_threshold)
    nutrition_dict = nutrition_values_to_json(extracted_nutrition)
    return nutrition_dict



def parse_result(response_obj, nutritions, threshold, confidence_threshold=0.5):
    """
    Parses the response object to extract nutritional information based on given nutrition strings and a threshold.

    Args:
        response_obj (list): A list of dictionaries representing objects with text and 'y' value information.
        nutritions (list): A list of strings representing the nutrition keywords to look for.
        threshold (int or float): The threshold value to determine proximity in 'y' values.

    Returns:
        list: A list of dictionaries, each containing a 'nutrition' key with the nutrition name and a 'values' key with a list of corresponding values found within the threshold.
    """
    # get all the objects that contain nutrition information
    nutrition_objs = []
    for obj in response_obj:
        try:
            if any([nutr in obj['texts'][0]['text'].lower().replace(' ', '') for nutr in nutritions]) and obj['confidence'] >= confidence_threshold:
                nutrition_objs.append(obj)
        except:
            print('Error:', obj)
            # remove the object from the list
            response_obj.remove(obj)
            continue
            
    # Going through each nutritional information object and extracting the values and find corresponding values by finding text that are within a threshold of a 'y' value from it
    extracted_nutrition = []
    for obj in nutrition_objs:
        # get the 'y' value of the object
        y = obj['y']
        
        extracted_vals = []
        # loop through all the objects and find the ones that are within the threshold of the 'y' value
        for obj2 in response_obj:
            if obj2['y'] - threshold <= y <= obj2['y'] + threshold and obj2['confidence'] >= confidence_threshold:
                print(obj2['confidence'], confidence_threshold)
                val = obj2['texts'][0]['text']
                val_x = obj2['x']
                if val == obj['texts'][0]['text']:
                    continue
                extracted_vals.append((val_x, val))
        
        # sort the extracted values by x value and return only the x value
        extracted_vals = [val[1] for val in sorted(extracted_vals, key=lambda x: x[0])]
        
        # add to the extracted nutrition list
        extracted_nutrition.append({
            'nutrition': obj['texts'][0]['text'],
            'values': extracted_vals
        })
        
    return extracted_nutrition

def nutrition_values_to_json(extracted_nutrition):
    """
    Converts the extracted nutritional information to a JSON format.
    
    Args:
        extracted_nutrition (list): A list of dictionaries, each containing a 'nutrition' key with the nutrition name and a 'values' key with a list of corresponding values.
        
    Returns:
        dict: A dictionary with the nutritional information in a JSON format.
    """
    parsed_nutrition = []
    for nutr in extracted_nutrition:
        nutrition = nutr['nutrition']
        values = nutr['values']
        
        clean_vals = clean_nutrition_values(values)
        
        parsed_vals = []
        for val in clean_vals:
            if re.sub(r'[^A-Za-z0-9]', '', val).isalpha():
                if 'serving' in nutrition.lower():
                    nutrition = nutrition + ' ' + val
                else:
                    nutrition = val + ' ' + nutrition
            else:
                parsed_vals.append(val)
        parsed_nutrition.append({
            'nutrition': nutrition,
            'values': parsed_vals
        })
        
    nutrition_dict = {}
    for nutr in parsed_nutrition:
        nutrition = nutr['nutrition']
        values = nutr['values']
        
        # remove all values with % in them
        values = [val for val in values if '%' not in val]
        if 'serving' in nutrition.lower():
            nutrition = 'serving'
        
        if len(values) == 1:
            nutrition_dict[nutrition.capitalize()] = values[0]
        else:
            for i, val in enumerate(values):
                nutrition_dict[f'{nutrition.capitalize()}_{i}'] = val
    
    return nutrition_dict

def clean_nutrition_values(values):
    clean_vals = []
    i = 0
    while i < len(values):
        # Check if the current item is a number and the next item is a unit
        if i + 1 < len(values) and values[i + 1] in units:
            clean_vals.append(values[i] + values[i + 1])  # Join number and unit
            i += 2  # Skip the unit
        else:
            clean_vals.append(values[i])  # Add the item as-is
            i += 1
            
    return clean_vals
