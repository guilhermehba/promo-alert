import requests
from bs4 import BeautifulSoup
from datetime import datetime

# ===== CONFIGURAÇÕES =====
JOGOS = ["Elden Ring", "Baldur's Gate 3", "Cyberpunk 2077"]
URLS = {
    "Steam": "https://store.steampowered.com/search/?term={}",
    "Nuuvem": "https://www.nuuvem.com/catalog/page/1/search/{}/price/sale"
}

# ===== DADOS DO TELEGRAM =====
TELEGRAM_TOKEN = "8301083964:AAGowxDYx_OQ0NPO7GE61MCp8emWLGURnjg"  # substitua pelo token do BotFather
CHAT_ID = 424718791  # seu chat_id real

# ===== FUNÇÕES =====
def enviar_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=payload)

def verificar_promocoes():
    resultados = []

    for jogo in JOGOS:
        for loja, url in URLS.items():
            r = requests.get(url.format(jogo))
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "html.parser")
                
                # --- Steam ---
                if loja == "Steam":
                    desconto = soup.find("span", {"class": "search_discount"})
                    preco = soup.find("div", {"class": "discount_final_price"})
                    if desconto and desconto.text.strip():
                        resultados.append(f"[{loja}] {jogo}: {desconto.text.strip()} → {preco.text.strip()}")

                # --- Nuuvem ---
                if loja == "Nuuvem":
                    desconto = soup.find("span", {"class": "price-discount"})
                    preco = soup.find("span", {"class": "price-current"})
                    if desconto and preco:
                        resultados.append(f"[{loja}] {jogo}: {desconto.text.strip()} → {preco.text.strip()}")

    return resultados

# ===== MAIN =====
if __name__ == "__main__":
    hoje = datetime.now().strftime("%d/%m/%Y %H:%M")
    promocoes = verificar_promocoes()

    if promocoes:
        mensagem = f"🔥 Promoções encontradas em {hoje}:\n\n" + "\n".join(promocoes)
    else:
        mensagem = f"Sem promoções para seus jogos em {hoje}."

    enviar_telegram(mensagem)
