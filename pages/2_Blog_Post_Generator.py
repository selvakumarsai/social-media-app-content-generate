import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import os
from langchain_openai import ChatOpenAI

# --- Page Config ---
st.set_page_config(page_title="Blog Post Generator", page_icon="✍️")

st.title("✍️ Blog Post Generator")
st.markdown("This tool uses a team of AI agents to research, write, and edit a blog post on any topic. Enter your API keys and a topic to begin.")

# --- Streamlit UI ---
with st.sidebar:
    

topic = st.text_input("Enter the topic for your blog post:", placeholder="e.g., The Future of Artificial Intelligence")

if st.button("Generate Blog Post"):
    if not topic:
        st.error("Please enter a topic for the blog post.")
    else:
        openai_api_key = st.secrets["openai_api_key"]
        os.environ['OPENAI_API_KEY'] = openai_api_key
        serper_api_key = st.secrets["serper_api_key"]
        os.environ['SERPER_API_KEY'] = serper_api_key
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)
        search_tool = SerperDevTool()
        scrape_tool = ScrapeWebsiteTool()

        with st.spinner("AI agents are crafting your blog post... This may take a moment."):
            # --- Agents ---
            planner = Agent(
                role="Content Planner",
                goal=f"Plan engaging content on {topic}",
                backstory=f"You are a content planner focused on {topic}. You gather information to inform the audience. Your plan guides the writer.",
                tools=[search_tool, scrape_tool],
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            writer = Agent(
                role="Content Writer",
                goal=f"Write an opinion piece about {topic}",
                backstory=f"You are a writer creating an opinion piece on {topic}, based on the content plan. You aim for insightful and balanced writing, distinguishing opinions from facts.",
                tools=[search_tool, scrape_tool],
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            editor = Agent(
                role="Editor",
                goal="Edit a blog post for style and accuracy.",
                backstory="You are an editor reviewing blog posts for quality, balance, and adherence to guidelines.",
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            # --- Tasks ---
            plan_task = Task(
                description=(
                    f"1. Gather key trends, players, and news on {topic}."
                    "2. Identify the target audience."
                    "3. Develop a concise content outline (under 100 words)."
                    "4. Include SEO keywords and relevant data."
                ),
                expected_output="A concise content plan with an outline, audience analysis, SEO keywords, and key resources (under 100 words).",
                agent=planner,
            )

            write_task = Task(
                description=(
                    f"1. Draft a blog post on {topic} using the content plan."
                    "2. Incorporate SEO keywords."
                    "3. Use engaging titles and structure: intro, body, conclusion."
                    "4. Proofread for errors and brand voice."
                ),
                expected_output="A well-written blog post in markdown (under 400 words), ready for publication, with distinct sections.",
                agent=writer,
                context=[plan_task]
            )

            edit_task = Task(
                description="Proofread the blog post for grammar, style, and brand voice.",
                expected_output="A final, proofread blog post in markdown format, ready for publication.",
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

                st.success("Your blog post has been generated!")
                st.markdown(result)

            except Exception as e:
                st.error(f"An error occurred during the kickoff process: {e}")

