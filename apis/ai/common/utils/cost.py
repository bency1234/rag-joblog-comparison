import json

from ai.common.utils.token import get_tokens
from ai.llms.constants import COST_PER_TOKENS


def get_cost(
    model,
    input_cost,
    output_cost,
    prompt,
    user_input,
    response,
    source_documents,
    message_log,
):
    """
    Calculates the cost associated with generating a response in a conversational AI system.
    This function calculates the cost of generating a response.
    """
    final_prompt = (
        prompt
        + "Human prompt"
        + "Message_log"
        + json.dumps(message_log, indent=2)
        + "User_input"
        + user_input
        + "Source_documents"
        + str(source_documents)
    )
    prompt_tokens = get_tokens(model, final_prompt)
    output_tokens = get_tokens(model, "Response" + response)

    return (
        prompt_tokens * input_cost / COST_PER_TOKENS
        + output_tokens * output_cost / COST_PER_TOKENS
    )
