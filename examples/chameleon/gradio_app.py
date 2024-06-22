import gradio as gr
import random
import time

from hippodrome.controllers.human.base import BaseHumanController


def display_message(message):
    if message.type == "verbose":
        print(f"VERBOSE: {message.content}")
    elif message.type == "debug":
        print(f"DEBUG: {message.content}")
    elif message.type != "agent":
        print(message.content)


    message_area = gr.TextArea(
        value="Please Enter your name, or leave blank to run an AI only game\n\n",
        interactive=False
    )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, message_area])

    msg.submit(respond, [msg, message_area], [msg, message_area])


class GradioController(BaseHumanController):
    def add_message(self, message):
        super().add_message(message)
        if message.type == "verbose":
            print(message.content)
        elif message.type == "debug":
            print("DEBUG: " + message.content)
        elif message.type != "agent":
            print(message.content)

    def _generate(self):
        while True:
            if self._response is not None:
                response = self._response
                self._response = None
                return response
            time.sleep(0.1)



with gr.Blocks() as demo:
    instructions = gr.Markdown(
        value="To begin, enter your name or leave blank to run an AI only game"
    )

    message_area = gr.Chatbot(
        label="Game Area",
        height="70vh"
    )
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, message_area])

    def respond(msg, chat_history):
        response = "Hello, " + msg

        chat_history.append((msg, response))

        return '', chat_history


    msg.submit(respond, [msg, message_area], [msg, message_area])

if __name__ == "__main__":
    demo.launch()