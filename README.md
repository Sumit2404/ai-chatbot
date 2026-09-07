# Sumit's AI Chatbot

A local AI chatbot built from scratch using **Python, Flask, SQLite, llama.cpp, and Qwen3-0.6B**.

The project is designed to run AI inference locally without depending on cloud-based AI APIs. It also supports multiple conversations, persistent chat history, personal context, and basic coding assistance.

---

## Project Screenshot

<img width="1365" height="703" alt="image" src="https://github.com/user-attachments/assets/9a9a4d2e-8285-4322-8238-d35a89f28c7a" />


---

## Features

* AI-powered conversational chatbot
* Local AI inference using **Qwen3-0.6B**
* Model execution using **llama.cpp**
* Multiple chat conversations
* Persistent chat history using **SQLite**
* Create, switch, clear, and delete chats
* Remembers user-specific information within conversations
* Custom chatbot identity and creator information
* Basic programming and coding assistance
* Automatic response cleanup and formatting
* Thinking/loading animation
* Responsive interface for different screen sizes
* Runs locally without requiring a cloud AI API

---

## Technologies Used

### Frontend

* HTML
* CSS
* JavaScript

### Backend

* Python
* Flask
* Requests

### Database

* SQLite

### AI / Inference

* llama.cpp
* Qwen3-0.6B
* GGUF model format

---

## Project Architecture

```text
User
 │
 ▼
HTML / CSS / JavaScript
 │
 ▼
Flask Backend
 │
 ├── SQLite Database
 │
 └── llama.cpp Server
          │
          ▼
     Qwen3-0.6B
```

The Flask backend handles chat requests, conversation management, user context, and database operations.

AI-generated responses are produced locally through the llama.cpp server running the Qwen3-0.6B model.

---

## Project Structure

```text
ai-chatbot/
│
├── app.py
├── chatbot.db
├── requirements.txt
├── README.md
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
└── venv/
```

> `venv/` is used only for the local Python environment and should not be uploaded to GitHub.

The AI model file is also kept separately from the project repository.

---

## How to Run

### 1. Clone the Repository

```bash
git clone https://github.com/Sumit2404/ai-chatbot.git
cd ai-chatbot
```

### 2. Create and Activate the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install the Required Python Packages

```bash
pip install -r requirements.txt
```

### 4. Start the llama.cpp Server

Make sure `llama.cpp` is installed and the Qwen3-0.6B GGUF model is available.

Example:

```bash
cd ~/llama.cpp
./build/bin/llama-server \
-m /home/sumit/llama-models/Qwen3-0.6B-Q4_0.gguf \
--host 127.0.0.1 \
--port 8080
```

The llama.cpp server should start on:

```text
http://127.0.0.1:8080
```

### 5. Start the Flask Application

Open another terminal:

```bash
cd ~/ai-chatbot
source venv/bin/activate
python app.py
```

The Flask application should start on:

```text
http://127.0.0.1:5000
```

Open the address in your browser to use the chatbot.

---

## Example Capabilities

The chatbot can answer questions such as:

```text
What is your name?
```

```text
Who created you?
```

```text
What technologies were used to build you?
```

```text
Explain what Flask is in simple words.
```

```text
Write a Python program to check whether a number is prime.
```

It can also maintain separate conversations using the multiple-chat system.

---

## Local AI

Unlike applications that send prompts to external AI APIs, this project performs inference locally using:

**Qwen3-0.6B → llama.cpp → Flask → Web Interface**

This makes the project useful for learning how a local language model can be integrated into a full-stack web application.

Because the model runs locally on CPU hardware, response speed and generation quality depend on the available system resources and the size of the model.

---

## Database

The application uses **SQLite** to persist chatbot data.

The database stores:

* Users
* Chat conversations
* Chat titles
* Messages
* User-specific context

This allows conversations to remain available even after refreshing or restarting the Flask application.

---

## Project Goals

This project was created to gain practical experience with:

* Full-stack web development
* Flask backend development
* REST-style API communication
* SQLite database integration
* Session-based authentication/context
* Local LLM inference
* llama.cpp
* Prompt engineering
* Conversation management
* Frontend and backend integration

---

## System Requirements

The project is designed to work with relatively lightweight hardware when using a small quantized model.

Example development environment:

```text
OS: Linux Mint XFCE
CPU: Intel Celeron N4120
RAM: 4 GB
Python: 3.x
Model: Qwen3-0.6B Q4_0 GGUF
Inference: CPU via llama.cpp
```

Performance will vary depending on the hardware and model configuration.

---

## Privacy

Since the AI model runs locally through llama.cpp, prompts and generated responses do not need to be sent to a third-party cloud AI service.

The application stores conversation data locally in its SQLite database.

---

## About

**Sumit's AI Chatbot** was developed as a personal learning and portfolio project to explore the integration of local AI models with a full-stack web application.

The project combines:

**Python + Flask + SQLite + JavaScript + llama.cpp + Qwen3-0.6B**

into a single local AI chatbot application.

---

## Future Improvements

Possible future improvements include:

* Deployment for remote access
* Improved response generation
* Support for larger models
* Streaming AI responses
* Better authentication
* Additional personalization
* Improved mobile UI

---

## Acknowledgements

* **Qwen** for the Qwen3 language model
* **llama.cpp** for the local LLM inference framework
* **Flask** for the Python web framework
* **SQLite** for the lightweight database system

---

If you find this project interesting, feel free to explore the repository and the implementation.
