# Custom Function (Tool) w AI Agencie  
## Automatyzacja zgłoszeń wsparcia technicznego (Python SDK)

---

## Cel projektu:

Celem tego warsztatu jest **stworzenie i podłączenie własnej funkcji narzędziowej (custom tool)** do agenta AI zbudowanego przy użyciu **Python SDK**.  
Funkcja ta umożliwi agentowi **automatyczne generowanie i zapisywanie zgłoszeń wsparcia technicznego (support tickets)** na podstawie danych przekazanych przez użytkownika.

---

## Kontekst:

W środowisku AI agenta funkcje narzędziowe pozwalają agentowi wykonywać rzeczywiste działania w świecie zewnętrznym — np. tworzenie plików, zapisywanie danych, wysyłanie wiadomości czy integrację z API.

W tym ćwiczeniu uczymy się, jak:
- zdefiniować niestandardową funkcję (custom tool),
- zarejestrować ją w agencie,
- umożliwić agentowi obsługę zgłoszeń użytkowników w sposób zautomatyzowany.

---

## Opis działania funkcji:

### Funkcja: `submit_support_ticket()`

**Cel:**  
Utworzenie pliku zgłoszenia serwisowego i zwrócenie potwierdzenia w formacie JSON.

**Etapy działania:**
1. **Pobranie danych wejściowych**  
   Funkcja przyjmuje dwa parametry:
   - `email_address` – adres e-mail użytkownika zgłaszającego problem,  
   - `description` – opis zgłaszanego problemu.

2. **Wygenerowanie unikalnego numeru zgłoszenia**  
   Przy użyciu modułu `uuid` tworzymy losowy identyfikator (UUID), skrócony do 6 znaków, np. `f3a9c2`.

3. **Utworzenie pliku zgłoszenia**  
   Plik zostaje zapisany w tym samym katalogu co skrypt, z nazwą:ticket-f3a9c2.txt

4. **Zapis treści zgłoszenia do pliku**  
W pliku znajdują się:

Support ticket: f3a9c2
Submitted by: user@example.com

Description:
Problem z logowaniem do aplikacji.

5. **Zwrot komunikatu JSON**  
Po zapisaniu zgłoszenia funkcja zwraca potwierdzenie:
```
{
  "message": "Support ticket f3a9c2 submitted. The ticket file has been saved as ticket-f3a9c2.txt."
}
```

## Testowanie fukcji:

1. Możesz przetestować funkcję lokalnie, uruchamiając w konsoli Python:
```
python
```

2. Następnie w interpreterze wpisz:
```
from support_tool import submit_support_ticket
print(submit_support_ticket("test2@example.com", "Cannot log into the systemu."))
```

3. Po wykonaniu w katalogu, w którym znajduje się skrypt, pojawi się nowy plik, np.:
```
ticket-abc123.txt
```

4. A w konsoli zobaczysz potwierdzenie w formacie JSON:
```
{
  "message": "Support ticket abc123 submitted. The ticket file has been saved as ticket-abc123.txt."
}
```
## Integracja z agentem AI:

Zbiór **`user_functions`** pozwala agentowi rozpoznać, które funkcje może wywoływać automatycznie.  
Dzięki temu agent może sam:

- przyjąć zgłoszenie od użytkownika,  
- zapisać je jako plik tekstowy,  
- odesłać potwierdzenie w formacie **JSON**.

W praktyce agent będzie mógł odpowiedzieć użytkownikowi w taki sposób:

>  „Zgłoszenie zostało utworzone. Numer Twojego zgłoszenia to **f3a9c2**.”


