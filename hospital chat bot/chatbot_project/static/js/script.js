// Function to handle sending the message
function sendMessage() {
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const userMessage = userInput.value.trim();

    // If input is empty, do nothing
    if (userMessage === '') return;

    // Display user message in the chat box
    displayMessage(userMessage, 'user');

    // Send the message to the Flask server
    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ symptoms: [userMessage] })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.message) {
            displayMessage(data.message, 'bot');
        } else if (data.possible_illnesses && data.possible_illnesses.length > 0) {
            let responseMessage = 'Possible illnesses:<br>';
            data.possible_illnesses.forEach(illness => {
                responseMessage += `<strong>${illness.illness}</strong> - Confidence: ${illness.confidence}<br>`;
            });
            displayMessage(responseMessage, 'bot');
        } else {
            displayMessage('No matching illnesses found. Please provide more symptoms.', 'bot');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        displayMessage('Sorry, there was an error processing your request.', 'bot');
    });
    

    // Clear the input field after sending the message
    userInput.value = '';
}

// Function to display messages in the chat box
function displayMessage(message, sender) {
    const chatBox = document.getElementById('chat-box');
    const messageElement = document.createElement('div');
    messageElement.className = sender === 'user' ? 'user-message' : 'bot-message';
    messageElement.innerHTML = message;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the bottom
}

// Handle pressing 'Enter' key to send the message
function handleKeyPress(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        sendMessage();
    }
}
