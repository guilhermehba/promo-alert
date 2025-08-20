import os
import requests
import urllib.parse

# ============================================
# CONFIGURAÇÕES BÁSICAS
# ============================================

# Token e chat_id serão lidos das variáveis de ambiente configuradas no GitHub
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# URL base da API do Telegram
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
# FUNÇÃO PARA VERIFICAR PROMOÇÕES NA STEAM
# ============================================
def check_game_discount(game_name: str):
    """
    Busca o jogo na API da Steam e verifica se está em promoção.
    Retorna uma string com o resultado.
    """
    try:
        # 1. Buscar o ID do jogo na Steam
        search_url = "https://store.steampowered.com/api/storesearch"
        params = {"term": game_name, "l": "english", "cc": "us"}
        response = requests.get(search_url, params=params)
        data = response.json()

        if not data.get("items"):
            return f"🔎 {game_name}: não encontrado na Steam."

        # Pega o primeiro resultado
        game = data["items"][0]
        appid = game["id"]

        # 2. Buscar detalhes do jogo
        details_url = f"https://store.steampowered.com/api/appdetails"
        params = {"appids": appid, "cc": "us", "l": "english"}
        response = requests.get(details_url, params=params)
        details = response.json()

        if not details[str(appid)]["success"]:
            return f"⚠️ {game_name}: erro ao buscar detalhes."

        game_data = details[str(appid)]["data"]

        # 3. Verificar promoções
        price_info = game_data.get("price_overview")
        if not price_info:
            return f"🎮 {game_name}: Jogo grátis ou sem preço listado."

        initial_price = price_info["initial"] / 100
        final_price = price_info["final"] / 100
        discount = price_info["discount_percent"]

        if discount > 0:
            return (
                f"🔥 <b>{game_name}</b> está em promoção!\n"
                f"💵 Preço original: ${initial_price:.2f}\n"
                f"💲 Preço com desconto: ${final_price:.2f}\n"
                f"📉 Desconto: {discount}%\n"
                f"🔗 <a href='https://store.steampowered.com/app/{appid}'>Ver na Steam</a>"
            )
        else:
            return f"❌ {game_name}: sem promoção. Preço atual: ${final_price:.2f}"

    except Exception as e:
        return f"⚠️ Erro ao verificar {game_name}: {e}"


# ============================================
# FUNÇÃO PRINCIPAL
# ============================================
def check_games():
    """
    Lê os jogos do arquivo games.txt e verifica promoções para cada um.
    """
    if not os.path.exists("games.txt"):
        send_telegram_message("⚠️ ERRO: O arquivo games.txt não foi encontrado.")
        return

    with open("games.txt", "r", encoding="utf-8") as file:
        games = [line.strip() for line in file.readlines() if line.strip()]

    if not games:
        send_telegram_message("⚠️ ERRO: Nenhum jogo listado em games.txt.")
        return

    for game in games:
        result = check_game_discount(game)
        send_telegram_message(result)


# ============================================
# EXECUÇÃO DO SCRIPT
# ============================================
if __name__ == "__main__":
    check_games()
