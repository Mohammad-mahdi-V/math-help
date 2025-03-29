from google.generativeai.generative_models import GenerativeModel
from google.generativeai import configure
configure(api_key="AIzaSyBCpiTAYNcd1qTIup_sfcI8lB9oI_klN9Y")
generation_config = {
            "top_p": 0.95,
            "top_k": 64,
            "response_mime_type": "text/plain"
        }
model = GenerativeModel(model_name="gemini-2.0-flash-thinking-exp-01-21", generation_config=generation_config)

response = model.generate_content("مجموعه اعداد فرد از 1 تا 9")
print(response.text)
