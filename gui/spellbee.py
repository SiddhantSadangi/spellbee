# Spellbee GUI app
# Copyright (C) 2022  Siddhant Sadangi (siddhant.sadangi@gmail.com)
# A copy of the GNU General Public License is attached with this program.

import json
import random
import webbrowser
from os import path, remove
from textwrap import wrap
from tkinter import DISABLED, END, HORIZONTAL, NORMAL, NSEW, Button, Label, StringVar, Tk, ttk

from gtts import gTTS
from playsound import playsound
from PyDictionary import PyDictionary

VERSION = "0.1.0"

dictionary = PyDictionary()
used_words = []


def play_word(word: str, slow: bool = False) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """
    if play["text"] in ["Hear word", "Restart", "Retry"]:
        play["text"] = "Repeat slowly"
        define["state"] = length["state"] = inputtxt["state"] = NORMAL
        result.config(text="")
        inputtxt.delete(0, END)

    try:
        translated = gTTS(word, slow=slow)
        if path.exists("audio.mp3"):
            remove("audio.mp3")
        translated.save("audio.mp3")

        return playsound("audio.mp3")

    except Exception as e:
        if (
            getattr(e, "message", repr(e))
            == "gTTSError('Failed to connect. Probable cause: Unknown')"
        ):
            definition.config(
                text="Cannot connect to the internet. Please check your connection.",
                fg="red",
            )
        else:
            definition.config(
                text=f"{getattr(e, 'message', repr(e))}",
                fg="red",
            )
        play["text"] = "Retry"


def get_word():

    if len(used_words) == 0:
        scorelbl.config(text="Score: 0")

    if play["text"] in ["Hear word", "Restart"]:
        word = random.choice(words)
        words.remove(word)
        used_words.append(word)
        return word

    return used_words[-1]


def get_definition(word):
    if meaning := dictionary.meaning(word, disable_errors=True):
        definition.config(
            text="\n".join(wrap(str(meaning), width=60)),
            fg="black",
        )
    else:
        definition.config(text="Definition not available", fg="red")
    define["state"] = DISABLED


def get_length(word):
    length["text"] = f"Word length = {len(word)}"
    length["state"] = DISABLED


def evaluate(_):
    global score, used_words
    guess = answer.get().strip().lower()
    word = get_word()
    if guess == word:
        result.config(text="Correct!", fg="green", font="bold")
        score = score + 1
        scorelbl.config(text=f"Score: {score}")
        play["text"] = "Hear word"
    else:
        result.config(
            text=f'Wrong answer.\nCorrect answer is "{word.upper()}".',
            fg="red",
            font="bold",
        )
        scorelbl.config(text=f"Final Score: {score}")
        play["text"] = "Restart"
        score = 0
        used_words = []

    inputtxt["state"] = length["state"] = define["state"] = DISABLED
    length["text"] = "Get word length"
    definition.config(text="")
    play.focus_set()


def click_button(_):
    widget = root.focus_get()
    if widget == inputtxt:
        evaluate(_)
    elif widget != root:
        widget.invoke()


# ---------- RUN APP ---------
score = 0

# Load words
with open(path.join(path.abspath(path.dirname(__file__)), "words.txt"), "r", encoding="utf8") as f:
    words = json.load(f)

root = Tk()
root.title(f"Spellbee 🐝 (v{VERSION})")
root.resizable(False, False)

# Center UI
root.eval("tk::PlaceWindow . center")

# Content frame
mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=NSEW)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

# Speak word
play = Button(
    mainframe,
    height=2,
    width=15,
    text="Hear word",
    font=("Arial", 13),
    command=lambda: play_word(get_word(), slow=play["text"] == "Repeat slowly"),
)

play.grid(column=0, row=0)
play.focus_set()

# Get definition
define = Button(
    mainframe,
    height=2,
    width=15,
    text="Get definition",
    font=("Arial", 13),
    command=lambda: get_definition(used_words[-1]),
    state=DISABLED,
)

define.grid(column=1, row=0)

# Get length
length = Button(
    mainframe,
    height=2,
    width=15,
    text="Get word length",
    font=("Arial", 13),
    command=lambda: get_length(used_words[-1]),
    state=DISABLED,
)

length.grid(column=2, row=0)

# Show definition
definition = Label(mainframe, width=60)
definition.config(font=("Courier", 12))
definition.grid(column=0, columnspan=3, row=1)

# Answer box
class PlaceholderEntry(ttk.Entry):
    def __init__(self, container, placeholder, *args, **kwargs):
        super().__init__(container, *args, style="Placeholder.TEntry", **kwargs)
        self.placeholder = placeholder

        self.insert("0", self.placeholder)
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)

    def _clear_placeholder(self, e):
        if self["style"] == "Placeholder.TEntry":
            self.delete("0", "end")
            self["style"] = "TEntry"

    def _add_placeholder(self, e):
        if not self.get():
            self.insert("0", self.placeholder)
            self["style"] = "Placeholder.TEntry"


style = ttk.Style(mainframe)
style.configure("Placeholder.TEntry", foreground="#d5d5d5")

answer = StringVar()
inputtxt = PlaceholderEntry(
    mainframe, "Type answer here. Press Enter to check", textvariable=answer
)
inputtxt.config(font=("Arial", 15))
inputtxt.grid(column=0, columnspan=3, row=2)

# Score
scorelbl = Label(mainframe, text=f"Score: {score}", fg="darkgreen")
scorelbl.config(font=("Arial", 15, "bold"))
scorelbl.grid(column=0, columnspan=3, row=5)

# Show result
result = Label(mainframe)
result.config(font=("Arial", 12))
result.grid(column=0, columnspan=3, row=4)

# Copyright
s = ttk.Separator(mainframe, orient=HORIZONTAL)
s.grid(column=0, columnspan=3, row=6)

cpl = Label(
    mainframe,
    text="""Copyright © 2022  Siddhant Sadangi.
This is a free software distributed under GPL v3.
siddhant.sadangi@gmail.com | linkedin.com/in/siddhantsadangi""",
    fg="#545961",
)
cpl.config(font=("Arial", 8))
cpl.grid(column=0, columnspan=3, row=7)

# BMAC
bmac = Label(
    mainframe,
    text="If you enjoyed this app, please consider buying me a coffee :)",
    fg="blue",
    cursor="hand2",
)
bmac.config(font=("Arial", 8))
bmac.grid(column=0, columnspan=3, row=8)
bmac.bind(
    "<Button-1>", lambda e: webbrowser.open_new("https://www.buymeacoffee.com/siddhantsadangi")
)

# Configuring grid
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5, sticky=NSEW)

root.bind("<Return>", click_button)

root.mainloop()
