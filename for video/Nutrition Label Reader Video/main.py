# pip install eyepop pandas python-dotenv
from eyepop import EyePopSdk
from dotenv import load_dotenv
from utils import get_nutrition_values

# Define the possible nutrition labels to extract
NUTRITIONS = [
    'protein', 'fat', 'calories', 'sugar', 'sodium', 'fiber', 'carbohydrate', 'cholesterol', 'carbs'
]
# Define the threshold for proximity in 'y' values
THRESHOLD = 10

# Define image filepath
filepath = 'images/label 2.jpg'

# Get EyePop Api key and id
load_dotenv() # Load the environment variables

# Initialize the EyePop SDK
with EyePopSdk.endpoint() as endpoint:
    response = endpoint.upload(filepath).predict()
    
print(get_nutrition_values(response, NUTRITIONS, THRESHOLD))