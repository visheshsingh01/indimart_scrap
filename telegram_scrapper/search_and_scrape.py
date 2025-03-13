import os
import re
import json
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import MessageEntityMention, MessageEntityMentionName
from telethon.tl.functions.users import GetFullUserRequest

# Replace with your credentials
API_ID = 21562607          # Your API ID
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2"  # Your API Hash
KEYWORD = "Diwakar"        # Keyword to search

# Base directory for scraped data
BASE_DIR = "scraped_data"
os.makedirs(BASE_DIR, exist_ok=True)
MEDIA_DIR = os.path.join(BASE_DIR, "media")
os.makedirs(MEDIA_DIR, exist_ok=True)

# Initialize Telegram client
client = TelegramClient("session_keyword_scraper", API_ID, API_HASH)

# Data structure to hold scraped data
scraped_data = {
    "keyword": KEYWORD,
    "channels": [],
    "groups": [],
    "users": []
}

with client:
    # Search for public chats and users
    result = client(SearchRequest(q=KEYWORD, limit=10))
    
    for chat in result.chats:
        chat_info = {
            "title": getattr(chat, 'title', 'No_Title'),
            "username": getattr(chat, 'username', None),
            "is_channel": chat.broadcast if hasattr(chat, 'broadcast') else False,
            "mentions": []  # Aggregate mentions for this channel if keyword appears
        }
        category = "channels" if chat_info["is_channel"] else "groups"
        
        # Try joining the chat
        try:
            client(JoinChannelRequest(chat))
            chat_info["joined"] = True
        except Exception as e:
            chat_info["joined"] = False
            chat_info["join_error"] = str(e)
        
        # Get member count
        try:
            full = client(GetFullChannelRequest(chat))
            chat_info["member_count"] = getattr(full.full_chat, 'participants_count', None)
        except Exception as e:
            chat_info["member_count"] = None
            chat_info["full_info_error"] = str(e)
        
        # Scrape messages
        chat_info["posts"] = []
        for message in client.iter_messages(chat, limit=10):  # Adjust limit as needed
            post = {
                "date": str(message.date),
                "views": message.views,
                "message_text": message.text,
                "urls": re.findall(r'(https?://\S+)', message.text) if message.text else [],
                "geo": str(message.geo) if message.geo else None,
                "reactions": str(message.reactions) if hasattr(message, 'reactions') else None,
                "replies": str(message.replies) if hasattr(message, 'replies') else None,
                "media": None
            }
            
            # Mention-based logic: only if the post text contains the keyword (case-insensitive)
            if message.text and KEYWORD.lower() in message.text.lower() and message.entities:
                mentions = []
                for entity in message.entities:
                    if isinstance(entity, (MessageEntityMention, MessageEntityMentionName)):
                        # Extract the mention text using offset and length
                        mention_text = message.text[entity.offset: entity.offset + entity.length]
                        mentions.append(mention_text)
                if mentions:
                    # Add these mentions to the channel-level "mentions" list
                    chat_info["mentions"].extend(mentions)
                    # Also store them in the post itself if you want
                    post["mentions"] = mentions
            
            # Instead of downloading media, store a media link if available (for public channels)
            if message.media and getattr(chat, 'username', None):
                post["media"] = f"https://t.me/{chat.username}/{message.id}"
            
            chat_info["posts"].append(post)
        
        scraped_data[category].append(chat_info)
    
    # Search for users
    for user in result.users:
        full_user = client(GetFullUserRequest(user.id))
        user_info = {
            "user_id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone": user.phone,
            "bio": getattr(full_user.full_user, 'about', None),
            "profile_picture": None
        }
        
        # Download profile picture (if available)
        profile_pic_path = os.path.join(MEDIA_DIR, f"profile_{user.id}.jpg")
        profile_pic = client.download_profile_photo(user, file=profile_pic_path)
        if profile_pic:
            user_info["profile_picture"] = profile_pic
        
        scraped_data["users"].append(user_info)
    
# Save data to JSON
json_path = os.path.join(BASE_DIR, "scraped_data.json")
with open(json_path, "w", encoding="utf-8") as jf:
    json.dump(scraped_data, jf, ensure_ascii=False, indent=4)

print(f"Scraping complete! Data saved to {json_path}")
