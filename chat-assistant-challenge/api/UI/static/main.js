// Simple JavaScript for the chat widget
document.addEventListener('DOMContentLoaded', function() {
    const chatWidget = document.getElementById('chat-widget');
    
    // Create a simple chat interface
    const chatInterface = document.createElement('div');
    chatInterface.innerHTML = `
        <div style="border: 1px solid #ccc; padding: 20px; border-radius: 5px; margin: 20px; font-family: Arial, sans-serif;">
            <h2>Humanity API Chatbot</h2>
            <div id="chat-messages" style="height: 300px; overflow-y: auto; border: 1px solid #eee; padding: 10px; margin-bottom: 10px;"></div>
            <div style="display: flex;">
                <input type="text" id="chat-input" style="flex-grow: 1; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" placeholder="Type your message here...">
                <button id="send-button" style="margin-left: 10px; padding: 8px 15px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer;">Send</button>
            </div>
        </div>
    `;
    chatWidget.appendChild(chatInterface);
    
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const sendButton = document.getElementById('send-button');
    
    // Add a welcome message
    addMessage('assistant', 'Welcome to the Humanity API Chatbot. Please log in to continue.');
    
    // Add login interface
    const loginInterface = document.createElement('div');
    loginInterface.innerHTML = `
        <div style="margin-top: 20px; padding: 10px; border: 1px solid #eee; border-radius: 4px;">
            <h3>Login</h3>
            <div style="margin-bottom: 10px;">
                <label for="username">Username: </label>
                <input type="text" id="username" style="padding: 5px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <div style="margin-bottom: 10px;">
                <label for="password">Password: </label>
                <input type="password" id="password" style="padding: 5px; border: 1px solid #ddd; border-radius: 4px;">
            </div>
            <button id="login-button" style="padding: 8px 15px; background-color: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;">Login</button>
        </div>
    `;
    chatWidget.appendChild(loginInterface);
    
    const loginButton = document.getElementById('login-button');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    loginButton.addEventListener('click', function() {
        const username = usernameInput.value;
        const password = passwordInput.value;
        
        if (!username || !password) {
            addMessage('assistant', 'Please enter both username and password.');
            return;
        }
        
        // Instead of trying to login with the server, we'll just simulate a successful login
        loginInterface.style.display = 'none';
        addMessage('assistant', `You are now logged in as ${username}. How can I help you today?`);
        
        // Enable the chat functionality
        chatInput.disabled = false;
        sendButton.disabled = false;
    });
    
    // Send button click event
    sendButton.addEventListener('click', sendMessage);
    
    // Enter key press event
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });
    
    // Disable input until logged in
    chatInput.disabled = true;
    sendButton.disabled = true;
    
    function sendMessage() {
        const message = chatInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage('user', message);
            
            // Clear input
            chatInput.value = '';
            
            // Simulate bot response based on user message
            setTimeout(() => {
                let response = "I'm sorry, I don't understand that query. You can ask about:";
                response += "\n- View my shifts";
                response += "\n- Request time off";
                response += "\n- Trade shifts";
                
                if (message.toLowerCase().includes('shift')) {
                    response = "You have the following shifts scheduled:\n- Monday 9am-5pm\n- Tuesday 9am-5pm\n- Wednesday 9am-5pm";
                } else if (message.toLowerCase().includes('time off') || message.toLowerCase().includes('leave')) {
                    response = "You currently have 15 days of vacation time available. Would you like to request time off?";
                } else if (message.toLowerCase().includes('trade')) {
                    response = "You can trade your shifts with the following colleagues:\n- John Doe\n- Jane Smith\n- Alex Johnson";
                } else if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
                    response = "Hello! How can I assist you with your shifts today?";
                }
                
                addMessage('assistant', response);
            }, 1000);
        }
    }
    
    function addMessage(role, content) {
        const messageElement = document.createElement('div');
        messageElement.style.marginBottom = '10px';
        messageElement.style.padding = '8px';
        messageElement.style.borderRadius = '4px';
        
        if (role === 'user') {
            messageElement.style.backgroundColor = '#e6f7ff';
            messageElement.style.textAlign = 'right';
            messageElement.style.marginLeft = '20%';
        } else {
            messageElement.style.backgroundColor = '#f0f0f0';
            messageElement.style.marginRight = '20%';
        }
        
        messageElement.textContent = content;
        chatMessages.appendChild(messageElement);
        
        // Auto scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}); 