import os
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
import gradio as gr
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

THEME = gr.themes.Base()

CUSTOM_CSS = """
body, .gradio-container { background: #fafafa !important; color: #0f172a; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, Apple Color Emoji, Segoe UI Emoji; }
#shell { display:flex; justify-content:center; padding:32px; }
#card { width:100%; max-width: 960px; background:#ffffff; border-radius: 16px; box-shadow: 0 10px 40px rgba(2,6,23,0.06); padding: 24px; }
#title h1 { margin:0 0 6px 0; font-size: 24px; font-weight: 800; letter-spacing:.2px; color:#0f172a; }
#subtitle p { margin:0 0 18px 0; color:#334155; font-size: 14px; }
#stack { gap: 14px; }
#system-box textarea, #user-box textarea { font-size: 16px !important; line-height: 1.55 !important; border-radius: 12px !important; }
#chatbot .wrap, #chatbot .gr-chatbot, #chatbot { border-radius: 14px !important; background:#ffffff; box-shadow: inset 0 0 0 1px rgba(2,6,23,0.06); }
.gr-chatbot .message { font-size: 16px; line-height: 1.55; padding: 10px 12px; border-radius: 12px; }
.gr-chatbot .message.user  { background:#f3f4f6 !important; color:#0f172a !important; }
.gr-chatbot .message.bot   { background:#fff7e6 !important; color:#0f172a !important; }
#actions { display:flex; gap:10px; justify-content:flex-end; align-items:center; background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:10px; }
#send-btn { background:#111827; color:white; border-radius:10px; font-weight:700; padding:10px 16px; }
#send-btn:hover { filter: brightness(0.92); }
#clear-btn { background:white; color:#111827; border:1px solid #cbd5e1; border-radius:10px; font-weight:600; padding:10px 16px; }
#clear-btn:hover { background:#f1f5f9; }
footer { visibility: hidden; }
"""

SYSTEM_DEFAULT = "You are a helpful AI assistant that answers questions clearly and concisely."

def _build_client():
    load_dotenv()
    endpoint = os.getenv("PROJECT_ENDPOINT")
    deployment = os.getenv("MODEL_DEPLOYMENT")
    if not endpoint or not deployment:
        raise RuntimeError("Missing PROJECT_ENDPOINT or MODEL_DEPLOYMENT in .env")
    project_client = AIProjectClient(
        credential=DefaultAzureCredential(exclude_environment_credential=True, exclude_managed_identity_credential=True),
        endpoint=endpoint,
    )
    openai_client = project_client.get_openai_client(api_version="2024-10-21")
    return openai_client, deployment

openai_client, MODEL_DEPLOYMENT = _build_client()

def _chat(messages: List[Dict[str, Any]]) -> str:
    resp = openai_client.chat.completions.create(model=MODEL_DEPLOYMENT, messages=messages)
    return resp.choices[0].message.content

def send_message(user_msg: str, chat_history: List[Dict[str, str]], system_msg: str, messages_state: List[Dict[str, Any]]):
    if not user_msg.strip():
        return gr.update(), messages_state
    if messages_state and messages_state[0].get("role") == "system":
        messages_state[0]["content"] = system_msg or SYSTEM_DEFAULT
    messages_state.append({"role": "user", "content": user_msg})
    try:
        assistant = _chat(messages_state)
    except Exception as e:
        assistant = f"Error: {e}"
    messages_state.append({"role": "assistant", "content": assistant})
    chat_history = chat_history + [{"role": "user", "content": user_msg}, {"role": "assistant", "content": assistant}]
    return chat_history, messages_state

def reset_chat(system_msg: str):
    return [], [{"role": "system", "content": system_msg or SYSTEM_DEFAULT}]

with gr.Blocks(css=CUSTOM_CSS, theme=THEME, elem_id="root") as demo:
    with gr.Column(elem_id="shell"):
        with gr.Column(elem_id="card"):
            gr.Markdown("# Project LevelUP – Generative AI Chat", elem_id="title")
            gr.Markdown("Type a question and get an answer using your configured Azure model deployment.", elem_id="subtitle")
            with gr.Column(elem_id="stack"):
                system_box = gr.Textbox(label="System message (optional)", value=SYSTEM_DEFAULT, lines=3, elem_id="system-box")
                chatbot = gr.Chatbot(height=520, elem_id="chatbot", type="messages")
                user_box = gr.Textbox(label="Your message", placeholder="Ask anything…", lines=3, elem_id="user-box")
                messages_state = gr.State(value=[{"role": "system", "content": SYSTEM_DEFAULT}])
                with gr.Row(elem_id="actions"):
                    clear_btn = gr.Button("Clear", elem_id="clear-btn")
                    send_btn = gr.Button("Send", elem_id="send-btn")
                send_btn.click(send_message, inputs=[user_box, chatbot, system_box, messages_state], outputs=[chatbot, messages_state])
                user_box.submit(send_message, inputs=[user_box, chatbot, system_box, messages_state], outputs=[chatbot, messages_state])
                clear_btn.click(reset_chat, inputs=[system_box], outputs=[chatbot, messages_state])

if __name__ == "__main__":
    demo.launch()  # zmiana portu

