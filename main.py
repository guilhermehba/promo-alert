import os
import requests

# ============================================
# CONFIGURAÇÕES BÁSICAS
# ============================================
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TELEGRAM_URL = f"https://api.telegram.org/bot{TOKEN}/sendMessage"


# ============================================
# FUNÇÃO PARA ENVIAR MENSAGEM NO TELEGRAM
# ============================================
def send_telegram_message(text: str):
    """
    Envia uma mensagem para o Telegram usando o bot.
    """
    if not TOKEN or not CHAT_ID:
        print("❌ ERRO: TELEGRAM_TOKEN ou CHAT_ID não configurados.")
        return

    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
    response = requests.post(TELEGRAM_URL, data=payload)

    if response.status_code == 200:
        print("✅ Mensagem enviada com sucesso:", text)
    else:
        print("❌ Erro ao enviar mensagem:", response.text)


# ============================================
# STEAM
# ============================================
def check_steam(game_name: str):
    try:
        search_url = "https://store.steampowered.com/api/storesearch"
        params = {"term": game_name, "l": "portuguese", "cc": "br"}
        response = requests.get(search_url, params=params)
        data = response.json()

        if not data.get("items"):
            return f"🔎 {game_name}: não encontrado na Steam."

        game = data["items"][0]
        appid = game["id"]

        details_url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": appid, "cc": "br", "l": "portuguese"}
        response = requests.get(details_url, params=params)
        details = response.json()

        if not details[str(appid)]["success"]:
            return f"⚠️ {game_name}: erro ao buscar detalhes na Steam."

        game_data = details[str(appid)]["data"]
        price_info = game_data.get("price_overview")
        if not price_info:
            return f"🎮 {game_name} (Steam): grátis ou sem preço listado."

        initial_price = price_info["initial"] / 100
        final_price = price_info["final"] / 100
        discount = price_info["discount_percent"]

        if discount > 0:
            return (
                f"🔥 <b>{game_name}</b> (Steam)\n"
                f"💵 Preço original: R$ {initial_price:.2f}\n"
                f"💲 Preço com desconto: R$ {final_price:.2f}\n"
                f"📉 Desconto: {discount}%\n"
                f"🔗 <a href='https://store.steampowered.com/app/{appid}'>Ver na Steam</a>"
            )
        else:
            return f"❌ {game_name} (Steam): sem promoção. Preço atual: R$ {final_price:.2f}"

    except Exception as e:
        return f"⚠️ Erro Steam ({game_name}): {e}"


# ============================================
# NUVEM
# ============================================
def check_nuuvem(game_name: str):
    try:
        search_url = "https://www.nuuvem.com/br-pt/catalog.json"
        params = {"q": game_name}
        response = requests.get(search_url, params=params)
        data = response.json()

        products = data.get("products", [])
        if not products:
            return f"🔎 {game_name}: não encontrado na Nuuvem."

        game = products[0]
        name = game.get("name")
        url = f"https://www.nuuvem.com{game.get('url')}"
        price_info = game.get("price", {})

        if not price_info:
            return f"🎮 {name} (Nuuvem): grátis ou sem preço listado."

        initial = float(price_info.get("amount", price_info.get("original_amount", 0)))
        promo = float(price_info.get("promotional_amount", initial))
        discount = game.get("discount", {}).get("percentage", 0)

        if discount > 0:
            return (
                f"🔥 <b>{name}</b> (Nuuvem)\n"
                f"💵 Preço original: R$ {initial:.2f}\n"
                f"💲 Preço com desconto: R$ {promo:.2f}\n"
                f"📉 Desconto: {discount}%\n"
                f"🔗 <a href='{url}'>Ver na Nuuvem</a>"
            )
        else:
            return f"❌ {name} (Nuuvem): sem promoção. Preço atual: R$ {initial:.2f}"

    except Exception as e:
        return f"⚠️ Erro Nuuvem ({game_name}): {e}"


# ============================================
# GREEN MAN GAMING (GMG)
# ============================================
def check_gmg(game_name: str):
    try:
        search_url = "https://www.greenmangaming.com/api/v2/catalogue/search/"
        params = {"query": game_name, "country": "BR"}
        response = requests.get(search_url, params=params)
        data = response.json()

        products = data.get("products", [])
        if not products:
            return f"🔎 {game_name}: não encontrado na GMG."

        game = products[0]
        name = game.get("name")
        url = f"https://www.greenmangaming.com{game.get('url')}"
        price_info = game.get("price", {})

        if not price_info:
            return f"🎮 {name} (GMG): grátis ou sem preço listado."

        initial = float(price_info.get("rrp", 0))
        promo = float(price_info.get("price", initial))
        discount = int(round(100 - (promo * 100 / initial))) if initial > 0 else 0

        if discount > 0:
            return (
                f"🔥 <b>{name}</b> (GMG)\n"
                f"💵 Preço original: R$ {initial:.2f}\n"
                f"💲 Preço com desconto: R$ {promo:.2f}\n"
                f"📉 Desconto: {discount}%\n"
                f"🔗 <a href='{url}'>Ver na GMG</a>"
            )
        else:
            return f"❌ {name} (GMG): sem promoção. Preço atual: R$ {promo:.2f}"

    except Exception as e:
        return f"⚠️ Erro GMG ({game_name}): {e}"


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def check_games():
    if not os.path.exists("games.txt"):
        send_telegram_message("⚠️ ERRO: O arquivo games.txt não foi encontrado.")
        return

    with open("games.txt", "r", encoding="utf-8") as file:
        games = [line.strip() for line in file.readlines() if line.strip()]

    if not games:
        send_telegram_message("⚠️ ERRO: Nenhum jogo listado em games.txt.")
        return

    for game in games:
        # Steam
        send_telegram_message(check_steam(game))
        # Nuuvem
        send_telegram_message(check_nuuvem(game))
        # GMG
        send_telegram_message(check_gmg(game))


# ============================================
# EXECUÇÃO DO SCRIPT
# ============================================
if __name__ == "__main__":
    check_games()
