const messageInput=document.getElementById("message-input");

const sendButton=document.getElementById("send-button");

const clearButton=document.getElementById("clear-button");

const newChatButton=document.getElementById("new-chat-button");

const chatBox=document.getElementById("chat-box");

const chatList=document.getElementById("chat-list");

function formatMessage(message)
{
let formattedMessage=message;

// Escape HTML characters

formattedMessage=formattedMessage
    .replace(/&/g,"&amp;")
    .replace(/</g,"&lt;")
    .replace(/>/g,"&gt;");


// Format code blocks

formattedMessage=formattedMessage.replace(
    /```(?:python|javascript|java|c|cpp|html|css|bash|sql)?\n?([\s\S]*?)```/gi,
    function(match,code)
    {
        return "<pre><code>"+
            code.trim()+
            "</code></pre>";
    }
);


// Format inline code

formattedMessage=formattedMessage.replace(
    /`([^`\n]+)`/g,
    "<code>$1</code>"
);


// Format bold text

formattedMessage=formattedMessage.replace(
    /\*\*(.*?)\*\*/g,
    "<strong>$1</strong>"
);


// Format line breaks

formattedMessage=formattedMessage.replace(
    /\n/g,
    "<br>"
);


// Restore code block line breaks

formattedMessage=formattedMessage.replace(
    /<pre><code>([\s\S]*?)<\/code><\/pre>/g,
    function(match,code)
    {
        return "<pre><code>"+
            code.replace(/<br>/g,"\n")+
            "</code></pre>";
    }
);


return formattedMessage;

}

function addMessage(message,role)
{
const messageElement=document.createElement("div");

if(role==="user")
{
    messageElement.className="message user-message";
}
else
{
    messageElement.className="message ai-message";
}


messageElement.innerHTML=formatMessage(message);


chatBox.appendChild(messageElement);


chatBox.scrollTop=chatBox.scrollHeight;

}

function showWelcomeMessage()
{
chatBox.innerHTML="";

addMessage(
    "Hello! I am Sumit's AI chatbot. How can I help you?",
    "assistant"
);

}

async function loadChats()
{
try
{
const response=await fetch("/chats");

    const data=await response.json();


    chatList.innerHTML="";


    data.chats.forEach(function(chat)
    {
        const chatItem=document.createElement("div");

        chatItem.className="chat-item";


        if(chat.chat_id===data.current_chat)
        {
            chatItem.classList.add("active-chat");
        }


        const chatTitle=document.createElement("span");

        chatTitle.className="chat-title";

        chatTitle.textContent=chat.title;


        const deleteButton=document.createElement("button");

        deleteButton.className="delete-chat-button";

        deleteButton.innerHTML=`
            <span class="chat-delete-sign">
                🗑
            </span>

            <span class="chat-delete-text">
                Delete
            </span>
        `;


        deleteButton.addEventListener(
            "click",
            function(event)
            {
                event.stopPropagation();

                deleteChat(chat.chat_id);
            }
        );


        chatItem.appendChild(chatTitle);

        chatItem.appendChild(deleteButton);


        chatItem.addEventListener(
            "click",
            function()
            {
                switchChat(chat.chat_id);
            }
        );


        chatList.appendChild(chatItem);
    });

}
catch(error)
{
    console.log("Could not load chats.");
}

}

async function loadCurrentChat()
{
try
{
const response=await fetch("/history");

    const data=await response.json();


    chatBox.innerHTML="";


    if(data.history.length===0)
    {
        showWelcomeMessage();

        return;
    }


    data.history.forEach(function(message)
    {
        addMessage(
            message.content,
            message.role
        );
    });

}
catch(error)
{
    showWelcomeMessage();
}

}

async function sendMessage()
{
const message=messageInput.value.trim();

if(message==="")
{
    return;
}


addMessage(
    message,
    "user"
);


messageInput.value="";

sendButton.disabled=true;


/*
 * Loading indicator
 * Uses a separate class so there is
 * no AI message box around the dots.
 */

const thinkingMessage=document.createElement("div");

thinkingMessage.className="thinking-message";


thinkingMessage.innerHTML=`
    <div class="dots-container">
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    </div>
`;


chatBox.appendChild(thinkingMessage);


chatBox.scrollTop=chatBox.scrollHeight;


try
{
    const response=await fetch(
        "/chat",
        {
            method:"POST",

            headers:
            {
                "Content-Type":"application/json"
            },

            body:JSON.stringify(
                {
                    message:message
                }
            )
        }
    );


    const data=await response.json();


    /*
     * Response is ready.
     * Change the loading element into
     * a normal AI message box.
     */

    thinkingMessage.className="message ai-message";

    thinkingMessage.innerHTML=formatMessage(
        data.response
    );


    await loadChats();

}
catch(error)
{
    /*
     * Error also becomes a normal
     * AI message box.
     */

    thinkingMessage.className="message ai-message";

    thinkingMessage.textContent=
        "Sorry, something went wrong.";
}


sendButton.disabled=false;

messageInput.focus();

chatBox.scrollTop=chatBox.scrollHeight;

}

async function createNewChat()
{
try
{
const response=await fetch(
"/new-chat",
{
method:"POST"
}
);

    const data=await response.json();


    if(response.ok)
    {
        chatBox.innerHTML="";


        showWelcomeMessage();


        await loadChats();


        messageInput.focus();
    }

}
catch(error)
{
    alert(
        "Sorry, a new chat could not be created."
    );
}

}

async function switchChat(chatId)
{
try
{
const response=await fetch(
"/switch-chat",
{
method:"POST",

            headers:
            {
                "Content-Type":"application/json"
            },

            body:JSON.stringify(
                {
                    chat_id:chatId
                }
            )
        }
    );


    if(!response.ok)
    {
        return;
    }


    await loadCurrentChat();

    await loadChats();


    messageInput.focus();

}
catch(error)
{
    alert(
        "Sorry, the chat could not be opened."
    );
}

}

/* ========================================= /
/ Custom Delete Confirmation /
/ ========================================= */

function showDeleteConfirmation(chatId)
{
const overlay=document.createElement("div");

overlay.className="delete-confirmation-overlay";


const card=document.createElement("div");

card.className="delete-confirmation-card";


const icon=document.createElement("div");

icon.className="delete-confirmation-icon";

icon.innerHTML="🗑️";


const heading=document.createElement("div");

heading.className="delete-confirmation-heading";

heading.textContent="Delete Chat?";


const description=document.createElement("div");

description.className="delete-confirmation-description";

description.textContent=
    "Are you sure you want to delete this chat? This action cannot be undone.";


const buttonContainer=document.createElement("div");

buttonContainer.className="delete-button-container";


const acceptButton=document.createElement("button");

acceptButton.className="delete-accept-button";

acceptButton.textContent="Delete";


const declineButton=document.createElement("button");

declineButton.className="delete-decline-button";

declineButton.textContent="Cancel";


buttonContainer.appendChild(acceptButton);

buttonContainer.appendChild(declineButton);


card.appendChild(icon);

card.appendChild(heading);

card.appendChild(description);

card.appendChild(buttonContainer);


overlay.appendChild(card);

document.body.appendChild(overlay);


/* Delete */

acceptButton.addEventListener(
    "click",
    async function()
    {
        overlay.remove();

        await performDeleteChat(chatId);
    }
);


/* Cancel */

declineButton.addEventListener(
    "click",
    function()
    {
        overlay.remove();
    }
);


/* Click outside card */

overlay.addEventListener(
    "click",
    function(event)
    {
        if(event.target===overlay)
        {
            overlay.remove();
        }
    }
);


declineButton.focus();

}

async function performDeleteChat(chatId)
{
try
{
const response=await fetch(
"/delete-chat",
{
method:"POST",

            headers:
            {
                "Content-Type":"application/json"
            },

            body:JSON.stringify(
                {
                    chat_id:chatId
                }
            )
        }
    );


    if(response.ok)
    {
        await loadCurrentChat();

        await loadChats();

        messageInput.focus();
    }

}
catch(error)
{
    alert(
        "Sorry, the chat could not be deleted."
    );
}

}

function deleteChat(chatId)
{
showDeleteConfirmation(chatId);
}

async function clearChat()
{
try
{
const response=await fetch(
"/clear",
{
method:"POST"
}
);

    if(response.ok)
    {
        showWelcomeMessage();

        await loadChats();

        messageInput.focus();
    }

}
catch(error)
{
    alert(
        "Sorry, the chat could not be cleared."
    );
}

}

/* ========================================= /
/ Event Listeners /
/ ========================================= */

sendButton.addEventListener(
"click",
sendMessage
);

clearButton.addEventListener(
"click",
clearChat
);

newChatButton.addEventListener(
"click",
createNewChat
);

messageInput.addEventListener(
"keydown",
function(event)
{
if(event.key==="Enter")
{
sendMessage();
}
}
);

window.addEventListener(
"load",
async function()
{
await loadCurrentChat();

    await loadChats();

    messageInput.focus();
}

);