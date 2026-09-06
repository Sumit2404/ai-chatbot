from flask import Flask,request,jsonify,render_template,session
import requests
import re
import uuid
import sqlite3

app=Flask(__name__)

app.secret_key="sumits-ai-chatbot-secret-key"

LLAMA_URL="http://127.0.0.1:8080/v1/chat/completions"

DATABASE="chatbot.db"

MAX_HISTORY=5
MAX_TOKENS=200


SYSTEM_PROMPT="""You are Sumit's AI Chatbot.

You were created by Sumit.

Your name is Sumit's AI Chatbot.

You are a local AI chatbot built using:
- Python
- Flask
- llama.cpp
- Qwen3-0.6B
- SQLite
- HTML
- CSS
- JavaScript

IMPORTANT IDENTITY RULES:

1. If the user asks about YOUR name or identity, answer about the chatbot.

2. If the user asks who created, made, built, or developed you, answer that Sumit created you.

3. If the user asks about the technologies you use, mention:
Python, Flask, llama.cpp, Qwen3-0.6B, SQLite, HTML, CSS, and JavaScript.

IMPORTANT USER CONTEXT RULES:

4. Words such as "I", "me", "my", and "mine" refer to the USER when the user is talking about themselves.

5. Words such as "you", "your", and "yours" refer to the CHATBOT when the user is talking directly to you.

6. Information that the user tells you about themselves is information about the USER.

7. If previous user messages contain information about the user, use that information when it is relevant to the current question.

8. Never change a fact about the user into a fact about yourself.

9. Never say that the user's preference, experience, opinion, possession, or personal information belongs to the chatbot.

10. If the user asks "What is my favorite X?", "My" means the USER.

11. If the user asks "What is your favorite X?", "Your" means the CHATBOT.

12. Do not invent personal information about the user. If the information has not been provided, say that you do not know.

IMPORTANT USER NAME RULES:

13. If the user asks about the USER'S name, answer using their stored name.

14. NEVER mention the user's name unless the user directly asks about their name or the conversation is specifically about their name.

15. NEVER add statements such as "Your name is Sumit" to unrelated answers.

IMPORTANT GENERAL ANSWERING RULES:

16. If the user asks a general question such as "What is Python?", "Explain Java", "What is networking?", etc., answer ONLY the question asked.

17. Do not add unrelated personal information at the end of an answer.

18. Do not invent technologies or facts.

19. Answer naturally, clearly, and according to the requested length or format.

20. ALWAYS finish your answer completely.

21. NEVER stop in the middle of a sentence, paragraph, list, example, or explanation.

22. Keep normal answers concise enough to finish completely within the available response length.

23. If the user requests a specific number of paragraphs, points, examples, or steps, follow that format.

IMPORTANT:
The user's name and the chatbot's name are different.

- "My name" refers to the USER'S name when the user asks about their own name.
- "Your name" refers to the CHATBOT'S name.
- "My favorite..." refers to the USER'S favorite when the user is talking about themselves.
- "Your favorite..." refers to the CHATBOT'S favorite.
- Always use previous conversation context when it is relevant.
"""


def get_db_connection():

    connection=sqlite3.connect(DATABASE)

    connection.row_factory=sqlite3.Row

    return connection


def initialize_database():

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            session_id TEXT PRIMARY KEY,
            user_name TEXT DEFAULT ''
        )
    """)


    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table' AND name='messages'
    """)

    messages_exists=cursor.fetchone()


    if messages_exists:

        cursor.execute("PRAGMA table_info(messages)")

        columns=cursor.fetchall()

        column_names=[column["name"] for column in columns]


        if "chat_id" not in column_names:

            cursor.execute("""
                ALTER TABLE messages
                ADD COLUMN chat_id TEXT
            """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats(
            chat_id TEXT PRIMARY KEY,
            session_id TEXT,
            title TEXT,
            user_name TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES users(session_id)
        )
    """)


    cursor.execute("PRAGMA table_info(chats)")

    chat_columns=cursor.fetchall()

    chat_column_names=[column["name"] for column in chat_columns]


    if "user_name" not in chat_column_names:

        cursor.execute("""
            ALTER TABLE chats
            ADD COLUMN user_name TEXT DEFAULT ''
        """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(chat_id) REFERENCES chats(chat_id)
        )
    """)


    connection.commit()

    connection.close()


def create_session():

    session_id=str(uuid.uuid4())


    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        "INSERT INTO users(session_id,user_name) VALUES(?,?)",
        (session_id,"")
    )


    connection.commit()

    connection.close()


    return session_id


def get_session_id():

    if "session_id" not in session:

        session["session_id"]=create_session()

    else:

        session_id=session["session_id"]


        connection=get_db_connection()

        cursor=connection.cursor()


        cursor.execute(
            "SELECT session_id FROM users WHERE session_id=?",
            (session_id,)
        )


        result=cursor.fetchone()


        if not result:

            cursor.execute(
                "INSERT INTO users(session_id,user_name) VALUES(?,?)",
                (session_id,"")
            )

            connection.commit()


        connection.close()


    return session["session_id"]


def create_chat(session_id,title="New Chat"):

    chat_id=str(uuid.uuid4())


    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        INSERT INTO chats(chat_id,session_id,title,user_name)
        VALUES(?,?,?,?)
        """,
        (chat_id,session_id,title,"")
    )


    connection.commit()

    connection.close()


    return chat_id


def get_current_chat_id():

    session_id=get_session_id()


    if "chat_id" not in session:

        session["chat_id"]=create_chat(session_id)

    else:

        chat_id=session["chat_id"]


        connection=get_db_connection()

        cursor=connection.cursor()


        cursor.execute(
            """
            SELECT chat_id
            FROM chats
            WHERE chat_id=? AND session_id=?
            """,
            (chat_id,session_id)
        )


        result=cursor.fetchone()


        connection.close()


        if not result:

            session["chat_id"]=create_chat(session_id)


    return session["chat_id"]


# ==========================================================
# CHAT-SPECIFIC USER NAME MEMORY
# ==========================================================

def get_user_name(chat_id):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        "SELECT user_name FROM chats WHERE chat_id=?",
        (chat_id,)
    )


    result=cursor.fetchone()


    connection.close()


    if result:

        return result["user_name"] or ""


    return ""


def save_user_name(chat_id,user_name):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        "UPDATE chats SET user_name=? WHERE chat_id=?",
        (user_name,chat_id)
    )


    connection.commit()

    connection.close()


def save_message(chat_id,role,content):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        INSERT INTO messages(chat_id,role,content)
        VALUES(?,?,?)
        """,
        (chat_id,role,content)
    )


    connection.commit()

    connection.close()


def get_conversation(chat_id):

    conversation=[
        {
            "role":"system",
            "content":SYSTEM_PROMPT
        }
    ]


    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        SELECT role,content
        FROM messages
        WHERE chat_id=?
        ORDER BY id DESC
        LIMIT ?
        """,
        (chat_id,MAX_HISTORY*2)
    )


    rows=cursor.fetchall()


    connection.close()


    rows=rows[::-1]


    for row in rows:

        conversation.append(
            {
                "role":row["role"],
                "content":row["content"]
            }
        )


    return conversation


def get_history(chat_id):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        SELECT role,content
        FROM messages
        WHERE chat_id=?
        ORDER BY id ASC
        """,
        (chat_id,)
    )


    rows=cursor.fetchall()


    connection.close()


    history=[]


    for row in rows:

        history.append(
            {
                "role":row["role"],
                "content":row["content"]
            }
        )


    return history


def get_chats(session_id):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        SELECT chat_id,title,created_at
        FROM chats
        WHERE session_id=?
        ORDER BY created_at DESC
        """,
        (session_id,)
    )


    rows=cursor.fetchall()


    connection.close()


    chats=[]


    for row in rows:

        chats.append(
            {
                "chat_id":row["chat_id"],
                "title":row["title"],
                "created_at":row["created_at"]
            }
        )


    return chats


def clear_chat_messages(chat_id):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )


    cursor.execute(
        """
        UPDATE chats
        SET title=?,user_name=?
        WHERE chat_id=?
        """,
        ("New Chat","",chat_id)
    )


    connection.commit()

    connection.close()


def delete_chat(chat_id,session_id):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        "DELETE FROM messages WHERE chat_id=?",
        (chat_id,)
    )


    cursor.execute(
        """
        DELETE FROM chats
        WHERE chat_id=? AND session_id=?
        """,
        (chat_id,session_id)
    )


    connection.commit()

    connection.close()


def update_chat_title(chat_id,user_message):

    title=user_message.strip()

    lower_message=title.lower()


    prefixes=[
        "what is ",
        "what are ",
        "what was ",
        "what were ",
        "who is ",
        "who are ",
        "who was ",
        "who were ",
        "how do i ",
        "how can i ",
        "how to ",
        "why is ",
        "why are ",
        "why do ",
        "why does ",
        "explain ",
        "tell me about ",
        "can you explain ",
        "can you tell me about "
    ]


    for prefix in prefixes:

        if lower_message.startswith(prefix):

            title=title[len(prefix):].strip()

            break


    title=title.rstrip("?!. ")


    if "difference between" in lower_message:

        parts=title.lower().split(
            "difference between",
            1
        )


        if len(parts)>1:

            comparison=parts[1].strip()

            comparison=comparison.replace(
                " and ",
                " vs "
            )

            title=comparison


    elif lower_message.startswith("how can i learn"):

        title=title.replace(
            "learn",
            "Learning",
            1
        )


    elif lower_message.startswith("how do i create"):

        title=title.replace(
            "create",
            "Creating",
            1
        )


    if len(title)>35:

        title=title[:35].strip()


        if " " in title:

            title=title.rsplit(" ",1)[0]


        title=title+"..."


    if title=="":

        title="New Chat"


    title=title[0].upper()+title[1:]


    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        UPDATE chats
        SET title=?
        WHERE chat_id=? AND title='New Chat'
        """,
        (title,chat_id)
    )


    connection.commit()

    connection.close()


def save_and_return(chat_id,user_message,ai_message):

    save_message(
        chat_id,
        "user",
        user_message
    )


    update_chat_title(
        chat_id,
        user_message
    )


    save_message(
        chat_id,
        "assistant",
        ai_message
    )


    return jsonify(
        {
            "response":ai_message
        }
    )


def clean_ai_response(ai_message):

    if not isinstance(ai_message,str):

        return ""


    ai_message=ai_message.strip()


    unwanted_name_patterns=[
        r"\s*Your name is Sumit[.!]?\s*$",
        r"\s*Your name is Sumit's AI Chatbot[.!]?\s*$"
    ]


    for pattern in unwanted_name_patterns:

        ai_message=re.sub(
            pattern,
            "",
            ai_message,
            flags=re.IGNORECASE
        ).strip()


    return ai_message


# ==========================================================
# USER FACT DETECTION
# ==========================================================

def detect_user_fact(user_message):

    patterns=[
        (
            r"^\s*my favorite programming language is\s+(.+?)\s*[.!]?\s*$",
            "favorite programming language"
        ),
        (
            r"^\s*my favourite programming language is\s+(.+?)\s*[.!]?\s*$",
            "favorite programming language"
        ),
        (
            r"^\s*my favorite language is\s+(.+?)\s*[.!]?\s*$",
            "favorite programming language"
        ),
        (
            r"^\s*my favourite language is\s+(.+?)\s*[.!]?\s*$",
            "favorite programming language"
        )
    ]


    for pattern,fact_name in patterns:

        match=re.match(
            pattern,
            user_message,
            re.IGNORECASE
        )


        if match:

            return fact_name,match.group(1).strip()


    return "", ""


def get_user_fact(chat_id,fact_name):

    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        SELECT content
        FROM messages
        WHERE chat_id=? AND role='user'
        ORDER BY id ASC
        """,
        (chat_id,)
    )


    rows=cursor.fetchall()


    connection.close()


    for row in rows:

        detected_fact,value=detect_user_fact(
            row["content"]
        )


        if detected_fact==fact_name:

            return value


    return ""


# ==========================================================
# USER FACT QUESTIONS
# ==========================================================

def is_favorite_programming_language_question(user_message):

    patterns=[
        r"\bwhat is my favorite programming language\b",
        r"\bwhat's my favorite programming language\b",
        r"\bwhat’s my favorite programming language\b",
        r"\bwhat is my favourite programming language\b",
        r"\bwhat's my favourite programming language\b",
        r"\bwhat’s my favourite programming language\b",
        r"\bwhat is my favorite language\b",
        r"\bwhat's my favorite language\b",
        r"\bwhat’s my favorite language\b",
        r"\bwhat is my favourite language\b",
        r"\bwhat's my favourite language\b",
        r"\bwhat’s my favourite language\b"
    ]


    for pattern in patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            return True


    return False


initialize_database()


@app.route("/")
def home():

    return render_template("index.html")


@app.route("/history",methods=["GET"])
def history():

    chat_id=get_current_chat_id()


    return jsonify(
        {
            "history":get_history(chat_id)
        }
    )


@app.route("/chats",methods=["GET"])
def chats():

    session_id=get_session_id()


    return jsonify(
        {
            "chats":get_chats(session_id),
            "current_chat":get_current_chat_id()
        }
    )


@app.route("/new-chat",methods=["POST"])
def new_chat():

    session_id=get_session_id()

    chat_id=create_chat(session_id)

    session["chat_id"]=chat_id


    return jsonify(
        {
            "message":"New chat created.",
            "chat_id":chat_id
        }
    )


@app.route("/switch-chat",methods=["POST"])
def switch_chat():

    session_id=get_session_id()

    data=request.get_json() or {}

    chat_id=data.get("chat_id","")


    if not chat_id:

        return jsonify(
            {
                "error":"Chat ID is required."
            }
        ),400


    connection=get_db_connection()

    cursor=connection.cursor()


    cursor.execute(
        """
        SELECT chat_id
        FROM chats
        WHERE chat_id=? AND session_id=?
        """,
        (chat_id,session_id)
    )


    result=cursor.fetchone()


    connection.close()


    if not result:

        return jsonify(
            {
                "error":"Chat not found."
            }
        ),404


    session["chat_id"]=chat_id


    return jsonify(
        {
            "message":"Chat switched successfully.",
            "chat_id":chat_id
        }
    )


@app.route("/delete-chat",methods=["POST"])
def remove_chat():

    session_id=get_session_id()

    data=request.get_json() or {}

    chat_id=data.get("chat_id","")


    if not chat_id:

        return jsonify(
            {
                "error":"Chat ID is required."
            }
        ),400


    delete_chat(
        chat_id,
        session_id
    )


    if session.get("chat_id")==chat_id:

        session["chat_id"]=create_chat(session_id)


    return jsonify(
        {
            "message":"Chat deleted successfully.",
            "chat_id":session["chat_id"]
        }
    )


@app.route("/clear",methods=["POST"])
def clear_chat():

    chat_id=get_current_chat_id()

    clear_chat_messages(chat_id)


    return jsonify(
        {
            "message":"Chat cleared successfully."
        }
    )


@app.route("/chat",methods=["POST"])
def chat():

    session_id=get_session_id()

    chat_id=get_current_chat_id()

    user_name=get_user_name(chat_id)


    data=request.get_json() or {}

    user_message=data.get("message","").strip()


    if user_message=="":

        return jsonify(
            {
                "response":"Please enter a message."
            }
        )


    # ==========================================================
    # USER NAME DETECTION
    # ==========================================================

    name_patterns=[
        r"^\s*my name is\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*i am\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*i'm\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*i am called\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*i'm called\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*call me\s+([a-zA-Z][a-zA-Z .'-]*)\s*$",
        r"^\s*you can call me\s+([a-zA-Z][a-zA-Z .'-]*)\s*$"
    ]


    detected_name=""


    for pattern in name_patterns:

        match=re.match(
            pattern,
            user_message,
            re.IGNORECASE
        )


        if match:

            detected_name=match.group(1).strip()

            break


    if detected_name:

        user_name=detected_name


        save_user_name(
            chat_id,
            user_name
        )


        return save_and_return(
            chat_id,
            user_message,
            "Nice to meet you, "+user_name+"!"
        )


    # ==========================================================
    # FAVORITE PROGRAMMING LANGUAGE DETECTION
    # ==========================================================

    detected_fact,fact_value=detect_user_fact(
        user_message
    )


    if detected_fact=="favorite programming language":

        return save_and_return(
            chat_id,
            user_message,
            "Got it! I'll remember that "
            +fact_value
            +" is your favorite programming language."
        )


    # ==========================================================
    # FAVORITE PROGRAMMING LANGUAGE QUESTION
    # ==========================================================

    if is_favorite_programming_language_question(
        user_message
    ):

        favorite_language=get_user_fact(
            chat_id,
            "favorite programming language"
        )


        if favorite_language:

            ai_message=(
                "Your favorite programming language is "
                +favorite_language
                +"."
            )

        else:

            ai_message=(
                "You haven't told me your favorite "
                "programming language yet."
            )


        return save_and_return(
            chat_id,
            user_message,
            ai_message
        )


    # ==========================================================
    # YES/NO USER NAME MEMORY QUESTIONS
    # ==========================================================

    yes_no_name_patterns=[
        r"\bdo you know my name\b",
        r"\bdo you remember my name\b",
        r"\bdo you know what my name is\b",
        r"\bdo you remember what my name is\b",
        r"\bdo you know my name or not\b",
        r"\bdo you remember my name or not\b"
    ]


    is_yes_no_name_question=False


    for pattern in yes_no_name_patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            is_yes_no_name_question=True

            break


    if is_yes_no_name_question:

        if user_name:

            ai_message="Yes."

        else:

            ai_message="No."


        return save_and_return(
            chat_id,
            user_message,
            ai_message
        )


    # ==========================================================
    # QUESTIONS ASKING FOR THE USER'S ACTUAL NAME
    # ==========================================================

    name_question_patterns=[
        r"\bwhat is my name\b",
        r"\bwhat's my name\b",
        r"\bwhat’s my name\b",
        r"\bcan you tell me my name\b",
        r"\bwhat do you call me\b",
        r"\bwhat is my full name\b",
        r"\bwhat's my full name\b",
        r"\bwhat’s my full name\b"
    ]


    is_name_question=False


    for pattern in name_question_patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            is_name_question=True

            break


    if is_name_question:

        if user_name:

            ai_message="Your name is "+user_name+"."

        else:

            ai_message="You haven't told me your name yet."


        return save_and_return(
            chat_id,
            user_message,
            ai_message
        )


    # ==========================================================
    # CHATBOT IDENTITY QUESTIONS
    # ==========================================================

    identity_patterns=[
        r"\bwhat is your name\b",
        r"\bwhat's your name\b",
        r"\bwhat’s your name\b",
        r"\bwho are you\b",
        r"\bwhat is your identity\b",
        r"\bwhat's your identity\b",
        r"\bwhat’s your identity\b"
    ]


    is_identity_question=False


    for pattern in identity_patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            is_identity_question=True

            break


    if is_identity_question:

        return save_and_return(
            chat_id,
            user_message,
            "My name is Sumit's AI Chatbot."
        )


    # ==========================================================
    # CREATOR QUESTIONS
    # ==========================================================

    creator_patterns=[
        r"\bwho created you\b",
        r"\bwho made you\b",
        r"\bwho built you\b",
        r"\bwho developed you\b",
        r"\bwho is your creator\b",
        r"\bwho is the creator of you\b",
        r"\bwho programmed you\b"
    ]


    is_creator_question=False


    for pattern in creator_patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            is_creator_question=True

            break


    if is_creator_question:

        return save_and_return(
            chat_id,
            user_message,
            "I was created by Sumit."
        )


    # ==========================================================
    # TECHNOLOGY QUESTIONS
    # ==========================================================

    technology_patterns=[
        r"\bwhat technologies do you use\b",
        r"\bwhat technology do you use\b",
        r"\bwhat tech do you use\b",
        r"\bwhat are you built with\b",
        r"\bwhat were you built with\b",
        r"\bwhat tools do you use\b",
        r"\bwhich technologies do you use\b",
        r"\bwhat is your technology\b",
        r"\bwhat technologies are you built with\b",
        r"\bwhich technologies are you built with\b"
    ]


    is_technology_question=False


    for pattern in technology_patterns:

        if re.search(
            pattern,
            user_message,
            re.IGNORECASE
        ):

            is_technology_question=True

            break


    if is_technology_question:

        ai_message=(
            "I use Python, Flask, llama.cpp, Qwen3-0.6B, "
            "SQLite, HTML, CSS, and JavaScript."
        )


        return save_and_return(
            chat_id,
            user_message,
            ai_message
        )


    # ==========================================================
    # NORMAL AI CONVERSATION
    # ==========================================================

    save_message(
        chat_id,
        "user",
        user_message
    )


    update_chat_title(
        chat_id,
        user_message
    )


    conversation=get_conversation(chat_id)


    try:

        response=requests.post(
            LLAMA_URL,
            json={
                "messages":conversation,
                "temperature":0.5,
                "max_tokens":MAX_TOKENS,
                "chat_template_kwargs":{
                    "enable_thinking":False
                }
            },
            timeout=120
        )


        response.raise_for_status()


        result=response.json()


        if (
            "choices" not in result
            or not result["choices"]
            or "message" not in result["choices"][0]
            or "content" not in result["choices"][0]["message"]
        ):

            raise ValueError(
                "Invalid response received from llama.cpp."
            )


        ai_message=result["choices"][0]["message"]["content"]


        ai_message=clean_ai_response(
            ai_message
        )


        if ai_message=="":

            ai_message=(
                "Sorry, I could not generate a complete response. "
                "Please try again."
            )


        save_message(
            chat_id,
            "assistant",
            ai_message
        )


        return jsonify(
            {
                "response":ai_message
            }
        )


    except requests.exceptions.ConnectionError:

        return jsonify(
            {
                "response":(
                    "Sorry, I cannot connect to the AI model. "
                    "Please make sure llama.cpp is running."
                )
            }
        ),500


    except requests.exceptions.Timeout:

        return jsonify(
            {
                "response":(
                    "Sorry, the AI model took too long to respond. "
                    "Please try again."
                )
            }
        ),500


    except requests.exceptions.RequestException as error:

        print("Request Error:",error)


        return jsonify(
            {
                "response":(
                    "Sorry, there was a problem communicating "
                    "with the AI model. Please try again."
                )
            }
        ),500


    except Exception as error:

        print("Error:",error)


        return jsonify(
            {
                "response":(
                    "Sorry, something went wrong while processing "
                    "your message."
                )
            }
        ),500


if __name__=="__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )