from __future__ import annotations

import logging

import discord
from discord.ext import commands


class Premium(commands.Cog):
    """Premium server management and priority support flagging."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def _config(self) -> dict:
        data = self.bot.storage._data  # type: ignore[attr-defined]
        data.setdefault("premium", {"server_slots": 3, "servers": []})
        return data["premium"]

    @commands.hybrid_command(name="premiumslots", description="Show available premium server slots.")
    async def premium_slots(self, ctx: commands.Context) -> None:
        premium = self._config()
        slots = premium["server_slots"]
        servers = premium["servers"]
        await ctx.send(f"⭐ Premium slots: {len(servers)}/{slots} in use.")

    @commands.hybrid_command(name="addpremium", description="Add this server to premium slots.")
    @commands.has_guild_permissions(administrator=True)
    async def add_premium(self, ctx: commands.Context) -> None:
        premium = self._config()
        servers = premium["servers"]
        if ctx.guild.id in servers:
            await ctx.send("This server is already premium.")
            return

        if len(servers) >= premium["server_slots"]:
            await ctx.send("No premium slots available.")
            return

        servers.append(ctx.guild.id)
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send("✅ Server added to premium slots.")

    @commands.hybrid_command(name="removepremium", description="Remove this server from premium slots.")
    @commands.has_guild_permissions(administrator=True)
    async def remove_premium(self, ctx: commands.Context) -> None:
        premium = self._config()
        servers = premium["servers"]
        if ctx.guild.id not in servers:
            await ctx.send("This server is not premium.")
            return

        servers.remove(ctx.guild.id)
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send("✅ Server removed from premium slots.")

    @commands.hybrid_command(name="prioritysupport", description="Request priority support.")
    async def priority_support(self, ctx: commands.Context, *, topic: str) -> None:
        premium = self._config()
        if ctx.guild.id not in premium["servers"]:
            await ctx.send("Priority support is only available for premium servers.")
            return

        await ctx.send(f"🚨 Priority support request received: {topic}")

    @add_premium.error
    @remove_premium.error
    async def on_premium_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Premium command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Premium(bot))
