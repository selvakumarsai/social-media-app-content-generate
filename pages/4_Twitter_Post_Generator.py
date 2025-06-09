import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
import os
from langchain_openai import ChatOpenAI

# --- Page Config ---
st.set_page_config(page_title="Twitter Post Generator", page_icon="🐦")

st.title("🐦 Twitter Post Generator")
st.markdown("This tool uses AI agents to generate a tweet on any topic. Enter your API keys and a topic to get started.")

# --- Streamlit UI ---
with st.sidebar:
    st.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")
   
topic = st.text_input("Enter the topic for your tweet:", placeholder="e.g., The latest news on electric cars")

if st.button("Generate Tweet"):
    if not topic:
        st.error("Please enter a topic for the tweet.")
    else:
        openai_api_key = st.secrets["openai_api_key"]
        os.environ['OPENAI_API_KEY'] = openai_api_key
        serper_api_key = st.secrets["serper_api_key"]
        os.environ['SERPER_API_KEY'] = serper_api_key
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=openai_api_key)
        search_tool = SerperDevTool()
        scrape_tool = ScrapeWebsiteTool()

        with st.spinner("AI agents are crafting your tweet..."):
            # --- Agents ---
            tweet_agent = Agent(
                name='Tweet Strategist',
                role='Social Media Expert',
                goal=f"Write concise, punchy tweets on {topic} that resonate with the target audience and encourage high engagement.",
                backstory=(
                    f"You are a seasoned Twitter expert creating a tweet on {topic}. "
                    "You specialize in distilling complex ideas into sharp, witty, or emotionally resonant tweets under 280 characters. "
                    "You work with the Hashtag Analyst to ensure your tweets are discoverable."
                ),
                tools=[search_tool, scrape_tool],
                allow_delegation=False,
                llm=llm,
                verbose=True
            )

            trend_agent = Agent(
                name='Hashtag & Trending Topic Analyst',
                role='Trend Analyst',
                goal="Identify high-traffic hashtags to enhance the discoverability of tweets created by the Tweet Strategist.",
                backstory=(
                    "You're a data-savvy analyst monitoring Twitter trends and hashtag performance. "
                    "You support the Tweet Strategist by ensuring their content aligns with trending themes and uses hashtags that maximize reach."
                ),
                allow_delegation=False,
                tools=[search_tool, scrape_tool],
                llm=llm,
                verbose=True
            )

            # --- Tasks ---
            task_tweets = Task(
                description=f"Generate a concise, impactful tweet on {topic} that hooks readers and aligns with current engagement styles. Attach a relevant, functional link.",
                agent=tweet_agent,
                expected_output="A concise and impactful tweet (under 280 characters) with a relevant, functional link."
            )

            task_trending = Task(
                description="Analyze Twitter trends for the tweet created by the tweet agent and suggest relevant hashtags and themes.",
                agent=trend_agent,
                expected_output="A list of 3-5 relevant hashtags to append to the tweet.",
                context=[task_tweets]
            )

            # --- Crew ---
            twitter_crew = Crew(
                agents=[tweet_agent, trend_agent],
                tasks=[task_tweets, task_trending],
                verbose=2
            )

            try:
                result = twitter_crew.kickoff(inputs={"topic": topic})
                st.success("Your tweet has been generated!")
                st.markdown("### Final Tweet:")
                st.markdown(result)
                
            except Exception as e:
                st.error(f"An error occurred during the kickoff process: {e}")

