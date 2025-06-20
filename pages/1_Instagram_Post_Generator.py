import streamlit as st
from crewai import Agent, Task, Crew
from crewai_tools import tool
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI

# --- Page Config ---
st.set_page_config(page_title="Instagram Post Generator", page_icon="📸")

st.title("📸 Instagram Post Generator")
st.markdown("This tool uses AI agents to generate a caption and an image for an Instagram post.")

# --- Tool Definition ---
@tool
def generate_image(query: str) -> str:
    """
    Generates an image using DALL-E based on chapter content and character details.
    """
    # This function is now designed to be called within the Streamlit app context
    # where the API key is already set as an environment variable.
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Create a realistic image of: {query}. Style: Focus on lifelike details, accurate lighting, and natural textures, with a realistic color palette. The scene should capture the true essence of the description, ensuring it looks as if it could exist in the real world.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        image_url = response.data[0].url
        return image_url
    except Exception as e:
        st.error(f"Error generating image: {e}")
        return "Failed to generate image."


# --- Streamlit UI ---
with st.sidebar:
    st.markdown("This tool uses AI agents to generate a caption and an image for an Instagram post")

theme = st.text_input("Enter the theme for your Instagram post:", placeholder="e.g., Summer vacation in the Maldives")

if st.button("Generate Instagram Post"):
    if not theme:
        st.error("Please enter a theme for the post.")
    else:
        openai_api_key = st.secrets["openai_api_key"]
        os.environ['OPENAI_API_KEY'] = openai_api_key
        llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=openai_api_key)

        with st.spinner("AI agents are crafting your post..."):
            # --- Agents ---
            caption_agent = Agent(
                name='Caption & Hashtag Strategist',
                role='Social Media Expert',
                goal='Create engaging captions and effective hashtag strategies',
                backstory=(
                    "You're a social media copywriter specializing in Instagram content. "
                    "Your goal is to craft engaging captions that resonate emotionally or humorously with audiences on {theme}, "
                    "while ensuring discoverability through relevant hashtags. "
                    "You analyze trends and write content that aligns with the visual's intent and the creator's brand voice. "
                    "Your work is based on the image generated by the Visual Content Creator."
                ),
                allow_delegation=False,
                verbose=True,
                llm=llm
            )

            visual_agent = Agent(
               name='Visual Content Creator',
               role='AI Image Generator',
               goal="Generate visually compelling and on-brand images for Instagram content based on the theme: {theme}",
              backstory=(
                  "You're an AI-based visual artist creating Instagram-ready images. "
                  "You work with the Caption & Hashtag Strategist, who builds captions around your visuals. "
                  "Your images attract attention, convey mood, and support the messaging. "
                  "You use DALL·E to create realistic, vibrant, and aesthetically pleasing images that don't look AI-generated."
              ),
               verbose=True,
               llm=llm,
               tools=[generate_image],
               allow_delegation=False
            )

            # --- Tasks ---
            task_captions = Task(
                  description=f"Generate a catchy Instagram caption and a set of 3-5 trending hashtags for the theme: '{theme}'.",
                  agent=caption_agent,
                  expected_output="A single catchy caption and a list of 3-5 relevant hashtags."
            )

            task_image = Task(
                 description=f"Generate a beautiful, natural-looking Instagram-style visual based on the theme: '{theme}'. The image should not look AI-generated.",
                 agent=visual_agent,
                 expected_output='A high-quality image URL matching the theme description and tone.',
            )

            # --- Crew ---
            crew = Crew(
              agents=[caption_agent, visual_agent],
              tasks=[task_image, task_captions], # Run image task first so caption can be based on it
              verbose=2,
            )

            try:
                result = crew.kickoff(inputs={"theme": theme})

                st.success("Your Instagram post has been generated!")

                # The final output from the sequential crew is the output of the last task
                # In this setup, task_captions is the last task.
                # However, CrewAI returns the output of all tasks in the `tasks_output` attribute
                
                image_output = crew.tasks[0].output.exported_output
                caption_output = crew.tasks[1].output.exported_output

                st.subheader("Generated Image")
                if image_output and image_output.startswith("http"):
                    st.image(image_output, caption="AI-Generated Image")
                else:
                    st.warning("Could not retrieve the generated image.")
                    st.write(image_output)


                st.subheader("Generated Caption & Hashtags")
                st.markdown(caption_output)

            except Exception as e:
                st.error(f"An error occurred during the kickoff process: {e}")
