import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

verify_button_id = "nsfw_verify_button"

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def postverify(ctx):
    embed = discord.Embed(title="NSFW Verification Required",
                          description="To access NSFW sections, click the button below to verify.",
                          color=0xff69b4)
    view = View()
    view.add_item(Button(label="🔞 Verify Me", style=discord.ButtonStyle.primary, custom_id=verify_button_id))
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_interaction(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'] == verify_button_id:
            user = interaction.user

            # Anti-alt check
            account_age_days = (discord.utils.utcnow() - user.created_at).days
            if account_age_days < config['min_account_age_days']:
                await interaction.response.send_message("Your account is too new to verify. Please try again later.", ephemeral=True)
                return

            try:
                await user.send("Hello! Let's get you verified for NSFW content in Lounge PH.")
                questions = [
                    "1. What is your Discord username and ID?",
                    "2. How old are you?",
                    "3. Do you consent to seeing NSFW content? (Yes/No)",
                    "4. Have you read and agreed to the NSFW rules? (Yes/No)",
                    "5. Upload a screenshot showing your age (blur other info)."
                ]

                answers = []
                for q in questions[:-1]:
                    await user.send(q)
                    msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel))
                    answers.append(msg.content)

                await user.send(questions[-1])
                img_msg = await bot.wait_for('message', check=lambda m: m.author == user and isinstance(m.channel, discord.DMChannel) and m.attachments)
                image_url = img_msg.attachments[0].url

                vr_channel = bot.get_channel(config['review_channel_id'])
                view = View()
                view.add_item(Button(label="✅ Approve", style=discord.ButtonStyle.success, custom_id=f"approve_{user.id}"))
                view.add_item(Button(label="❌ Reject", style=discord.ButtonStyle.danger, custom_id=f"reject_{user.id}"))

                await vr_channel.send(
                    f"NSFW Verification Request from {user.mention}\n"
                    f"🆔 Username & ID: {answers[0]}\n"
                    f"🎂 Age: {answers[1]}\n"
                    f"✅ Consent: {answers[2]}\n"
                    f"📜 Agreed to Rules: {answers[3]}\n"
                    f"🖼️ Screenshot: {image_url}",
                    view=view
                )

                await interaction.response.send_message("I've sent you a DM with the verification form.", ephemeral=True)

            except discord.Forbidden:
                await interaction.response.send_message("I couldn't DM you. Please enable your DMs and try again.", ephemeral=True)

@bot.event
async def on_interaction_response(interaction):
    if interaction.type == discord.InteractionType.component:
        if interaction.data['custom_id'].startswith("approve_"):
            user_id = int(interaction.data['custom_id'].split("_")[1])
            guild = interaction.guild
            user = guild.get_member(user_id)
            role = guild.get_role(config['verified_role_id'])
            await user.add_roles(role)
            await interaction.response.send_message(f"Approved {user.mention}.", ephemeral=True)
            try:
                await user.send("You have been approved for NSFW access!")
            except:
                pass
        elif interaction.data['custom_id'].startswith("reject_"):
            user_id = int(interaction.data['custom_id'].split("_")[1])
            guild = interaction.guild
            user = guild.get_member(user_id)
            await interaction.response.send_message(f"Rejected {user.mention}.", ephemeral=True)
            try:
                await user.send("Your NSFW verification has been rejected.")
            except:
                pass

bot.run(os.environ['DISCORD_BOT_TOKEN'])
