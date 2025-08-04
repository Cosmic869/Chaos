# Chaos
# Discord NSFW Verification Bot

A comprehensive Discord bot for handling NSFW content verification with age verification, DM-based questionnaires, and moderation review system.

## Features

- 🔞 Age verification with anti-alt account protection
- 📝 Interactive DM-based verification questionnaire
- 🖼️ Screenshot-based age proof requirement
- 👥 Moderation review system with approve/reject buttons
- 📊 Comprehensive logging and error handling
- ⏰ Timeout protection for all user interactions
- 🛡️ Robust error handling and validation

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- A Discord bot token
- A Discord server with appropriate permissions

### 2. Installation

1. Navigate to the discord_bot directory:
   ```bash
   cd discord_bot
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Configuration

1. **Bot Token Setup:**
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and replace `your_bot_token_here` with your actual Discord bot token

2. **Server Configuration:**
   - Edit `config.json` and replace the placeholder values:
     ```json
     {
       "min_account_age_days": 7,
       "review_channel_id": "YOUR_ACTUAL_REVIEW_CHANNEL_ID",
       "verified_role_id": "YOUR_ACTUAL_VERIFIED_ROLE_ID"
     }
     ```

### 4. Getting Discord IDs

To get the required Discord IDs:

1. **Enable Developer Mode:**
   - Go to Discord Settings → Advanced → Enable Developer Mode

2. **Get Channel ID:**
   - Right-click on your review channel → Copy ID
   - Paste this ID in `config.json` as `review_channel_id`

3. **Get Role ID:**
   - Go to Server Settings → Roles
   - Right-click on your verified role → Copy ID
   - Paste this ID in `config.json` as `verified_role_id`

### 5. Bot Permissions

Your bot needs the following permissions:
- Send Messages
- Use Slash Commands
- Embed Links
- Attach Files
- Read Message History
- Manage Roles
- Send Messages in DMs

### 6. Running the Bot

1. Make sure you're in the discord_bot directory:
   ```bash
   cd discord_bot
   ```

2. Run the bot:
   ```bash
   python main.py
   ```

## Usage

### For Server Administrators

1. **Post Verification Embed:**
   ```
   !postverify
   ```
   This creates an embed with a verification button that users can click.

2. **Monitor Review Channel:**
   - All verification requests appear in your configured review channel
   - Use the ✅ Approve or ❌ Reject buttons to process requests

### For Users

1. Click the "🔞 Verify Me" button on the verification embed
2. Complete the DM questionnaire (5 questions + screenshot upload)
3. Wait for moderation review
4. Receive approval/rejection notification via DM

## Verification Process

1. **Anti-Alt Check:** Account must be at least 7 days old (configurable)
2. **Age Verification:** User must confirm they are 18+
3. **Consent Confirmation:** User must explicitly consent to NSFW content
4. **Rules Agreement:** User must agree to server NSFW rules
5. **Photo Verification:** User must upload age verification screenshot
6. **Moderation Review:** Staff reviews and approves/rejects the request

## Security Features

- **Timeout Protection:** All user interactions have timeouts (5-10 minutes)
- **Input Validation:** Age responses are validated as numbers ≥18
- **Consent Validation:** Only "Yes" responses are accepted for consent questions
- **Error Handling:** Comprehensive error handling with user-friendly messages
- **Logging:** All actions are logged for audit purposes

## Troubleshooting

### Common Issues

1. **"Config file not found" error:**
   - Make sure `config.json` exists in the discord_bot directory
   - Check that the JSON syntax is valid

2. **"Invalid bot token" error:**
   - Verify your bot token in the `.env` file
   - Make sure there are no extra spaces or characters

3. **"Review channel not found" error:**
   - Verify the channel ID in `config.json`
   - Make sure the bot has access to the channel

4. **"Verified role not found" error:**
   - Verify the role ID in `config.json`
   - Make sure the bot has permission to assign the role

5. **Users can't receive DMs:**
   - Users need to enable DMs from server members
   - Check if users have blocked the bot

### Log Files

The bot creates a `discord_bot.log` file with detailed information about:
- Bot startup and configuration
- User verification attempts
- Errors and exceptions
- Moderation actions

## File Structure

```
discord_bot/
├── main.py              # Main bot code
├── config.json          # Server configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
├── .env                # Your actual environment variables (create this)
├── README.md           # This file
└── discord_bot.log     # Log file (created when bot runs)
```

## Support

If you encounter issues:

1. Check the log file (`discord_bot.log`) for error details
2. Verify all configuration values are correct
3. Ensure the bot has proper permissions
4. Make sure all dependencies are installed

## Legal Notice

This bot is designed for age verification purposes. Server administrators are responsible for:
- Complying with local laws and regulations
- Properly configuring age requirements
- Reviewing verification requests appropriately
- Maintaining user privacy and data security

## Version History

- **v1.0.0** - Initial release with comprehensive verification system
  - DM-based questionnaire system
  - Screenshot age verification
  - Moderation review interface
  - Comprehensive error handling and logging
