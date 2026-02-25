import streamlit as st
import openai
import requests
from io import BytesIO
from dotenv import load_dotenv
import os
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables from the .env file
load_dotenv()

# Set the OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Firebase Configuration
firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")  # Ensure this is added
}

# Initialize Pyrebase and Firebase Admin
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Function to generate ad copy
def generate_ad(product_name, target_audience, tone, key_features, product_description):
    try:
        prompt = f"Create a catchy tagline and description for a product. The product is {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Highlight its comfort, sustainability, and performance."
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant that generates ad copy."},
                      {"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}"

# Function to generate images
def generate_image(prompt, num_images=1):
    try:
        response = openai.Image.create(
            prompt=prompt,
            n=num_images,
            size="1024x1024"
        )
        return [image['url'] for image in response['data']]
    except Exception as e:
        return f"Error: {e}"

# Function to download images
def download_image(image_url):
    try:
        response = requests.get(image_url)
        return BytesIO(response.content)
    except Exception as e:
        return f"Error downloading image: {e}"

# Function to generate A/B test ads
def generate_ab_test(product_name, target_audience, tone, key_features, product_description):
    try:
        prompt_a = f"Create an ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Make it catchy and engaging."
        prompt_b = f"Create a different ad for {product_name}. Target audience: {target_audience}. Tone: {tone}. Key features: {key_features}. Description: {product_description}. Focus on benefits and quality."

        ad_a = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant that generates ad copy."},
                      {"role": "user", "content": prompt_a}],
            max_tokens=150
        )

        ad_b = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": "You are an assistant that generates ad copy."},
                      {"role": "user", "content": prompt_b}],
            max_tokens=150
        )

        return ad_a['choices'][0]['message']['content'].strip(), ad_b['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error: {e}",None

# Streamlit app
st.title("Ad Gen using AI")

menu = ["Login", "Sign Up"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Sign Up":
    st.subheader("Create a New Account")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter a password")
    if st.button("Sign Up"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("Account created successfully! Please log in.")
        except Exception as e:
            st.error(f"Error: {e}")

elif choice == "Login":
    st.subheader("Login to Your Account")
    email = st.text_input("Email", placeholder="Enter your email")
    password = st.text_input("Password", type="password", placeholder="Enter your password")
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success("Logged in successfully!")
            st.session_state["user"] = user
        except Exception as e:
            st.error(f"Error: {e}")

if "user" in st.session_state:
    user_email = st.session_state["user"]["email"]
    st.sidebar.success(f"Welcome {user_email}!")
    product_name = st.text_input("Product Name", placeholder="e.g., Eco-friendly water bottle")
    target_audience = st.text_input("Target Audience", placeholder="e.g., Health-conscious individuals")
    tone = st.selectbox("Ad Tone", ["Professional", "Friendly", "Humorous", "Inspirational"])
    key_features = st.text_area("Key Features", placeholder="e.g., Lightweight, Sustainable, Stylish")
    product_description = st.text_area("Product Description", placeholder="e.g., Made from recyclable materials and perfect for active lifestyles")
    ab_test_choice = st.selectbox("Do you want to perform A/B testing on the ad copy?", ["No", "Yes"])
    generate_image_choice = st.selectbox("Do you want to generate an image for your ad?", ["No", "Yes"])

    if generate_image_choice == "Yes":
        image_description = st.text_input("Enter the image description", placeholder="e.g., Eco-friendly water bottle on a green background")
        num_images = st.slider("Number of Images to Generate", min_value=1, max_value=5, value=1)

    if st.button("Generate Ad, Image, and Video"):
        if generate_image_choice == "Yes" and not image_description:
            st.error("Please provide an image description to generate the image.")
        else:
            if ab_test_choice == "Yes":
                ad_a, ad_b = generate_ab_test(product_name, target_audience, tone, key_features, product_description)
                st.subheader("Ad A - Version 1")
                st.write(ad_a)
                st.subheader("Ad B - Version 2")
                st.write(ad_b)
            else:
                ad_text = generate_ad(product_name, target_audience, tone, key_features, product_description)
                st.subheader("Your Generated Ad")
                st.write(ad_text)

            if generate_image_choice == "Yes":
                image_urls = generate_image(image_description, num_images)
                st.subheader("Generated Images")
                for i, url in enumerate(image_urls):
                    st.image(url, caption=f"Image {i+1}")
                    img = download_image(url)
                    st.download_button(f"Download Image {i+1}", data=img, file_name=f"image_{i+1}.png", mime="image/png")