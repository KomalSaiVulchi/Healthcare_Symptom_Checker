
import os
from pathlib import Path
from dotenv import load_dotenv

# Prefer the older google-generativeai SDK; fall back to the newer google-genai if present
_LIB_IMPL = None
try:
    import google.generativeai as genai  # type: ignore
    _LIB_IMPL = "generativeai"
except Exception:
    try:
        from google import genai  # type: ignore
        _LIB_IMPL = "genai"
    except Exception:
        genai = None  # type: ignore
        _LIB_IMPL = None

# Load .env located alongside this file, regardless of the current working directory
_DOTENV_PATH = Path(__file__).with_name('.env')
load_dotenv(dotenv_path=_DOTENV_PATH if _DOTENV_PATH.exists() else None)
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("WARNING: Missing GEMINI_API_KEY/GOOGLE_API_KEY in environment. LLM calls will fail until configured.")

# Configure client for the detected library
if _LIB_IMPL == "generativeai" and API_KEY:
    try:
        genai.configure(api_key=API_KEY)  # type: ignore[attr-defined]
    except Exception:
        pass

GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 2048,
    "response_mime_type": "text/plain",
}

# Constants per library flavor
_MODEL_NAME_GENERATIVEAI = "gemini-2.5-flash"
_MODEL_NAME_GENAI = "gemini-2.0-flash-001"

def _prompt_for(symptom_text: str) -> list[str]:
    return [f"Symptoms: {symptom_text}\n\nSuggest probable conditions and next steps."]

def _generate_with_generativeai(symptom_text: str) -> str:
    try:
        model = genai.GenerativeModel(  # type: ignore[attr-defined]
            model_name=_MODEL_NAME_GENERATIVEAI,
            generation_config=GENERATION_CONFIG,
            system_instruction=(
                "You are a helpful, factual, and empathetic healthcare assistant. "
                "When given symptoms, suggest possible medical conditions, causes, and self-care steps. "
                "Always include a disclaimer that this is for educational purposes only and not a diagnosis. "
                "Use structured formatting with bullet points or numbered lists when possible."
            ),
        )
        resp = model.generate_content(_prompt_for(symptom_text))
        return (getattr(resp, "text", None) or "").strip() or "No response generated."
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"

def _generate_with_genai(symptom_text: str) -> str:
    try:
        client = genai.Client(api_key=API_KEY)  # type: ignore[call-arg]
        resp = client.models.generate_content(
            model=_MODEL_NAME_GENAI,
            contents=_prompt_for(symptom_text),
        )
        # google-genai responses typically expose .text; fallback to first candidate if needed
        text = getattr(resp, "text", None)
        if not text:
            try:
                # Best-effort fallback
                text = resp.candidates[0].content.parts[0].text  # type: ignore[attr-defined]
            except Exception:
                text = ""
        return text.strip() or "No response generated."
    except Exception as e:
        return f"An error occurred while processing your request: {str(e)}"

def generate_diagnosis(symptom_text: str) -> str:
    if not symptom_text or not symptom_text.strip():
        return "Please provide a valid symptom description."

    if not API_KEY:
        return "LLM is not configured (missing GEMINI_API_KEY)."

    if _LIB_IMPL == "generativeai":
        return _generate_with_generativeai(symptom_text)
    elif _LIB_IMPL == "genai":
        return _generate_with_genai(symptom_text)
    else:
        return (
            "Neither 'google-generativeai' nor 'google-genai' Python packages are installed. "
            "Install one of them to enable diagnosis."
        )


if __name__ == "__main__":
    result = generate_diagnosis("I have cough, mild fever, and sore throat for 2 days")
    print(result)
