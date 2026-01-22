from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands


class Admin(commands.Cog):
    """Administrative and moderation commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @commands.hybrid_command(name="kick", description="Kick a member from the server.")
    @commands.has_guild_permissions(kick_members=True)
    async def kick_member(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: Optional[str] = None,
    ) -> None:
        await member.kick(reason=reason)
        await ctx.send(f"✅ Kicked {member.mention}. Reason: {reason or 'No reason provided.'}")

    @commands.hybrid_command(name="ban", description="Ban a member from the server.")
    @commands.has_guild_permissions(ban_members=True)
    async def ban_member(
        self,
        ctx: commands.Context,
        member: discord.Member,
        *,
        reason: Optional[str] = None,
    ) -> None:
        await member.ban(reason=reason, delete_message_days=0)
        await ctx.send(f"✅ Banned {member.mention}. Reason: {reason or 'No reason provided.'}")

    @commands.hybrid_command(name="purge", description="Delete a number of messages from the channel.")
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_messages(self, ctx: commands.Context, amount: int) -> None:
        if amount <= 0:
            await ctx.send("Please provide a number greater than 0.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Deleted {len(deleted) - 1} messages.", delete_after=5)

    @kick_member.error
    @ban_member.error
    @purge_messages.error
    async def on_admin_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Admin command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))
