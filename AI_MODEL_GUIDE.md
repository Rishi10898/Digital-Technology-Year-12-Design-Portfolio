# 🤖 AI Model Configuration Guide

## 🔄 **How to Change the AI Model**

### **Step 1: Install a Different Model**
```bash
# List available models
ollama list

# Install a different model (examples)
ollama pull llama3.1:70b        # Larger, more capable model
ollama pull llama3.1:3b         # Smaller, faster model
ollama pull mistral:7b          # Alternative model
ollama pull codellama:7b        # Code-focused model
ollama pull neural-chat:7b      # Chat-optimized model
```

### **Step 2: Update the Flask Server**
Edit `llama_server.py` and change this line:
```python
MODEL_NAME = "llama3.1:8b"  # Change this to your desired model
```

**Examples:**
```python
MODEL_NAME = "llama3.1:70b"     # Larger model (better responses, slower)
MODEL_NAME = "llama3.1:3b"      # Smaller model (faster responses)
MODEL_NAME = "mistral:7b"       # Alternative model
MODEL_NAME = "neural-chat:7b"   # Chat-optimized model
```

### **Step 3: Adjust Parameters for Different Models**
Different models work better with different parameters:

```python
# For larger models (70b, 34b) - Better quality, slower
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 500
REQUEST_TIMEOUT = 120

# For smaller models (3b, 7b) - Faster, less detailed
DEFAULT_TEMPERATURE = 0.5
DEFAULT_TOP_P = 0.8
DEFAULT_MAX_TOKENS = 300
REQUEST_TIMEOUT = 45

# For chat-optimized models
DEFAULT_TEMPERATURE = 0.6
DEFAULT_TOP_P = 0.85
DEFAULT_MAX_TOKENS = 400
REQUEST_TIMEOUT = 60
```

### **Step 4: Restart the Server**
```bash
# Stop the current server (Ctrl+C)
# Then restart
python llama_server.py
```

---

## 🌐 **Connecting Other HTML Pages to AI**

### **Option 1: Add Chat Widget to Any Page**

Add this code to any HTML page to include the AI chat:

```html
<!-- Add this in the <head> section -->
<style>
/* Chat Widget Styles */
.chat-widget {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 350px;
    height: 500px;
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(15px);
    border-radius: 15px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    display: none;
    flex-direction: column;
    z-index: 1000;
}

.chat-widget.active {
    display: flex;
}

.chat-header {
    background: #4caf50;
    color: white;
    padding: 15px;
    border-radius: 15px 15px 0 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.chat-messages {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    max-height: 350px;
}

.chat-input-container {
    padding: 15px;
    border-top: 1px solid #eee;
}

.chat-input {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 20px;
    margin-bottom: 10px;
}

.chat-toggle {
    position: fixed;
    bottom: 20px;
    right: 20px;
    width: 60px;
    height: 60px;
    background: #4caf50;
    color: white;
    border: none;
    border-radius: 50%;
    font-size: 24px;
    cursor: pointer;
    z-index: 1001;
    box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
}

.loading-dots::after {
    content: '';
    animation: dots 1.5s steps(5, end) infinite;
}

@keyframes dots {
    0%, 20% { content: ''; }
    40% { content: '.'; }
    60% { content: '..'; }
    80%, 100% { content: '...'; }
}
</style>

<!-- Add this before closing </body> tag -->
<button class="chat-toggle" onclick="toggleChat()">🤖</button>

<div class="chat-widget" id="chatWidget">
    <div class="chat-header">
        <span>AINZUNI AI Assistant</span>
        <button onclick="toggleChat()" style="background: none; border: none; color: white; font-size: 18px;">✕</button>
    </div>
    <div class="chat-messages" id="chatMessages">
        <p style="opacity: 0.7; font-style: italic;">Hello! I'm AINZUNI, your AI assistant. How can I help you today?</p>
    </div>
    <div class="chat-input-container">
        <input type="text" class="chat-input" id="chatInput" placeholder="Ask me anything..." onkeypress="if(event.key==='Enter') sendChatMessage()">
        <button onclick="sendChatMessage()" style="background: #4caf50; color: white; border: none; padding: 8px 15px; border-radius: 15px; cursor: pointer;">Send</button>
    </div>
</div>

<script>
function toggleChat() {
    const widget = document.getElementById('chatWidget');
    widget.classList.toggle('active');
}

async function sendChatMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    const chatMessages = document.getElementById('chatMessages');

    if (!message) return;

    // User message
    const userDiv = document.createElement('div');
    userDiv.style.cssText = 'text-align: right; margin: 10px 0; padding: 8px 12px; background: #4caf50; color: white; border-radius: 15px 15px 5px 15px; display: inline-block; max-width: 80%; float: right; clear: both;';
    userDiv.textContent = message;
    chatMessages.appendChild(userDiv);
    input.value = '';

    // Loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.style.cssText = 'text-align: left; margin: 10px 0; padding: 8px 12px; background: rgba(119, 187, 198, 0.3); border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 80%; float: left; clear: both;';
    loadingDiv.innerHTML = '<span class="loading-dots">AINZUNI is thinking</span>';
    chatMessages.appendChild(loadingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const response = await fetch("http://localhost:5000/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        loadingDiv.remove();

        if (response.ok) {
            const data = await response.json();
            if (data.error) {
                const errorDiv = document.createElement('div');
                errorDiv.style.cssText = 'text-align: left; margin: 10px 0; padding: 8px 12px; background: rgba(244, 67, 54, 0.2); border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 80%; float: left; clear: both; color: #d32f2f;';
                errorDiv.innerHTML = `<strong>⚠️ Error:</strong> ${data.message || data.error}`;
                chatMessages.appendChild(errorDiv);
            } else {
                const botDiv = document.createElement('div');
                botDiv.style.cssText = 'text-align: left; margin: 10px 0; padding: 8px 12px; background: rgba(119, 187, 198, 0.3); border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 80%; float: left; clear: both;';
                botDiv.textContent = data.response;
                chatMessages.appendChild(botDiv);
            }
        } else {
            throw new Error(`Server error: ${response.status}`);
        }
    } catch (err) {
        loadingDiv.remove();
        const errorDiv = document.createElement('div');
        errorDiv.style.cssText = 'text-align: left; margin: 10px 0; padding: 8px 12px; background: rgba(244, 67, 54, 0.2); border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 80%; float: left; clear: both; color: #d32f2f;';
        errorDiv.innerHTML = `<strong>⚠️ Connection Error:</strong> ${err.message}`;
        chatMessages.appendChild(errorDiv);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;
}
</script>
```

### **Option 2: Full Chat Page Integration**

Replace the entire content of any HTML page with the AI chat interface by copying the content from `AINZUNI.html`.

---

## ⚡ **Speed Optimization Tips**

### **1. Model Selection for Speed**
```bash
# Fastest models (3-5 seconds response time)
ollama pull llama3.1:3b
ollama pull phi:2.7b
ollama pull tinyllama:1.1b

# Balanced models (10-15 seconds response time)
ollama pull llama3.1:8b
ollama pull mistral:7b
ollama pull neural-chat:7b

# Quality models (20-30 seconds response time)
ollama pull llama3.1:70b
ollama pull llama3.1:34b
```

### **2. Parameter Optimization**
```python
# For maximum speed
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.7
DEFAULT_MAX_TOKENS = 150
REQUEST_TIMEOUT = 30

# For balanced speed/quality
DEFAULT_TEMPERATURE = 0.5
DEFAULT_TOP_P = 0.8
DEFAULT_MAX_TOKENS = 300
REQUEST_TIMEOUT = 45

# For maximum quality
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_MAX_TOKENS = 500
REQUEST_TIMEOUT = 120
```

### **3. System Optimization**
```bash
# Increase system memory allocation for Ollama
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*

# For Windows, add to environment variables
set OLLAMA_HOST=0.0.0.0:11434
set OLLAMA_ORIGINS=*
```

---

## 🔧 **Advanced Configuration**

### **Custom Context for Different Pages**
You can customize the AI's knowledge base for different pages:

```python
# In llama_server.py, modify the context based on the page
PAGE_CONTEXTS = {
    "universities": "You are AINZUNI, specializing in NZ universities...",
    "courses": "You are AINZUNI, specializing in academic programs...",
    "admissions": "You are AINZUNI, specializing in admission processes...",
    "general": "You are AINZUNI, a general AI assistant..."
}

# Then use different contexts for different endpoints
@app.route('/api/chat/universities', methods=['POST'])
def chat_universities():
    # Use universities context
    pass

@app.route('/api/chat/courses', methods=['POST'])
def chat_courses():
    # Use courses context
    pass
```

### **Multiple Model Support**
You can support multiple models simultaneously:

```python
# In llama_server.py
MODELS = {
    "fast": "llama3.1:3b",
    "balanced": "llama3.1:8b",
    "quality": "llama3.1:70b"
}

@app.route('/api/chat/<model_type>', methods=['POST'])
def chat_with_model(model_type):
    if model_type in MODELS:
        model_name = MODELS[model_type]
        # Use the specified model
        pass
```

---

## 📊 **Performance Monitoring**

### **Response Time Tracking**
Add this to monitor performance:

```python
import time

def generate_response(prompt, temperature=0.5, top_p=0.8, max_tokens=300):
    start_time = time.time()
    try:
        # ... existing code ...
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload, timeout=REQUEST_TIMEOUT)
        end_time = time.time()
        logger.info(f"Response time: {end_time - start_time:.2f} seconds")
        return result.get("response", "")
    except Exception as e:
        end_time = time.time()
        logger.error(f"Error after {end_time - start_time:.2f} seconds: {e}")
        raise e
```

This guide gives you complete control over the AI model and allows you to integrate AI chat into any page of your website!
