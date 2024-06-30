import asyncio
import json
import logging
import random

import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Setup the Game
from game_chameleon import ChameleonGame
from hippodrome.controllers.human.base import BaseHumanController


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

    game = None
    user_input = None

    class FastAPIHumanController(BaseHumanController):
        def _generate(self) -> str:
            nonlocal user_input
            response = user_input
            user_input = None
            return response

    last_round_id = 0

    while True:
        player_message = await websocket.receive_json()
        logger.info(f"Received data: {player_message}")

        user_input = player_message["message"]["content"]

        if game is None:
            game = ChameleonGame.from_human_name(user_input, FastAPIHumanController)
            user_input = None

        await game.run_game()

        for message in game.messages[last_round_id : player_message.id]:
            for recipient in message.recipients:
                if "human" in recipient:
                    await websocket.send_json(
                        {"sender": message.sender, "content": message.content}
                    )
                    break

        last_round_id = player_message.id
