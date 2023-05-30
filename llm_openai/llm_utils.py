"""
   Created on Tue May 30 2023
   Copyright (c) 2023 Subramanya N
"""
import logging
from typing import Text, List, Dict, Tuple, Any
import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

logger = logging.getLogger(__name__)


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def create_chat_completion(
    messages: List[Dict[str, Any]],
    model: Text = "gpt-3.5-turbo",
    temperature: float = 0,
    top_p: float = 1,
) -> Tuple[Text, Dict[Text, Any]]:
    """
    Creates a chat completion using OpenAI's GPT-3.

    Args:
        messages (List[Dict[str, Any]]): A list of message objects, where each object
            has a 'role' (either "system", "user", or "assistant") and 'content'
            (the message text).
        model (str, optional): The name of the GPT-3 model to use. Defaults to
            "gpt-3.5-turbo".
        temperature (float, optional): Controls the randomness of the output. Higher
            values make the output more random, lower values make it more deterministic.
            Defaults to 0.
        top_p (float, optional): Controls the diversity of the output by limiting the
            token selection to a subset of the most likely tokens. Defaults to 1.

    Returns:
        Tuple[str, Dict[str, Any]]: A tuple containing the generated message content
            (Text) and the usage information (dict).
    """
    logger.debug(f"Creating chat completion with messages: {str(messages)}")
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=2048,
        top_p=top_p,
    )
    return response["choices"][0]["message"]["content"], response["usage"]


@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def create_embedding(text: Text, model: Text = "text-embedding-ada-002") -> List[float]:
    """
    Creates a text embedding using OpenAI's Text Embedding model.

    Args:
        text (str): The text to embed.
        model (str, optional): The name of the text embedding model to use. Defaults to
            "text-embedding-ada-002".

    Returns:
        List[float]: The text embedding.
    """
    logger.debug(f"Creating embedding for text: {text}")
    response = openai.Embedding.create(
        model=model,
        input=text,
    )
    return response["data"][0]["embedding"]
