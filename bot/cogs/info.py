from __future__ import annotations

import discord
from discord.ext import commands


class Info(commands.Cog):
    """Information commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="ping", description="Check the bot's latency.")
    async def ping(self, ctx: commands.Context) -> None:
        await ctx.send(f"🏓 Pong! {round(self.bot.latency * 1000)}ms")

    @commands.hybrid_command(name="server", description="Show server information.")
    async def server_info(self, ctx: commands.Context) -> None:
        guild = ctx.guild
        if not guild:
            await ctx.send("This command can only be used in a server.")
            return

        embed = discord.Embed(title=guild.name, color=discord.Color.blurple())
        embed.add_field(name="Members", value=guild.member_count)
        embed.add_field(name="Owner", value=str(guild.owner))
        embed.add_field(name="Created", value=guild.created_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=guild.icon.url if guild.icon else discord.Embed.Empty)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="user", description="Show user information.")
    async def user_info(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or ctx.author
        embed = discord.Embed(title=str(target), color=discord.Color.green())
        embed.add_field(name="ID", value=target.id)
        embed.add_field(name="Joined", value=target.joined_at.strftime("%Y-%m-%d"))
        embed.add_field(name="Created", value=target.created_at.strftime("%Y-%m-%d"))
        embed.set_thumbnail(url=target.display_avatar.url)
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Info(bot))
