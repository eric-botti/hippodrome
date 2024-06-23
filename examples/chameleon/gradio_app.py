import gradio as gr
import random
import time

from hippodrome.controllers.human.base import BaseHumanController
from game_chameleon import ChameleonGame

game_messages = []
current_user_message = None


class GradioController(BaseHumanController):
    def add_message(self, message):
        super().add_message(message)
        game_messages.append(message.content)

    def _generate(self):
        global current_user_message
        response = current_user_message
        current_user_message = None
        return response


game = None

with gr.Blocks() as demo:
    instructions = gr.Markdown(
        value="To begin, enter your name or leave blank to run an AI only game"
    )

    message_area = gr.Chatbot(label="Game Area", height="70vh")
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, message_area])

    def respond(msg, chat_history):
        global game
        global game_messages

        if game is None:
            game = ChameleonGame.from_human_name(msg, GradioController)
            game_messages.append(f"Welcome {msg}!")

            game.run_game()
        else:
            global current_user_message
            current_user_message = msg

            game.run_game()

        game_messages_str = "\n\n".join(game_messages)
        # reset game messages
        game_messages = []

        chat_history.append((msg, game_messages_str))

        return "", chat_history

    msg.submit(respond, [msg, message_area], [msg, message_area])

if __name__ == "__main__":
    demo.launch()
