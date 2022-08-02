# SpellBee CLI app
# Copyright (C) 2022  Siddhant Sadangi (siddhant.sadangi@gmail.com)
# A copy of the GNU General Public License is attached with this program.

import json
import random
import os
import sys

from gtts import gTTS
from PyDictionary import PyDictionary
from playsound import playsound
from rich import print
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

dictionary = PyDictionary()


def clean_and_exit():
    print("\nIf you enjoyed this app, please consider buying me a coffee:")
    print("https://www.buymeacoffee.com/siddhantsadangi")
    print("[bold]Bye bye. See you soon ✨")
    input("\nPress any key to exit")

    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")

    sys.exit()


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def play(word: str, slow: bool = False) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """

    translated = gTTS(word, slow=slow)
    if os.path.exists("audio.mp3"):
        os.remove("audio.mp3")
    translated.save("audio.mp3")
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

    answer = Prompt.ask("[bold]Enter spelling").lower().strip()

    while answer in ["d", "r", "l", "e"]:

        if answer == "d":
            if meaning := dictionary.meaning(word, disable_errors=True):
                print(meaning)
            else:
                print("[red]Sorry, definition is not available")
        elif answer == "r":
            play(word, slow=True)
        elif answer == "l":
            print(f"[italics]No. of letters: {len(word)}")
        else:
            clean_and_exit()
        answer = Prompt.ask("[bold]Enter spelling").lower().strip()

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
            clean_and_exit()


# ---------- RUN ---------
if __name__ == "__main__":

    print(
        Panel.fit(
            """SpellBee CLI app
Copyright (C) 2022  Siddhant Sadangi (siddhant.sadangi@gmail.com)
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions."""
        )
    )

    print(
        """[bold]\nDuring the course of the game, enter:\n
* 'd' to view the dictionary definition of the word,
* 'l' to get the number of letters in the word,
* 'r' to repeat the word slowly,
* 'e' to exit."""
    )

    input("\nPress any key to start")

    with open(resource_path("words.txt"), "r", encoding="utf8") as f:
        words = json.load(f)

    run(words)
