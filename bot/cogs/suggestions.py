from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from bot.localization import Localizer


class Suggestions(commands.Cog):
    """Suggestion system with voting."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def _guild_config(self, guild_id: int) -> dict:
        guild_data = self.bot.storage.guild(guild_id)  # type: ignore[attr-defined]
        guild_data.setdefault("suggestions", {"channel_id": None, "next_id": 1, "items": {}})
        return guild_data

    def _localizer(self, guild_id: int) -> Localizer:
        lang = self._guild_config(guild_id).get("language", "en")
        return Localizer(language=lang)

    @commands.hybrid_command(name="setsuggestions", description="Set the suggestions channel.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_suggestions(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["suggestions"]["channel_id"] = channel.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Suggestions channel set to {channel.mention}.")

    @commands.hybrid_command(name="suggest", description="Send a suggestion for the server.")
    async def suggest(self, ctx: commands.Context, *, text: str) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        channel_id = guild_config["suggestions"].get("channel_id")
        if not channel_id:
            await ctx.send("Suggestions channel not configured.")
            return

        channel = ctx.guild.get_channel(int(channel_id))
        if not isinstance(channel, discord.TextChannel):
            await ctx.send("Suggestions channel is not available.")
            return

        suggestion_id = guild_config["suggestions"]["next_id"]
        guild_config["suggestions"]["next_id"] = suggestion_id + 1

        embed = discord.Embed(title=f"Suggestion #{suggestion_id}", description=text, color=discord.Color.teal())
        embed.set_author(name=str(ctx.author), icon_url=ctx.author.display_avatar.url)
        message = await channel.send(embed=embed)
        await message.add_reaction("👍")
        await message.add_reaction("👎")

        guild_config["suggestions"]["items"][str(suggestion_id)] = {
            "author_id": ctx.author.id,
            "message_id": message.id,
            "channel_id": channel.id,
            "text": text,
        }
        self.bot.storage.save()  # type: ignore[attr-defined]

        localizer = self._localizer(ctx.guild.id)
        await ctx.send(localizer.t("suggestion_received", suggestion_id=suggestion_id))

    @set_suggestions.error
    async def on_suggestions_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Suggestions command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Suggestions(bot))
