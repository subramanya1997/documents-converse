function createMessageElement(message, isUser) {
    var messageElement = document.createElement("div");
    messageElement.className = "message " + (isUser ? "user-message" : "bot-message");
    messageElement.textContent = message;
    return messageElement;
  }

function submitQuestion() {
    var question = document.getElementById("question").value.trim();
    var language = document.getElementById("language").value;
    var chatElement = document.getElementById("chat");

    if (question.length === 0) {
        // If the question is empty, do nothing
        return;
    }

    // Hide the drop-zone container
    document.getElementById('drop-zone').style.display = 'none';
    
    // Create and display the user message
    var userMessage = createMessageElement(question, true);
    chatElement.appendChild(userMessage);

    // Construct the request URL
    var url = "/generateAnswer";

    // Create form data with the query and language
    var formData = new FormData();
    formData.append("query", question);
    formData.append("language", language);

    // Send a POST request to the backend
    fetch(url, {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Request failed');
        }
    }).then(data => {
        // Create and display the bot message
        const responseText = data.answer;
        var botMessage = createMessageElement(responseText, false);
        chatElement.appendChild(botMessage);
    }).catch(error => {
        // Display the error message if there was an error with the request
        var errorMessage = error.message || "An error occurred. Please try again later.";
        var errorBotMessage = createMessageElement(errorMessage, false);
        chatElement.appendChild(errorBotMessage);
    }).finally(() => {
        // Scroll to the bottom of the chat
        chatElement.scrollTop = chatElement.scrollHeight;
        // Clear the input field
        document.getElementById("question").value = "";
    });
}

// Add an event listener for the "keydown" event on the input element
document.getElementById("question").addEventListener("keydown", function(event) {
    // Check if the pressed key is the Enter key (key code 13)
    if (event.key === "Enter") {
        // If the Enter key is pressed, call the submitQuestion() function
        submitQuestion();
    }
});

const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');

dropZone.addEventListener('click', () => {
    fileInput.click();
});

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drop-zone-hover');
});

dropZone.addEventListener('dragleave', () => {
    dropZone.classList.remove('drop-zone-hover');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drop-zone-hover');
    const files = e.dataTransfer.files;
    handleFiles(files);
});

fileInput.addEventListener('change', () => {
    const files = fileInput.files;
    handleFiles(files);
});

function handleFiles(files) {
    // Process the uploaded files here
    console.log(files);
}