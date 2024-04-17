import tiktoken


def get_tokens(model_name, text):
    """
    Calculates the number of tokens in the given text using the specified model.

    Args:
        model_name (str): The name of the model used for tokenization.
        text (str): The input text to be tokenized.

    Returns:
        int: The total number of tokens in the text.

    Example:
        >>> get_tokens("bert-base-uncased", "Hello, how are you?")
        Estimated tokens: 8
        8
    """
    enc = tiktoken.encoding_for_model(model_name)

    total_word_count = len(text)
    total_token_count = len(enc.encode(text))

    print(f"\nTotal word count: {total_word_count}")
    print(f"\nEstimated tokens: {total_token_count}")
    return total_token_count