from social_media_agent import get_transcript

if __name__ == "__main__":
    video_id = "8RvAKRoIDqU"  # Example video ID
    try:
        transcript = get_transcript(video_id, ["iw", "en"])
        print("Transcript fetched successfully:")
        print(transcript)
    except Exception as e:
        print(f"Failed to fetch transcript: {e}")
