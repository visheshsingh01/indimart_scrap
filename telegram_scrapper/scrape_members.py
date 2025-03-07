from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
import pandas as pd

API_ID = 21562607
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2"
GROUP_USERNAME = "https://t.me/FXWOLF_00"

client = TelegramClient("session_name", API_ID, API_HASH)

with client:
    participants = client(GetParticipantsRequest(
        GROUP_USERNAME, ChannelParticipantsSearch(""), 0, 100, hash=0
    ))

    data = []
    for user in participants.users:
        data.append([user.id, user.username, user.first_name, user.last_name])

    df = pd.DataFrame(data, columns=["User ID", "Username", "First Name", "Last Name"])
    df.to_csv("telegram_members.csv", index=False)

print("✅ Members saved to telegram_members.csv!")
