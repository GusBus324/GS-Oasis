from openai import OpenAI

# Step 1: Set up your API key
client = OpenAI(api_key="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")  # Replace with your actual OpenAI API key

# Step 2: Write your prompt
user_prompt = "Explain how a black hole works in simple terms."

# Step 3: Send the prompt to OpenAI
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # Or "gpt-4" if you have access
    messages=[
        {"role": "system", "content": "You are a helpful and friendly tutor."},
        {"role": "user", "content": user_prompt}
    ],
    max_tokens=150,
    temperature=0.7
)

# Step 4: Print the response
print("AI Response:")
print(response.choices[0].message.content.strip())
 