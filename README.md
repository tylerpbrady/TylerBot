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
- Initiates a poll asking the server if the messages were “provoking.”
- If a majority votes "Yes", the "days since last argument" counter resets to zero.

### GL Status Checker
- `/gl` checks if the group leader is currently online.

### Washing Machine
- `/washingmachine [username]` moves a user between 2 voice channels back and fourth repeatedly, putting them back in their original voice channel when done.
---

## 🛠 Setup & Installation
- Simply invite the bot to your server with [this link](https://discord.com/oauth2/authorize?client_id=1315206352712503357&permissions=562952117906448&integration_type=0&scope=bot+applications.commands)
