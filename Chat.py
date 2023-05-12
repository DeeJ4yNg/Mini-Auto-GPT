import time
import token_counter
from openai.error import RateLimitError, APIError
import openai

#↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓A Magic function that use AI to return the result - -!!!
def call_ai_function(
    function: str, args: list, description: str, model: str | None = None
) -> str:

    if model is None:
        model = "gpt-3.5-turbo"
    # For each arg, if any are None, convert to "None":
    args = [str(arg) if arg is not None else "None" for arg in args]
    # parse args to comma separated string
    args = ", ".join(args)
    messages = [
        {
            "role": "system",
            "content": f"You are now the following python function: ```# {description}"
            f"\n{function}```\n\nOnly respond with your `return` value.",
        },
        {"role": "user", "content": args},
    ]

    return create_chat_completion(model=model, messages=messages, temperature=0)

#↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑

def create_chat_message(role, content):
    return {"role": role, "content": content}

def generate_context(prompt, relevant_memory, full_message_history, model):
    current_context = [
        create_chat_message("system", prompt),
        create_chat_message(
            "system", f"The current time and date is {time.strftime('%c')}"
        ),
        create_chat_message(
            "system",
            f"This reminds you of these events from your past:\n{relevant_memory}\n\n",
        ),
    ]

    next_message_to_add_index = len(full_message_history) - 1
    insertion_index = len(current_context)

    current_tokens_used = token_counter.count_message_tokens(current_context, model)
    return (
        next_message_to_add_index,
        current_tokens_used,
        insertion_index,
        current_context,
    )

# Core chat function:::
def create_chat_completion(
    messages: list, 
    model: str | None = None,
    temperature: float = 0,
    max_tokens: int | None = None,
) -> str:
    response = None
    num_retries = 10
    for attempt in range(num_retries):
        backoff = 2 ** (attempt + 2)
        try:
            response = openai.ChatCompletion.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
            )
            break
        except RateLimitError:
            print("Error: Reached rate limit, passing...")
        except APIError as e:
            if e.http_status == 502:
                pass
            else:
                raise
            if attempt == num_retries - 1:
                raise
        time.sleep(backoff)
    if response is None:
        raise RuntimeError(f"Failed to get response after {num_retries} retries")

    return response.choices[0].message["content"]


def chat_with_ai(prompt, user_input, full_message_history, permanent_memory, token_limit):
    while True:
        try:
            model = "gpt-3.5-turbo"
            print(f"Token limit: {token_limit}")
            send_token_limit = token_limit - 1000
            #check this out
            relevant_memory = (
                ""
                if len(full_message_history) == 0
                else permanent_memory.get_relevant(str(full_message_history[-9:]), 10)
            )
            print(f"Memory Stats: {permanent_memory.get_stats()}")

            (
                next_message_to_add_index,
                current_tokens_used,
                insertion_index,
                current_context,
            ) = generate_context(prompt, relevant_memory, full_message_history, model)

            while current_tokens_used > 2500:
                # remove memories until we are under 2500 tokens
                relevant_memory = relevant_memory[:-1]
                (
                    next_message_to_add_index,
                    current_tokens_used,
                    insertion_index,
                    current_context,
                ) = generate_context(
                    prompt, relevant_memory, full_message_history, model
                )

            current_tokens_used += token_counter.count_message_tokens(
            [create_chat_message("user", user_input)], model
            )
                
            while next_message_to_add_index >= 0:
                message_to_add = full_message_history[next_message_to_add_index]

                tokens_to_add = token_counter.count_message_tokens(
                [message_to_add], model
                )
                if current_tokens_used + tokens_to_add > send_token_limit:
                    break

                current_context.insert(
                    insertion_index, full_message_history[next_message_to_add_index]
                )

                current_tokens_used += tokens_to_add

                next_message_to_add_index -= 1

                current_context.extend([create_chat_message("user", user_input)])

                tokens_remaining = token_limit - current_tokens_used
                print(f"Token limit: {token_limit}")
                print(f"Send Token Count: {current_tokens_used}")
                print(f"Tokens remaining for response: {tokens_remaining}")
                print("------------ CONTEXT SENT TO AI ---------------")
                for message in current_context:
                    if message["role"] == "system" and message["content"] == prompt:
                        continue
                    print(f"{message['role'].capitalize()}: {message['content']}")
                print("----------- END OF CONTEXT ----------------")


                #Core chat function:::
                assistant_reply = create_chat_completion(
                model=model,
                messages=current_context,
                max_tokens=tokens_remaining,
                )

                full_message_history.append(create_chat_message("user", user_input))
                full_message_history.append(
                create_chat_message("assistant", assistant_reply)
                )

                return assistant_reply
        except RateLimitError:
            print("Error: ", "API Rate Limit Reached. Waiting 10 seconds...")
            time.sleep(10)
