# TODO: 
# Create event using hikari api (/command)
# Read that event's details to make sure it was created properly and see what the bot can access (using /command)
# Figure out scheduling messages based on event times
# Schedule a simple message send using a /command
# Schedule a message based off of an event time
# Need to store some data in a data base (probably sqlite)
import hikari
import lightbulb
from dotenv import dotenv_values
from datetime import datetime, timedelta, timezone

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
        user = ctx.user
        username = user.username
        mention = user.mention
        global_name = user.global_name
        await ctx.respond(f"{mention} Pong!")

@client.register()
class Fathers(
    # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
    lightbulb.SlashCommand,
    # Command declaration parameters
    name="fathers",
    description="the son loves his fathers",
):
    # Define the command's invocation method. This method must take the context as the first
    # argument (excluding self) which contains information about the command invocation.
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Send a message to the channel the command was used in
        await ctx.respond("I love my fathers")

@client.register()
class Receipt(
    # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
    lightbulb.SlashCommand,
    # Command declaration parameters
    name="receipt",
    description="Creates a new receipt event",
):
    attachment = lightbulb.attachment("receipt", "An image of the receipt")
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Send a message to the channel the command was used in
        await ctx.respond(f"@everyone {ctx.user.mention} just uploaded a receipt:\n{self.attachment.url}\nPlease respond to this message to take responsibility for it")
        guild = ctx.guild_id
        date = datetime.now(timezone.utc)
        await ctx.respond(f"Event time: {str(date + timedelta(hours=1))}")
        await bot.rest.create_external_event(guild,
                                       f"{ctx.member.display_name}'s Receipt {datetime.now().strftime("%m/%d/%y")}",
                                       "None",
                                       (date + timedelta(minutes=2)), (date + timedelta(days=5)),
                                       description="A receipt event. Please assign yourself to the event through the \"interested\" button",
                                        image=self.attachment
                                       )


@client.register()
class ReadEvent(
    # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
    lightbulb.SlashCommand,
    # Command declaration parameters
    name="read-event",
    description="reads an existing discord event",
):
    event_name = lightbulb.string("name", "the name of the event")
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Send a message to the channel the command was used in
        await ctx.respond(f"Reading event {self.event_name}")
        guild = ctx.guild_id
        events = await bot.rest.fetch_scheduled_events(guild)
        for event in events:
            await ctx.respond(f"Id: {event.id}\nname: {event.name}\nstart time:{event.start_time}\nend_time: {event.end_time}\ndescription: {event.description}")
            users = await bot.rest.fetch_scheduled_event_users(guild, event.id)
            for user in users:
                await ctx.respond(f"{user.user.mention} is interested in this event")


# @client.register()
# class ReadEvent(
#     # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
#     lightbulb.SlashCommand,
#     # Command declaration parameters
#     name="read-event",
#     description="reads an existing discord event",
# ):
#     event_name = lightbulb.string("name", "the name of the event")
#     @lightbulb.invoke
#     async def invoke(self, ctx: lightbulb.Context) -> None:
#         # Send a message to the channel the command was used in
#         reponse = f"Reading event {self.event_name}\n"
#         guild = ctx.guild_id
#         events = await bot.rest.fetch_scheduled_events(guild=guild)
#         for event in events:
#             reponse += f"Id: {event.id}\nname: {event.name}\nstart time:{event.start_time}\nend_time: {event.end_time}\ndescription: {event.description}\n"
#             users = await bot.rest.fetch_scheduled_event_users(guild=guild, event=event.id)
#             for user in users:
#                 response += f"{user.user.mention} is interested in this event"
#                 await ctx.respond(reponse)

# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
