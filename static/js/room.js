document.addEventListener("DOMContentLoaded", () => {
    const chatPanel = document.getElementById("chat-panel");
    const chatBtn = document.getElementById("chat-toggle-btn");
    const closeChat = document.getElementById("close-chat");

    const chatLog = document.getElementById("chat-log");
    const messageInput = document.getElementById("chat-message-input");
    const sendBtn = document.getElementById("send");
    const typingIndicator = document.getElementById("typing-indicator");

    const resizeHandle = document.getElementById("chat-resize-handle");

    let isResizing = false;
    let typingTimeout;
    const typingUsers = new Set();

    /* ================= UTILS ================= */

    function scrollBottom() {
        const nearBottom =
            chatLog.scrollHeight - chatLog.scrollTop - chatLog.clientHeight < 100;

        if (nearBottom) {
            chatLog.scrollTop = chatLog.scrollHeight;
        }
    }

    function sendSocket(data) {
        if (chatSocket && chatSocket.readyState === WebSocket.OPEN) {
            chatSocket.send(JSON.stringify(data));
        }
    }

    /* ================= CHAT PANEL ================= */

    chatBtn?.addEventListener("click", () => {
        chatPanel.classList.toggle("open");
    });

    closeChat?.addEventListener("click", () => {
        chatPanel.classList.remove("open");
    });

    /* ================= WEBSOCKET ================= */

    const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";

    const chatSocket = new WebSocket(
        protocol + window.location.host + "/ws/room/chat/" + roomName + "/"
    );

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);

        /* ===== CHAT MESSAGE ===== */
        if (data.type === "chat") {
            const cls = data.username === currentUser ? "me" : "other";

            const msgDiv = document.createElement("div");
            msgDiv.className = `msg ${cls}`;

            msgDiv.innerHTML = `
                <div class="sender">${data.username}</div>
                <div class="message-text">${data.message}</div>
                <div class="time">now</div>
            `;

            chatLog.appendChild(msgDiv);
            scrollBottom();
        }

        /* ===== TYPING ===== */
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

    /* ================= SEND MESSAGE ================= */

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

    /* ================= TYPING ================= */

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

    /* ================= RESIZE CHAT PANEL ================= */

    if (resizeHandle) {
        resizeHandle.addEventListener("mousedown", () => {
            isResizing = true;
            document.body.style.cursor = "ew-resize";
        });

        document.addEventListener("mousemove", (e) => {
            if (!isResizing) return;

            const newWidth = window.innerWidth - e.clientX;

            if (newWidth >= 260 && newWidth <= 800) {
                chatPanel.style.width = newWidth + "px";
            }
        });

        document.addEventListener("mouseup", () => {
            isResizing = false;
            document.body.style.cursor = "default";
        });
    }
});