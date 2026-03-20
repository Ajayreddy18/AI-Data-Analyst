import streamlit as st
import requests

st.set_page_config(page_title="AI Data Analyst", layout="wide")

st.title(" AI Data Analyst")
st.write("Upload your dataset and ask questions!")

# Backend URL
API_URL = "http://127.0.0.1:8000"


if "chat" not in st.session_state:
    st.session_state.chat = []

#  File Upload
uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

if uploaded_file is not None:
    files = {"file": uploaded_file.getvalue()}
    response = requests.post(f"{API_URL}/upload/", files={"file": uploaded_file})

    if response.status_code == 200:
        st.success("File uploaded successfully!")

#  Chat Input
user_input = st.text_input("Ask a question about your data:")

if st.button("Submit") and user_input:
    response = requests.post(
        f"{API_URL}/ask/",
        params={"question": user_input}
    )

    result = response.json()

    st.session_state.chat.append((user_input, result))

#  Chat Display
for user_q, res in st.session_state.chat:
    st.markdown(f"**🧑 You:** {user_q}")

    if res["output"]["type"] == "plot":
        image_url = f"{API_URL}/{res['output']['path']}"
        st.image(image_url)
        st.markdown(f"**🧠 Insight:** {res.get('insight', '')}")
    elif res["output"]["type"] == "text":
        st.markdown(f"**🤖 AI:** {res['output']['value']}")
    else:
        st.markdown(f"⚠️ Error: {res['output']['value']}")
