
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    # Don't raise here; allow the app to start but return a helpful error when the model is used
    print("WARNING: Missing GEMINI_API_KEY/GOOGLE_API_KEY in environment. LLM calls will fail until configured.")
else:
    genai.configure(api_key=API_KEY)

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    generation_config=GENERATION_CONFIG,
    system_instruction=(
        "You are a helpful, factual, and empathetic healthcare assistant. "
        "When given symptoms, suggest possible medical conditions, causes, and self-care steps. "
        "Always include a disclaimer that this is for educational purposes only and not a diagnosis. "
        "Use structured formatting with bullet points or numbered lists when possible."
    ),
)

def generate_diagnosis(symptom_text: str) -> str:

    if not symptom_text or not symptom_text.strip():
        return "Please provide a valid symptom description."

    try:
        response = model.generate_content(
            [f"Symptoms: {symptom_text}\n\nSuggest probable conditions and next steps."]
        )
        return response.text.strip() if response and response.text else "No response generated."
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"


if __name__ == "__main__":
    result = generate_diagnosis("I have cough, mild fever, and sore throat for 2 days")
    print(result)
