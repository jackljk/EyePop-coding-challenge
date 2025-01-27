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
def call_eye_pop(uploaded_file):
    if st.session_state.uploaded_file is None and uploaded_file != st.session_state.uploaded_file:
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
        confidence_threshold (float): Minimum confidence level for valid objects.

    Returns:
        dict: A dictionary with the nutritional information in a JSON format.
    """
    response_obj = response.get("objects", [])
    extracted_nutrition = parse_result(
        response_obj, nutritions, threshold, confidence_threshold
    )
    return nutrition_values_to_json(extracted_nutrition)


def parse_result(response_obj, nutritions, threshold, confidence_threshold=0.5):
    """
    Parses the response object to extract nutritional information based on given nutrition strings and a threshold.

    Args:
        response_obj (list): List of objects containing text and 'y' value information.
        nutritions (list): Keywords representing the nutrition to look for.
        threshold (int or float): Threshold for proximity in 'y' values.
        confidence_threshold (float): Minimum confidence level for valid objects.

    Returns:
        list: Extracted nutritional information as a list of dictionaries.
    """
    # get all the objects that contain nutrition information
    nutrition_objs = []
    for obj in response_obj:
        text = obj.get("texts", [{}])[0].get("text", "").lower().replace(" ", "")
        if (
            any([
                    nutr in text
                    for nutr in nutritions
                ])
            and obj.get("confidence", 0) >= confidence_threshold
        ):
            nutrition_objs.append(obj)

    extracted_nutrition = []
    for obj in nutrition_objs:
        y = obj.get("y", 0)
        extracted_vals = []
        for comparison_obj in response_obj:
            if (  # check if the object is within the threshold
                comparison_obj.get("confidence", 0) >= confidence_threshold
                and 
                comparison_obj["y"] - threshold <= y <= comparison_obj["y"] + threshold
            ):
                val = comparison_obj.get("texts", [{}])[0].get("text", "")  # get the text value
                val_x = comparison_obj["x"]  # get the x value
                if (
                    val == obj["texts"][0]["text"]
                ):  # handle case where the value is the same as the nutrition
                    continue
                extracted_vals.append((val_x, val))  # add to the extracted values

        # Sort the extracted values by x value and return only the text value
        extracted_vals = [val[1] for val in sorted(extracted_vals, key=lambda x: x[0])]
        extracted_nutrition.append(
            {"nutrition": obj["texts"][0]["text"], "values": extracted_vals}
        )

    return extracted_nutrition


def nutrition_values_to_json(extracted_nutrition):
    """
    Converts the extracted nutritional information to a JSON format.

    Args:
        extracted_nutrition (list): List of dictionaries containing 'nutrition' and 'values'.

    Returns:
        dict: Nutritional information in a structured JSON format.
    """
    parsed_nutrition = []

    for nutr in extracted_nutrition:
        # Clean and format the nutritional values to ensure we get strings of 10mg instead of ['10', 'mg']
        # We do this as EyePop can sometimes get texts in separate objects
        nutrition, values = nutr["nutrition"], clean_nutrition_values(nutr["values"])
        
        parsed_vals = [] 
        for val in values:
            # Use regex to check if the value is alphanumeric, 
            # if it is, it is part of the nutrition name
            # Otherwise, it is a value
            if re.sub(r"[^A-Za-z0-9]", "", val).isalpha():
                # Check if the value is part of the nutrition name
                # E.g 'Total Fat' from ['Total', 'Fat']
                nutrition = (
                    f"{nutrition} {val}"
                    if "serving" in nutrition.lower()
                    else f"{val} {nutrition}"
                )
            else:
                parsed_vals.append(val)

        parsed_nutrition.append({"nutrition": nutrition, "values": parsed_vals})

    nutrition_dict = {}
    for nutr in parsed_nutrition:
        # Compose the nutrition dictionary/json objec deliverable
        nutrition, values = nutr["nutrition"], [
            val for val in nutr["values"] if "%" not in val
        ] # Ignore percentage values
        if "serving" in nutrition.lower():
            nutrition = "serving"

        if len(values) == 1:
            # If there is only one value, add it directly to the dictionary 
            # E.g 'Calories': '100' (given that the label only has one value)
            # Or, the CV tool did not extract the other values
            nutrition_dict[nutrition.capitalize()] = values[0]
        else:
            # If there are multiple values, add them with an index
            for i, val in enumerate(values):
                nutrition_dict[f"{nutrition.capitalize()}_{i}"] = val

    return nutrition_dict


def clean_nutrition_values(values):
    """
    Cleans the nutritional values extracted from the EyePop response.
    """
    units = {"mg", "g", "%", "kg", "lb", "oz"}
    clean_vals = []
    i = 0
    while i < len(values):
        if i + 1 < len(values) and values[i + 1] in units:
            clean_vals.append(f"{values[i]}{values[i + 1]}")
            i += 2
        else:
            clean_vals.append(values[i])
            i += 1

    return clean_vals
