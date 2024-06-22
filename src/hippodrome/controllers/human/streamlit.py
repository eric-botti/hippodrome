from hippodrome.message import Message
from hippodrome.controllers.human.base import BaseHumanController

import streamlit as st
from streamlit import session_state


def display_message(message: Message):
    if message.type == "verbose":
        st.markdown(f":green[{message.content}]")
    elif message.type == "debug":
        st.markdown(f":orange[DEBUG: {message.content}]")
    elif message.type == "system":
        # Don't display system message as it is displayed in the "How to Play" expander
        pass
    else:
        st.markdown(f"{message.content}")


if "messages" not in session_state:
    session_state.messages = []
    session_state.user_input = None


class StreamlitHumanController(BaseHumanController):
    def add_message(self, message: Message):
        super().add_message(message)
        session_state.messages.append(message)
        display_message(message)

    def _generate(self) -> str:
        response = session_state.user_input
        session_state.user_input = None
        return response