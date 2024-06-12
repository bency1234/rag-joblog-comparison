import re

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, context_utilization, faithfulness


def evaluate_chatbot_data(user_input, bot_response, source_documents):
    """
    Evaluate the chatbot response on the following RAGAS metrics
        - faithfulness
        - answer relevancy
        - context utilization

    Parameters:
        user_input (str): The user input/query.
        bot_response (str): The response generated by the chatbot.
        source_documents (str): The source documents or context \
        from which the response was generated.

        Returns:
        dict: A dictionary containing the evaluation results, \
        including faithfulness, answer relevancy, and context utilization.
    """
    pattern = r'page_content=(".*?[^\\]"|\'.*?[^\\]\')'
    contexts = []
    questions = user_input
    answers = bot_response

    # Extracting matching strings from source_documents
    matches = re.findall(pattern, source_documents, re.DOTALL)

    # Decoding escape characters and adding to the contexts list
    page_content = [bytes(m[1:-1], "utf-8").decode("unicode_escape") for m in matches]
    contexts.append(page_content)

    data = {"question": [questions], "answer": [answers], "contexts": contexts}
    dataset = Dataset.from_dict(data)

    # Evaluate the chatbot response
    results = evaluate(
        dataset=dataset,
        metrics=[faithfulness, answer_relevancy, context_utilization],
    )
    return results
