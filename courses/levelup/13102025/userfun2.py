import json       # Moduł json — służy do kodowania/dekodowania danych w formacie JSON
import uuid       # Moduł uuid — generuje unikalne identyfikatory, przydatne np. do numerów zgłoszeń
from pathlib import Path   # Path — ułatwia pracę ze ścieżkami plików w sposób niezależny od systemu operacyjnego
from typing import Any, Callable, Set  # Typy używane do oznaczenia typów zmiennych i zbiorów funkcji

# Tworzymy funkcję do zgłaszania problemu technicznego (support ticket)
def submit_support_ticket(email_address: str, description: str) -> str:
    """Generate a support ticket file and return a confirmation message in JSON."""
    # Pobieramy katalog, w którym znajduje się ten skrypt (plik .py)
    # Dzięki temu plik zgłoszenia zostanie zapisany w tym samym folderze.
    script_dir = Path(__file__).parent  
    
    # Generujemy unikalny numer zgłoszenia z UUID (uniwersalnego identyfikatora)
    # Usuwamy myślniki i bierzemy tylko pierwsze 6 znaków dla czytelności.
    ticket_number = str(uuid.uuid4()).replace("-", "")[:6]
    
    # Tworzymy nazwę pliku w formacie ticket-XXXXXX.txt
    file_name = f"ticket-{ticket_number}.txt"
    
    # Łączymy katalog skryptu z nazwą pliku, aby uzyskać pełną ścieżkę do pliku.
    file_path = script_dir / file_name

    # Przygotowujemy treść zgłoszenia, zawierającą numer, adres e-mail i opis problemu.
    text = (
        f"Support ticket: {ticket_number}\n"
        f"Submitted by: {email_address}\n"
        f"Description:\n{description}"
    )

    # Zapisujemy treść zgłoszenia do pliku tekstowego.
    # Jeśli plik nie istnieje, zostanie utworzony automatycznie.
    file_path.write_text(text)

    # Tworzymy komunikat zwrotny w formacie JSON,
    # informujący użytkownika, że zgłoszenie zostało przyjęte i zapisane.
    message_json = json.dumps({
        "message": f"Support ticket {ticket_number} submitted. "
                   f"The ticket file has been saved as {file_name}."
    })
    
    # Zwracamy komunikat JSON jako wynik funkcji.
    return message_json

# Definiujemy zbiór funkcji, które można wywołać (callable functions).
# W tym przypadku zawiera tylko jedną funkcję — submit_support_ticket.
# Set pozwala w przyszłości łatwo dodać więcej funkcji, np. do obsługi użytkowników.
user_functions: Set[Callable[..., Any]] = {
    submit_support_ticket
}
