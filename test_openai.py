from openai import OpenAI

# Replace with your REAL OpenAI key (starts with sk-)
client = OpenAI(api_key="enter_your_API_Key")

try:
    models = client.models.list()
    print("✅ OpenAI API key is valid!")
    print("Available models:")
    for model in models.data[:5]:  # Show first 5 models
        print(f" - {model.id}")
except Exception as e:
    print(f"❌ OpenAI API error: {e}")


# from google import genai

# client = genai.Client(api_key="enter_your_API_Key")

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents="How does AI work?"
# )
# print(response.text)