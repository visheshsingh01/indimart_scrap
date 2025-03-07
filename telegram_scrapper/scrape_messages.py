from telethon.sync import TelegramClient
import pandas as pd

API_ID = 21562607
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2"
CHANNEL_USERNAME = "https://t.me/FXWOLF_00"  # Example: "@pythonhub"

client = TelegramClient("session_name", API_ID, API_HASH)

with client:
    messages = client.get_messages(CHANNEL_USERNAME, limit=1000)

    data = []
    for msg in messages:
        data.append([msg.sender_id, msg.date, msg.text])

    df = pd.DataFrame(data, columns=["Sender ID", "Date", "Message"])
    df.to_csv("telegram_messages.csv", index=False)

print("✅ Messages saved to telegram_messages.csv!")
