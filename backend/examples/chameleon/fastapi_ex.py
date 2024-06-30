import asyncio
import json
import logging
import random

import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse

# Setup the Game
from backend.examples.chameleon.chameleon_game import ChameleonGame
from hippodrome.controllers.human.base import BaseHumanController
from hippodrome import Message

from chameleon_player import ChameleonPlayer

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


class FastAPIHumanController(BaseHumanController):
    websocket = None

    async def add_message(self, message: Message):
        await self.websocket.send_json(
            {"sender": message.sender, "content": message.content}
        )

    async def _generate(self) -> str:
        player_message = await self.websocket.receive_json()
        logger.info(f"Received data: {player_message}")

        user_input = player_message["message"]["content"]
        return user_input


def setup_game(player_name: str):
    """Set up the game."""

    human_player = ChameleonPlayer(name=player_name, controller=FastAPIHumanController)

    game = ChameleonGame.from_human_name(player_name, FastAPIHumanController)

    return game


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

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
