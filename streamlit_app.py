import streamlit as st
import asyncio
import json
from social_media_agent import get_transcript, content_writer_agent, Runner, ItemHelpers, trace

st.set_page_config(page_title="Social Media Content Writer", layout="centered")
st.title("📹 Social Media Content Writer Agent")


SOCIAL_MEDIA_OPTIONS = [
    "LinkedIn",
    "Instagram",
    "Twitter",
    "Facebook",
    "TikTok",
    "YouTube Shorts",
    "Threads",
    "Other"
]

with st.form("input_form"):
    video_id = st.text_input("YouTube Video ID", "")
    selected_platforms = st.multiselect(
        "Select social media platforms to generate content for:",
        SOCIAL_MEDIA_OPTIONS,
        default=["LinkedIn", "Instagram"]
    )
    query = st.text_area(
        "Describe what you want (optional)",
        "Generate a post for each selected platform."
    )
    submitted = st.form_submit_button("Generate Content")

if submitted and video_id and selected_platforms:
    with st.spinner("Fetching transcript and generating content..."):
        try:
            transcript = get_transcript(video_id)
            results = {}
            for platform in selected_platforms:
                msg = f"{query}\nPlatform: {platform}\nVideo transcript: {transcript}"
                input_items = [{"content": msg, "role": "user"}]
                async def run_agent():
                    with trace(f"Writing content for {platform}"):
                        result = await Runner.run(content_writer_agent, input_items)
                        return result.new_items
                agent_items = asyncio.run(run_agent())
                # agent_items is a list of Post dataclass objects, extract platform and content fields
                if isinstance(agent_items, list) and len(agent_items) > 0:
                    # Try to extract platform and content from dataclass or dict
                    item = agent_items[0]
                    plat = getattr(item, 'platform', platform)
                    response_from_openAI = json.loads(item.raw_item.content[0].text)["response"][0]
                    content = getattr(item, 'content', response_from_openAI["content"])
                    if content is None and isinstance(item, dict):
                        plat = item.get('platform', platform)
                        content = item.get('content', str(item))
                    elif content is None:
                        content = str(item)
                else:
                    plat = platform
                    content = str(agent_items)
                results[platform] = {"platform": plat, "content": content}
            st.success("Content generated!")
            st.markdown("### Output by Platform:")
            for platform in selected_platforms:
                st.subheader(results[platform]["platform"])
                st.markdown(f"**Platform:** {results[platform]['platform']}")
                st.markdown(f"**Content:** {results[platform]['content']}")
                st.code(results[platform]["content"], language="markdown")
        except Exception as e:
            st.error(f"Error: {e}")
else:
    st.info("Enter a YouTube video ID, select at least one platform, then click 'Generate Content'.")
