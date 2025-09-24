# -------------------------------------
# Step 0: Import pacjages and modules
# -------------------------------------
import asyncio
import os
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import WebshareProxyConfig
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from agents import Agent, Runner, WebSearchTool, function_tool, ItemHelpers, trace
from openai import OpenAI
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import List
# -------------------------------------
# Step 1: Get OpenAI API key
# -------------------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -------------------------------------
# Step 2: Define tools for agents
# -------------------------------------

# Tool: Generate social media content from transcript


@function_tool
def generate_content(video_transcript: str, social_media_platform: str):
    print(f"Generating social media content for {social_media_platform}...")

    # Initialize OpenAI client
    client = OpenAI(api_key=OPENAI_API_KEY)

    # Generate contnt
    response = client.responses.create(
        model="gpt-4o",
        input=[
            {"role": "user",
                "content": f"Here is a new video transcript:\n{video_transcript}\n\n"
                f"Generate a social media post on my {social_media_platform} based on my provided video transcript.\n"}
        ],
        max_output_tokens=100

    )
    return response.output_text


# -------------------------------------
# Step 3: Define agent (content writer agent)
# -------------------------------------

@dataclass
class Post:
    platform: str
    content: str


content_writer_agent = Agent(
    name="Content write agent",
    instructions="""
    You are a talented content writer who writes engaging, humorous, informative and 
                    highly readable social media posts. 
                    You will be given a video transcript and social media platforms. 
                    You will generate a social media post based on the video transcript 
                    and the social media platforms.
                    You may search the web for up-to-date information on the topic and 
                    fill in some useful details if needed.""",
    model="gpt-4o-mini",
    tools=[generate_content,
           WebSearchTool()],
    output_type=List[Post]

)

# -------------------------------------
# Step 4: Define helper functions
# -------------------------------------
# fetch trascript from a youtube video useing the video id


def get_transcript(video_id: str, languages: list = None) -> str:
    """
    Fetches the transcript of a YouTube video using its video ID.

    Args:
        video_id (str): The ID of the YouTube video.

    Returns:
        str: The transcript of the video as a single string.

    Raises:
        Exception: If the transcript cannot be fetched.
    """
    if languages is None:
        languages = ["en"]

    try:
        # Use the Youtube transcript API
        ytt_api = YouTubeTranscriptApi(
            proxy_config=WebshareProxyConfig(
                proxy_username="rytewsal",
                proxy_password="q3i4qcuwd610"
            )
        )

        fetched_transcript = ytt_api.fetch(video_id, languages)

        # More efficient way to concatenate all text snippets
        transcript_text = " ".join(
            snippet.text for snippet in fetched_transcript)

        return transcript_text

    except TranscriptsDisabled:
        print(f"Transcripts are disabled for the video with ID {video_id}.")
        raise

    except NoTranscriptFound:
        print(f"No transcript found for the video with ID {video_id}.")
        raise

    except VideoUnavailable:
        print(f"The video with ID {video_id} is unavailable.")
        raise

    except Exception as e:
        # Catch-all for any other exceptions
        print(
            f"An unexpected error occurred while fetching the transcript for video ID {video_id}: {e}")
        raise

# -------------------------------------
# Step 5: Run the agent
# -------------------------------------


async def main():
    video_id = "OZ5OZZZ2cvk"
    transcript = get_transcript(video_id)

    msg = f"Generate a LinkedIn post and an Instagram caption based on this video transcript: {transcript}"

    # Package input for the agent
    input_items = [{"content": msg, "role": "user"}]

    # Run content writer agent
    # Add trace to see the agent's execution steps
    # You can check the trace on https://platform.openai.com/traces
    with trace("Writing content"):
        result = await Runner.run(content_writer_agent, input_items)
        output = ItemHelpers.text_message_outputs(result.new_items)
        print("Generated Post:\n", output)

if __name__ == "__main__":
    asyncio.run(main())
