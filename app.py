"""
Edugenie AI - Flask Backend (Google Gemini powered)
Features:
1. /chat  -> AI study helper (answers student questions)
2. /quiz  -> AI quiz generator (generates MCQs on a given topic)

Setup:
1. pip install -r requirements.txt
2. Get a free Gemini API key: https://aistudio.google.com/app/apikey
3. Set your Gemini API key as an environment variable:
   Windows (cmd):   set GEMINI_API_KEY=your_key_here
   Windows (PS):    $env:GEMINI_API_KEY="your_key_here"
   Mac/Linux:       export GEMINI_API_KEY=your_key_here
4. Run: python app.py
5. Open: http://127.0.0.1:5000
"""

import os
import json
import re
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-flash-latest"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"


def call_gemini(system_instruction, user_prompt, max_tokens=800):
    """Helper to call Google Gemini's generateContent API."""
    if not GEMINI_API_KEY:
        return None, "No API key set. Please set GEMINI_API_KEY environment variable."

    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {
        "system_instruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [
            {"role": "user", "parts": [{"text": user_prompt}]}
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": max_tokens,
        },
    }
    try:
        resp = requests.post(GEMINI_URL, headers=headers, params=params, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        content = data["candidates"][0]["content"]["parts"][0]["text"]
        return content, None
    except Exception as e:
        # Print full details to the console so we can see exactly what's wrong
        print("=" * 60)
        print("GEMINI API ERROR:", str(e))
        try:
            print("RESPONSE BODY:", resp.text)
        except Exception:
            pass
        print("=" * 60)
        return None, str(e)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    """AI Study Helper - answers student's academic questions."""
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please enter a question."}), 400

    system_instruction = (
        "You are Edugenie AI, a friendly and knowledgeable study assistant. "
        "Explain concepts clearly and simply, like a helpful tutor. "
        "Keep answers concise but complete, use examples when useful."
    )

    answer, error = call_gemini(system_instruction, question, max_tokens=500)

    if error:
        # Fallback so the app still works / demos without an API key
        answer = fallback_chat_response(question)

    return jsonify({"answer": answer})


@app.route("/quiz", methods=["POST"])
def quiz():
    """AI Quiz Generator - generates MCQs on a topic."""
    data = request.get_json()
    topic = data.get("topic", "").strip()
    num_questions = int(data.get("num_questions", 5))
    difficulty = data.get("difficulty", "medium")

    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400

    system_instruction = "You are a quiz generator that outputs strict JSON only, with no markdown formatting."
    prompt = f"""Generate {num_questions} multiple choice questions on the topic "{topic}" at {difficulty} difficulty.
Return ONLY valid JSON, no extra text, in this exact format:
{{
  "questions": [
    {{
      "question": "question text",
      "options": ["A", "B", "C", "D"],
      "answer": "correct option text",
      "explanation": "short explanation"
    }}
  ]
}}"""

    content, error = call_gemini(system_instruction, prompt, max_tokens=1500)

    if error:
        return jsonify({"questions": fallback_quiz_response(topic, num_questions)})

    # Clean up in case model wraps JSON in markdown fences
    cleaned = re.sub(r"```json|```", "", content).strip()

    try:
        parsed = json.loads(cleaned)
        return jsonify(parsed)
    except json.JSONDecodeError:
        return jsonify({"questions": fallback_quiz_response(topic, num_questions)})


@app.route("/summarize", methods=["POST"])
def summarize():
    """Summary Module - condenses a long passage into key points."""
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Please paste some text to summarize."}), 400

    system_instruction = (
        "You are a summarization assistant for students. Read the passage and "
        "produce a concise, clear summary that retains the key points, suitable "
        "for quick revision. Use short bullet points where helpful."
    )

    summary, error = call_gemini(system_instruction, text, max_tokens=500)

    if error:
        summary = (
            "(Demo mode - no API key set)\n\n"
            "To get a real AI-generated summary, set your GEMINI_API_KEY "
            "environment variable and restart the server."
        )

    return jsonify({"summary": summary})


@app.route("/learning-path", methods=["POST"])
def learning_path():
    """Learning Path Module - generates a structured roadmap for a topic."""
    data = request.get_json()
    topic = data.get("topic", "").strip()

    if not topic:
        return jsonify({"error": "Please enter a topic."}), 400

    system_instruction = (
        "You are a learning-path generator. Create a structured roadmap to "
        "learn the given topic, organized into Beginner, Intermediate, and "
        "Advanced stages. For each stage list 2-4 subtopics and 1-2 suggested "
        "resources (type: video, article, or book). Keep it concise."
    )

    path, error = call_gemini(system_instruction, topic, max_tokens=700)

    if error:
        path = (
            "(Demo mode - no API key set)\n\n"
            f"Sample roadmap for '{topic}':\n"
            "Beginner: basics and terminology\n"
            "Intermediate: core concepts and practice\n"
            "Advanced: real-world projects\n\n"
            "Set your GEMINI_API_KEY environment variable and restart the "
            "server for a real, detailed roadmap."
        )

    return jsonify({"path": path})


def fallback_chat_response(question):
    """Used when no API key is configured, so the demo still works."""
    return (
        f"(Demo mode - no API key set)\n\n"
        f"You asked: '{question}'.\n"
        f"To get real AI-generated answers, set your GEMINI_API_KEY environment "
        f"variable and restart the server."
    )


def fallback_quiz_response(topic, num_questions):
    """Used when no API key is configured, so the demo still works."""
    questions = []
    for i in range(num_questions):
        questions.append(
            {
                "question": f"Sample question {i+1} about {topic}? (Demo mode - set GEMINI_API_KEY for real questions)",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "answer": "Option A",
                "explanation": "This is placeholder content shown because no API key is configured.",
            }
        )
    return questions


if __name__ == "__main__":
    app.run(debug=True)
