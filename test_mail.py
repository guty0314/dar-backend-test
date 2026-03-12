import asyncio
from dotenv import load_dotenv
load_dotenv()

from services.email_service import send_user_credentials

async def main():
    try:
        await send_user_credentials(
            email="btv09029@gmail.com",
            username="test_user",
            password="test1234"
        )
        print("✅ Mail enviado correctamente")
    except Exception as e:
        print("❌ Error:", e)

asyncio.run(main())