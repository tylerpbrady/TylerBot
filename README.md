# TylerBot – Argument Tracker & Community Tools

A custom-built Discord bot that improves Discord server moderation and engagement by tracking arguments, posting daily updates, running community polls, and interacting via slash commands. Hosted using Amazon EC2.

---

## Features

### Argument Counter
- Automatically tracks and posts the number of days since the last argument.
- Sends a daily message at a specific time in a designated channel.
- Admin-only command `/setcounter` to manually adjust the count.

### Provoking Behavior Poll
- `/provoke [username]` retrieves a user’s recent messages and formats them cleanly.
- Automatically identifies if a message was a GIF/image.
- Initiates a poll asking the server if the messages were “provoking.”
- If a majority votes "Yes", the counter resets to zero.

### GL Status Checker
- `/gl` checks if a specific user (e.g. "GL") is currently online.

### Smart Text Responses
- Responds to messages using custom logic in `responses.py`.
- Filters out bot messages to prevent loops.

---

## 🛠 Setup & Installation

### Requirements
- Python 3.10+
- `discord.py` (latest version)
- `.env` file with:
  ```env
  DISCORD_TOKEN=your_token_here
