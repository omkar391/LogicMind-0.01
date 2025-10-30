"""
Test script to demonstrate the enhanced error handling
"""
import streamlit as st
import sys
import os

# Add utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from ai_helper import AIHelper

def test_error_handling():
    """Test different error scenarios"""
    st.title("🧪 Error Handling Test")
    
    st.write("This script tests various API error scenarios to demonstrate the enhanced error handling.")
    
    # Test with invalid API key
    st.subheader("1. Invalid API Key Test")
    if st.button("Test Invalid API Key"):
        try:
            ai_helper = AIHelper("invalid-key-123", "gpt-3.5-turbo", "OpenAI")
            result = ai_helper.test_connection()
            st.write(f"Connection result: {result}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Test with rate limit (if you have a valid key with low limits)
    st.subheader("2. Rate Limit Test")
    api_key = st.text_input("Enter a valid API key to test rate limits", type="password")
    if st.button("Test Rate Limit") and api_key:
        try:
            ai_helper = AIHelper(api_key, "gpt-3.5-turbo", "OpenAI")
            # Make multiple rapid requests to trigger rate limit
            for i in range(5):
                result = ai_helper.generate_cypher_query(f"Test query {i}")
                st.write(f"Request {i+1}: {result.get('success', False)}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Test with invalid model
    st.subheader("3. Invalid Model Test")
    if st.button("Test Invalid Model"):
        try:
            ai_helper = AIHelper("sk-test-key", "invalid-model-xyz", "OpenAI")
            result = ai_helper.test_connection()
            st.write(f"Connection result: {result}")
        except Exception as e:
            st.error(f"Error: {e}")
    
    # Test Gemini errors
    st.subheader("4. Google Gemini Test")
    gemini_key = st.text_input("Enter Gemini API key", type="password")
    if st.button("Test Gemini") and gemini_key:
        try:
            ai_helper = AIHelper(gemini_key, "gemini-1.5-flash", "Google Gemini")
            result = ai_helper.test_connection()
            st.write(f"Connection result: {result}")
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    test_error_handling()

