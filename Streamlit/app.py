import json
import random
import os

from gtts import gTTS
from PyDictionary import PyDictionary

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px

from supabase import create_client, Client

dictionary = PyDictionary()
VERSION = "1.1.0"

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
    st.components.v1.html(sidebar_html, height=600)


# ---------- Init supabase connection ------------
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = init_connection()

# ---------- USER AUTHENTICATION ----------
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "username" not in st.session_state:
    st.session_state["username"] = None


with st.expander("Authentication", expanded=not st.session_state["authenticated"]):
    create_tab, login_tab, guest_tab = st.tabs(
        [
            "Create new account :baby: ",
            "Login to existing account :prince: ",
            "Play as guest :ninja: ",
        ]
    )

    ## ---------- CREATE NEW ACCOUNT ------------
    with create_tab:
        with st.form(key="create"):
            username = st.text_input(
                label="Create a unique username",
                placeholder="Username will be visible in the global leaderboard.",
                max_chars=50,
                disabled=st.session_state["authenticated"],
            )

            password = st.text_input(
                label="Create a password",
                placeholder="Password will be stored as plain text. You won't be able to recover it if you forget.",
                type="password",
                max_chars=50,
                disabled=st.session_state["authenticated"],
            )

            if st.form_submit_button(
                label="Create account",
                disabled=st.session_state["authenticated"],
            ):
                try:
                    data, _ = (
                        supabase.table("users")
                        .insert({"username": username, "password": password})
                        .execute()
                    )
                except Exception as e:
                    st.error(e.message)
                else:
                    st.success("Account created :tada:")
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username

    ## ---------- LOGIN TO EXISTING ACCOUNT ------------
    with login_tab:
        with st.form(key="login"):
            username = st.text_input(
                label="Enter your unique username",
                max_chars=50,
                disabled=st.session_state["authenticated"],
            )

            password = st.text_input(
                label="Enter your password",
                type="password",
                max_chars=50,
                disabled=st.session_state["authenticated"],
            )

            if st.form_submit_button(
                label="Login",
                disabled=st.session_state["authenticated"],
                type="primary",
            ):
                data, _ = (
                    supabase.table("users")
                    .select("username, password")
                    .eq("username", username)
                    .eq("password", password)
                    .execute()
                )

                if len(data[-1]) > 0:
                    st.success("Login succeeded :tada:")
                    st.session_state["authenticated"] = True
                    st.session_state["username"] = username
                else:
                    st.error("Wrong username/password :x: ")

    ## ---------- PLAY AS GUEST ----------
    with guest_tab:
        if st.button(
            label="Play as a guest ⚠️ Scores won't be saved",
            disabled=st.session_state["authenticated"],
        ):
            st.session_state["authenticated"] = True

if st.session_state["authenticated"]:
    # ---------- HEADER ----------
    if st.session_state["username"]:
        st.title(f"🐝 Welcome to Spellbee, {st.session_state['username']}!")
    else:
        st.title(f"Welcome to Spellbee 🐝!")

    # --- SELECT AND PLAY WORD ----
    def play(word: str) -> None:
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
    def set_session_states() -> None:
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
    def evaluate() -> None:
        if (
            st.session_state.answer.lower().strip()
            == st.session_state["used_words"][-1]
        ):
            st.success("Correct!")
            st.session_state.disabled["hear"] = False
            st.session_state["correct_words"].append(st.session_state["used_words"][-1])
            st.session_state["score"] += 1

        else:
            game_over()
        st.session_state.disabled["get_length"] = st.session_state.disabled[
            "define"
        ] = True
        st.session_state.persist_audio = (
            st.session_state.persist_definition
        ) = st.session_state.persist_length = False

    def game_over() -> None:
        st.error(
            f"Wrong answer. Correct spelling is \"{st.session_state['used_words'][-1]}\", you guessed \"{st.session_state.answer.lower().strip()}\"."
        )
        st.write(
            f"__Words correctly spelled__: {', '.join(st.session_state['correct_words'])}"
        )
        st.subheader(f"Final score: {st.session_state['score']}")

        # ---------- RECORD SCORE ----------
        if st.session_state["username"]:
            try:
                supabase.table("scores").insert(
                    {
                        "username": st.session_state["username"],
                        "score": st.session_state["score"],
                    }
                ).execute()
            except Exception as e:
                st.error(e.message)
            else:
                st.success("Score saved :writing_hand: ")

            # ---------- SHOW USER HISTORY ----------
            user_scores, count = (
                supabase.table("scores")
                .select("*", count="exact")
                .eq("username", st.session_state["username"])
                .execute()
            )

            if count:
                user_history_plot(user_scores)
        # ---------- SHOW LEADERBOARD ----------
        scores, _ = supabase.table("scores").select("username, score").execute()
        scores = pd.DataFrame(scores[-1])

        leaderboard = (
            scores.groupby("username")
            .max()
            .sort_values(by="score", ascending=False)[:10]
            .reset_index()
        )

        st.plotly_chart(
            px.bar(
                leaderboard,
                x="username",
                y="score",
                title="Global leaderboard 👑 ",
            ),
            use_container_width=True,
        )

        # ---------- RESTART ----------
        st.session_state.disabled["hear"] = True

        st.button(
            "Restart",
            use_container_width=True,
            type="primary",
            on_click=set_session_states,
        )

        c1, c2, c3, c4, _ = st.columns([3, 1, 1, 1, 2])
        c1.write("Share the word on social media")
        with c2:
            components.html(
                """
                    <a href="https://www.facebook.com/sharer/sharer.php?kid_directed_site=0&sdk=joey&u=https%3A%2F%2Fspellbee.streamlit.app%2F&display=popup&ref=plugin&src=share_button"
                        target="_blank">
                        <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/de66032a-4ff1-4505-8960-848884a3c29e"
                            alt="Share on Facebook" width="40" height="40">
                    </a>
                """
            )
        with c3:
            components.html(
                """
                    <a href="https://www.linkedin.com/sharing/share-offsite/?url=https%3A%2F%2Fspellbee.streamlit.app%2F"
                        target="_blank">
                        <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/78caca71-10a3-45ac-949b-961b3ebf2429"
                            alt="Share on LinkedIn" height="40" width="40">
                    </a>
                """
            )
        with c4:
            components.html(
                f"""
                    <a href="https://twitter.com/intent/tweet?original_referer=http%3A%2F%2Flocalhost%3A8501%2F&ref_src=twsrc%5Etfw%7Ctwcamp%5Ebuttonembed%7Ctwterm%5Eshare%7Ctwgr%5E&text=Can%20you%20beat%20my%20score%20of%20{st.session_state['score']}%3F%20Try%20this%20awesome%20Streamlit%20Spellbee%20app%20and%20let%20me%20know%20your%20score%20in%20the%20comments&url=https%3A%2F%2Fspellbee.streamlit.app%2F"
                        target="_blank">
                        <img src="https://github.com/SiddhantSadangi/SiddhantSadangi/assets/41324509/3d3f7366-2f96-4456-8476-e6b319cdc328"
                            alt="Share on Twitter" height="40" width="40">
                    </a>
                """
            )

    def user_history_plot(user_scores) -> None:
        user_scores = user_scores[-1]
        user_scores = (
            pd.DataFrame(user_scores)
            .sort_values(by="created_at")
            .drop(columns="username")
        )

        user_scores["Date"] = pd.to_datetime(user_scores["created_at"]).dt.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        fig = px.bar(
            user_scores,
            x="Date",
            y="score",
            title="Your history 📊 ",
        )
        fig.update_xaxes(type="category")

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    # ---------- INITIALIZING ----------
    if "words" not in st.session_state:
        with open("Streamlit/words.txt", "r") as f:
            st.session_state["words"] = json.load(f)

        set_session_states()

    def disable_widget() -> None:
        st.session_state.disabled = dict(
            hear=True,
            get_length=False,
            define=False,
        )
        st.session_state.persist_audio = True

    def persist_length() -> None:
        st.session_state["persist_length"] = st.session_state.disabled[
            "get_length"
        ] = True

    def persist_definition() -> None:
        st.session_state["persist_definition"] = st.session_state.disabled[
            "define"
        ] = True

    def get_word() -> None:
        word = random.choice(st.session_state["words"])
        if meaning_dict := dictionary.meaning(word, disable_errors=True):
            st.session_state["used_words"].append(word)
            st.session_state["words"].remove(word)
            st.session_state.meaning = meaning_dict
            play(word)
        else:
            get_word()

    st.subheader(f"Score: {st.session_state['score']}")

    r1c1, r1c2 = st.columns([1, 2])

    r1c1.button(
        "Get word",
        on_click=disable_widget,
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
        on_click=persist_length,
        key="get_length",
        disabled=st.session_state.disabled["get_length"],
        use_container_width=True,
    )

    r4c1, r4c2 = st.columns([1, 2])

    r4c1.button(
        "Get definition",
        on_click=persist_definition,
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
            get_word()

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
            "Type spelling and press enter to evaluate. ⚠️ Clicking anywhere else after you start typing will submit the answer. ",
            key="answer",
            on_change=evaluate,
        )

        # Nothing after this will be executed
