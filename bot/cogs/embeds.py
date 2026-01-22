from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands


class Embeds(commands.Cog):
    """Embed builder utilities."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    @commands.hybrid_command(name="embed", description="Create an embed message.")
    @commands.has_guild_permissions(manage_messages=True)
    async def create_embed(
        self,
        ctx: commands.Context,
        title: str,
        description: str,
        color: Optional[str] = None,
        footer: Optional[str] = None,
    ) -> None:
        embed_color = discord.Color.blurple()
        if color:
            try:
                embed_color = discord.Color(int(color.strip("#"), 16))
            except ValueError:
                await ctx.send("Color must be a hex value like #5865F2.")
                return

        embed = discord.Embed(title=title, description=description, color=embed_color)
        if footer:
            embed.set_footer(text=footer)

        await ctx.send(embed=embed)

    @create_embed.error
    async def on_embed_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Embed command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Embeds(bot))
