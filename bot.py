# TODO: 
# Create event using hikari api (/command)
# Read that event's details to make sure it was created properly and see what the bot can access (using /command)
# Figure out scheduling messages based on event times
# Schedule a simple message send using a /command
# Schedule a message based off of an event time
import hikari
import lightbulb
from dotenv import dotenv_values

secrets = dotenv_values("token.env")

token = secrets["TOKEN"]
# Create a GatewayBot instance
bot = hikari.GatewayBot(token)
client = lightbulb.client_from_app(bot)

# Ensure the client will be started when the bot is run
bot.subscribe(hikari.StartingEvent, client.start)

# Register the command with the client
@client.register()
class Ping(
    # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
    lightbulb.SlashCommand,
    # Command declaration parameters
    name="ping",
    description="checks the bot is alive",
):
    # Define the command's invocation method. This method must take the context as the first
    # argument (excluding self) which contains information about the command invocation.
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Send a message to the channel the command was used in
        await ctx.respond("Pong!")

# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
