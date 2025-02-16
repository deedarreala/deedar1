import streamlit as st
import requests
from datetime import datetime, timedelta

# YouTube API Key
API_KEY = "AIzaSyDGm4W32Nn2j27iqAxSYur4YZBq3_bG4pI"
YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEO_URL = "https://www.googleapis.com/youtube/v3/videos"
YOUTUBE_CHANNEL_URL = "https://www.googleapis.com/youtube/v3/channels"

st.title("YouTube Viral Topics Tool")

days = st.number_input("Enter Days to Search (1-30):", min_value=1, max_value=30, value=5)

keywords = [
    "Affair Relationship Stories", "Reddit Cheating", "Open Marriage", "Exposed Wife", 
    "Cheating Story Real", "True Cheating Story", "Reddit Marriage", "Cheat Exposed"
]

if st.button("Fetch Data"):
    try:
        start_date = (datetime.utcnow() - timedelta(days=int(days))).isoformat("T") + "Z"
        all_results = []

        for keyword in keywords:
            st.write(f"🔍 Searching for keyword: **{keyword}**")

            search_params = {
                "part": "snippet",
                "q": keyword,
                "type": "video",
                "order": "viewCount",
                "publishedAfter": start_date,
                "maxResults": 5,
                "key": API_KEY,
            }

            response = requests.get(YOUTUBE_SEARCH_URL, params=search_params)
            data = response.json()

            if "error" in data:
                st.error(f"❌ API Error: {data['error'].get('message', 'Unknown error')}")
                break  

            if "items" not in data or not data["items"]:
                st.warning(f"⚠ No videos found for keyword: {keyword}")
                continue

            video_ids = [video["id"]["videoId"] for video in data["items"] if "id" in video and "videoId" in video["id"]]
            channel_ids = [video["snippet"]["channelId"] for video in data["items"] if "snippet" in video and "channelId" in video["snippet"]]

            if not video_ids or not channel_ids:
                st.warning(f"⚠ Skipping keyword: {keyword} due to missing data.")
                continue

            stats_response = requests.get(YOUTUBE_VIDEO_URL, params={"part": "statistics", "id": ",".join(video_ids), "key": API_KEY})
            stats_data = stats_response.json()

            if "items" not in stats_data:
                st.warning(f"⚠ Failed to fetch video statistics for: {keyword}")
                continue

            channel_response = requests.get(YOUTUBE_CHANNEL_URL, params={"part": "statistics", "id": ",".join(channel_ids), "key": API_KEY})
            channel_data = channel_response.json()

            if "items" not in channel_data:
                st.warning(f"⚠ Failed to fetch channel statistics for: {keyword}")
                continue

            for video, stat, channel in zip(data["items"], stats_data["items"], channel_data["items"]):
                title = video["snippet"].get("title", "N/A")
                description = video["snippet"].get("description", "")[:200]
                video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                views = int(stat["statistics"].get("viewCount", 0))
                subs = int(channel["statistics"].get("subscriberCount", 0))

                if subs < 3000:
                    all_results.append({
                        "Title": title,
                        "Description": description,
                        "URL": video_url,
                        "Views": views,
                        "Subscribers": subs
                    })

        if all_results:
            st.success(f"✅ Found {len(all_results)} trending videos!")
            st.dataframe(all_results)  # Improved UI
        else:
            st.warning("⚠ No results found for channels with fewer than 3,000 subscribers.")

    except Exception as e:
        st.error(f"🚨 Error occurred: {e}")
