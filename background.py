import asyncio
import os
from aiohttp import web


async def handle(request):
    return web.Response(text="Bot is alive!")


async def keep_alive_async():
    """Запускает веб-сервер для "живучести" бота на хостинге"""
    app = web.Application()
    app.router.add_get("/", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    # Use PORT from environment if provided by host (e.g., Railway), otherwise default to 8080
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"🌐 Web server started on port {port}")


def keep_alive():
    """Wrapper for async keep_alive - schedules it as a background task"""
    # This will be called from async context, so we just schedule the coroutine
    asyncio.create_task(keep_alive_async())

