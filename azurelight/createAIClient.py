import aiohttp

def createAIClient(ENDPOINT, DEPLOYMENT_NAME, API_KEY, max_chars=3000, max_tokens=100):
    """
    Creates a context-aware client for querying the Azure OpenAI model with context trimming by character count.

    :param ENDPOINT: The endpoint of the Azure OpenAI service.
    :param DEPLOYMENT_NAME: The deployment name for the Azure OpenAI model.
    :param API_KEY: The API key for authentication.
    :param max_chars: Maximum total character count for the conversation context.
    :return: An async function that takes a prompt and returns a response.
    """
    # Maintain conversation history
    messages = [
        {"role": "system", "content": "You are an AI assistant."}
    ]

    async def client(prompt):
        """
        Query the Azure OpenAI model for a response asynchronously while maintaining context.

        :param prompt: The input prompt to send to the model.
        :return: The response from the model.
        """
        nonlocal messages  # Allows modification of the messages list
        url = f"{ENDPOINT}openai/deployments/{DEPLOYMENT_NAME}/chat/completions?api-version=2024-08-01-preview"

        headers = {
            "Content-Type": "application/json",
            "api-key": API_KEY
        }

        # Add the user prompt to the conversation history
        messages.append({"role": "user", "content": prompt})

        # Calculate the total character count of the conversation
        total_chars = sum(len(message["content"]) for message in messages)

        # Ensure the messages list does not exceed the maximum character count
        while total_chars > max_chars:
            if len(messages) > 1:  # Always keep the system message
                removed_message = messages.pop(1)  # Remove the oldest user/assistant message
                print(f"Trimming message: {removed_message['content'][:30]}... (length: {len(removed_message['content'])})")
                total_chars = sum(len(message["content"]) for message in messages)
            else:
                break

        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                print(f"POST {url} -> Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    # Extract the assistant's reply and add it to the conversation history
                    assistant_reply = data["choices"][0]["message"]["content"]
                    messages.append({"role": "assistant", "content": assistant_reply})
                    return assistant_reply
                else:
                    error_message = await response.text()
                    return f"Error: {response.status} - {error_message}"

    return client
