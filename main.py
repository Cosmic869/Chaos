import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
import logging
import asyncio

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('discord_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration with error handling
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    logger.info("Configuration loaded successfully")
except FileNotFoundError:
    logger.error("config.json file not found. Please create it with the required settings.")
    exit(1)
except json.JSONDecodeError as e:
    logger.error(f"Error parsing config.json: {e}")
    exit(1)

# Validate required config keys
required_keys = ['min_account_age_days', 'review_channel_id', 'verified_role_id']
missing_keys = [key for key in required_keys if key not in config]
if missing_keys:
    logger.error(f"Missing required configuration keys: {missing_keys}")
    exit(1)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

verify_button_id = "nsfw_verify_button"

@bot.event
async def on_ready():
    logger.info(f'Bot logged in as {bot.user} (ID: {bot.user.id})')
    logger.info(f'Bot is in {len(bot.guilds)} guilds')

    # Sync slash commands on startup
    try:
        synced = await bot.tree.sync()
        logger.info(f'Synced {len(synced)} slash commands')
    except Exception as e:
        logger.error(f'Failed to sync slash commands: {e}')

async def create_verification_embed():
    """Create the verification embed and view"""
    embed = discord.Embed(
        title="🔞 NSFW Verification Required",
        description="To access NSFW sections, click the button below to verify your age and consent.\n\n"
                   "**Requirements:**\n"
                   f"• Account must be at least {config['min_account_age_days']} days old\n"
                   "• Must be 18+ years old\n"
                   "• Age verification screenshot (optional)",
        color=0xff69b4
    )
    embed.set_footer(text="This verification process is required for legal compliance.")

    view = View(timeout=None)  # Persistent view
    view.add_item(Button(
        label="🔞 Verify Me", 
        style=discord.ButtonStyle.primary, 
        custom_id=verify_button_id
    ))

    return embed, view

@bot.command()
async def postverify(ctx):
    """Post the NSFW verification embed with button (prefix command)"""
    try:
        embed, view = await create_verification_embed()
        await ctx.send(embed=embed, view=view)
        logger.info(f"Verification embed posted by {ctx.author} in {ctx.channel} (prefix command)")

    except Exception as e:
        logger.error(f"Error posting verification embed: {e}")
        await ctx.send("An error occurred while posting the verification embed.")

# Slash Commands
@bot.tree.command(name="postverify", description="Post the NSFW verification embed with button")
@discord.app_commands.describe()
async def slash_postverify(interaction: discord.Interaction):
    """Post the NSFW verification embed with button (slash command)"""
    try:
        embed, view = await create_verification_embed()
        await interaction.response.send_message(embed=embed, view=view)
        logger.info(f"Verification embed posted by {interaction.user} in {interaction.channel} (slash command)")

    except Exception as e:
        logger.error(f"Error posting verification embed: {e}")
        await interaction.response.send_message("An error occurred while posting the verification embed.", ephemeral=True)

@bot.tree.command(name="botstats", description="Show bot statistics and health information")
async def slash_botstats(interaction: discord.Interaction):
    """Show bot statistics"""
    try:
        uptime = discord.utils.utcnow() - bot.user.created_at

        embed = discord.Embed(
            title="🤖 Bot Statistics",
            color=0x00ff00,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(name="🏓 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
        embed.add_field(name="🏠 Servers", value=str(len(bot.guilds)), inline=True)
        embed.add_field(name="👥 Users", value=str(len(bot.users)), inline=True)
        embed.add_field(name="⏰ Bot Created", value=bot.user.created_at.strftime("%Y-%m-%d"), inline=True)
        embed.add_field(name="🔧 Commands", value="Prefix: `!` | Slash: `/`", inline=True)
        embed.add_field(name="📊 Status", value="🟢 Online", inline=True)

        embed.set_thumbnail(url=bot.user.display_avatar.url)
        embed.set_footer(text=f"Bot ID: {bot.user.id}")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Bot stats requested by {interaction.user}")

    except Exception as e:
        logger.error(f"Error showing bot stats: {e}")
        await interaction.response.send_message("An error occurred while fetching bot statistics.", ephemeral=True)

@bot.tree.command(name="help", description="Show available commands and bot information")
async def slash_help(interaction: discord.Interaction):
    """Show help information"""
    try:
        embed = discord.Embed(
            title="🆘 Bot Help & Commands",
            description="Here are all available commands for this NSFW verification bot:",
            color=0x3498db
        )

        embed.add_field(
            name="🔞 Verification Commands",
            value="`/postverify` - Post the verification embed\n"
                  "`!postverify` - Same as above (prefix version)",
            inline=False
        )

        embed.add_field(
            name="📊 Information Commands", 
            value="`/botstats` - Show bot statistics\n"
                  "`/help` - Show this help message\n"
                  "`/ping` - Check bot response time",
            inline=False
        )

        embed.add_field(
            name="🔧 How Verification Works",
            value="1. Click the 🔞 Verify Me button\n"
                  "2. Complete the DM questionnaire\n"
                  "3. Upload age verification screenshot (optional)\n"
                  "4. Wait for moderator approval\n"
                  "5. Get notified of the result",
            inline=False
        )

        embed.add_field(
            name="⚙️ Configuration",
            value=f"• Minimum account age: {config['min_account_age_days']} days\n"
                  "• Age requirement: 18+ years\n"
                  "• Verification method: Screenshot optional",
            inline=False
        )

        embed.set_footer(text="Need help? Contact a server administrator")

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Help requested by {interaction.user}")

    except Exception as e:
        logger.error(f"Error showing help: {e}")
        await interaction.response.send_message("An error occurred while showing help.", ephemeral=True)

@bot.tree.command(name="ping", description="Check bot response time")
async def slash_ping(interaction: discord.Interaction):
    """Check bot latency"""
    try:
        latency = round(bot.latency * 1000)

        if latency < 100:
            status = "🟢 Excellent"
            color = 0x00ff00
        elif latency < 200:
            status = "🟡 Good"
            color = 0xffff00
        else:
            status = "🔴 Poor"
            color = 0xff0000

        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"**Latency:** {latency}ms\n**Status:** {status}",
            color=color
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"Ping command used by {interaction.user} - {latency}ms")

    except Exception as e:
        logger.error(f"Error with ping command: {e}")
        await interaction.response.send_message("An error occurred while checking ping.", ephemeral=True)

# Admin-only slash commands
@bot.tree.command(name="sync", description="Sync slash commands (Admin only)")
@discord.app_commands.describe()
async def slash_sync(interaction: discord.Interaction):
    """Sync slash commands - Admin only"""
    try:
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need Administrator permissions to use this command.", ephemeral=True)
            return

        synced = await bot.tree.sync()
        await interaction.response.send_message(f"✅ Synced {len(synced)} slash commands!", ephemeral=True)
        logger.info(f"Slash commands synced by {interaction.user} - {len(synced)} commands")

    except Exception as e:
        logger.error(f"Error syncing commands: {e}")
        await interaction.response.send_message("An error occurred while syncing commands.", ephemeral=True)

@bot.event
async def on_interaction(interaction):
    """Handle all button interactions"""
    if interaction.type != discord.InteractionType.component:
        return

    custom_id = interaction.data.get("custom_id", "")

    try:
        if custom_id == verify_button_id:
            await handle_verification_start(interaction)
        elif custom_id.startswith("approve_"):
            await handle_approval(interaction, custom_id)
        elif custom_id.startswith("reject_"):
            await handle_rejection(interaction, custom_id)
    except Exception as e:
        logger.error(f"Error handling interaction {custom_id}: {e}")
        try:
            await interaction.response.send_message(
                "An error occurred while processing your request. Please try again later.", 
                ephemeral=True
            )
        except:
            pass

async def handle_verification_start(interaction):
    """Handle the initial verification button click"""
    user = interaction.user

    # Anti-alt check
    account_age_days = (discord.utils.utcnow() - user.created_at).days
    if account_age_days < config['min_account_age_days']:
        await interaction.response.send_message(
            f"❌ Your account is too new to verify. Account must be at least {config['min_account_age_days']} days old.\n"
            f"Your account age: {account_age_days} days", 
            ephemeral=True
        )
        logger.info(f"Verification denied for {user} - account too new ({account_age_days} days)")
        return

    try:
        # Send initial response
        await interaction.response.send_message(
            "✅ I've sent you a DM with the verification form. Please check your direct messages.", 
            ephemeral=True
        )

        # Start DM verification process
        await user.send(
            "🔞 **NSFW Verification Process**\n\n"
            "Hello! Let's get you verified for NSFW content access.\n"
            "Please answer the following questions honestly and completely.\n"
            "⏰ You have 5 minutes to complete each step.\n\n"
            "**Let's begin:**"
        )

        questions = [
            "**1.** What is your Discord username and ID? (You can copy this: `{}`#{})".format(user.name, user.discriminator),
            "**2.** How old are you? (Must be 18 or older)",
            "**3.** Do you consent to seeing NSFW content? (Type 'Yes' or 'No')",
            "**4.** Have you read and agreed to the server's NSFW rules? (Type 'Yes' or 'No')"
        ]

        answers = []

        # Ask text questions with timeout
        for i, question in enumerate(questions, 1):
            await user.send(f"{question}")

            try:
                def check(m):
                    return (m.author == user and 
                           isinstance(m.channel, discord.DMChannel) and 
                           len(m.content.strip()) > 0)

                msg = await bot.wait_for('message', timeout=300, check=check)  # 5 minutes
                answers.append(msg.content.strip())

                # Validate critical answers
                if i == 2:  # Age question
                    try:
                        age = int(msg.content.strip())
                        if age < 18:
                            await user.send("❌ You must be 18 or older to access NSFW content. Verification cancelled.")
                            logger.info(f"Verification cancelled for {user} - under 18 (claimed age: {age})")
                            return
                    except ValueError:
                        await user.send("❌ Please provide a valid age number. Verification cancelled.")
                        logger.info(f"Verification cancelled for {user} - invalid age format")
                        return
                elif i in [3, 4]:  # Consent questions
                    if msg.content.strip().lower() not in ['yes', 'y']:
                        await user.send("❌ You must consent and agree to the rules to access NSFW content. Verification cancelled.")
                        logger.info(f"Verification cancelled for {user} - did not consent/agree")
                        return

                await user.send("✅ Answer recorded.")

            except asyncio.TimeoutError:
                await user.send("⏰ Verification timed out. Please start over by clicking the verification button again.")
                logger.info(f"Verification timed out for {user} at question {i}")
                return

        # Ask for screenshot (now optional)
        await user.send(
            "**5.** Please upload a screenshot showing your age verification, or type 'skip' to proceed without one.\n"
            "This could be:\n"
            "• Government ID (blur out sensitive info, keep age/DOB visible)\n"
            "• Birth certificate (blur sensitive info)\n"
            "• Any official document showing your date of birth\n\n"
            "**Important:** Blur out all personal information except your age/date of birth.\n"
            "**Note:** You can type 'skip' if you prefer not to upload a screenshot."
        )

        image_url = None
        try:
            def check_image_or_skip(m):
                return (m.author == user and 
                       isinstance(m.channel, discord.DMChannel) and 
                       (len(m.attachments) > 0 or m.content.strip().lower() in ['skip', 's']))

            img_msg = await bot.wait_for('message', timeout=600, check=check_image_or_skip)  # 10 minutes for upload

            if img_msg.content.strip().lower() in ['skip', 's']:
                image_url = "No screenshot provided (skipped by user)"
                await user.send("✅ Screenshot skipped. Proceeding with verification.")
            else:
                image_url = img_msg.attachments[0].url
                await user.send("✅ Screenshot received.")

        except asyncio.TimeoutError:
            await user.send("⏰ Image upload timed out. Please start over by clicking the verification button again.")
            logger.info(f"Image upload timed out for {user}")
            return

        # Send to review channel
        guild = interaction.guild
        review_channel_id = config['review_channel_id']

        if review_channel_id == "REPLACE_WITH_YOUR_REVIEW_CHANNEL_ID":
            await user.send("❌ Bot configuration error. Please contact an administrator.")
            logger.error("Review channel ID not configured properly")
            return

        # Extract actual ID from mention format if needed
        clean_channel_id = extract_id(review_channel_id)
        vr_channel = guild.get_channel(int(clean_channel_id))
        if vr_channel is None:
            await user.send("❌ Review channel not found. Please contact an administrator.")
            logger.error(f"Review channel {review_channel_id} not found or bot lacks access")
            return

        # Create review embed
        review_embed = discord.Embed(
            title="🔞 NSFW Verification Request",
            color=0xffa500,
            timestamp=discord.utils.utcnow()
        )
        review_embed.add_field(name="👤 User", value=f"{user.mention} ({user})", inline=False)
        review_embed.add_field(name="🆔 Username & ID", value=answers[0], inline=False)
        review_embed.add_field(name="🎂 Age", value=answers[1], inline=True)
        review_embed.add_field(name="✅ Consent", value=answers[2], inline=True)
        review_embed.add_field(name="📜 Agreed to Rules", value=answers[3], inline=True)
        review_embed.add_field(name="📅 Account Created", value=user.created_at.strftime("%Y-%m-%d"), inline=True)
        review_embed.add_field(name="⏰ Account Age", value=f"{account_age_days} days", inline=True)
        review_embed.add_field(name="🖼️ Age Verification", value=f"[View Screenshot]({image_url})", inline=False)
        review_embed.set_thumbnail(url=user.display_avatar.url)

        view = View(timeout=None)
        view.add_item(Button(
            label="✅ Approve", 
            style=discord.ButtonStyle.success, 
            custom_id=f"approve_{user.id}"
        ))
        view.add_item(Button(
            label="❌ Reject", 
            style=discord.ButtonStyle.danger, 
            custom_id=f"reject_{user.id}"
        ))

        await vr_channel.send(embed=review_embed, view=view)
        await user.send(
            "✅ **Verification submitted successfully!**\n\n"
            "Your verification request has been sent to the moderation team for review.\n"
            "You will receive a DM with the result once it's processed.\n\n"
            "Thank you for your patience! 🙏"
        )

        logger.info(f"Verification request submitted for {user}")

    except discord.Forbidden:
        await interaction.response.send_message(
            "❌ I couldn't send you a DM. Please:\n"
            "1. Enable DMs from server members\n"
            "2. Make sure you haven't blocked the bot\n"
            "3. Try again after adjusting your privacy settings", 
            ephemeral=True
        )
        logger.info(f"Could not DM {user} for verification")
    except Exception as e:
        logger.error(f"Error in verification process for {user}: {e}")
        await user.send("❌ An error occurred during verification. Please try again or contact an administrator.")

def extract_id(id_string):
    """Extract ID from mention format or return as-is if already an ID"""
    if isinstance(id_string, str):
        # Remove role mention format <@&123456789> -> 123456789
        if id_string.startswith('<@&') and id_string.endswith('>'):
            return id_string[3:-1]
        # Remove channel mention format <#123456789> -> 123456789
        elif id_string.startswith('<#') and id_string.endswith('>'):
            return id_string[2:-1]
        # Remove user mention format <@123456789> -> 123456789
        elif id_string.startswith('<@') and id_string.endswith('>'):
            return id_string[2:-1]
    return str(id_string)

async def handle_approval(interaction, custom_id):
    """Handle verification approval"""
    user_id = int(custom_id.split("_")[1])
    guild = interaction.guild
    user = guild.get_member(user_id)

    if not user:
        await interaction.response.send_message("❌ User not found in server.", ephemeral=True)
        return

    verified_role_id = config['verified_role_id']
    if verified_role_id == "REPLACE_WITH_YOUR_VERIFIED_ROLE_ID":
        await interaction.response.send_message("❌ Verified role not configured.", ephemeral=True)
        logger.error("Verified role ID not configured properly")
        return

    # Extract actual ID from mention format if needed
    clean_role_id = extract_id(verified_role_id)
    role = guild.get_role(int(clean_role_id))
    if not role:
        await interaction.response.send_message("❌ Verified role not found.", ephemeral=True)
        logger.error(f"Verified role {verified_role_id} not found")
        return

    try:
        await user.add_roles(role, reason=f"NSFW verification approved by {interaction.user}")
        await interaction.response.send_message(f"✅ **Approved** {user.mention} for NSFW access.", ephemeral=True)

        # Update the original message
        embed = interaction.message.embeds[0]
        embed.color = 0x00ff00  # Green
        embed.title = "✅ NSFW Verification - APPROVED"
        embed.add_field(name="📋 Action", value=f"Approved by {interaction.user.mention}", inline=False)

        await interaction.edit_original_response(embed=embed, view=None)

        try:
            await user.send(
                "🎉 **Verification Approved!**\n\n"
                "Congratulations! You have been approved for NSFW access.\n"
                "You can now access all NSFW channels and content in the server.\n\n"
                "Please remember to follow all server rules and guidelines. Enjoy! ✨"
            )
        except discord.Forbidden:
            logger.info(f"Could not DM approval notification to {user}")

        logger.info(f"NSFW verification approved for {user} by {interaction.user}")

    except discord.Forbidden:
        await interaction.response.send_message("❌ I don't have permission to assign roles.", ephemeral=True)
        logger.error(f"No permission to assign role to {user}")
    except Exception as e:
        await interaction.response.send_message("❌ An error occurred while approving.", ephemeral=True)
        logger.error(f"Error approving {user}: {e}")

async def handle_rejection(interaction, custom_id):
    """Handle verification rejection"""
    user_id = int(custom_id.split("_")[1])
    guild = interaction.guild
    user = guild.get_member(user_id)

    if not user:
        await interaction.response.send_message("❌ User not found in server.", ephemeral=True)
        return

    try:
        await interaction.response.send_message(f"❌ **Rejected** {user.mention}'s verification request.", ephemeral=True)

        # Update the original message
        embed = interaction.message.embeds[0]
        embed.color = 0xff0000  # Red
        embed.title = "❌ NSFW Verification - REJECTED"
        embed.add_field(name="📋 Action", value=f"Rejected by {interaction.user.mention}", inline=False)

        await interaction.edit_original_response(embed=embed, view=None)

        try:
            await user.send(
                "❌ **Verification Rejected**\n\n"
                "Unfortunately, your NSFW verification request has been rejected.\n\n"
                "This could be due to:\n"
                "• Insufficient age verification\n"
                "• Incomplete or unclear responses\n"
                "• Not meeting server requirements\n\n"
                "If you believe this was an error, please contact a moderator directly."
            )
        except discord.Forbidden:
            logger.info(f"Could not DM rejection notification to {user}")

        logger.info(f"NSFW verification rejected for {user} by {interaction.user}")

    except Exception as e:
        await interaction.response.send_message("❌ An error occurred while rejecting.", ephemeral=True)
        logger.error(f"Error rejecting {user}: {e}")

@bot.event
async def on_error(event, *args, **kwargs):
    """Global error handler"""
    logger.error(f"An error occurred in {event}: {args}, {kwargs}")

# Run the bot
if __name__ == "__main__":
    token = os.environ.get('DISCORD_BOT_TOKEN')
    if not token:
        logger.error("DISCORD_BOT_TOKEN environment variable not set")
        exit(1)

    try:
        bot.run(token)
    except discord.LoginFailure:
        logger.error("Invalid bot token")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
