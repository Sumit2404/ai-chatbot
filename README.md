# AI Chatbot

A locally running AI chatbot built using Python, Flask, SQLite, JavaScript, llama.cpp and the Qwen3-0.6B language model.

The project provides a web-based chat interface with persistent conversations, multiple chat sessions and personalized conversation handling.

## Features

- AI-powered conversational interface
- Local LLM inference using llama.cpp
- Qwen3-0.6B language model
- Web interface built with HTML, CSS and JavaScript
- Python Flask backend
- SQLite database for persistent chat storage
- Multiple chat sessions
- Create new conversations
- Switch between previous conversations
- Delete conversations
- Clear chat history
- Flask session-based user handling
- Enter-to-send support
- Automatic chat scrolling
- Thinking/loading indicator
- Conversation isolation between chats

## Technologies Used

### Frontend

- HTML5
- CSS3
- JavaScript

### Backend

- Python
- Flask
- Requests

### Database

- SQLite

### AI and LLM

- llama.cpp
- Qwen3-0.6B
- GGUF model format

## Project Architecture

The application follows this architecture:

```text
User
 |
 | interacts with
 v
HTML / CSS / JavaScript
 |
 | HTTP requests
 v
Python Flask Backend
 |
 +--------------------> SQLite Database
 |                         |
 |                         +-- Users
 |                         +-- Chats
 |                         +-- Messages
 |
 | API request
 v
llama.cpp Server
 |
 v
Qwen3-0.6B GGUF Model
 |
 | generated response
 v
Flask Backend
 |
 v
Web Chat Interface
