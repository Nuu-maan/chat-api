class ChatClient {
    constructor(roomId, userId) {
        this.roomId = roomId;
        this.userId = userId;
        this.ws = null;
        this.messageHandlers = new Map();
        this.connected = false;
    }

    connect() {
        const wsUrl = `ws://localhost:8000/ws/${this.roomId}/${this.userId}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to chat server');
            this.connected = true;
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            const handler = this.messageHandlers.get(data.type);
            if (handler) {
                handler(data);
            }
        };

        this.ws.onclose = () => {
            console.log('Disconnected from chat server');
            this.connected = false;
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.connected = false;
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
            this.connected = false;
        }
    }

    sendMessage(content, metadata = {}, replyTo = null) {
        if (!this.connected) {
            throw new Error('Not connected to chat server');
        }

        const message = {
            content,
            metadata,
            reply_to: replyTo
        };

        this.ws.send(JSON.stringify(message));
    }

    onMessage(handler) {
        this.messageHandlers.set('message', handler);
    }

    onHistory(handler) {
        this.messageHandlers.set('history', handler);
    }

    onSystem(handler) {
        this.messageHandlers.set('system', handler);
    }

    onError(handler) {
        this.messageHandlers.set('error', handler);
    }

    async getChatHistory(limit = 50) {
        const response = await fetch(`http://localhost:8000/api/v1/rooms/${this.roomId}/messages?limit=${limit}`);
        if (!response.ok) {
            throw new Error('Failed to fetch chat history');
        }
        return response.json();
    }

    async getRoomDetails() {
        const response = await fetch(`http://localhost:8000/api/v1/rooms/${this.roomId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch room details');
        }
        return response.json();
    }

    async getUserDetails(userId) {
        const response = await fetch(`http://localhost:8000/api/v1/users/${userId}`);
        if (!response.ok) {
            throw new Error('Failed to fetch user details');
        }
        return response.json();
    }
}

// Example usage:
const chat = new ChatClient('room123', 'user456');

// Set up message handlers
chat.onMessage((data) => {
    console.log('New message:', data.message);
});

chat.onHistory((data) => {
    console.log('Chat history:', data.messages);
});

chat.onSystem((data) => {
    console.log('System message:', data.message);
});

chat.onError((data) => {
    console.error('Error:', data.message);
});

// Connect to chat
chat.connect();

// Send a message
chat.sendMessage('Hello, world!', { type: 'text' });

// Get chat history
chat.getChatHistory().then(history => {
    console.log('Chat history:', history);
});

// Get room details
chat.getRoomDetails().then(room => {
    console.log('Room details:', room);
});

// Get user details
chat.getUserDetails('user456').then(user => {
    console.log('User details:', user);
}); 