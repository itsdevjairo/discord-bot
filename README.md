# Discord Bot

A full-featured Discord bot starter with:

- Prefix commands + slash command sync
- Modular cogs (admin, info, fun, community, embeds, suggestions, tickets, premium)
- Environment-based configuration
- Structured logging
- Welcome/goodbye messages + auto roles
- Public ticket transcripts
- Multi-language messaging (EN/NL starter)
- Embed builder
- Advanced suggestion system with voting
- AI-style helpdesk responses
- Priority support and premium slots

## Setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create a `.env` file (see `.env.example`) and set your bot token.

3. Run the bot:

```bash
python -m bot.main
```

## Notes

- The bot uses `commands.Bot` with slash command syncing on startup.
- Admin actions require the `Manage Guild` permission.
- Ticket transcripts are stored in `DATA_DIR` (default: `data/storage.json`).
