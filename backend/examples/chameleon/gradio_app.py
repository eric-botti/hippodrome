import gradio as gr
import random
import time


def ui_message(message):
    message_string = f"{message['sender']}\n{message['content']}"

    return [None, message_string]


def user(user_message, history):
    return "", history + [[user_message, None]]


def stream_messages():
    messages = [
        {"sender": "John", "content": "Hello! How can I help you today?"},
        {"sender": "Jane", "content": "I'm looking for a restaurant in the center."},
        {"sender": "Abby", "content": "I'm very shy."},
    ]

    for _ in range(5):
        time.sleep(0.5)
        yield random.choice(messages)



# game endpoint for API
def game():
    for bot_message in stream_messages():
        yield bot_message


# UI for Gradio
def game_ui(history):
    for bot_message in stream_messages():
        history.append(ui_message(bot_message))

        yield history


with gr.Blocks() as demo:
    chatroom = gr.Chatbot(
        value=[(None, "Hello! How can I help you today?")],
        height="70vh",
        bubble_full_width=False
    )

    api_response = gr.JSON()

    msg = gr.Textbox()
    clear = gr.Button("Clear")


    msg.submit(user, [msg, chatroom], [msg, chatroom], queue=False).then(
        game_ui, chatroom, chatroom
    )

    msg.submit(game, [], api_response, queue=False)

    clear.click(lambda: None, None, chatroom, queue=False)


demo.queue()
if __name__ == "__main__":
    demo.launch()