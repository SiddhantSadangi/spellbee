import json
import random
import os

from gtts import gTTS
from PyDictionary import PyDictionary

import streamlit as st
import streamlit.components.v1 as components

dictionary = PyDictionary()
VERSION = "0.2.1"

st.set_page_config(
    page_title="Spellbee",
    page_icon="icon.ico",
    menu_items={
        "About": f"Spellbee 🐝 v{VERSION}  "
        f"\nApp contact: [Siddhant Sadangi](mailto:siddhant.sadangi@gmail.com)",
        "Report a Bug": "https://github.com/SiddhantSadangi/SpellBee/issues/new",
        "Get help": None,
    },
)

# ---------- SIDEBAR ----------
with open("Streamlit/sidebar.html", "r", encoding="UTF-8") as sidebar_file:
    sidebar_html = sidebar_file.read().replace("{VERSION}", VERSION)

with st.sidebar:
    with st.expander("Instructions"):
        st.info(
            '1. Click on "Get word" to load a new word\n'
            '2. Once word is loaded, click on the ▶️ button next to "Get word" to hear the word in normal speed\n'
            '3. Click on the ▶️ button next to "Hear slowly" to hear the word in slow speed\n'
            '4. Type the spelling in the text box and press "Enter" to evaluate\n'
            "5. If the answer is correct, repeat from step 1. Else restart."
        )
        st.warning(
            "Once you have started entering an answer, do not click anywhere else on the screen before completing."
        )
    st.components.v1.html(sidebar_html, height=600)

# ---------- HEADER ----------
st.title("Welcome to Spellbee 🐝!")


# --- SELECT AND PLAY WORD ----
def _play(word: str) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced.
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """

    fast = gTTS(text=word, lang_check=False)
    if os.path.exists("Streamlit/fast.mp3"):
        os.remove("Streamlit/fast.mp3")
    fast.save("Streamlit/fast.mp3")

    slow = gTTS(text=word, slow=True, lang_check=False)
    if os.path.exists("Streamlit/slow.mp3"):
        os.remove("Streamlit/slow.mp3")
    slow.save("Streamlit/slow.mp3")


# --------- RESTART ----------
def _set_session_states():
    st.session_state["used_words"] = []
    st.session_state["correct_words"] = []
    st.session_state["score"] = 0
    st.session_state["disabled"] = dict(
        hear=False,
        get_length=True,
        define=True,
    )
    st.session_state["persist_audio"] = st.session_state[
        "persist_definition"
    ] = st.session_state["persist_length"] = False


# --------- SCORE ---------
def _evaluate() -> None:
    if st.session_state.answer.lower().strip() == st.session_state["used_words"][-1]:
        st.success("Correct!")
        st.session_state.disabled["hear"] = False
        st.session_state["correct_words"].append(st.session_state["used_words"][-1])
        st.session_state["score"] += 1

    else:
        st.error(
            f"Wrong answer. Correct spelling is \"{st.session_state['used_words'][-1]}\""
        )
        st.subheader(f"Final score: {st.session_state['score']}")

        st.session_state.disabled["hear"] = True

        c1, c2, c3, c4 = st.columns([4, 1, 1, 1])

        c1.button(
            "Restart",
            use_container_width=True,
            type="primary",
            on_click=_set_session_states,
        )

        with c2:
            components.html(
                """
                    <div id="fb-root"></div>
                    <script async defer crossorigin="anonymous" src="https://connect.facebook.net/en_GB/sdk.js#xfbml=1&version=v16.0" nonce="0kKz6j3l"></script>
                    <div class="fb-share-button" 
                    data-href="https://spellbee.streamlit.app/" 
                    data-layout="button" 
                    data-size="large">
                    <a target="_blank" 
                    href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fspellbee.streamlit.app%2F&amp;src=sdkpreparse" 
                    class="fb-xfbml-parse-ignore">Share</a>
                    </div>
                """
            )

        with c3:
            components.html(
                f"""
                    <a href="https://twitter.com/share" class="twitter-share-button" 
                    data-text="Can you beat my score of {st.session_state['score']}? Post your score in the comments." 
                    data-url="https://spellbee.streamlit.app/"
                    data-show-count="true">
                    data-size="Large" 
                    data-hashtags="streamlit,python,spellbee"
                    data-related="streamlit"
                    Tweet
                    </a>
                    <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>
                """
            )

        with c4:
            components.html(
                """
                    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fspellbee.streamlit.app%2F"
                    target="_blank">
                    <img src="https://www.jobget.com/img/Linkedin-Share-Button.png" alt="Share on LinkedIn" height="25"
                        width="80">
                    </a>
                """
            )

    st.session_state.disabled["get_length"] = st.session_state.disabled["define"] = True
    st.session_state.persist_audio = (
        st.session_state.persist_definition
    ) = st.session_state.persist_length = False
    st.write(
        f"__Words correctly spelled__: {', '.join(st.session_state['correct_words'])}"
    )


# ---------- INITIALIZING ----------
if "words" not in st.session_state:
    with open("Streamlit/words.txt", "r") as f:
        st.session_state["words"] = json.load(f)

    _set_session_states()


def _disable_widget():
    st.session_state.disabled = dict(
        hear=True,
        get_length=False,
        define=False,
    )
    st.session_state.persist_audio = True


def _persist_length():
    st.session_state["persist_length"] = st.session_state.disabled["get_length"] = True


def _persist_definition():
    st.session_state["persist_definition"] = st.session_state.disabled["define"] = True


def _get_word():
    word = random.choice(st.session_state["words"])
    if meaning_dict := dictionary.meaning(word, disable_errors=True):
        st.session_state["used_words"].append(word)
        st.session_state["words"].remove(word)
        st.session_state.meaning = meaning_dict
        _play(word)
    else:
        _get_word()


st.subheader(f"Score: {st.session_state['score']}")

r1c1, r1c2 = st.columns([1, 2])

r1c1.button(
    "Get word",
    on_click=_disable_widget,
    key="hear",
    type="primary",
    disabled=st.session_state.disabled["hear"],
    use_container_width=True,
)

r2c1, r2c2 = st.columns([1, 2])

r2c1.button(
    "Hear slowly",
    key="repeat",
    disabled=True,
    use_container_width=True,
)

r3c1, r3c2 = st.columns([1, 2])

r3c1.button(
    "Get word length",
    on_click=_persist_length,
    key="get_length",
    disabled=st.session_state.disabled["get_length"],
    use_container_width=True,
)

r4c1, r4c2 = st.columns([1, 2])

r4c1.button(
    "Get definition",
    on_click=_persist_definition,
    key="define",
    disabled=st.session_state.disabled["define"],
    use_container_width=True,
)

if any(
    [
        st.session_state.persist_audio,
        st.session_state.persist_length,
        st.session_state.persist_definition,
        st.session_state.get_length,
        st.session_state.hear,
    ]
):
    if st.session_state.hear:
        _get_word()

    word = st.session_state["used_words"][-1]

    if st.session_state.persist_audio:
        r1c2.audio("Streamlit/fast.mp3", format="audio/mpeg")
        r2c2.audio("Streamlit/slow.mp3", format="audio/mpeg")

    if st.session_state.persist_length:
        r3c2.markdown(
            f'<span style="font-weight:700;font-size:20px">{len(word)}</span>',
            unsafe_allow_html=True,
        )

    if st.session_state.persist_definition:
        r4c2.markdown(
            "<br>".join(
                f"{item}: {meaning}"
                for item, meaning in st.session_state.meaning.items()
            ),
            unsafe_allow_html=True,
        )

    st.text_input(
        "Type spelling and press enter to evaluate",
        key="answer",
        on_change=_evaluate,
    )

    # Nothing after this will be executed
