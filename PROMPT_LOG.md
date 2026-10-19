# PROMPT_LOG

AI assistant used: an LLM chat assistant.

## 1. Initial prompt

> Write a Python script that loads output.json (a list of objects with device_id and avg_temperature) and generates a matplotlib bar chart comparing average temperature per device. Save it to chart.png

## 2. Bug / formatting mistake in the first attempt

The first script worked on valid input but had two robustness problems:

- If `output.json` was missing, it crashed with a `FileNotFoundError` traceback.
- If `output.json` contained an empty list `[]`, it exited successfully (code 0) but silently saved a blank chart with no bars and printed no warning.

I found both by running the script against the real file, a missing file, and an empty list.

## 3. Follow-up prompt used to fix it

> The script you gave me has two robustness problems:
>
> 1. If output.json is missing, it crashes with a FileNotFoundError traceback.
> 2. If output.json contains an empty list [], it exits successfully but silently saves a blank chart with no bars.
>
> Please fix both:
> - If the file is missing, print a clear error message to stderr and exit with code 1.
> - If the JSON is invalid or the list is empty, print a clear message and exit with code 1 without creating chart.png.
> - Keep the rest of the behavior the same (title, axis labels, saving to chart.png).

**Result:** the missing file, invalid JSON and empty list cases now print a clear error to stderr, exit with code 1, and do not create `chart.png`. I tested all three.

## Additional changes after the fix

After the AI's fix I kept reviewing the script and also made two improvements:

- Added validation so entries missing `device_id` or a numeric `avg_temperature` exit with a clear error instead of a `KeyError` traceback.
- Added a unit to the y-axis label: "Average Temperature (°C)". The brief does not state a unit, so °C is an assumption.

## AI usage in other sections

- **Section 1 (`sanitize.py`):** written by me without AI. I asked the AI assistant only to review it afterwards, which found two issues that I then fixed: `min(number, 500)` returned an int instead of a float, and `None` input crashed the function.
- **Section 2 (`summarize.py`):** generated with the AI assistant, then reviewed line by line and tested with a missing file, an empty file, bad rows (blank or text temperature, unknown status, missing device_id) and a case where every device is filtered out.
- **Section 3 (`plot_temps.py`):** generated with the AI assistant, then fixed as described above.