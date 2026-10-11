# CreatorLink

Rights-safe, vernacular AI creators for small brands, with a "try before you hire" preview.

## Run it (2 minutes)

```
pip install flask
python app.py
```

Open http://127.0.0.1:5000 in your browser.

If `python` does not work, use `python3 app.py`. On Windows you can also try `py app.py`.

## Demo flow (60 seconds)

1. Home page: tap a sample brief chip (the form fills itself), press **Find my creators**.
2. Show the top 3 matches: score, reasons, sample concept, rights badge.
3. Press **Shortlist and get agreement** on one creator.
4. Open **Creators**, add a new creator, then run a brief again to show it appears in matching.
5. Ask a judge for their own brief and type it in live.

## Files

- `app.py`: the web pages (Flask)
- `core.py`: sample creators, matching score, sample concepts, agreement text
- `templates/`: the HTML pages
- `creators_extra.json`: created automatically when someone joins as a creator. Delete it to reset.

## How the match score works

Language 35%, brand type 30%, style words 15%, budget fit 20%. It runs offline, so there is
no API cost and nothing breaks if the Wi-Fi does.

## Things to do before the demo

- Ask a native speaker to check the Hindi, Tamil, Telugu and Marathi taglines in `core.py` (`HOOKS`).
- The 10 starter creators are made-up sample profiles. Say so in the pitch.
- The agreement is a template, not legal advice.
