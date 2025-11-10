import streamlit as st

# Title
st.title("My First Streamlit App")

# Text
st.write("Hello! This is a simple Streamlit application.")

# User input
name = st.text_input("Enter your name:")

# Button
if st.button("Submit"):
    st.write(f"Welcome, **{name}**! 🎉")

# Slider
age = st.slider("Select your age:", 1, 100, 18)
st.write(f"Your age is: {age}")

# Checkbox
if st.checkbox("Show a secret message"):
    st.success("🎇 Streamlit is fun!")
