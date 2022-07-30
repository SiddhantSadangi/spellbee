# Spell🐝 CLI App

How good are you at spelling?  
Try this interactive Spell🐝 app to find out!

## Usage

### Windows

Just download and run the [spellbee.exe](https://github.com/SiddhantSadangi/spellbee/raw/main/spellbee.exe) file

### Other platforms

You will need to download and build from the source.

1. Installation

    ```bash
    git clone https://github.com/siddhantsadangi/spellbee
    cd SpellBee
    pip install -r requirements.txt 
    ```

2. Usage

    ```bash
    python .\spellbee.py
    ```

3. Create executable (optional)

    i. Install [pyinstaller](https://pyinstaller.org/en/stable/)  
    ii. Run the below command in the terminal

    ```bash
    pyinstaller --distpath . -i .\icon.ico -F --add-data 'words.txt;.' .\spellbee.py
    ```

## Known issues

* Some words are missing from the `PyDictionary()` corpus. Their definitions cannot be fetched

* `metadata-generation-failed` error while installing `PyDictionary()` -
Please install `PyDictionary()` using the below command:

    ```bash
    pip install PyDictionary --use-deprecated=backtrack-on-build-failures
    ```

To report bugs, please create an [issue](https://github.com/SiddhantSadangi/spellbee/issues/new).

To submit feedback, please reach out to me
at [siddhant.sadangi@gmail.com](mailto:siddhant.sadangi@gmail.com) and/or connect with me
on [LinkedIn](https://linkedin.com/in/siddhantsadangi).

<p align="center">
    <a href="https://www.buymeacoffee.com/siddhantsadangi" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;">
    </a>
</p>
