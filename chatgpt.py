def chatgpt():
    # Simple chat example
    user_message = (
        "Give me a clear list of 20 bands that is similar to "
        + getPlayString()
        + " that is of the same era or genre or style  - no bullets, no intro text, no numbers"
    )
    response = chat_with_gpt(user_message)

    SimilarBands = process_chatgpt_list(response)

    print(f"User: {user_message}", end="\n")
    return process_chatgpt_list(response)

    # Example with conversation history
    def chat_with_history(messages, model="gpt-3.5-turbo"):
        """
        Chat with conversation history
        messages should be a list of {"role": "user"/"assistant", "content": "..."}
        """
        try:
            response = client.chat.completions.create(
                model=model, messages=messages, max_tokens=150, temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"

    # Conversation with history
    conversation = [
        {"role": "user", "content": "What's the capital of France?"},
        {"role": "assistant", "content": "The capital of France is Paris."},
        {"role": "user", "content": "What's the population of that city?"},
    ]

    response = chat_with_history(conversation)
    print(f"\nConversation response: {response}")


def chat_with_gpt(message, model="gpt-3.5-turbo"):
    """
    Send a message to ChatGPT and get a response
    """
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": message}],
            max_tokens=150,
            temperature=0.7,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"Error: {str(e)}"


def process_chatgpt_list(response_text):
    """
    Process a ChatGPT response that contains a list and clean it up
    Handles various formats: JSON arrays, comma-separated, newline-separated, numbered lists, etc.
    """

    response_text = response_text.strip()

    if response_text.startswith("[") and response_text.endswith("]"):
        try:
            items = json.loads(response_text)
            return [str(item).strip() for item in items if str(item).strip()]
        except json.JSONDecodeError:
            pass

    cleaned_text = response_text

    # Remove numbered list markers (1. 2. 3. etc.)
    cleaned_text = re.sub(r"^\d+\.\s*", "", cleaned_text, flags=re.MULTILINE)

    # Remove bullet points (•, -, *, etc.)
    cleaned_text = re.sub(r"^[•\-\*]\s*", "", cleaned_text, flags=re.MULTILINE)

    # Remove "Here are" type prefixes
    cleaned_text = re.sub(
        r"^(here are|here is|the list is|list:|items:).*?[:]\s*",
        "",
        cleaned_text,
        flags=re.IGNORECASE,
    )

    # Split by various delimiters
    items = []

    # Try splitting by newlines first
    if "\n" in cleaned_text:
        items = cleaned_text.split("\n")
    # Then try commas
    elif "," in cleaned_text:
        items = cleaned_text.split(",")
    # Finally try semicolons
    elif ";" in cleaned_text:
        items = cleaned_text.split(";")
    else:
        # If no clear delimiter, try to extract items using regex
        # Look for patterns that might be list items
        items = re.findall(r"[A-Z][^.!?]*(?:[.!?]|$)", cleaned_text)

    # Clean up each item
    cleaned_items = []
    for item in items:
        item = item.strip()

        # Remove quotes
        item = item.strip("\"'")

        # Remove trailing punctuation that's not part of the content
        item = re.sub(r"[,;]+$", "", item)

        # Skip empty items
        if item:
            cleaned_items.append(item)

    return cleaned_items
