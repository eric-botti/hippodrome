import asyncio
import json
import logging
import random

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Setup the Game
from game_chameleon import ChameleonGame
from hippodrome.controllers.human.base import BaseHumanController


class FastAPIHumanController(BaseHumanController):
    async def _generate(self) -> str:
        return "Hello!"



# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()


@app.get("/")
async def get():
    """A simple UI for testing the chatbot."""

    with open("index.html") as f:
        html = f.read()

    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    game = ChameleonGame().from_human_name("John", "fastapi")

    while True:
        player_message = await websocket.receive_json()
        logger.info(f"Received data: {player_message}")

        user_input = player_message["content"]

        for _ in range(random.randint(2, 5)):
            message = random.choice(["Hello!", "How are you?", "Goodbye!"])
            sender = random.choice(["john", "jane", "bot1"])

            await asyncio.sleep(1)

            await websocket.send_json({"sender": sender, "content": message})