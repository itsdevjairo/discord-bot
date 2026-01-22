from __future__ import annotations

import logging
from typing import Optional

import discord
from discord.ext import commands

from bot.localization import Localizer


class Community(commands.Cog):
    """Welcome/goodbye messages, auto-roles, and language settings."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def _guild_config(self, guild_id: int) -> dict:
        guild_data = self.bot.storage.guild(guild_id)  # type: ignore[attr-defined]
        guild_data.setdefault("welcome_channel_id", None)
        guild_data.setdefault("goodbye_channel_id", None)
        guild_data.setdefault("auto_role_id", None)
        guild_data.setdefault("language", self.bot.config.default_language)  # type: ignore[attr-defined]
        return guild_data

    def _localizer(self, guild_id: int) -> Localizer:
        lang = self._guild_config(guild_id).get("language", "en")
        return Localizer(language=lang)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild_config = self._guild_config(member.guild.id)
        localizer = self._localizer(member.guild.id)

        role_id = guild_config.get("auto_role_id")
        if role_id:
            role = member.guild.get_role(int(role_id))
            if role:
                await member.add_roles(role, reason="Auto role")

        channel_id = guild_config.get("welcome_channel_id")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if isinstance(channel, discord.TextChannel):
                await channel.send(
                    localizer.t("welcome", guild=member.guild.name, member=member.mention)
                )

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        guild_config = self._guild_config(member.guild.id)
        localizer = self._localizer(member.guild.id)

        channel_id = guild_config.get("goodbye_channel_id")
        if channel_id:
            channel = member.guild.get_channel(int(channel_id))
            if isinstance(channel, discord.TextChannel):
                await channel.send(
                    localizer.t("goodbye", guild=member.guild.name, member=member.display_name)
                )

    @commands.hybrid_command(name="setwelcome", description="Set the welcome channel.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_welcome(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["welcome_channel_id"] = channel.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Welcome channel set to {channel.mention}.")

    @commands.hybrid_command(name="setgoodbye", description="Set the goodbye channel.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_goodbye(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["goodbye_channel_id"] = channel.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Goodbye channel set to {channel.mention}.")

    @commands.hybrid_command(name="setautorole", description="Set the auto role for new members.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_autorole(self, ctx: commands.Context, role: discord.Role) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["auto_role_id"] = role.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Auto role set to {role.mention}.")

    @commands.hybrid_command(name="setlanguage", description="Set the bot language for this server.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_language(self, ctx: commands.Context, language: str) -> None:
        language = language.lower()
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["language"] = language
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Language set to {language}.")

    @set_welcome.error
    @set_goodbye.error
    @set_autorole.error
    @set_language.error
    async def on_settings_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Community command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Community(bot))
