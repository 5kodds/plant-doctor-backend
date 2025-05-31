from django.shortcuts import render

# Create your views here.
# backend/analyzer/views.py
import json
import google.generativeai as genai
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

# Configure Gemini API Client
gemini_model_initialized = False
model = None

if settings.GOOGLE_API_KEY:
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        generation_config = {
            "response_mime_type": "application/json",
            "response_schema": {
                "type": "OBJECT",
                "properties": {
                    "diagnosis": {"type": "STRING"},
                    "plant_health_details": {"type": "STRING"},
                    "soil_condition_assessment": {"type": "STRING"},
                    "recommendations_plant": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "recommendations_soil": {"type": "ARRAY", "items": {"type": "STRING"}}
                },
                "required": ["diagnosis", "plant_health_details", "soil_condition_assessment", "recommendations_plant", "recommendations_soil"]
            }
        }
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Or your preferred model
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        gemini_model_initialized = True
        print("🟢 Gemini Model Initialized Successfully.")
    except Exception as e:
        print(f"🔴 Error initializing Gemini Model: {e}")
else:
    print("🔴 Gemini API Key not found. API calls will fail.")


@csrf_exempt # Important for APIs called by external JS without Django's CSRF mechanism
@require_POST
def analyze_plant_view(request):
    if not gemini_model_initialized or not model:
        return JsonResponse({"error": "Gemini model not initialized. Check API key and server logs."}, status=500)

    try:
        request_data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON in request body"}, status=400)

    user_text = request_data.get('text', '')
    base64_image_data = request_data.get('base64ImageData')
    mime_type = request_data.get('mimeType', 'image/jpeg') # Default if not provided

    if not user_text and not base64_image_data:
        return JsonResponse({"error": "Please provide a description or upload an image."}, status=400)

    prompt = f"""You are an expert agronomist and plant pathologist. Analyze the following inputs: a user-provided text description and/or an image of a plant and its soil.
User's text input: "{user_text if user_text else 'No text description provided.'}"

Based on all available information (text and/or image):
1.  Provide a concise diagnosis of the plant's overall health.
2.  Describe any specific details observed about the plant's condition.
3.  Assess the visible or described soil condition.
4.  Offer actionable recommendations to improve the plant's health.
5.  Offer actionable recommendations to improve the soil's condition.

Please provide your response in the specified JSON format.
"""

    contents_for_gemini = [prompt]
    if base64_image_data:
        image_part = {
            "mime_type": mime_type,
            "data": base64_image_data
        }
        # Correct structure for multimodal input with inline data
        contents_for_gemini = [
            {"parts": [{"text": prompt}]}, # Text part
            {"parts": [{"inline_data": image_part}]} # Image part
        ]
        # If only one type of content (e.g., only image with a generic prompt, or only text), structure accordingly.
        # For combined, you often send them as separate parts in the 'contents' list for the model if it's a multi-turn like structure,
        # or embed image within a more complex single prompt if model supports it well.
        # The gemini-flash model prefers separate parts in the `contents` list, where each part can be text or inline_data.
        # Simpler structure for gemini-flash (single turn):
        parts_list = [{"text": prompt}]
        if base64_image_data:
            parts_list.append({"inline_data": image_part})
        contents_for_gemini = parts_list # This is a list of Part objects (dict in JSON)


    try:
        # Use the already initialized 'model'
        response = model.generate_content(contents_for_gemini)
        
        if response.parts and response.text:
            gemini_json_string = response.text
            # The response.text should be the JSON string as per generation_config
            return JsonResponse(json.loads(gemini_json_string))
        else:
            error_detail = "Unknown error or empty response from Gemini."
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 error_detail = f"Prompt Feedback: {response.prompt_feedback}"
            elif hasattr(response, 'candidates') and not response.candidates:
                 error_detail = "No candidates returned from Gemini."
            return JsonResponse({"error": "Failed to get valid content from Gemini.", "details": error_detail}, status=500)

    except Exception as e:
        print(f"🔴 Gemini API call failed: {e}") # Log to server console
        return JsonResponse({"error": f"An error occurred with the AI service: {str(e)}"}, status=500)