import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import os
from langchain_openai import ChatOpenAI

# --- Page Config ---
st.set_page_config(page_title="LinkedIn Post Generator", page_icon="🔗")

st.title("🔗 LinkedIn Post Generator")
st.markdown("This tool uses AI agents to craft a professional LinkedIn post on any topic.")

# --- Streamlit UI ---
with st.sidebar:
    st.markdown("This tool uses AI agents to craft a professional LinkedIn post on any topic")

topic = st.text_input("Enter the topic for your LinkedIn post:", placeholder="e.g., The rise of Multi-Agent AI Frameworks")

if st.button("Generate LinkedIn Post"):
    if not topic:
        st.error("Please enter a topic for the post.")
    else:
        openai_api_key = st.secrets["openai_api_key"]
        os.environ['OPENAI_API_KEY'] = openai_api_key
        serper_api_key = st.secrets["serper_api_key"]
        os.environ['SERPER_API_KEY'] = serper_api_key
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
        serper_tool_top5 = SerperDevTool(n_results=2)
        scrape_tool = ScrapeWebsiteTool()

        with st.spinner("AI agents are crafting your LinkedIn post..."):
            # --- Agents ---
            planner = Agent(
                role="LinkedIn Content Planner",
                goal=f"Plan engaging and factually accurate content for LinkedIn on {topic}",
                backstory=(
                    f"You're planning a concise LinkedIn post about {topic}. "
                    "You collect information that helps the audience learn and make informed decisions. "
                    "Your work is the basis for the Content Writer."
                ),
                allow_delegation=False,
                tools=[serper_tool_top5, scrape_tool],
                verbose=True,
                llm=llm
            )

            writer = Agent(
                role="Content Writer",
                goal=f"Write an insightful and factually accurate opinion piece about {topic} for LinkedIn",
                backstory=(
                    f"You're writing a new opinion piece about {topic} for LinkedIn. "
                    "You base your writing on the Content Planner's outline. "
                    "You follow the main objectives, provide impartial insights, and back them up with information. "
                    "You make it engaging, use bullet points, and end with a question to encourage comments. "
                    "Your post must be under 300 words. You are a LinkedIn content expert who can write viral posts."
                ),
                tools=[serper_tool_top5, scrape_tool],
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            editor = Agent(
                role="Editor",
                goal="Edit a given blog post to align with the writing style of the organization.",
                backstory=(
                    "You are an editor reviewing a LinkedIn article. "
                    "Your goal is to ensure it follows best practices, provides balanced viewpoints, and avoids controversy. "
                    "You fix grammar, improve flow, and make the tone natural and engaging. "
                    "You are a meticulous editor, polishing posts to sound professional."
                ),
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            # --- Tasks ---
            plan_task = Task(
                description=(
                    f"1. Create a concise content plan for a LinkedIn post on {topic}.\n"
                    "2. Focus on key trends, players, and news.\n"
                    "3. Identify the target audience's interests and pain points.\n"
                    "4. Develop a concise outline (introduction, key points, call to action).\n"
                ),
                expected_output="A concise content plan (under 150 words) with an outline, audience analysis, and relevant resources.",
                agent=planner,
            )

            write_task = Task(
                description=(
                    f"1. Craft a concise LinkedIn post on {topic} based on the content plan.\n"
                    "2. Ensure the post is engaging, insightful, and factual.\n"
                    "3. Structure with an introduction, body with bullet points, and a conclusion.\n"
                    "4. Keep the content under 300 words and add relevant hashtags.\n"
                ),
                expected_output="A LinkedIn post under 300 words with a hook, insights, call-to-action, and hashtags.",
                agent=writer,
                context=[plan_task]
            )

            edit_task = Task(
                description="Proofread and refine the LinkedIn post for grammar, flow, tone, and clarity. Ensure it is engaging, professional, and suitable for LinkedIn.",
                expected_output="A final polished LinkedIn post ready for publication.",
                agent=editor,
                context=[write_task]
            )

            # --- Crew ---
            crew = Crew(
                agents=[planner, writer, editor],
                tasks=[plan_task, write_task, edit_task],
                verbose=2
            )

            try:
                result = crew.kickoff(inputs={"topic": topic})
                st.success("Your LinkedIn post has been generated!")
                st.markdown(result)
            except Exception as e:
                st.error(f"An error occurred during the kickoff process: {e}")
