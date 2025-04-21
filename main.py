import discord
from discord.ext import commands
import random

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

user_data = {}

suits = ['♠', '♦', '♣', '♥']
values = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
    '7': 7, '8': 8, '9': 9, '10': 10,
    'J': 10, 'Q': 10, 'K': 10, 'A': 11
}


def draw_card():
    value = random.choice(list(values.keys()))
    suit = random.choice(suits)
    return f"{suit}{value}", values[value], value


def calculate_hand(hand_values):
    total = sum(hand_values)
    aces = hand_values.count(11)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


@bot.event
async def on_ready():
    print(f"Bot ist online als {bot.user}")


@bot.command()
async def blackjack(ctx, einsatz: int):
    user_id = str(ctx.author.id)

    if user_id not in user_data:
        user_data[user_id] = {"coins": 1000}
        await ctx.send(f"{ctx.author.mention} Willkommen! Du erhältst 1000 AcesCoins.")

    coins = user_data[user_id]["coins"]

    if einsatz < 1 or einsatz > 5000:
        await ctx.send("Der Einsatz muss zwischen 1 und 5000 AcesCoins liegen.")
        return

    if coins < einsatz:
        await ctx.send("Du hast nicht genug AcesCoins.")
        return

    player_cards = []
    dealer_cards = []

    player_values = []
    dealer_values = []

    for _ in range(2):
        card, val, raw = draw_card()
        player_cards.append(card)
        player_values.append(val)

    for _ in range(2):
        card, val, raw = draw_card()
        dealer_cards.append(card)
        dealer_values.append(val)

    player_total = calculate_hand(player_values)
    dealer_total = calculate_hand(dealer_values)

    def get_hand_str(name, cards, total):
        return f"**{name}**: {' • '.join(cards)}\nWert: {total}"

    msg = await ctx.send(embed=discord.Embed(
        title="🚩Red Aces Blackjack🃏",
        description=f"Einsatz: {einsatz} AcesCoins\n\n"
                    f"{get_hand_str('Spieler: ' + ctx.author.name, player_cards, player_total)}\n\n"
                    f"{get_hand_str('Dealer: Der Bär🐻', [dealer_cards[0], '??'], '?')}",
        color=discord.Color.red()
    ))

    await msg.add_reaction("✋")  # Stand
    await msg.add_reaction("🃏")  # Hit

    def check(reaction, user):
        return user == ctx.author and reaction.message.id == msg.id and str(reaction.emoji) in ["✋", "🃏"]

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        except:
            await ctx.send("Zeit abgelaufen.")
            return

        if str(reaction.emoji) == "🃏":
            card, val, raw = draw_card()
            player_cards.append(card)
            player_values.append(val)
            player_total = calculate_hand(player_values)

            if player_total > 21:
                user_data[user_id]["coins"] -= einsatz
                await ctx.send(embed=discord.Embed(
                    title="🚩Red Aces Blackjack🃏",
                    description=f"Einsatz: {einsatz} AcesCoins\n\n"
                                f"{get_hand_str('Spieler: ' + ctx.author.name, player_cards, player_total)}\n\n"
                                f"{get_hand_str('Dealer: Der Bär🐻', dealer_cards, dealer_total)}\n\n"
                                f"**Du hast verloren!** Neuer Kontostand: {user_data[user_id]['coins']} AcesCoins",
                    color=discord.Color.dark_red()
                ))
                return
            else:
                await msg.edit(embed=discord.Embed(
                    title="🚩Red Aces Blackjack🃏",
                    description=f"Einsatz: {einsatz} AcesCoins\n\n"
                                f"{get_hand_str('Spieler: ' + ctx.author.name, player_cards, player_total)}\n\n"
                                f"{get_hand_str('Dealer: Der Bär🐻', [dealer_cards[0], '??'], '?')}",
                    color=discord.Color.red()
                ))
        elif str(reaction.emoji) == "✋":
            while dealer_total < 17:
                card, val, raw = draw_card()
                dealer_cards.append(card)
                dealer_values.append(val)
                dealer_total = calculate_hand(dealer_values)

            result_text = ""
            if dealer_total > 21 or player_total > dealer_total:
                user_data[user_id]["coins"] += einsatz
                result_text = f"**Du hast gewonnen!** Neuer Kontostand: {user_data[user_id]['coins']} AcesCoins"
            elif player_total < dealer_total:
                user_data[user_id]["coins"] -= einsatz
                result_text = f"**Du hast verloren!** Neuer Kontostand: {user_data[user_id]['coins']} AcesCoins"
            else:
                result_text = f"**Unentschieden!** Kontostand bleibt: {user_data[user_id]['coins']} AcesCoins"

            await ctx.send(embed=discord.Embed(
                title="🚩Red Aces Blackjack🃏",
                description=f"Einsatz: {einsatz} AcesCoins\n\n"
                            f"{get_hand_str('Spieler: ' + ctx.author.name, player_cards, player_total)}\n\n"
                            f"{get_hand_str('Dealer: Der Bär🐻', dealer_cards, dealer_total)}\n\n"
                            f"{result_text}",
                color=discord.Color.green() if "gewonnen" in result_text else discord.Color.orange()
            ))
            return
