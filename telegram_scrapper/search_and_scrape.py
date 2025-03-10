import os
import re
import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest

# Replace with your credentials
API_ID = 21562607          # Your API ID
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2"  # Your API Hash
KEYWORD = "dune movie"     # Keyword to search for channels/groups

# Base directory for JSON output
BASE_DIR = "scraped_data"
os.makedirs(BASE_DIR, exist_ok=True)

# Initialize the Telegram client (authentication is handled automatically)
client = TelegramClient("session_keyword_scraper", API_ID, API_HASH)

# Data structure to hold all scraped data
scraped_data = {"channels": []}

with client:
    # 1. Searching for Public Chats by Keyword
    result = client(SearchRequest(q=KEYWORD, limit=5))
    
    for chat in result.chats:
        channel_info = {}
        channel_title = getattr(chat, 'title', 'No_Title')
        channel_info["title"] = channel_title
        channel_info["username"] = getattr(chat, 'username', None)
        
        # 2. Optionally join the channel/group if required
        try:
            client(JoinChannelRequest(chat))
            channel_info["joined"] = True
        except Exception as e:
            channel_info["joined"] = False
            channel_info["join_error"] = str(e)
        
        # 3. Get Channel/Group Membership and Engagement Metadata
        try:
            full = client(GetFullChannelRequest(chat))
            channel_info["member_count"] = (full.full_chat.participants_count 
                                            if hasattr(full.full_chat, 'participants_count') 
                                            else None)
        except Exception as e:
            channel_info["member_count"] = None
            channel_info["full_info_error"] = str(e)
        
        # Prepare a list for posts
        channel_info["posts"] = []
        
        # 4. Scrape Messages and Associated Data
        for message in client.iter_messages(chat, limit=5):  # Adjust limit as needed
            post = {}
            post["date"] = str(message.date)
            post["views"] = message.views
            post["message_text"] = message.text
            post["urls"] = re.findall(r'(https?://\S+)', message.text) if message.text else []
            post["geo"] = str(message.geo) if message.geo else None

            # Check for reactions (if available)
            if hasattr(message, 'reactions'):
                try:
                    post["reactions"] = message.reactions.stringify() if hasattr(message.reactions, "stringify") else str(message.reactions)
                except Exception:
                    post["reactions"] = str(message.reactions)
            else:
                post["reactions"] = None

            # Check for replies (if available)
            if hasattr(message, 'replies') and message.replies:
                try:
                    post["replies"] = message.replies.to_dict() if hasattr(message.replies, "to_dict") else str(message.replies)
                except Exception:
                    post["replies"] = str(message.replies)
            else:
                post["replies"] = None

            # Instead of downloading media, store a media link if available.
            # For public channels (with a username) you can build a permalink for the message.
            if message.media and getattr(chat, 'username', None):
                post["media"] = f"https://t.me/{chat.username}/{message.id}"

            # Append this post to the channel's posts list
            channel_info["posts"].append(post)
        
        # 5. (Optional) Scrape Channel/Group Member List
        try:
            participants = client.get_participants(chat, limit=100)
            members = []
            for user in participants:
                members.append({
                    "user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                })
            channel_info["members"] = members
        except Exception as e:
            channel_info["members"] = []
            channel_info["members_error"] = str(e)
        
        # Append this channel's data to our main scraped_data list
        scraped_data["channels"].append(channel_info)

# Save all collected data to a single JSON file
json_path = os.path.join(BASE_DIR, "scraped_data.json")
with open(json_path, "w", encoding="utf-8") as jf:
    json.dump(scraped_data, jf, ensure_ascii=False, indent=4)

print(f"Scraping complete! Data saved to {json_path}")
