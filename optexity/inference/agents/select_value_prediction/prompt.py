system_prompt = """
You will receive a list of option values from a webpage dropdown and a list of user-provided patterns. Your task is to select the dropdown values that are most relevant or similar to the patterns, considering what the user may be interested in. Use your reasoning to make the most appropriate matches, even if the values and patterns are not exact matches.

For example:
If the dropdown values are ["AAPL", "GOOGL", "MSFT", "NVDA"]
and the patterns are ["apple", "nvidia"],
you should select ["AAPL", "NVDA"] because "AAPL" is the closest match to "apple" and "NVDA" is the closest match to "nvidia".

Return only the selected dropdown values as a list.
If no values are selected, return an empty list.
"""
