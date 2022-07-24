# SpellBee Python command-line app
# Copyright (C) 2022  Siddhant Sadangi (siddhant.sadangi@gmail.com)
# A copy of the GNU General Public License is attached with this program.

import json
import random
import os
from gtts import gTTS
from PyDictionary import PyDictionary
from playsound import playsound
from rich import print
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

dictionary = PyDictionary()


def play(word: str, slow: bool = False) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """

    t1 = gTTS(word, slow=slow)
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    t1.save("audio.mp3")
    return playsound("audio.mp3")


# --------- RECURSIVE FUNCTION ---------
def run(words: list, score: int = 0) -> None:
    """Recursive scoring function.

    Args:
        words (list): List of words to choose from
        score (int, optional): Current score. Defaults to 0.
    """

    word = random.choice(words)
    words.remove(word)
    play(word)

    answer = (
        Prompt.ask(
            '[bold]Enter spelling[/] ([italic]type "d" to get the definition or "r" to hear again, slowly[/])'
        )
        .lower()
        .strip()
    )

    while answer in ["d", "r"]:

        if answer == "d":
            if meaning := dictionary.meaning(word, disable_errors=True):
                print(meaning)
            else:
                print("[red]Sorry, definition is not available")
        else:
            play(word, slow=True)
        answer = (
            Prompt.ask('Enter spelling ([italic]type "r" to repeat slowly[/])')
            .lower()
            .strip()
        )

    if answer == word:
        score += 1
        print(f"[bold green]Correct! [/]Score: {score}")
        run(words, score)
    else:
        print(f'[bold red]Wrong answer.[/] The correct answer is "{word}"\n')
        print(Panel.fit(f"[bold]Final score: [green]{score}"))

        if Confirm.ask("Play again?"):
            run(words, 0)
        else:
            print("[bold]Bye bye!")


# ---------- RUN ---------

with open("words.txt", "r") as f:
    words = json.load(f)

run(words)
