import requests
import logging
from django.shortcuts import render
from gtts import gTTS
import os
import base64
import time
from user_app.models import Userinfo


logger = logging.getLogger(__name__)


def create_talking_avatar(image_path, audio_path):
    try:
        # Read image and audio files
        print(f"Reading image from {image_path}")
        with open(image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
        
        print(f"Reading audio from {audio_path}")
        with open(audio_path, "rb") as audio_file:
            audio_data = base64.b64encode(audio_file.read()).decode('utf-8')
        

         # Print file sizes for debugging
        print(f"Image file size: {os.path.getsize(image_path)} bytes")
        print(f"Audio file size: {os.path.getsize(audio_path)} bytes")

        # Step 1: Create talk
        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": "Basic  dXNlcnVuaXZlcnNlOTlAZ21haWwuY29t:hiwpc65DLkkg_mu12giIr",
            "Content-Type": "application/json"
        }
        data = {
            "script": {
                "type": "audio",
                "audio": audio_data
            },
            "image": img_data,
            "config": {
                "fluent": True
            }
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code != 200:
            print(f"Error creating talk: {response.status_code} - {response.text}")
            return None

        print("Talk created successfully. Processing talk ID...")
        talk_id = response.json().get('id')
        if not talk_id:
            return None

        # Step 2: Poll for video completion
        poll_url = f"https://api.d-id.com/talks/{talk_id}"
        for attempt in range(10):
            # print(f"Polling for video completion, attempt {attempt + 1}")
            poll_response = requests.get(poll_url, headers=headers)
            
            if poll_response.status_code == 200:
                poll_data = poll_response.json()
                if poll_data.get('result_url'):
                    print(f"Video generated successfully. Result URL: {poll_data['result_url']}")
                    return poll_data['result_url']
                else:
                    print("Result URL not found yet. Retrying...")
            else:
                print(f"Error polling for video: {poll_response.status_code} - {poll_response.text}")
            
            time.sleep(2)  
        return None
    except Exception as e:
        return None

API_KEY = '7d33c4c21a3ab7ce946e1ec3f311a61ccc8f724cefd0fab92ad8b116fbf88db3' 

def generate_response(prompt):
    """
    Function to generate text using Together AI API.
    """
    url = "https://api.together.xyz/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        logger.debug(f"Sending request to {url} with data: {data}")
        
        response = requests.post(url, headers=headers, json=data)
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response content: {response.text[:200]}...") 
        
        response.raise_for_status()
        result = response.json()
        
        if "choices" in result and len(result["choices"]) > 0:
            if "message" in result["choices"][0]:
                return result["choices"][0]["message"]["content"]
        
        logger.error(f"Could not parse response: {result}")
        return "Error: Could not parse AI response"
        
    except requests.exceptions.HTTPError as err:
        logger.error(f"HTTP error occurred: {err}")
        return f"HTTP error occurred: {err}"
    except Exception as err:
        logger.error(f"An unexpected error occurred: {err}")
        return f"An unexpected error occurred: {err}"

LANGUAGE_MAP = {
    'ar': 'Arabic',
    'bn': 'Bengali',
    'de': 'German',
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'gu': 'Gujarati',
    'hi': 'Hindi',
    'it': 'Italian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ml': 'Malayalam',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'ta': 'Tamil',
    'te': 'Telugu',
    'tr': 'Turkish',
    'ur': 'Urdu',
    'vi': 'Vietnamese',
    'zh': 'Chinese',
}
def search(request):
    logger.debug(f"Request method: {request.method}")
    logger.debug(f"Request POST data: {request.POST}")

    context = {} 

    user_id = request.session.get('user_id')
    if user_id:
        try:
            user = Userinfo.objects.get(id=user_id)
            context['first_name'] = user.first_name
        except Userinfo.DoesNotExist:
            context['first_name'] = "Guest"
    else:
        context['first_name'] = "Guest"

    if request.method == "POST":
        prompt = request.POST.get('topic')
        language = request.POST.get('language', 'en')

        logger.debug(f"Received search request with prompt: {prompt} in language: {language}")

        if prompt:
            # Check the user's membership type and set prompt limits accordingly
            plan = user.membership_type  # Assuming membership_type is stored in the Userinfo model
            if plan == "Basic":
                max_prompts = 5
            elif plan == "Pro":
                max_prompts = 10
            elif plan == "Premium":
                max_prompts = 100  # or unlimited
            else:
                max_prompts = 0  # Default case if no plan found (shouldn't happen)

            # Check if the user has any prompts left
            if user.attempt > 0:
                # Proceed with response generation
                language_name = LANGUAGE_MAP.get(language, 'English')

                if language != 'en':
                    full_prompt = f"Explain about '{prompt}' completely in {language_name}."
                else:
                    full_prompt = f"Explain about '{prompt}' completely in English."

                generated_text = generate_response(full_prompt)

                # Convert the generated text to speech using gTTS
                tts = gTTS(text=generated_text, lang=language)
                audio_file = "static/audio/explanation.mp3"
                tts.save(audio_file)

                avatar_video_url = create_talking_avatar("static/images/images.jpeg", audio_file)
                
                # Decrease the number of attempts left for the user
                user.attempt -= 1
                user.save()

                context['explanation'] = generated_text
                context['audio_url'] = f'/{audio_file}'
                context['avatar_video_url'] = avatar_video_url if avatar_video_url else None
                context['topic'] = prompt
                context['remaining_prompts'] = user.attempt
            else:
                # If no attempts left, inform the user
                logger.warning(f"User {user.username} has no attempts left.")
                context['error'] = "You have run out of prompts. Please upgrade your plan."

        else:
            logger.warning("No prompt provided.")
            context['error'] = 'Please provide a valid prompt.'

    return render(request, 'search.html', context)

# def search(request):
#     logger.debug(f"Request method: {request.method}")
#     logger.debug(f"Request POST data: {request.POST}")

#     context = {} 

#     user_id = request.session.get('user_id')
#     if user_id:
#         try:
#             user = Userinfo.objects.get(id=user_id)
#             context['first_name'] = user.first_name
#         except Userinfo.DoesNotExist:
#             context['first_name'] = "Guest"
#     else:
#         context['first_name'] = "Guest"

#     if request.method == "POST":
#         prompt = request.POST.get('topic')
#         language = request.POST.get('language', 'en')

#         logger.debug(f"Received search request with prompt: {prompt} in language: {language}")

#         if prompt:
#             language_name = LANGUAGE_MAP.get(language, 'English')

#             if language != 'en':
#                 full_prompt = f"Explain about '{prompt}' completely in {language_name}."
#             else:
#                 full_prompt = f"Explain about '{prompt}' completely in English."

#             generated_text = generate_response(full_prompt)

#             # Convert the generated text to speech using gTTS
#             tts = gTTS(text=generated_text, lang=language)
#             audio_file = "static/audio/explanation.mp3"
#             tts.save(audio_file)

#             avatar_video_url = create_talking_avatar("static/images/images.jpeg", audio_file)
#             context['explanation'] = generated_text
#             context['audio_url'] = f'/{audio_file}'
#             context['avatar_video_url'] = avatar_video_url if avatar_video_url else None
#             context['topic'] = prompt
#         else:
#             logger.warning("No prompt provided.")
#             context['error'] = 'Please provide a valid prompt.'

#     return render(request, 'search.html', context)


# User submits form ➔ Django backend sends request to Together AI ➔ 
# Receives explanation ➔ Converts text to audio using gTTS ➔ 
# Returns text and audio file to the frontend ➔ 
# User sees text + hears audio ➔ Avatar lip-syncs
