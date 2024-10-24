# llm-price-calculator

A price calculator for LLM models and services, using Streamlit.

You can view this app in action in [Streamlit](https://llm-price-calculator.streamlit.app/).

## Requirements:

- Python 3.x
- curl
- jq
- Streamlit (configured on `setup.sh`)

## Usage

1. Clone this project.
2. Run `setup.sh`
   - This will configure the Streamlit setup on your working directory.
3. Run `start.sh`
   - This downloads the price list from OpenRouter, and starts Streamlit locally. 