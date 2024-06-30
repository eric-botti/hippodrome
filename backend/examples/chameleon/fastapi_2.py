import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

app = FastAPI()

# GameSimulator class
class GameSimulator:
    def __init__(self, message_queue):
        self.message_queue = message_queue

    async def run(self):
        for i in range(5):
            print(f"Sending message {i + 1}/5")
            message = f"Message {i + 1} from GameSimulator"
            await self.message_queue.put(message)
            await asyncio.sleep(2 + i)  # Vary sleep time for demonstration


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    # Create asyncio Queue for messages
    print("Creating message queue")
    message_queue = asyncio.Queue()

    # Create an instance of GameSimulator
    print("Creating GameSimulator")
    game_simulator = GameSimulator(message_queue)

    # Start the game simulator loop
    print("Starting game simulator loop")
    asyncio.create_task(game_simulator.run())

    while True:
        # Check if there are new messages in the queue
        if not message_queue.empty():

            message = await message_queue.get()
            await websocket.send_text(message)


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
