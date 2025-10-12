import os
import base64
import mimetypes
from urllib.request import urlopen, Request
from pathlib import Path
from dotenv import load_dotenv

# Azure
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient


def _image_file_to_data_url(file_path: Path) -> str:
    if not file_path.exists() or not file_path.is_file():
        raise FileNotFoundError(f"Nie znaleziono pliku: {file_path}")

    mime, _ = mimetypes.guess_type(str(file_path))
    if not mime or not mime.startswith("image/"):
        # prosta walidacja — dopuszczamy najczęstsze rozszerzenia
        allowed = {"jpg", "jpeg", "png", "gif", "webp", "bmp"}
        ext = file_path.suffix.lower().lstrip(".")
        if ext not in allowed:
            raise ValueError(
                f"Nieobsługiwany typ pliku: .{ext}. Dopuszczalne: {', '.join(sorted(allowed))}"
            )
        mime = f"image/{ext if ext != 'jpg' else 'jpeg'}"

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def _image_url_to_data_url(url: str) -> str:
    # Zachowujemy możliwość użycia URL jako fallback (przydatne w testach)
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urlopen(req).read()
    # Zgadujemy MIME prosto po rozszerzeniu
    mime, _ = mimetypes.guess_type(url)
    if not mime or not mime.startswith("image/"):
        # jeśli nie da się zgadnąć, przyjmujemy jpeg (najczęściej)
        mime = "image/jpeg"
    encoded = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{encoded}"


def main():
    # Wyczyść konsolę
    os.system('cls' if os.name == 'nt' else 'clear')

    try:
        # Konfiguracja
        load_dotenv()
        project_endpoint = os.getenv("PROJECT_ENDPOINT")
        model_deployment = os.getenv("MODEL_DEPLOYMENT")
        if not project_endpoint or not model_deployment:
            raise EnvironmentError(
                "Brak zmiennych środowiskowych PROJECT_ENDPOINT i/lub MODEL_DEPLOYMENT. "
                "Dodaj je do pliku .env."
            )

        # Klient projektu + klient OpenAI
        project_client = AIProjectClient(
            credential=DefaultAzureCredential(
                exclude_environment_credential=True,
                exclude_managed_identity_credential=True,
            ),
            endpoint=project_endpoint,
        )
        openai_client = project_client.get_openai_client(api_version="2024-10-21")

        # Persona systemowa
        system_message = (
            "You are an AI assistant in a grocery store that sells fruit. "
            "You provide detailed answers to questions about produce."
        )

        # --- NOWE: wybór obrazu lokalnie lub przez URL ---
        print("Wczytywanie obrazu do analizy\n")
        img_input = input(
            "Podaj ścieżkę do lokalnego pliku obrazu (np. C:/zdj/pomarancza.jpg)\n"
            "albo wklej URL obrazu. Pozostaw puste, aby użyć domyślnego zdjęcia pomarańczy.\n> "
        ).strip()

        if img_input:
            if img_input.lower().startswith(("http://", "https://")):
                data_url = _image_url_to_data_url(img_input)
            else:
                data_url = _image_file_to_data_url(Path(img_input).expanduser())
        else:
            # Domyślne zdjęcie (fallback)
            default_url = (
                "https://github.com/MicrosoftLearning/mslearn-ai-vision/raw/refs/heads/main/"
                "Labfiles/gen-ai-vision/orange.jpeg"
            )
            data_url = _image_url_to_data_url(default_url)

        # Pętla QA
        while True:
            prompt = input("\nZadaj pytanie o obraz (lub wpisz 'quit' aby wyjść)\n> ")
            if prompt.lower() == "quit":
                break
            if not prompt.strip():
                print("Podaj treść pytania.")
                continue

            print("\nPobieram odpowiedź...\n")

            # Wywołanie chat completions z tekstem i obrazem
            response = openai_client.chat.completions.create(
                model=model_deployment,
                messages=[
                    {"role": "system", "content": system_message},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": data_url}},
                        ],
                    },
                ],
            )

            print(response.choices[0].message.content)

    except Exception as ex:
        print("[BŁĄD]", ex)


if __name__ == "__main__":
    main()
