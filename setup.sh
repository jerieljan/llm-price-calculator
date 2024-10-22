#!/usr/bin/env bash

# This is basically just https://docs.streamlit.io/get-started/installation/command-line
# Note that these use the MacOS / Linux instructions. Adjust accordingly if you're on Windows.
python -m venv .venv
source .venv/bin/activate
pip install streamlit
