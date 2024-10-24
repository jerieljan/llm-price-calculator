import streamlit as st
import json
import pandas as pd


# Load the JSON data
def load_json_data():
    with open('models.json', 'r') as file:
        data = json.load(file)
    return data['data']


# Calculate prices and costs
def calculate_prices(model, input_tokens, output_tokens, monthly_use, budget):
    prompt_price = float(model['pricing']['prompt'])
    completion_price = float(model['pricing']['completion'])

    input_price = prompt_price * 1_000_000
    output_price = completion_price * 1_000_000
    transaction_price = input_price + output_price

    user_transaction_cost = (input_tokens * prompt_price) + (output_tokens * completion_price)
    user_monthly_cost = user_transaction_cost * monthly_use

    # Handle division by zero
    try:
        user_tx_per_budget = f"{(budget / user_transaction_cost):,.0f}"
    except ZeroDivisionError:
        user_tx_per_budget = float('nan')

    user_balance = budget - user_monthly_cost

    return {
        'id': model['id'],
        'name': model['name'],
        'input_price': input_price,
        'output_price': output_price,
        'transaction_price': transaction_price,
        'user_transaction_cost': user_transaction_cost,
        'user_monthly_cost': user_monthly_cost,
        'user_balance': user_balance,
        'user_tx_per_budget': user_tx_per_budget
    }


def filter_models(df, includes, excludes):
    # If no keywords or excludes, return the original dataframe
    if not includes and not excludes:
        return df

    # Filter by keywords and excludes
    filtered = df[df.apply(
        lambda row: (
                (not includes or any(
                    include.lower() in row['id'].lower() or include.lower() in row['name'].lower() for include in
                    includes)) and
                (not excludes or all(
                    exclude.lower() not in row['id'].lower() and exclude.lower() not in row['name'].lower() for exclude
                    in excludes))
        ),
        axis=1
    )]
    return filtered


def format_price(value):
    if value >= 1:
        return f"${value:,.2f}"
    return f"${value:,.6f}"


def highlight_row(row, budget):
    user_balance = row['user_balance']
    if user_balance <= 0:
        return ['background-color: #fecaca'] * len(row)
    elif user_balance <= budget * 0.2:
        return ['background-color: #fde68a'] * len(row)
    return [''] * len(row)


def main():
    with st.sidebar:
        with st.popover("Overview"):
            st.markdown("""
                        ### Overview

                        Computing LLM costs can be tricky. This calculator isn't definitive either, but maybe it helps giving a better picture.

                        The idea here is that you'll provide how much tokens you'll generally use (listed as Input Tokens and Output Tokens), 
                        and if we have that many transactions in a given month (listed as Monthly Use).
                        
                        This calculator will tell you how much it costs depending on the models listed on the right, and how much transactions
                        with that many tokens you can do with each model.

                        You can also provide a "budget" below so you can see how much of it you'll burn if you were to perform that many in a month.
                        
                        ### Credits

                        Pricing is based on [**OpenRouter**](https://openrouter.ai/)'s pricing, which generally provides the best pricing for public users.
                        I strongly recommend the service!

                        This Streamlit app was made by [**jerieljan**](https://links.jerieljan.com/contact).
                        You can check the code and its GitHub repository here: https://github.com/jerieljan/llm-price-calculator

                        """)
        st.markdown("""
                    ## Input Parameters
                    Provide how much tokens you're expecting to use.
                    """)
        input_tokens = st.number_input("Input Tokens (User Input)", min_value=1, value=1000, step=100)
        output_tokens = st.number_input("Output Tokens (User Output)", min_value=1, value=100, step=100)
        monthly_use = st.number_input("Monthly Transactions", min_value=1, value=1000)
        budget = st.number_input("Monthly Budget ($)", min_value=0.01, value=100.00, step=1.0)
        includes = st.text_input("Filter Keywords (comma-separated)", "")
        excludes = st.text_input("Filter Exclusions (comma-separated)", "")

        with st.popover("Filtering Tips"):
            st.markdown(f"""
                        The first box filters the overall models list to what you provide (e.g., {includes}).
                        After that, the list is filtered further by removing models with keywords indicated in the second box (e.g., {excludes}).

                        ### Examples:

                        - You can write `gpt,gemini,claude` in your keywords to get all OpenAI, Google and Anthropic models.
                        - You can write `free` in your exclusions to remove the free models.
                        - You can write `llama` in keywords and `meta` in exclusions to get Llama models hosted by other providers or remixed by other providers.

                        """)

        st.markdown(f"""
                    Based on your input, the table on the right...
                    - says that your query of {input_tokens} input tokens and {output_tokens} output tokens will cost you `user_transactions_cost` per query.
                    - `user_monthly_cost` indicates your spend, if you were to run {input_tokens} + {output_tokens} at {monthly_use} times.
                    - `user_balance` indicates how much money is left over from your budget at ${budget:,.2f}.
                    - Finally, `user_tx_per_budget` tells you how many queries you can run with your ${budget:,.2f} budget.
                    """)

        st.info("Prices are provided by [OpenRouter](https://openrouter.ai/) and their API.")

    # Perform calculations whenever any input changes
    models_data = load_json_data()
    results = [calculate_prices(model, input_tokens, output_tokens, monthly_use, budget) for model in models_data]

    df = pd.DataFrame(results)

    includes_list = [include.strip() for include in includes.split(',') if include.strip()]
    exclusions_list = [exclude.strip() for exclude in excludes.split(',') if exclude.strip()]
    filtered_df = filter_models(df, includes_list, exclusions_list)

    if filtered_df.empty:
        st.warning("No models match the given keywords.")
    else:

        # Format the DataFrame and apply the row highlighting based on user_balance
        styled_df = filtered_df.style.apply(highlight_row, budget=budget, axis=1).format({
            'input_price': format_price,
            'output_price': format_price,
            'transaction_price': format_price,
            'user_transaction_cost': format_price,
            'user_monthly_cost': format_price,
            'user_balance': format_price
        })

        # Display the styled DataFrame with increased height
        st.dataframe(styled_df, use_container_width=True, height=800, hide_index=True)

    filter_message = ""
    if includes_list:
        filter_message += f"Filtering models: \"{', '.join(includes_list)}\". "
    if exclusions_list:
        filter_message += f"Excluding models: \"{', '.join(exclusions_list)}\". "
    if includes_list or exclusions_list:
        filter_message += f"Showing {len(filtered_df)} out of {len(df)} models."

    if filter_message:
        st.text(filter_message)


# Main Content

st.set_page_config(layout="wide")
st.title("LLM Pricing Calculator")

main()
