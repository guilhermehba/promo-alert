import requests
import schedule
import time
from datetime import datetime

# =========================
# CONFIGURAÇÕES PRINCIPAIS
# =========================
API_BASE_URL = "https://api.isthereanydeal.com/v01/"
API_KEY = "SUA_API_KEY_AQUI"  # Coloque aqui sua API key do isthereanydeal
GAMES = ["Cyberpunk 2077", "Elden Ring", "Red Dead Redemption 2"]
CURRENCY = "BRL"  # Forçar a API a trazer preços em reais (R$)

# =========================
# FUNÇÕES AUXILIARES
# =========================
def get_game_plain(game_name: str) -> str:
    """
    Pega o identificador 'plain' do jogo a partir do nome.
    Esse plain é necessário para consultar os preços na API.
    """
    url = f"{API_BASE_URL}game/plain/"
    params = {
        "key": API_KEY,
        "title": game_name
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        plain = data.get("data", {}).get("plain")
        if plain:
            return plain
        else:
            print(f"[ERRO] Não foi possível encontrar plain para {game_name}")
            return None
    except Exception as e:
        print(f"[ERRO] Falha ao buscar plain de {game_name}: {e}")
        return None


def get_game_deals(plain: str) -> dict:
    """
    Pega os preços em reais (BRL) para o jogo especificado pelo plain.
    """
    url = f"{API_BASE_URL}game/prices/"
    params = {
        "key": API_KEY,
        "plains": plain,
        "region": "BR",   # Região Brasil
        "country": "BR",  # País Brasil
        "shops": "steam,epic,gog,greenmangaming,hb"  # Algumas lojas suportadas
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        deals = data.get("data", {}).get(plain, {}).get("list", [])
        return deals
    except Exception as e:
        print(f"[ERRO] Falha ao buscar preços: {e}")
        return []


def check_promotions():
    """
    Verifica promoções em reais para todos os jogos configurados.
    """
    print("="*50)
    print(f"Verificação de promoções - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("="*50)

    for game in GAMES:
        plain = get_game_plain(game)
        if not plain:
            continue

        deals = get_game_deals(plain)
        if not deals:
            print(f"Nenhuma promoção encontrada para {game}.")
            continue

        # Mostrar as melhores promoções
        print(f"\n🎮 {game}")
        for deal in deals[:3]:  # mostra só os 3 melhores preços
            shop = deal.get("shop", {}).get("name", "Desconhecido")
            price_new = deal.get("price_new", 0)
            price_old = deal.get("price_old", 0)
            discount = deal.get("price_cut", 0)

            print(f"  - Loja: {shop}")
            print(f"    Preço atual: R${price_new:.2f}")
            print(f"    Preço anterior: R${price_old:.2f}")
            print(f"    Desconto: {discount}%\n")


# =========================
# AGENDAMENTO AUTOMÁTICO
# =========================
def run_scheduler():
    # Define horário fixo: todo dia às 10h
    schedule.every().day.at("10:00").do(check_promotions)

    print("🔔 Monitor de promoções iniciado!")
    print("Esperando próximo horário agendado...\n")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    # Rodar imediatamente na inicialização
    check_promotions()
    # Ativar agendamento diário
    run_scheduler()
