#!/usr/bin/env bash

FILE=models.json

# Check if models.json exists and is older than 1 day
if [[ ! -f "$FILE" || $(find "$FILE" -mtime +1 -print) ]]; then
  echo "Downloading models list from Openrouter..."
  curl https://openrouter.ai/api/v1/models | jq > "$FILE"
fi
uv run streamlit run llm-calculator.py
# python -m streamlit run llm-calculator.py
