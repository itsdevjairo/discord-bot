from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands

from bot.localization import Localizer


class Tickets(commands.Cog):
    """Ticketing system with transcripts and AI-style responses."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.logger = logging.getLogger(self.__class__.__name__)

    def _guild_config(self, guild_id: int) -> dict:
        guild_data = self.bot.storage.guild(guild_id)  # type: ignore[attr-defined]
        guild_data.setdefault(
            "tickets",
            {
                "category_id": None,
                "support_role_id": None,
                "next_id": 1,
                "transcripts": {},
            },
        )
        return guild_data

    def _localizer(self, guild_id: int) -> Localizer:
        lang = self._guild_config(guild_id).get("language", "en")
        return Localizer(language=lang)

    @commands.hybrid_group(name="ticket", description="Ticketing commands.", fallback="create")
    async def ticket(self, ctx: commands.Context, *, reason: Optional[str] = None) -> None:
        await self.create_ticket(ctx, reason=reason)

    @ticket.command(name="create", description="Create a support ticket.")
    async def create_ticket(self, ctx: commands.Context, *, reason: Optional[str] = None) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        category_id = guild_config["tickets"].get("category_id")
        support_role_id = guild_config["tickets"].get("support_role_id")

        category = None
        if category_id:
            category = ctx.guild.get_channel(int(category_id))

        ticket_id = guild_config["tickets"]["next_id"]
        guild_config["tickets"]["next_id"] = ticket_id + 1

        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False),
            ctx.author: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
        }
        if support_role_id:
            support_role = ctx.guild.get_role(int(support_role_id))
            if support_role:
                overwrites[support_role] = discord.PermissionOverwrite(
                    view_channel=True, send_messages=True, read_message_history=True
                )

        channel = await ctx.guild.create_text_channel(
            name=f"ticket-{ticket_id}",
            category=category if isinstance(category, discord.CategoryChannel) else None,
            overwrites=overwrites,
            topic=f"Ticket {ticket_id} | Owner: {ctx.author.id}",
        )

        await channel.send(
            f"Hi {ctx.author.mention}, a support member will be with you shortly.\n"
            f"Reason: {reason or 'No reason provided.'}"
        )

        localizer = self._localizer(ctx.guild.id)
        await ctx.send(localizer.t("ticket_created", channel=channel.mention))
        self.bot.storage.save()  # type: ignore[attr-defined]

    @ticket.command(name="close", description="Close the current ticket and create a transcript.")
    @commands.has_guild_permissions(manage_channels=True)
    async def close_ticket(self, ctx: commands.Context) -> None:
        if not isinstance(ctx.channel, discord.TextChannel):
            await ctx.send("This command can only be used in a text channel.")
            return

        guild_config = self._guild_config(ctx.guild.id)
        transcript_id = f"{ctx.guild.id}-{int(datetime.utcnow().timestamp())}"
        messages = [message async for message in ctx.channel.history(limit=200, oldest_first=True)]

        transcript_lines = []
        for message in messages:
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M")
            transcript_lines.append(f"[{timestamp}] {message.author}: {message.content}")

        guild_config["tickets"]["transcripts"][transcript_id] = {
            "channel_id": ctx.channel.id,
            "created_at": datetime.utcnow().isoformat(),
            "content": "\n".join(transcript_lines),
        }
        self.bot.storage.save()  # type: ignore[attr-defined]

        localizer = self._localizer(ctx.guild.id)
        await ctx.send(localizer.t("ticket_closed", transcript_id=transcript_id))
        await ctx.channel.delete(reason="Ticket closed")

    @ticket.command(name="transcript", description="Get a public transcript by ID.")
    async def get_transcript(self, ctx: commands.Context, transcript_id: str) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        transcript = guild_config["tickets"]["transcripts"].get(transcript_id)
        if not transcript:
            await ctx.send("Transcript not found.")
            return

        content = transcript["content"]
        if len(content) > 1900:
            content = content[:1900] + "..."
        await ctx.send(f"```\n{content}\n```")

    @commands.hybrid_command(name="setticketcategory", description="Set the ticket category.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_ticket_category(self, ctx: commands.Context, category: discord.CategoryChannel) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["tickets"]["category_id"] = category.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Ticket category set to {category.name}.")

    @commands.hybrid_command(name="setsupportrole", description="Set the support role for tickets.")
    @commands.has_guild_permissions(manage_guild=True)
    async def set_support_role(self, ctx: commands.Context, role: discord.Role) -> None:
        guild_config = self._guild_config(ctx.guild.id)
        guild_config["tickets"]["support_role_id"] = role.id
        self.bot.storage.save()  # type: ignore[attr-defined]
        await ctx.send(f"✅ Support role set to {role.mention}.")

    @commands.hybrid_command(name="aihelp", description="AI-style helpdesk response.")
    async def ai_help(self, ctx: commands.Context, *, question: str) -> None:
        response = (
            "🤖 I can help with server basics like roles, channels, and commands. "
            f"You asked: '{question}'. A moderator will follow up if needed."
        )
        await ctx.send(response)

    @ticket.error
    @create_ticket.error
    @close_ticket.error
    @get_transcript.error
    @set_ticket_category.error
    @set_support_role.error
    async def on_ticket_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have permission to use this command.")
            return

        self.logger.exception("Ticket command error", exc_info=error)
        await ctx.send("Something went wrong while running the command.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Tickets(bot))
