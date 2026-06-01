document.addEventListener("DOMContentLoaded", () => {
    const chatPanel = document.getElementById("chat-panel");
    const chatBtn = document.getElementById("chat-toggle-btn");
    const closeChat = document.getElementById("close-chat");

    const chatLog = document.getElementById("chat-log");
    const messageInput = document.getElementById("chat-message-input");
    const sendBtn = document.getElementById("send");
    const typingIndicator = document.getElementById("typing-indicator");

    let typingTimeout;
    const typingUsers = new Set();

    function scrollBottom() {
        chatLog.scrollTop = chatLog.scrollHeight;
    }

    function sendSocket(data) {
        if (chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify(data));
        }
    }

    /* PANEL */
    chatBtn?.addEventListener("click", () => {
        chatPanel.classList.toggle("open");
    });

    closeChat?.addEventListener("click", () => {
        chatPanel.classList.remove("open");
    });

    /* SOCKET FIX */
    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

    const chatSocket = new WebSocket(
        protocol + window.location.host + "/ws/chat/" + roomName + "/"
    );

    chatSocket.onmessage = (e) => {
        const data = JSON.parse(e.data);

        if (data.type === "chat") {
            const cls = data.username === currentUser ? "me" : "other";

            chatLog.insertAdjacentHTML(
                "beforeend",
                `
                <div class="msg ${cls}">
                    <div class="sender">${data.username}</div>
                    <div class="message-text">${data.message}</div>
                    <div class="time">now</div>
                </div>
                `
            );

            scrollBottom();
        }

        if (data.type === "typing" && data.username !== currentUser) {
            if (data.is_typing) {
                typingUsers.add(data.username);
            } else {
                typingUsers.delete(data.username);
            }

            typingIndicator.innerHTML =
                typingUsers.size > 0
                    ? [...typingUsers].join(", ") + " typing..."
                    : "";
        }
    };

    chatSocket.onerror = (e) => console.error("WebSocket error:", e);
    chatSocket.onclose = (e) => console.error("WebSocket closed:", e);

    function sendMessage() {
        const msg = messageInput.value.trim();
        if (!msg) return;

        sendSocket({
            type: "chat",
            message: msg,
        });

        messageInput.value = "";
    }

    sendBtn?.addEventListener("click", sendMessage);

    messageInput?.addEventListener("keyup", (e) => {
        if (e.key === "Enter") sendMessage();
    });

    messageInput?.addEventListener("input", () => {
        sendSocket({
            type: "typing",
            is_typing: true,
        });

        clearTimeout(typingTimeout);

        typingTimeout = setTimeout(() => {
            sendSocket({
                type: "typing",
                is_typing: false,
            });
        }, 800);
    });
});
