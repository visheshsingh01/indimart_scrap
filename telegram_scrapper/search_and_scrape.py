import os
import re
from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetFullChannelRequest, JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import ChannelParticipantsSearch

# Replace with your credentials
API_ID = 21562607          # Your API ID
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2" # Your API Hash
KEYWORD = "crypto"         # Keyword to search for channels/groups

# Base directory for storing scraped data
BASE_DIR = "scraped_data"
os.makedirs(BASE_DIR, exist_ok=True)

# Initialize the Telegram client (authentication is handled automatically)
client = TelegramClient("session_keyword_scraper", API_ID, API_HASH)

with client:
    # ---------------------------
    # 1. Searching for Public Chats by Keyword
    # ---------------------------
    result = client(SearchRequest(q=KEYWORD, limit=5))
    
    for chat in result.chats:
        channel_title = getattr(chat, 'title', 'No_Title')
        safe_title = "".join(c for c in channel_title if c.isalnum() or c in " -_").rstrip()
        
        # Create a folder for this channel
        channel_dir = os.path.join(BASE_DIR, safe_title)
        os.makedirs(channel_dir, exist_ok=True)
        print(f"\nFound Chat: {channel_title}")

        # ---------------------------
        # 2. Optionally join the channel/group if required
        # ---------------------------
        try:
            client(JoinChannelRequest(chat))
            print(f"Joined {channel_title}")
        except Exception as e:
            print(f"Could not join {channel_title}: {e}")

        # ---------------------------
        # 3. Get Channel/Group Membership and Engagement Metadata
        # ---------------------------
        try:
            full = client(GetFullChannelRequest(chat))
            member_count = full.full_chat.participants_count if hasattr(full.full_chat, 'participants_count') else "N/A"
            print(f"Member Count for {channel_title}: {member_count}")
        except Exception as e:
            print(f"Could not get full channel info for {channel_title}: {e}")

        # ---------------------------
        # 4. Scrape Messages and Associated Data
        # ---------------------------
        messages_file = os.path.join(channel_dir, "messages.txt")
        with open(messages_file, "w", encoding="utf-8") as text_file:
            for message in client.iter_messages(chat, limit=5):  # Adjust limit as needed
                # Write basic metadata (timestamp, views, etc.)
                text_file.write(f"Date: {message.date} | Views: {message.views}\n")
                
                # Write the message text if present
                if message.text:
                    text_file.write(f"Message: {message.text}\n")
                    
                    # Extract and log any URLs from the message text
                    urls = re.findall(r'(https?://\S+)', message.text)
                    if urls:
                        text_file.write(f"URLs: {urls}\n")
                
                # Log geolocation if available
                if message.geo:
                    text_file.write(f"Geo: {message.geo}\n")
                
                text_file.write("-" * 50 + "\n")
                
                # Download media if present and log associated text with it
                if message.media:
                    media_path = message.download_media(file=channel_dir)
                    if media_path:
                        print(f"Downloaded media file: {media_path}")
                        # Save associated text with the media file if any
                        if message.text:
                            base_name = os.path.splitext(os.path.basename(media_path))[0]
                            media_text_file = os.path.join(channel_dir, f"{base_name}.txt")
                            with open(media_text_file, "w", encoding="utf-8") as mf:
                                mf.write(f"Date: {message.date}\nMessage: {message.text}\n")
                    else:
                        print("Media download returned None, skipping associated text.")

        # ---------------------------
        # 5. (Optional) Scrape Channel/Group Member List
        # ---------------------------
        try:
            participants = client.get_participants(chat, limit=100)
            members_file = os.path.join(channel_dir, "members.txt")
            with open(members_file, "w", encoding="utf-8") as mf:
                for user in participants:
                    mf.write(f"User ID: {user.id} | Username: {user.username} | Name: {user.first_name} {user.last_name}\n")
            print(f"Scraped {len(participants)} members for {channel_title}")
        except Exception as e:
            print(f"Could not scrape members for {channel_title}: {e}")
