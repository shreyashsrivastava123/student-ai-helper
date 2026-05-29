from flask import Flask, render_template, request,redirect,url_for
import requests
import markdown
import json
import os
import time
app = Flask(__name__)
CHAT_FILE = "chats.json"

def load_chats():
    global all_chats

    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r", encoding="utf-8") as file:
            all_chats = json.load(file)
    else:
        all_chats = {
            "Chat 1": []
        }

def save_chats():
    with open(CHAT_FILE, "w", encoding="utf-8") as file:
        json.dump(all_chats, file, ensure_ascii=False, indent=4)

load_chats()

current_chat = list(all_chats.keys())[0]
@app.route("/", methods=["GET", "POST"])
def home():

    answer = ""
    question = ""
    language = "English"
    subject = "Science"
    if request.method == "POST":

        question = request.form["question"]
        subject = request.form["subject"]
        language = request.form["language"]
        print("Selected language:", language)
        start_time = time.time()
        response = requests.post(
            "http://127.0.0.1:1234/v1/chat/completions",
            json={
                "model": "google/gemma-3n-e4b",
                "messages": [
                    {
                        "role": "system",
                       "content": f"""

You are a helpful {subject} teacher.

The selected language is {language}.

You MUST answer ONLY in the selected language.

If subject is Maths:
Explain step-by-step clearly.
Keep formulas and mathematical terms in English.
Avoid difficult Hindi mathematical words.
Keep explanations concise and easy to understand.

If subject is Science:
Use simple explanations with examples.

If subject is History:
Explain in simple storytelling style.

If language is English:
Give detailed educational answers with explanations and examples.
Answer only in English.

If language is Hindi:
Use simple Hindi with common English educational terms.
Keep sentences short and easy.
Answer only in Hindi. Do not use any language other than the selected language and common English educational terms.

Keep answers clear, accurate and student-friendly.

Do not start answers with greetings.

Avoid excessive formatting unless necessary for clarity.

"""
                       
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }
        )

        data = response.json()

        answer = markdown.markdown(
            data["choices"][0]["message"]["content"]
            
        )
        end_time = time.time()

        response_time = round(end_time - start_time, 2)
        all_chats[current_chat].append({
    "question": question,
    "answer": answer,
    "response_time": response_time
})

        save_chats()
        return redirect(url_for("home", animate="true"))
    return render_template(
    "index.html",
    chat_history=all_chats.get(current_chat, []),
    chats=all_chats.keys(),
    current_chat=current_chat,
    selected_subject=subject,
    selected_language=language
)
@app.route("/new_chat")
def new_chat():
    global current_chat

    chat_number = 1

    while f"Chat {chat_number}" in all_chats:
     chat_number += 1
    chat_name = f"Chat {chat_number}"

    all_chats[chat_name] = []
    save_chats()
    current_chat = chat_name

    return redirect("/")
@app.route("/chat/<chat_name>")
def open_chat(chat_name):
    global current_chat

    if chat_name in all_chats:
        current_chat = chat_name

    return redirect("/")
@app.route("/delete_chat/<chat_name>")
def delete_chat(chat_name):

    global current_chat

    if chat_name in all_chats:

        del all_chats[chat_name]

        if len(all_chats) == 0:
            all_chats["Chat 1"] = []

        current_chat = list(all_chats.keys())[0]

        save_chats()

    return redirect("/")
@app.route("/rename_chat/<old_name>/<new_name>")
def rename_chat(old_name, new_name):

    global current_chat

    if old_name in all_chats:

        all_chats[new_name] = all_chats.pop(old_name)

        if current_chat == old_name:
            current_chat = new_name

        save_chats()

    return redirect("/")
app.run(debug=True)