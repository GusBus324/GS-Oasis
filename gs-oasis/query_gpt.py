import openai

def get_open_ai_repsonse(user_question):
    openai.api_key = "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"


    user_prompt = "Take a look at the following message. Decide whether it is a phishing scam. Explain why it is if you believe it is."

    modifier  = "Provide the reponse in a JSON format with the following: Final decision, rationale, educational content, and a list of red flags. The educational content should be a short paragraph explaining how to identify phishing scams. The red flags should be a list of common signs of phishing scams."

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": user_prompt + user_question + modifier},
        ]
    )

    return response.choices[0].message['content']
    


