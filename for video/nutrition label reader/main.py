from eyepop import EyePopSdk
from utils import get_nutrition_values
from dotenv import load_dotenv

# Define the possible nutrition labels to extract
NUTRITIONS = [
    'protein', 'fat', 'calories', 'sugar', 'sodium', 'fiber', 'carbohydrate', 'cholesterol', 'carbs'
]
# Define the threshold for proximity in 'y' values
THRESHOLD = 10

# Define image filepath
filepath = 'images/uploaded_image.png'

# Get EyePop Api key and id
load_dotenv() # Load the environment variables

# Initialize the EyePop SDK
with EyePopSdk.endpoint() as endpoint:
    response = endpoint.upload(filepath).predict()
    
# Extract nutritional information from the response
nutrition_data = get_nutrition_values(response, NUTRITIONS, THRESHOLD)

# Print the extracted nutritional information
print(nutrition_data)





