
import os
import asyncio
from aiohttp import web
from pyrogram import Client
from lazybot import LazyPrincessBot
from lazybot.clients import initialize_clients
from database.ia_filterdb import Media
from database.users_chats_db import db
from utils import temp
import logging
import pytz
from datetime import date, datetime
from Script import script
from plugins import web_server

# Define webhook URL & port
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST", "https://comparable-orel-aerofilms-bd14adfe.koyeb.app")  # Change to your actual domain
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
PORT = int(os.getenv("PORT", 8443))  # Change if needed

async def start_bot():
    print("\nStarting Lucy Bot with Webhook Mode")
    
    bot_info = await LazyPrincessBot.get_me()
    LazyPrincessBot.username = bot_info.username

    await initialize_clients()
    
    # Get banned users and chats
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    await Media.ensure_indexes()
    
    me = await LazyPrincessBot.get_me()
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    LazyPrincessBot.username = '@' + me.username
    
    logging.info(f"{me.first_name} started using Pyrogram Webhooks.")

    # Send bot restart message
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await LazyPrincessBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))

    # Set webhook
    await LazyPrincessBot.set_webhook(WEBHOOK_URL)

    # Start aiohttp web server
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, webhook_handler)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()

    await asyncio.Event().wait()  # Keep the bot running

# Handle incoming webhook updates
async def webhook_handler(request):
    update = await request.json()
    await LazyPrincessBot.process_update(update)
    return web.Response()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_bot())
    except KeyboardInterrupt:
        logging.info("Shutting down webhook bot. Goodbye! 👋")
