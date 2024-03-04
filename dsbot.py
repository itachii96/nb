import discord
from discord.ext import commands
import mysql.connector
import os
# Connect to MySQL database

host=os.environ.get("host")
user=os.environ.get("user")
password=os.environ.get("password")
database=os.environ.get("database")
token=os.environ.get("token")
def connect_to_database():
    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=database
    )
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".",intents=intents)

@bot.event
async def on_ready():
    await bot.tree.sync()
    activity = discord.Game(name="NB/AUTOFARM", type=3)
    await bot.change_presence(status=discord.Status.idle, activity=activity)
    print(f'Logged in as {bot.user}')

@bot.command()
async def premium(ctx,user: discord.Member):
    if ctx.author.id != bot.owner_id:
        return await ctx.send("Only the bot owner can use this command.")
    user_id=str(user.id)
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        # Check if the user already exists in the database
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_exists = cursor.fetchone()
        
        if not user_exists:
            # If user doesn't exist, insert them into the database with premium status
            cursor.execute("INSERT INTO users (id, d_mission, d_report, d_tower, d_ch, mission, report, tower, ch, date, premium) VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0, CURDATE(), 'True')", (user_id,))
            connection.commit()
            await ctx.send(f"User **{user.name}** added to the database and granted premium status.")
        else:
            # If user exists, update their premium status to True
            cursor.execute("UPDATE users SET premium = 'True' WHERE id = %s", (user_id,))
            connection.commit()
            await ctx.send(f"User **{user.name}** updated to premium status.")
    
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        await ctx.send("An error occurred while processing your request.")


@bot.command()
async def top(ctx, field: str):
    connection = connect_to_database()
    cursor = connection.cursor()
    m_list=["m","mission","mession","messions","missions","mes","mis"]
    r_list=["r","rep","report","reports"]
    ch_list=["c","ch","challange","chalange","challanges"]
    t_list=["t","to","tow","tower"]
    if field.lower() in m_list:
        field="mission"
    elif field.lower() in r_list:
        field="report"
    elif field.lower() in ch_list:
        field="ch"
    elif field.lower() in t_list:
        field="tower"
    else:
        await ctx.send("Please choose a valid field (`'m','r','ch','t'`)")
        return  # End command if invalid field is chosen

    try:
        cursor.execute(f"SELECT id, {field} FROM users ORDER BY {field} DESC LIMIT 10")  # Assuming you want top 10
        top_list = cursor.fetchall()
        connection.commit()

        embed = discord.Embed(title=f"Top 10 Leaderboard for {field.capitalize()}", color=discord.Color.blue())

        for index, entry in enumerate(top_list):
            user_id, value = entry
            user_id=int(user_id)
            user = await bot.fetch_user(user_id)  # Replace with appropriate method to get user object
            print(user)
            if user:
                embed.add_field(name=f"#{index + 1}: {user.display_name}", value=f"{field.capitalize()}: {value}", inline=False)
            else:
                embed.add_field(name=f"#{index + 1}: <@{user_id}>", value=f"{field.capitalize()}: {value}", inline=False)

        await ctx.send(embed=embed)

    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        await ctx.send("An error occurred while processing your request.")

    cursor.close()
    connection.close()


@bot.tree.command(name="premium", description="Give User Premium Role And Premium NB/AUTOFARM")
async def premium(interaction: discord.Interaction, user: discord.Member):
    if interaction.user.id != bot.owner_id:
        return await interaction.response.send_message("Only the bot owner can use this command.",ephemeral=True)
    user_id = str(user.id)
    connection = connect_to_database()
    cursor = connection.cursor()
    try:
        # Send initial response indicating command is being processed
        await interaction.response.send_message(f"Processing your request for user **{user.name}**...")

        # Check if the user already exists in the database
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user_exists = cursor.fetchone()

        if not user_exists:
            # If user doesn't exist, insert them into the database with premium status
            cursor.execute("INSERT INTO users (id, d_mission, d_report, d_tower, d_ch, mission, report, tower, ch, date, premium) VALUES (%s, 0, 0, 0, 0, 0, 0, 0, 0, CURDATE(), 'True')", (user_id,))
            connection.commit()
            await interaction.followup.send(f"User **{user.name}** added to the database and granted premium status.")
        else:
            # If user exists, update their premium status to True
            cursor.execute("UPDATE users SET premium = 'True' WHERE id = %s", (user_id,))
            connection.commit()
            await interaction.followup.send(f"User **{user.name}** updated to premium status.")

    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        await interaction.followup.send("An error occurred while processing your request.")

@bot.tree.command(name="top", description="Get Top 10 Users In Leaderboard")
async def top(interaction: discord.Interaction, field: str):
    connection = connect_to_database()
    cursor = connection.cursor()
    m_list=["m","mission","mession","messions","missions","mes","mis"]
    r_list=["r","rep","report","reports"]
    ch_list=["c","ch","challange","chalange","challanges"]
    t_list=["t","to","tow","tower"]
    if field.lower() in m_list:
        field="mission"
    elif field.lower() in r_list:
        field="report"
    elif field.lower() in ch_list:
        field="ch"
    elif field.lower() in t_list:
        field="tower"
    else:
        await interaction.response.send_message("Please choose a valid field (`'m','r','ch','t'`)",ephemeral=True)
        return  # End command if invalid field is chosen

    try:
        cursor.execute(f"SELECT id, {field} FROM users ORDER BY {field} DESC LIMIT 10")  # Assuming you want top 10
        top_list = cursor.fetchall()
        connection.commit()

        embed = discord.Embed(title=f"Top 10 Leaderboard for {field.capitalize()}", color=discord.Color.blue())

        for index, entry in enumerate(top_list):
            user_id, value = entry
            user_id=int(user_id)
            user = await bot.fetch_user(user_id)  # Replace with appropriate method to get user object
            if user:
                embed.add_field(name=f"#{index + 1}: {user.display_name}", value=f"{field.capitalize()}: {value}", inline=False)
            else:
                embed.add_field(name=f"#{index + 1}: <@{user_id}>", value=f"{field.capitalize()}: {value}", inline=False)
        await interaction.response.send_message(embed=embed)
    except mysql.connector.Error as e:
        print("Error while connecting to MySQL", e)
        await interaction.response.send_message("An error occurred while processing your request.")

    cursor.close()
    connection.close()
bot.run(token)