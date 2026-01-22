import asyncio
import logging
from pathlib import Path
from typing import Iterable

import discord
from discord.ext import commands

from bot.config import load_config
from bot.storage import Storage


COG_EXTENSIONS: Iterable[str] = (
    "bot.cogs.admin",
    "bot.cogs.info",
    "bot.cogs.fun",
    "bot.cogs.community",
    "bot.cogs.embeds",
    "bot.cogs.suggestions",
    "bot.cogs.tickets",
    "bot.cogs.premium",
)


async def load_cogs(bot: commands.Bot) -> None:
    for extension in COG_EXTENSIONS:
        await bot.load_extension(extension)


async def setup_bot() -> commands.Bot:
    config = load_config()

    logging.basicConfig(
        level=getattr(logging, config.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    intents = discord.Intents.default()
    intents.message_content = True
    intents.members = True

    bot = commands.Bot(command_prefix=config.prefix, intents=intents)
    bot.config = config  # type: ignore[attr-defined]
    bot.storage = Storage(path=Path(config.data_dir) / "storage.json")  # type: ignore[attr-defined]
    bot.storage.load()  # type: ignore[attr-defined]

    @bot.event
    async def on_ready() -> None:
        logging.getLogger("bot").info("Logged in as %s", bot.user)

    await load_cogs(bot)
    await bot.tree.sync()
    return bot


async def main() -> None:
    bot = await setup_bot()
    config = load_config()
    await bot.start(config.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger("bot").info("Shutting down")
