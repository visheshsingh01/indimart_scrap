from telethon.sync import TelegramClient

# Replace with your credentials
API_ID = 21562607  # Your API ID
API_HASH = "a6dba1cf80b2a8b273222ac6b5e551e2"
PHONE_NUMBER = "+919354218809"  # Your Telegram phone number

client = TelegramClient("session_name", API_ID, API_HASH)

client.connect()

if not client.is_user_authorized():
    client.send_code_request(PHONE_NUMBER)
    code = input("Enter the code sent to your Telegram: ")
    client.sign_in(PHONE_NUMBER, code)

print("✅ Login successful! Session saved.")
client.disconnect()
