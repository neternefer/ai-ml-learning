# gradio_text_chat.py
import os
from typing import List, Dict, Any, Tuple

from dotenv import load_dotenv
import gradio as gr

from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# To instrukcja dla modelu („bądź pomocny, odpowiadaj krótko”). Możesz ją zmienić w UI. Czyli jak ma się zachowywać asystent
SYSTEM_DEFAULT = (
    "You are a helpful AI assistant that answers questions clearly and concisely."
)

# Budowanie klienta do Azure – połączenie i model
def _build_client():
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    deployment = os.getenv("MODEL_DEPLOYMENT")
    if not endpoint or not deployment:
        raise RuntimeError(
            "Missing PROJECT_ENDPOINT or MODEL_DEPLOYMENT in .env"
        )
# Tworzy klienta Projektu.
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(
            exclude_environment_credential=True,
            exclude_managed_identity_credential=True
        ),
        endpoint=endpoint,
    )
    openai_client = project_client.get_openai_client(api_version="2024-10-21")
    return openai_client, deployment

openai_client, MODEL_DEPLOYMENT = _build_client()

# Funkcja, która gada z modelem
def _chat(messages: List[Dict[str, Any]]) -> str:
    resp = openai_client.chat.completions.create(
        model=MODEL_DEPLOYMENT,
        messages=messages
    )
    return resp.choices[0].message.content
# Co się dzieje po kliknięciu „Send” – obsługa jednej tury czatu
def send_message(user_msg: str,
                 chat_history: List[Tuple[str, str]],
                 system_msg: str,
                 messages_state: List[Dict[str, Any]]):
    if not user_msg.strip():
        return gr.update(), messages_state

    # Append user turn
    messages_state.append({"role": "user", "content": user_msg})

    try:
        assistant = _chat(messages_state)
    except Exception as e:
        assistant = f"Error: {e}"

    # Append assistant turn
    messages_state.append({"role": "assistant", "content": assistant})
    chat_history = chat_history + [(user_msg, assistant)]
    return chat_history, messages_state

# „Wyczyść rozmowę” – start od nowa
def reset_chat(system_msg: str):
    # (re)seed message list with system message
    return [], [{"role": "system", "content": system_msg or SYSTEM_DEFAULT}]

# Budowa okienka w Gradio (UI)
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    gr.Markdown("# Project LevelUP Generative AI Chat")
    gr.Markdown("Type a question and get an answer using your configured Azure model deployment.")

    system_box = gr.Textbox(
        label="System message (optional)",
        value=SYSTEM_DEFAULT,
        lines=3
    )

    chatbot = gr.Chatbot(height=420)
    user_box = gr.Textbox(
        label="Your message",
        placeholder="Ask anything…",
    )

    messages_state = gr.State(value=[{"role": "system", "content": SYSTEM_DEFAULT}])

    with gr.Row():
        send_btn = gr.Button("Send", variant="primary")
        clear_btn = gr.Button("Clear")

    # co ma się stać po kliknięciu/enterze
    send_btn.click(
        send_message,
        inputs=[user_box, chatbot, system_box, messages_state],
        outputs=[chatbot, messages_state]
    )
    user_box.submit(
        send_message,
        inputs=[user_box, chatbot, system_box, messages_state],
        outputs=[chatbot, messages_state]
    )
    clear_btn.click(
        reset_chat,
        inputs=[system_box],
        outputs=[chatbot, messages_state]
    )
# Start aplikacji
if __name__ == "__main__":
    demo.launch()
