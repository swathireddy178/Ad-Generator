import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the test variable and check if it's loaded correctly
test_variable = os.getenv("TEST_VARIABLE")

if test_variable:
    print(f"Test Variable Loaded: {test_variable}")
else:
    print("Test Variable not found in the .env file.")

# Optional: Check some Firebase keys to ensure they're loaded
firebase_api_key = os.getenv("FIREBASE_API_KEY")
if firebase_api_key:
    print(f"Firebase API Key Loaded: {firebase_api_key}")
else:
    print("Firebase API Key not found in the .env file.")