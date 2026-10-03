const chatBox = document.getElementById("chat-box");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");


function addMessage(sender, message, type) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";

    const senderName = document.createElement("strong");
    senderName.textContent = sender;

    const messageText = document.createElement("div");
    messageText.className = "ai-response";

    messageText.textContent = message;

    contentDiv.appendChild(senderName);
    contentDiv.appendChild(messageText);

    messageDiv.appendChild(contentDiv);
    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


function addRecommendations(recommendations) {
    if (!recommendations || recommendations.length === 0) {
        return;
    }

    const container = document.createElement("div");
    container.className = "message bot-message";

    const content = document.createElement("div");
    content.className = "message-content recommendations";

    const title = document.createElement("strong");
    title.textContent = "Recommended AI Tools";

    content.appendChild(title);

    recommendations.forEach((tool) => {
        const card = document.createElement("div");
        card.className = "tool-card";

        const toolName = document.createElement("h3");
        toolName.textContent = tool.name;

        const description = document.createElement("p");
        description.textContent = tool.description;

        const bestFor = document.createElement("p");
        bestFor.innerHTML =
            "<strong>Best for:</strong> " +
            tool.best_for.join(", ");

        const categories = document.createElement("p");
        categories.innerHTML =
            "<strong>Categories:</strong> " +
            tool.categories.join(", ");

        const limitations = document.createElement("p");
        limitations.innerHTML =
            "<strong>Limitations:</strong> " +
            tool.limitations.join(", ");

        const link = document.createElement("a");
        link.href = tool.website;
        link.textContent = "Visit website →";
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        link.className = "tool-link";

        card.appendChild(toolName);
        card.appendChild(description);
        card.appendChild(bestFor);
        card.appendChild(categories);
        card.appendChild(limitations);
        card.appendChild(link);

        content.appendChild(card);
    });

    container.appendChild(content);
    chatBox.appendChild(container);

    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage() {
    const message = userInput.value.trim();

    if (!message) {
        return;
    }

    addMessage("You", message, "user");

    userInput.value = "";
    sendButton.disabled = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: message
            })
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const thinkingElement = document.getElementById("thinking-message");

if (thinkingElement) {
    thinkingElement.remove();
}
        const data = await response.json();

        addMessage(
            "AI Navigator",
            data.ai_reply,
            "bot"
        );

        addRecommendations(data.recommendations);

    } catch (error) {
        const thinkingElement = document.getElementById("thinking-message");

if (thinkingElement) {
    thinkingElement.remove();
}
        console.error("Chat error:", error);

        addMessage(
            "AI Navigator",
            "Sorry, something went wrong. Please try again.",
            "bot"
        );
    }

    sendButton.disabled = false;
    const thinkingMessage = document.createElement("div");
thinkingMessage.className = "message bot-message";
thinkingMessage.id = "thinking-message";

thinkingMessage.innerHTML = `
    <div class="message-content">
        <strong>AI Navigator</strong>
        <p>Thinking...</p>
    </div>
`;

chatBox.appendChild(thinkingMessage);
chatBox.scrollTop = chatBox.scrollHeight;
    userInput.focus();
}


sendButton.addEventListener("click", sendMessage);


userInput.addEventListener("keydown", function(event) {
    if (event.key === "Enter") {
        sendMessage();
    }
});


userInput.focus();