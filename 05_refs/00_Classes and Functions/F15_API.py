"""
[F05_API.py]
Purpose: store function for ILH project.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1. https://platform.openai.com/docs/guides/vision
    2.

Status: Complete.
"""
import requests
import json
import datetime
from openai import OpenAI
import base64




# Function to encode the image
def encode_image(image_path):
    import os
    # Check if the file exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"The file {image_path} does not exist.")
    # Extract the file extension
    _, file_extension = os.path.splitext(image_path)
    # Define acceptable image formats
    acceptable_formats = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    # Check if the file is an acceptable image format
    if file_extension.lower() not in acceptable_formats:
        raise ValueError(f"Unsupported file format: {file_extension}. Please use one of the following formats: {', '.join(acceptable_formats)}")
    # If the file format is acceptable, proceed with encoding
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')




def OpenAI_GPT_API_long(model_callsigns, openai_api_key, question_content, temperature, additional_info=0):
    # API portle and header for autherization.
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    data = {
        "model": model_callsigns,
        "messages": [{'role': 'user', 'content': question_content}],
        #"role" can be "system"(provide instructions or contextual information to the AI model) 
        # or "user"(normal human asking questions).
        "temperature": temperature 
        #"temperature" is the randomness of the response. 0 is very deterministic and 1 is very creative.
    }

    #[] Send the POST request to the OpenAI API
    response = requests.post(openai_api_url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        #[Dictionary] response_data were stored in a format of python dictionary with multiple "key:value" pairs.
        response_data = response.json() 
        """print('\n[Response begin]')
        print(json.dumps(response_data, indent=4)) #Uncomment if you want to see all the information openai sent back.
        print('[Response end]\n')"""
        
        content = response_data["choices"][0]["message"]["content"]
        if additional_info == 1:
            info_id = str(response_data["id"])
            info_object = str(response_data["object"])
            info_created = str(datetime.datetime.utcfromtimestamp(response_data["created"]))
            info_model = str(response_data["model"])
            usage_prompt = str(response_data["usage"]["prompt_tokens"])
            usage_completion = str(response_data["usage"]["completion_tokens"])
            usage_total = str(response_data["usage"]["total_tokens"])
            #[] Combine text (Change this part if you prefer other reporting format.)
            info_1st_row = '[ID | Object | Timestamp | Model]    ' + info_id + ' | ' + info_object + ' | ' + info_created + ' | ' + info_model  
            info_2nd_row = '[Token prompt | completion | total]  ' + usage_prompt + ' | ' + usage_completion + ' | ' + usage_total
            content = info_1st_row + '\n' + info_2nd_row + '\n\n' + content + '\n'
        print('[Response preview]\n', str(content)[:200])
    else:
        print("Error:", response.status_code, response.text, sep='\n')
    return content




#[] Ask text question. Used most frequent.
def OpenAI_GPT_API_short(model_callsigns, openai_api_key, question_content, temperature):
    openai_api_url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": model_callsigns,
        "messages": [{'role': 'user', 'content': question_content}],
        "temperature": temperature 
    }
    response = requests.post(openai_api_url, headers=headers, data=json.dumps(data))
    content = None
    if response.status_code == 200:
        response_data = response.json() 
        content = response_data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text, sep='\n')
    return content




def OpenAI_GPT_API_image_url(model_callsigns, openai_api_key, question_content, url_image):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }

    payload = {
        "model": model_callsigns,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": url_image}
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    print('[response]\n', response)
    if response.status_code == 200:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text, sep='\n')
        content = None

    return content




def OpenAI_GPT_API_image_path(model_callsigns, openai_api_key, question_content, path_image, additional_info):
    base64_image = encode_image(path_image)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    payload = {
        "model": model_callsigns,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": question_content},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    if response.status_code == 200:
        response_data = response.json()
        content = response_data["choices"][0]["message"]["content"]
        if additional_info == 1:
            info_id = str(response_data["id"])
            info_object = str(response_data["object"])
            info_created = str(datetime.datetime.utcfromtimestamp(response_data["created"]))
            info_model = str(response_data["model"])
            usage_prompt = str(response_data["usage"]["prompt_tokens"])
            usage_completion = str(response_data["usage"]["completion_tokens"])
            usage_total = str(response_data["usage"]["total_tokens"])
            #[] Combine text
            info_1st_row = '[ID | Object | Timestamp | Model]    ' + info_id + ' | ' + info_object + ' | ' + info_created + ' | ' + info_model  
            info_2nd_row = '[Token prompt | completion | total]  ' + usage_prompt + ' | ' + usage_completion + ' | ' + usage_total
            content = info_1st_row + '\n' + info_2nd_row + '\n\n' + content + '\n'
    else:
        print("Error:", response.status_code, response.text, sep='\n')
        content = None

    return content





def OpenAI_GPT_API_test_1(model_callsigns, openai_api_key, question_content):
    openai_api_url = "https://api.openai.com/v1/fine_tuning/jobs"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}"
    }
    data = {
        "model": model_callsigns,
        "messages": [{'role': 'user', 'content': question_content}],
    }
    response = requests.post(openai_api_url, headers=headers, data=json.dumps(data))
    content = None
    if response.status_code == 200:
        response_data = response.json() 
        content = response_data["choices"][0]["message"]["content"]
    else:
        print("Error:", response.status_code, response.text, sep='\n')
    return content




def OpenAI_GPT_API_test_2(model_callsigns, openai_api_key, question_content):
    client = OpenAI(
        api_key = openai_api_key, # My secret API key.
    )
  
    response = client.completions.create(
    model = model_callsigns,
    messages=[
        {"role": "system", "content": question_content},
    ]
    )
    content = response.choices[0].message
    return content