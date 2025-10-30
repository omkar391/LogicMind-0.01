import google.generativeai as genai

# Use your existing Google API key
genai.configure(api_key="AIzaSyBUKWTUGPNOy2rJEyT-6aB1fG7KtS5_HGw")  # Your actual key

try:
    # List available models first
    print("🔍 Available models:")
    available_models = []
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            available_models.append(model.name)
            print(f" - {model.name}")
    
    # Try with available models
    test_models = [
        'models/gemini-2.0-flash-exp',
        'models/gemini-2.0-flash', 
        'models/gemini-2.0-flash-001',
        'models/gemini-2.5-flash',
        'models/gemini-2.5-flash-preview-05-20'
    ]
    
    for model_name in test_models:
        if model_name in available_models:
            print(f"\n🧪 Testing model: {model_name}")
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, are you working? Reply with just 'Yes' or 'No'.")
                print(f"✅ {model_name} is working!")
                print(f"Response: {response.text}")
                break
            except Exception as e:
                print(f"❌ {model_name} failed: {e}")
    
except Exception as e:
    print(f"❌ Gemini API error: {e}")