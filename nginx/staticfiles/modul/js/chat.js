let chatSocket;
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const getModulId = document.getElementById("idModul");
const idModul = getModulId.getAttribute("data-id");
console.log("js conncted")
function connectWebSocket() {
    chatSocket = new WebSocket(
        'wss://' + window.location.host + `/ws/chat/${idModul}/`
    );
    chatSocket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const message = data.message;
        const isSentByUser = data.is_user;
        const fullName = data.full_name;
        const timestamp = data.timestamp;

        // Create chat message element
        const messageElement = document.createElement('div');
        messageElement.className = isSentByUser ? 'chat-message sent' : 'chat-message received';
        messageElement.innerHTML = isSentByUser ? `
            <div class="message-header">
                <span class="user-name">${fullName}</span>
            </div>
            <div class="message-content">${message}</div>
            <span class="timestamp text-white">${timestamp}</span>
        ` : `<div class="message-header">
            <span class="user-name">${fullName}</span>
        </div>
        <div class="message-content">${message}</div>
        <span class="timestamp">${timestamp}</span>`;

        chatMessages.appendChild(messageElement);
        scrollToBottom();
    };

    chatSocket.onopen = function(e) {
        console.log('Connected to chat');
    };

    sendButton.onclick = function() {
        const message = messageInput.value.trim();
        if (message) {
            chatSocket.send(JSON.stringify({
                'message': message,
                'is_user': true, 
            }));
            messageInput.value = '';
        }
    };

    messageInput.onkeyup = function(e) {
        if (e.key === 'Enter') {
            sendButton.click();
        }
    };

    chatSocket.onclose = function(e) {
        console.error('Chat socket closed unexpectedly, attempting to reconnect...');
        setTimeout(connectWebSocket, 3000); 
    };
}
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
scrollToBottom();
connectWebSocket();