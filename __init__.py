import discord
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

intents = discord.Intents.all()
intents.members = True


client = discord.Client(intents=intents)
sentiment_analyzer = SentimentIntensityAnalyzer()

@client.event
async def on_message(message):
    # skip messages from the bot itself
    if message.author == client.user:
        return
    
    # check if the message is in a specific category ID
    # this also prevents it from flagging the embed reports, which for me are in another category
    if message.channel.category_id not in [953803234395451462]: # replace with the desired category IDs
        return
    
    # check if the user has the Manage Server or Administrator role
    has_permission = False
    for role in message.author.roles:
        if role.permissions.manage_guild or role.permissions.administrator:
            has_permission = True
            break
    
    # if the user does not have permission, get the sentiment score and check if it's too negative
    if not has_permission:
        # get the sentiment score of the message
        sentiment_score = sentiment_analyzer.polarity_scores(message.content)['compound']

        # set a threshold for the sentiment score
        threshold = -0.8

        # if the sentiment score is too negative, reply to the user and delete the message
        if sentiment_score < threshold:
            reply_message = f"{message.author.mention}, your message has a negative sentiment score of {sentiment_score}. Please refrain from using excessive negativity."
            await message.reply(reply_message)
            await message.delete()

            # send a report about the message to a specific channel ID using an embed
            report_channel = 1032000169232826478 # replace with the desired channel ID
            embed = discord.Embed(title="Negative Message Removed", description=f"A negative message was sent by {message.author} and deleted.", color=0xff0000)
            embed.add_field(name="Message Content", value='||'+message.content+'||')
            embed.add_field(name="Sentiment Score", value=sentiment_score)
            await report_channel.send(embed=embed)

# Replace the bot_token with your bot's token
client.run(os.getenv('BOT_TOKEN'))
