# EyePop-coding-challenge
EyePop interview coding challenge

## How it works
After simply using the API to parse the image and get the response, I got the relevant information by:
- Looping through the entire response.object list and getting all the `map` that contained a text with text that had any nutrition name on it e.g. "calories", "sodium", etc.
- Then noticing that the values that correspond to the found nutritions would be in a relative close **y** coordinate to the nutrition name, I looped through the response.object list again and got all the `map` that had a **y** coordinate that was within 10 pixels of the nutrition name (ignoring the nutrition name itself). Giving me a list of mapping where we had `{'<nutrition_name>': ['<nutrition_value_1>', '<nutrition_value_2>', ...]}`.
- Then using that list, I cleaned the information by sorting the lists of nutrition values by the **x** coordinate, making sure the values were in the correct order and to handle the situation where there were 2 columns of nutrition values due to different serving sizes. 
    - While also cleaning the values ensuring that the number values and the units in one string (handling the fact that EyePop sometimes sees the unit and the numeric value as 2 different objects).
- Finally, I created the final mapping by ignoring all percentages, and handling if there are multiple values for the same nutrition name, and returning the final mapping of `{'<nutrition_name>': '<nutrition_value>'}`. As the final output JSON.

### Example output 
```json
{
    "calories": "200",
    "total fat": "8g",
    "sodium": "230mg",
    "total carbohydrates": "27g",
    "protein": "3g"
}
```

## Streamlit Dashboard
For the project that was given to me, I wanted to showcase my ability to not only utilize the EyePop API effectively, but also an example of how one could create a simple and easy to use dashboard with the API. 

So after utilizing the API to parse the images, and using `pandas` to clean and extract the data from the response from EyePops API (which took about an hour or slightly less due to how easy it was to use EyePop), I used somemore time to create a simple dashboard that would allow users to upload images, send the image to the EyePop API, and then display the results in a JSON which can be copy/downloaded, or a dataframe which can be used to edit any mistakes the model may have made when parsing the image. And also a section that jus returns/give the raw response from the API.

### To run the dashboard
1. Install the required packages
```bash
pip install eyepop pandas streamlit
```
2. Run the dashboard
```bash
streamlit run app.py
```
![dashboard](/assets/dashboard.png)


## Notes
Recorded notes of things that I noticed while using the API/documentation:


- Should have an option to close the helper codes on Dashboard so it would be easier for people to see all their available models and only upon clicking on it have it open up the helper code. Or have a grid view of all the models similar to the templates.
    - Personally, I would prefer to have the dashboard layout like this, as the tabs of the code helpers being out constantly, made it the screen very cluttered. And I think would make it harder to navigate if someone had a lot of models.

<!-- insert image -->
![code_helper](/assets/notes/code_helpers.png)


- Example code does not work.. Gives error that the `EyePopSdk` does not take any positional arguments.
```python
from eyepop import EyePopSdk

pop_id = "8c7a47acf2374af4b9add0a80fea8424"
secret_key = "<My Api Key>"

with EyePopSdk.endpoint(pop_id, secret_key) as endpoint:
    
    result = endpoint.upload('example.jpg').predict()
    print(result)
```
![error](/assets/notes/example_error.png)

- PythonSDK docs could be improved with:
    - Clearer separations between the different sections, by maybe adding more formatting to the docs. 
    - A table that shows all the variables and that attributes that are available for each object.



- **Possible bug?** but when parsing image_3 one of my test run, it detected a "text" item but did not provide a "texts" list in the response. Couldn't tell where the box was located, and the confidence score was relatively high as well. There were about 10 others the same way. 
    - Only happened on image_3, and I did not see any other issues with the other images. (Could be due to the webp format?)
    - I think a detection before returning the object to prune these falsified detections would be a nice way to handle it.

<!-- insert image -->
![text_detection](/assets/notes/possible_bug.png)