# main.py

import asyncio
import random
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# Create asyncio Queue for messages
message_queue = asyncio.Queue()


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await asyncio.sleep(5)
        if random.random() < 0.3:
            await add_message("Hello!")

        # Check if there are new messages in the queue
        if not message_queue.empty():
            message = await message_queue.get()
            await websocket.send_text(message)


# Function to add messages to the queue
async def add_message(message):
    await message_queue.put(message)


# Example HTTP endpoint to add messages
@app.post("/add_message/{message}")
async def add_message_endpoint(message: str):
    await add_message(message)
    return {"status": "Message added to queue"}


# Example HTML endpoint to view the WebSocket client
@app.get("/")
async def get():
    return HTMLResponse(
        """
    <html>
        <head>
            <title>WebSocket Test</title>
        </head>
        <body>
            <h1>WebSocket Test</h1>
            <script>
                var ws = new WebSocket("ws://127.0.0.1:8000/ws");
                ws.onmessage = function(event) {
                    var messages = document.getElementById("messages");
                    var messageElement = document.createElement("p");
                    messageElement.innerText = event.data;
                    messages.appendChild(messageElement);
                };
            </script>
            <div id="messages">
                <!-- WebSocket messages will be displayed here -->
            </div>
        </body>
    </html>
    """
    )


# Run the FastAPI application
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
