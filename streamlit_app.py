import streamlit as st

st.set_page_config(
    page_title="AI Content Generation Suite",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("🤖 AI Content Generation Suite")

st.markdown("""
Welcome to the AI Content Generation Suite! This application leverages the power of AI agentic workflows (using CrewAI) to help you generate content for various social media platforms and blogs.

**What can you do?**

Use the navigation panel on the left to select a content generator:

- **Instagram Post Generator:** Create an engaging caption and a relevant image for your Instagram post based on a theme.
- **Blog Post Generator:** Generate a complete blog post from a topic, including a content plan, the written article, and an edited final version.
- **LinkedIn Post Generator:** Craft a professional and insightful LinkedIn post on any topic.
- **Twitter Post Generator:** Create a concise and impactful tweet, complete with relevant hashtags.

**How to get started?**

1.  Select a generator from the sidebar.
2.  Enter the required API keys (OpenAI and/or Serper). Your keys are not stored.
3.  Provide a topic or theme.
4.  Click the "Generate" button and watch the AI agents work their magic!

This tool is designed to streamline your content creation process, making it faster and more efficient. Let's get started!
""")
