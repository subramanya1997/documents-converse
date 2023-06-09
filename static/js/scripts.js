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
    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    // Send a POST request to the backend
    fetch('/uploadzip', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            showNotification('File upload failed', true);
            throw new Error('Request failed');
        }
    }).then(data => {
        showNotification('File uploaded successfully');
        const filename = data.filename;
        validateUploadedZip(filename);
    }).catch(error => {
        showNotification('File upload failed', true);
        console.log("Error during upload: " + error);
    })
}

function validateUploadedZip(filename) {
    showNotification('Validating file...', false, true);
    fetch(`/validateuploadedzip?filename=${filename}`, {
        method: 'GET',
    }).then(response => {
        if (response.ok) {
            return response.json();
        }
        else {
            showNotification('File validation failed', true);
            throw new Error('Request failed');
        }
    }).then(data => {
        showNotification('File validated successfully', false);
        processUploadedZip(filename=filename);
    }
    ).catch(error => {
        showNotification('File validation failed', true);
        deleteUploadedZip(filename=filename);
        console.log("Error during validation: " + error);
    })
}

function deleteUploadedZip(filename) {
    const formData = new FormData();
    formData.append('filename', filename);

    fetch('/deleteuploadedzip', {
        method: 'POST',
        body: formData
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Request failed');
        }
    }).then(data => {
        console.log('File deleted successfully');
    }).catch(error => {
        console.log("Error during deletion: " + error);
    })
}

function processUploadedZip(filename) {
    showNotification('Processing files...', false, true);
    fetch(`/processuploadedzip?filename=${filename}`, {
        method: 'GET',
    }).then(response => {
        if (response.ok) {
            return response.json();
        } else {
            showNotification('File processing failed', true);
            throw new Error('Request failed');
        }
    }).then(data => {
        showNotification('File processed successfully and updated pinecone');
    }).catch(error => {
        showNotification('File processing failed', true);
        console.log("Error during processing: " + error);
    })
}

var timeouts = [];

function showNotification(message, isError = false, isNeutral = false) {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.classList.remove('error', 'success', 'neutral');

    // Clear previous timeouts
    for (var i = 0; i < timeouts.length; i++) {
        clearTimeout(timeouts[i]);
    }

    // Empty the timeouts array
    timeouts = [];

    if (isError) {
        notification.classList.add('error');
        // No timeout is set here, so the error message will stay until a new notification comes in
    } else if (isNeutral) {
        notification.classList.add('neutral');
        // No timeout is set here, so the neutral message will stay until a new notification comes in
    } else {
        notification.classList.add('success');
        // Only in case of success, a timeout is set to clear the notification after 5 seconds
        var _timout = setTimeout(clearNotification, 5000);
        timeouts.push(_timout);
    }
}

function clearNotification() {
    const notification = document.getElementById('notification');
    notification.textContent = '';
    notification.classList.remove('error', 'success', 'neutral');
}