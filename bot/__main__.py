# TODO:
# Figure out scheduling messages based on event times
# Schedule a simple message send using a /command
# Schedule a message based off of an event time
# Read reactions to a message that was sent and subscribe users to events
import hikari
import lightbulb
import aiosqlite
import math
from dotenv import dotenv_values
from datetime import datetime, timedelta, timezone


class State:
    def __init(self):
        self.db = None


async def get_default_channel(guild_id):
    cur = await state.db.execute(f"""
    SELECT default_channel_id FROM Guilds WHERE guild_id={guild_id};
                     """)
    row = await cur.fetchone()
    if row is None:
        # TODO: Error handling
        print("No Default Channel")
        return
    default_channel_id = row[0]
    await cur.close()
    return default_channel_id


state = State()

secrets = dotenv_values("token.env")

token = secrets["TOKEN"]
# Create a GatewayBot instance
bot = hikari.GatewayBot(token)
client = lightbulb.client_from_app(bot)

# Ensure the client will be started when the bot is run
bot.subscribe(hikari.StartingEvent, client.start)


async def open_database(*_: hikari.StartingEvent):
    print("Connecting to db")
    state.db = await aiosqlite.connect(secrets["DATABASE_URL"])
    # Make sure the database exists
    await state.db.execute("""
    CREATE TABLE IF NOT EXISTS Guilds(
        guild_id INTEGER NOT NULL,
        default_channel_id INTEGER,
        PRIMARY KEY (guild_id)
        );
    """)


bot.subscribe(hikari.StartingEvent, open_database)


async def close_database(*_: hikari.StoppedEvent):
    print("Closing database")
    await state.db.close()


bot.subscribe(hikari.StoppedEvent, close_database)


async def inform_of_event(create_event_event: hikari.ScheduledEventCreateEvent):
    event = create_event_event.event
    default_channel_id = await get_default_channel(event.guild_id)
    time_to_event = event.start_time - datetime.now(timezone.utc)
    hours = math.floor(time_to_event.seconds / 3600)
    minutes = math.ceil((time_to_event.seconds - (hours * 3600)) / 60)
    await bot.rest.create_message(
        default_channel_id,
        content=f"@everyone Event {event.name} was just created! It starts in {time_to_event.days} days, {hours} hours and {minutes} minutes",
    )

    users = await bot.rest.fetch_scheduled_event_users(event.guild_id, event.id)

    if len(users) == 0:
        await bot.rest.create_message(
            default_channel_id,
            content=f"@everyone No one has taken responsibility for event: *{event.name}*. Someone please take responsibility asap!!!",
        )
    # for user in users:
    #     await bot.rest.create_message(
    #         default_channel_id,
    #         content=f"{user.mention} It's time for {event.name}!",
    #     )


bot.subscribe(hikari.ScheduledEventCreateEvent, inform_of_event)


async def event_started(update_event: hikari.ScheduledEventUpdateEvent):
    event = update_event.event
    if event.status != hikari.scheduled_events.ScheduledEventStatus.ACTIVE:
        return

    default_channel_id = await get_default_channel(event.guild_id)

    await bot.rest.create_message(
        default_channel_id,
        content=f"Event {event.name} is starting!",
    )
    users = await bot.rest.fetch_scheduled_event_users(event.guild_id, event.id)
    if len(users) == 0:
        await bot.rest.create_message(
            default_channel_id,
            content=f"@everyone No one has taken responsibility for event: *{event.name}*. Someone please take responsibility asap!!!",
        )
    for user in users:
        await bot.rest.create_message(
            default_channel_id,
            content=f"{user.member.mention} It's time for {event.name}!",
        )


bot.subscribe(hikari.ScheduledEventUpdateEvent, event_started)


@client.register()
class SetDefaultChannel(
    lightbulb.SlashCommand,
    name="set_default_channel",
    description="set a default channel for the bot to send commands in",
):
    channel = lightbulb.channel("channel", "new default channel")

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        guild_id = ctx.guild_id
        await state.db.execute(f"""
            INSERT INTO Guilds (guild_id, default_channel_id)
                VALUES ({ctx.guild_id}, {self.channel.id})
            ON CONFLICT DO
                UPDATE SET default_channel_id={self.channel.id}
                WHERE guild_id={guild_id};
        """)
        await state.db.commit()
        await ctx.respond(f"Default Channel is now {self.channel.mention}")


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
        # TODO: Implement reactions
        await ctx.respond(
            f"@everyone {ctx.user.mention} just uploaded a receipt:\n{self.attachment.url}\n (Not yet implemented) Please respond to this message to take responsibility for it"
        )
        guild = ctx.guild_id
        date = datetime.now(timezone.utc)
        await bot.rest.create_external_event(
            guild,
            f"{ctx.member.display_name}'s Receipt {datetime.now().strftime('%m/%d/%y')}",
            "None",
            (date + timedelta(minutes=2)),
            (date + timedelta(days=5)),
            description='A receipt event. Please assign yourself to the event through the "interested" button',
            image=self.attachment,
        )


@client.register()
class ReadEvents(
    # Command type - builtins include SlashCommand, UserCommand, and MessageCommand
    lightbulb.SlashCommand,
    # Command declaration parameters
    name="read-all-events",
    description="reads all events from the server and returns info on them",
):
    # event_name = lightbulb.string("name", "the name of the event")
    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        # Send a message to the channel the command was used in
        await ctx.respond("Reading all events")
        guild = ctx.guild_id
        events = await bot.rest.fetch_scheduled_events(guild)
        for event in events:
            await ctx.respond(
                f"Id: {event.id}\nname: {event.name}\nstart time:{event.start_time}\nend_time: {event.end_time}\ndescription: {event.description}"
            )
            users = await bot.rest.fetch_scheduled_event_users(guild, event.id)
            if len(users) == 0:
                await ctx.respond(
                    f"@everyone No one has taken responsibility for event: *{event.name}*. Someone please take responsibility asap!!!"
                )
            for user in users:
                await ctx.respond(f"{user.user.mention} is interested in this event")


@client.register()
class ScheduleMessage(
    lightbulb.SlashCommand, name="schedule_message", description="schedule a message"
):
    message = lightbulb.string("message", "the message to send")
    time = lightbulb.integer("time", "should be a unix timestamp")

    @lightbulb.invoke
    async def invoke(self, ctx: lightbulb.Context) -> None:
        time = datetime.fromtimestamp(self.time)
        await ctx.respond(f"Time to send {time.strftime('%H:%M:%S')}")

# Run the bot
# Note that this is blocking meaning no code after this line will run
# until the bot is shut off
bot.run()
