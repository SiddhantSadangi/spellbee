# Spellbee CLI app
# Copyright (C) 2022  Siddhant Sadangi (siddhant.sadangi@gmail.com)
# This is a free software distributed under GPL v3.

import json
import random
import sys
from os import path, remove

from gtts import gTTS
from playsound import playsound
from PyDictionary import PyDictionary
from rich import print
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

VERSION = "0.2.2"

dictionary = PyDictionary()


def clean_and_exit():
    print("\nIf you enjoyed this app, please consider buying me a coffee:")
    print("https://www.buymeacoffee.com/siddhantsadangi")
    print("[bold]Bye bye. See you soon ✨")
    input("\nPress any key to exit")

    if path.exists("audio.mp3"):
        remove("audio.mp3")

    sys.exit()


def play(word: str, slow: bool = False) -> None:
    """Pronounces `word`

    Args:
        word (str): Word to be pronounced
        slow (bool, optional): Pronounces `word` slowly. Defaults to False.
    """
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
            print("[bold red]Cannot connect to the internet. Please check your connection.")
            if Confirm.ask("Retry?"):
                play(word)
            else:
                clean_and_exit()
        else:
            print(f"[bold red]{getattr(e, 'message', repr(e))}")


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

    answer = Prompt.ask("\n[bold]Enter spelling").lower().strip()

    while answer in ["d", "r", "l", "e"]:

        if answer == "d":
            if meaning_dict := dictionary.meaning(word, disable_errors=True):
                print("\n".join(f"{item}:{meaning}" for item, meaning in meaning_dict.items()))
            else:
                print("[red]Sorry, definition is not available")
        elif answer == "r":
            play(word, slow=True)
        elif answer == "l":
            print(f"[italics]No. of letters: {len(word)}")
        else:
            clean_and_exit()
        answer = Prompt.ask("\n[bold]Enter spelling").lower().strip()

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
            f"""Spellbee CLI app v{VERSION}
Copyright (C) 2022  Siddhant Sadangi
siddhant.sadangi@gmail.com | linkedin.com/in/siddhantsadangi
This is a free software distributed under GPL v3."""
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

    with open(
        path.join(path.abspath(path.dirname(__file__)), "words.txt"), "r", encoding="utf8"
    ) as f:
        words = json.load(f)

    run(words)
