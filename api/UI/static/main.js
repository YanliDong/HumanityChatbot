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
    
    // Add conversation state tracking
    let conversationState = {
        waitingForTimeOffDates: false,
        lastMessage: '',
        inTimeOffFlow: false,
        inTradeFlow: false,
        waitingForEmployeeId: false,
        inShiftCreationFlow: false,
        isAdmin: false,
        currentWeek: 'this', // 'this' or 'next'
        selectedShiftId: null
    };
    
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
        
        // Check if user is admin
        conversationState.isAdmin = username.toLowerCase().includes('admin');
        
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
                response += "\n- View my shifts (this/next week)";
                response += "\n- Request time off";
                response += "\n- Trade shifts";
                if (conversationState.isAdmin) {
                    response += "\n- Create shift";
                }
                
                // First check if we're in a time off flow
                if (conversationState.inTimeOffFlow) {
                    if (message.toLowerCase() === 'yes') {
                        if (conversationState.waitingForTimeOffDates) {
                            response = "Please provide dates in the format YYYY-MM-DD (e.g., 2025-03-25 to 2025-03-30)";
                        } else {
                            response = "Your time off request has been submitted successfully!";
                            conversationState.inTimeOffFlow = false;
                            conversationState.waitingForTimeOffDates = false;
                        }
                    } else if (message.toLowerCase().includes('yes, it is from') ||
                             message.toLowerCase().includes('yes, i would like to request time off') ||
                             message.toLowerCase().includes('request time off from') ||
                             message.toLowerCase().includes('yes, 2025-03-25 to 2025-03-30')) {
                        // Check if the message contains dates
                        const datePattern = /(\d{4}-\d{2}-\d{2})/g;
                        const dates = message.match(datePattern);
                        
                        if (dates && dates.length >= 2) {
                            const startDate = dates[0];
                            const endDate = dates[1];
                            response = `Here are your time off request details:\nStart Date: ${startDate}\nEnd Date: ${endDate}\nDuration: 6 days\n\nWould you like to submit this request? (yes/no)`;
                            conversationState.waitingForTimeOffDates = false;
                        } else {
                            response = "Please provide dates in the format YYYY-MM-DD (e.g., 2025-03-25 to 2025-03-30)";
                            conversationState.waitingForTimeOffDates = true;
                        }
                    } else if (conversationState.waitingForTimeOffDates) {
                        // Check if the message contains dates
                        const datePattern = /(\d{4}-\d{2}-\d{2})/g;
                        const dates = message.match(datePattern);
                        
                        if (dates && dates.length >= 2) {
                            const startDate = dates[0];
                            const endDate = dates[1];
                            response = `Here are your time off request details:\nStart Date: ${startDate}\nEnd Date: ${endDate}\nDuration: 6 days\n\nWould you like to submit this request? (yes/no)`;
                            conversationState.waitingForTimeOffDates = false;
                        } else {
                            response = "Please provide dates in the format YYYY-MM-DD (e.g., 2025-03-25 to 2025-03-30)";
                        }
                    }
                }
                // Then check for time off request
                else if (message.toLowerCase().includes('time off') || 
                          message.toLowerCase().includes('leave') || 
                          message.toLowerCase().includes('vacation') ||
                          message.toLowerCase().includes('request time off')) {
                    // Check if the message contains dates
                    const datePattern = /(\d{4}-\d{2}-\d{2})/g;
                    const dates = message.match(datePattern);
                    
                    if (dates && dates.length >= 2) {
                        const startDate = dates[0];
                        const endDate = dates[1];
                        response = `Here are your time off request details:\nStart Date: ${startDate}\nEnd Date: ${endDate}\nDuration: 6 days\n\nWould you like to submit this request? (yes/no)`;
                        conversationState.inTimeOffFlow = false;
                        conversationState.waitingForTimeOffDates = false;
                    } else {
                        response = "You currently have 15 days of vacation time available. Would you like to request time off? Please provide dates in the format YYYY-MM-DD (e.g., 2025-03-25 to 2025-03-30)";
                        conversationState.inTimeOffFlow = true;
                    }
                }
                // Then check if we're in a trade flow
                else if (conversationState.inTradeFlow) {
                    if (message.toLowerCase() === 'yes') {
                        response = "Your shift trade request has been submitted successfully!";
                        conversationState.inTradeFlow = false;
                        conversationState.waitingForEmployeeId = false;
                    } else if (conversationState.waitingForEmployeeId) {
                        // Handle employee ID selection
                        const employeeId = message.match(/\d+/);
                        if (employeeId) {
                            const selectedEmployee = {
                                '101': 'John Doe',
                                '102': 'Jane Smith',
                                '103': 'Alex Johnson'
                            }[employeeId[0]];
                            
                            const selectedShift = {
                                '1': 'Monday 9am-5pm',
                                '2': 'Tuesday 9am-5pm',
                                '3': 'Wednesday 9am-5pm'
                            }[conversationState.selectedShiftId];
                            
                            if (selectedEmployee && selectedShift) {
                                response = `Here are your shift trade request details:\nShift: ${selectedShift}\nTrading with: ${selectedEmployee}\n\nWould you like to submit this trade request? (yes/no)`;
                                conversationState.waitingForEmployeeId = false;
                            } else {
                                response = "Please enter a valid employee ID number.";
                            }
                        } else {
                            response = "Please enter a valid employee ID number.";
                        }
                    } else {
                        // Handle shift ID selection
                        const shiftId = message.match(/\d+/);
                        if (shiftId) {
                            const selectedShift = {
                                '1': 'Monday 9am-5pm',
                                '2': 'Tuesday 9am-5pm',
                                '3': 'Wednesday 9am-5pm'
                            }[shiftId[0]];
                            
                            if (selectedShift) {
                                response = "Here are the eligible employees you can trade with:\n- John Doe (ID: 101)\n- Jane Smith (ID: 102)\n- Alex Johnson (ID: 103)\n\nPlease enter the ID of the employee you want to trade with.";
                                conversationState.waitingForEmployeeId = true;
                                conversationState.selectedShiftId = shiftId[0];
                            } else {
                                response = "Please enter a valid shift ID number.";
                            }
                        } else {
                            response = "Please enter a valid shift ID number.";
                        }
                    }
                }
                // Then check for shift-related queries
                else if (message.toLowerCase().includes('shift')) {
                    if (message.toLowerCase().includes('trade')) {
                        response = "Here are your available shifts for trading:\n- Monday 9am-5pm (ID: 1)\n- Tuesday 9am-5pm (ID: 2)\n- Wednesday 9am-5pm (ID: 3)\n\nPlease enter the ID of the shift you want to trade.";
                        conversationState.inTradeFlow = true;
                    } else if (message.toLowerCase().includes('create') && conversationState.isAdmin) {
                        response = "Please provide shift details in the format:\nDate: YYYY-MM-DD\nStart Time: HH:MM\nEnd Time: HH:MM\nPosition: [position name]";
                        conversationState.inShiftCreationFlow = true;
                    } else if (message.toLowerCase().includes('view')) {
                        if (message.toLowerCase().includes('next')) {
                            conversationState.currentWeek = 'next';
                        } else {
                            conversationState.currentWeek = 'this';
                        }
                        response = `Here are your shifts for ${conversationState.currentWeek} week:\nMonday: 9am-5pm\nTuesday: 9am-5pm\nWednesday: 9am-5pm\nThursday: 9am-5pm\nFriday: 9am-5pm`;
                    } else {
                        response = "You have the following shifts scheduled:\n- Monday 9am-5pm\n- Tuesday 9am-5pm\n- Wednesday 9am-5pm";
                    }
                }
                // Then check for trade requests
                else if (message.toLowerCase().includes('trade')) {
                    response = "Here are your available shifts for trading:\n- Monday 9am-5pm (ID: 1)\n- Tuesday 9am-5pm (ID: 2)\n- Wednesday 9am-5pm (ID: 3)\n\nPlease enter the ID of the shift you want to trade.";
                    conversationState.inTradeFlow = true;
                }
                // Finally check for greetings
                else if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
                    response = "Hello! How can I assist you with your shifts today?";
                }
                
                conversationState.lastMessage = message;
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