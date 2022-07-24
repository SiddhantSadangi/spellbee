# Spell🐝 Python CLI App

How good are you at spelling?  
Try this Python-powered interactive Spell🐝 app to find out!

## Installation

```bash
  git clone https://github.com/siddhantsadangi/spellbee
  cd SpellBee
  pip install -r requirements.txt 
```

## Usage

1. Increase volume or wear headphones
2. Open a terminal, and run the below

    ```bash
    python .\spellbee.py
    ```

3. You will hear a word. Enter the spelling. You can also enter "d" to get the definition (if available), or "r" to hear the word again, slowly
4. Repeat till you get a word wrong. Your final score will be displayed and you'll be asked if you want to play again.

## Known issues

* `metadata-generation-failed` error while installing `PyDictionary()` -
Please install `PyDictionary()` using the below command:

    ```bash
    pip install PyDictionary --use-deprecated=backtrack-on-build-failures
    ```

* Some words are missing from the `PyDictionary()` corpus. Their definitions cannot be fetched

To report bugs, please create an [issue](https://github.com/SiddhantSadangi/spellbee/issues/new).

To submit feedback, please reach out to me
at [siddhant.sadangi@gmail.com](mailto:siddhant.sadangi@gmail.com) and/or connect with me
on [LinkedIn](https://linkedin.com/in/siddhantsadangi).

<p align="center">
    <a href="https://www.buymeacoffee.com/siddhantsadangi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;">
    </a>
</p>
