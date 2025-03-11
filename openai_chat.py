import os
import random
import tiktoken
from rich import print

def num_tokens_from_messages(messages, model='gpt-4o'):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":  
                    num_tokens += -1  
        num_tokens += 2  # every reply is primed with <im_start>assistant
        return num_tokens
    except Exception:
        raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
        See https://github.com/openai/openai-python/blob/main/chatml.md for more info.""")

class OpenAiManager:
    
    def __init__(self):
        self.chat_history = []  # Stores conversation history
        try:
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                print("[yellow]WARNING: No OpenAI API Key found. Running in MOCK mode.[/yellow]")
                self.mock_mode = True
            else:
                self.mock_mode = False
                from openai import OpenAI  # Import only if API key is set
                self.client = OpenAI(api_key=self.api_key)
        except Exception:
            print("[red]Error initializing OpenAI. Running in MOCK mode.[/red]")
            self.mock_mode = True

    # Generates a fake AI response for testing
    def mock_response(self, prompt):
        mock_replies = [
            "That's an interesting perspective!",
            "I strongly agree with this viewpoint.",
            "This issue is more complex than it seems.",
            "I believe this policy would have a major impact on society.",
            "Historically, similar laws have had mixed results.",
            "There are both benefits and drawbacks to this approach.",
            "This could be a step in the right direction.",
            "I completely oppose this idea."
        ]
        return random.choice(mock_replies)

    # Simulated chat function (no OpenAI calls)
    def chat(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return
        
        if self.mock_mode:
            return self.mock_response(prompt)
        
        # If OpenAI is enabled, make the API call
        chat_question = [{"role": "user", "content": prompt}]
        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=chat_question
        )

        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer

    # Simulated chat with history
    def chat_with_history(self, prompt=""):
        if not prompt:
            print("Didn't receive input!")
            return
        
        self.chat_history.append({"role": "user", "content": prompt})
        
        if self.mock_mode:
            return self.mock_response(prompt)

        print("[yellow]\nAsking ChatGPT a question...")
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=self.chat_history
        )

        self.chat_history.append({"role": completion.choices[0].message.role, "content": completion.choices[0].message.content})
        openai_answer = completion.choices[0].message.content
        print(f"[green]\n{openai_answer}\n")
        return openai_answer
