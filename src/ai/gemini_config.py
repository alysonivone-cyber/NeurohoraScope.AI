
import os

from dotenv import load_dotenv


load_dotenv()


def get_gemini_config():
    api_key = os.getenv("GEMINI_API_KEY")

    configured = bool(
        api_key
        and api_key.strip()
        and api_key != "your_api_key_here"
    )

    return {
        "sdk": "google-genai",
        "api_key_configured": configured,
        "model": os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash",
        ),
    }


if __name__ == "__main__":
    config = get_gemini_config()

    print("\nNEUROSCOPE GEMINI CONFIGURATION")
    print("SDK:", config["sdk"])
    print(
        "API key:",
        "CONFIGURED"
        if config["api_key_configured"]
        else "NOT CONFIGURED",
    )
    print("Model:", config["model"])
    print(
        "Ready for API calls:",
        config["api_key_configured"],
    )
