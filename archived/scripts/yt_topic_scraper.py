import os
import csv
import time
from googleapiclient.discovery import build


API_KEY = "API"

youtube = build("youtube", "v3", developerKey=API_KEY)
MAX_RESULTS = 50  
PAUSE_BETWEEN_CALLS = 1 

def scrape_videos_for_topic(topic, max_videos=1000):
    print(f"\n🚀 Scraping topic: {topic} (target: {max_videos} videos)")

    collected = 0
    next_page_token = None
    seen_video_ids = set()

    output_file = f"datasets/{topic.replace(' ', '_').lower()}_videos.csv"
    os.makedirs("datasets", exist_ok=True)

    
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                seen_video_ids.add(row["video_id"])

    with open(output_file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "video_id", "title", "url", "description",
            "publish_date", "channel_title", "view_count",
            "duration", "tags", "topic"
        ])
        if f.tell() == 0:
            writer.writeheader()

        while collected < max_videos:
            search_request = youtube.search().list(
                q=topic,
                type="video",
                part="id,snippet",
                maxResults=MAX_RESULTS,
                pageToken=next_page_token
            )
            search_response = search_request.execute()

            video_ids = [
                item["id"]["videoId"] for item in search_response["items"]
                if item["id"]["kind"] == "youtube#video"
            ]
            filtered_ids = [vid for vid in video_ids if vid not in seen_video_ids]

            if not filtered_ids:
                next_page_token = search_response.get("nextPageToken")
                if not next_page_token:
                    print("✅ No further videos found, stopping.")
                    break
                continue

            videos_request = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(filtered_ids)
            )
            videos_response = videos_request.execute()

            for item in videos_response["items"]:
                video_id = item["id"]
                snippet = item["snippet"]
                statistics = item.get("statistics", {})
                content_details = item.get("contentDetails", {})

                writer.writerow({
                    "video_id": video_id,
                    "title": snippet["title"],
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "description": snippet.get("description", ""),
                    "publish_date": snippet.get("publishedAt", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "view_count": statistics.get("viewCount", "0"),
                    "duration": content_details.get("duration", ""),
                    "tags": "|".join(snippet.get("tags", [])),
                    "topic": topic
                })
                collected += 1
                seen_video_ids.add(video_id)

                if collected >= max_videos:
                    break

            print(f"✅ Collected: {collected}/{max_videos} for {topic}")

            next_page_token = search_response.get("nextPageToken")
            if not next_page_token:
                break

            time.sleep(PAUSE_BETWEEN_CALLS)

    print(f"🎉 Finished scraping {collected} videos for {topic}")

if __name__ == "__main__":
    topics = [
        # "Introduction to Python",
        # "Data Structures",
        # "Object Oriented Programming",
        # "Machine Learning",
        # "Deep Learning",
        # "Natural Language Processing",
        "Computer Vision",
        "Data Science",
        "Flask",
        "Django",
        "Data Analysis",
        "TensorFlow",
        "PyTorch",
        "Linear Regression",
        "Decision Trees"
    ]

    for topic in topics:
        scrape_videos_for_topic(topic, max_videos=1000)
