from __future__ import annotations

import random

from discord.ext import commands


class Fun(commands.Cog):
    """Fun and utility commands."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="roll", description="Roll dice. Example: 2d6")
    async def roll(self, ctx: commands.Context, dice: str = "1d6") -> None:
        try:
            rolls, limit = dice.lower().split("d")
            total_rolls = max(1, min(int(rolls), 20))
            limit_value = max(2, min(int(limit), 100))
        except ValueError:
            await ctx.send("Format has to be NdN, e.g. 2d6")
            return

        results = [random.randint(1, limit_value) for _ in range(total_rolls)]
        await ctx.send(f"🎲 Rolled {dice}: {', '.join(map(str, results))} (total {sum(results)})")

    @commands.hybrid_command(name="coin", description="Flip a coin.")
    async def coin(self, ctx: commands.Context) -> None:
        await ctx.send(f"🪙 {random.choice(['Heads', 'Tails'])}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Fun(bot))
