import json
import random
import os

from gtts import gTTS
from playsound import playsound

import streamlit as st

VERSION = "0.1.0"

st.set_page_config(
    page_title="Spellbee",
    page_icon="../icon.ico",
    menu_items={
        "About": f"Spellbee 🐝 v{VERSION}  "
        f"\nApp contact: [Siddhant Sadangi](mailto:siddhant.sadangi@gmail.com)",
        "Report a Bug": "https://github.com/SiddhantSadangi/SpellBee/issues/new",
        "Get help": None,
    },
)

# ---------- SIDEBAR ----------
with open("sidebar.html", "r", encoding="UTF-8") as sidebar_file:
    sidebar_html = sidebar_file.read().replace("{VERSION}", VERSION)

with st.sidebar:
    st.components.v1.html(sidebar_html, height=400)

# ---------- HEADER ----------
st.title("Welcome to Spellbee 🐝!")

# --- SELECT AND PLAY WORD ----
def play(word: str, slow: bool = False) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """

    t1 = gTTS(word, slow=True)
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    t1.save("audio.mp3")
    return playsound("audio.mp3")


# --------- SCORE ---------
def iscorrect(word: str, answer: str) -> bool:

    if answer == word:
        st.success("Correct!")
        return True
    else:
        st.error(f"Wrong answer. Correct spelling is {word}")
        return False


# ---------- INITIALIZING ----------
if "words" not in st.session_state:
    with open("words.txt", "r") as f:
        st.session_state["words"] = json.load(f)

    st.session_state["used_words"] = []

st.session_state["used_words"]

# Function to update the value in session state
def started(button):
    st.session_state.clicked[button] = True
    st.session_state.disabled = True


if "start" not in st.session_state:
    st.session_state.disabled = False

st.button(
    "Start",
    on_click=started,
    args=[1],
    key="start",
    disabled=st.session_state.disabled,
)

lcol, _ = st.columns(2)
st.subheader(f"Score: {len(st.session_state['used_words'])}")


# Initialize the key in session state
if "clicked" not in st.session_state:
    st.session_state.clicked = {1: False, 2: False}


if st.session_state.clicked[1]:
    st.session_state["used_words"].append(random.choice(st.session_state["words"]))
    st.session_state["words"].remove(st.session_state["used_words"][-1])

    play(st.session_state["used_words"][-1])

    st.text_input(
        "Type spelling and press enter to evaluate",
        key=st.session_state["used_words"][-1],
    ).lower().strip()

    print(st.session_state[st.session_state["used_words"][-1]])
    if st.session_state[st.session_state["used_words"][-1]]:
        if not iscorrect(
            st.session_state["used_words"][-1], st.session_state[st.session_state["used_words"][-1]]
        ):
            print("incorrect")
            st.session_state["used_words"] = []
        else:
            print("correct")
