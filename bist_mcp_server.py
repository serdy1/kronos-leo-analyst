import yfinance as yf
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
import pytz
import re
from mcp.server.fastmcp import FastMCP

# Konfigürasyon
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BIST-Scanner-v7")
mcp = FastMCP("BIST Intelligence Terminal v7.0")

# TRT Timezone
TRT = pytz.timezone('Europe/Istanbul')

def is_bist_trading_hours():
    """BIST işlem saatleri (09:55 - 18:10 TRT) kontrolü."""
    now = datetime.now(TRT)
    if now.weekday() >= 5: # Hafta sonu
        return False
    current_time = now.time()
    return time(9, 55) <= current_time <= time(18, 10)

def scrape_midas(symbol: str):
    """Primary Source: Midas Canlı Borsa."""
    try:
        clean_symbol = symbol.replace(".IS", "").upper()
        # Midas uses a consolidated page for many tickers
        url = "https://www.getmidas.com/canli-borsa/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
        }
        # Note: In production, we might want to cache this page for 60s to avoid hammering
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Method 1: Row Search
        rows = soup.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if cells and clean_symbol == cells[0].get_text(strip=True):
                price_text = cells[1].get_text(strip=True).replace(".", "").replace(",", ".")
                return float(price_text)
                
        # Method 2: Link Search
        link = soup.find('a', string=re.compile(f"^{clean_symbol}$", re.I))
        if link:
            parent_row = link.find_parent('tr')
            if parent_row:
                cells = parent_row.find_all('td')
                if len(cells) > 1:
                    price_text = cells[1].get_text(strip=True).replace(".", "").replace(",", ".")
                    return float(price_text)
    except Exception as e:
        logger.error(f"Midas scraping error for {symbol}: {e}")
    return None

def scrape_bigpara(symbol: str):
    """Fallback 2: Bigpara scraping."""
    try:
        clean_symbol = symbol.replace(".IS", "").lower()
        url = f"https://bigpara.hurriyet.com.tr/borsa/hisse-fiyatlari/{clean_symbol}-detay/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_span = soup.find('span', {'class': 'lastPrice'})
        if price_span:
            return float(price_span.text.replace(",", "."))
    except Exception as e:
        logger.error(f"Bigpara scraping error for {symbol}: {e}")
    return None

def scrape_mynet(symbol: str):
    """Fallback 3: Mynet scraping."""
    try:
        clean_symbol = symbol.replace(".IS", "").lower()
        url = f"https://finans.mynet.com/borsa/hisseler/{clean_symbol}/"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(response.content, 'html.parser')
        price_div = soup.find('div', {'class': 'fn-price'})
        if price_div:
            return float(price_div.text.replace(",", ".").strip())
    except Exception as e:
        logger.error(f"Mynet scraping error for {symbol}: {e}")
    return None

def get_ticker_price(symbol: str):
    """Multi-Source Redundancy & Volatility Guard."""
    prices = []
    
    # Source 1: Midas (Primary for BIST)
    if ".IS" in symbol:
        midas_price = scrape_midas(symbol)
        if midas_price: prices.append(midas_price)

    # Source 2: yfinance (Primary for Global, Fallback for BIST)
    try:
        ticker = yf.Ticker(symbol)
        yf_price = ticker.fast_info.last_price
        if yf_price and yf_price > 0:
            prices.append(yf_price)
    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")

    # Source 3 & 4 (Fallback for BIST)
    if ".IS" in symbol:
        bp_price = scrape_bigpara(symbol)
        if bp_price: prices.append(bp_price)
        
        mn_price = scrape_mynet(symbol)
        if mn_price: prices.append(mn_price)

    if not prices:
        return None

    # Volatility Guard: Anomali kontrolü
    prices.sort()
    median_price = prices[len(prices)//2]
    valid_prices = [p for p in prices if 0.9 * median_price <= p <= 1.1 * median_price]
    
    return sum(valid_prices) / len(valid_prices) if valid_prices else median_price

@mcp.tool()
async def get_market_data(ticker: str) -> str:
    """
    Self-healing Telemetry System v7.0
    Primary Source: Midas (BIST ground-truth)
    Triple-Source Fallback: yfinance -> Bigpara -> Mynet
    Volatility Guard: Anomaly cross-checks active.
    USD/TRY Decoupling: Strict 46.67 rate active.
    """
    mapping = {
        "XU100": "XU100.IS",
        "FROTO": "FROTO.IS",
        "PGSUS": "PGSUS.IS",
        "ANHYT": "ANHYT.IS",
        "USDTRY": "USDTRY=X",
        "BTC": "BTC-USD",
        "GOLD": "GC=F",
        "KCHOL": "KCHOL.IS",
        "THYAO": "THYAO.IS",
        "DOAS": "DOAS.IS"
    }
    
    query = ticker.upper().strip()
    symbol = mapping.get(query, query if ".IS" in query or "=" in query else f"{query}.IS")
    
    # Fixed USD/TRY Decoupling
    FIXED_USDTRY = 46.67
    
    price = get_ticker_price(symbol)
    if price is None:
        return f"Error: {query} verisi çekilemedi. Telemetry failed."

    # TTL Context
    is_active = is_bist_trading_hours()
    ttl = "60s (ACTIVE)" if is_active else "3600s (IDLE)"

    if query == "BTC":
        price_tl = price * FIXED_USDTRY
        return f"BTC: {price:,.2f} USD | {price_tl:,.2f} TL [TTL: {ttl}]"
    
    if query == "GOLD":
        gram_gold_tl = (price / 31.1035) * FIXED_USDTRY
        return f"Ons Altın: {price:,.2f} USD | Gram Altın: {gram_gold_tl:,.2f} TL [TTL: {ttl}]"

    if query == "USDTRY":
        return f"USD/TRY: {FIXED_USDTRY} (DECOUPLED) | Market: {price:.4f} [TTL: {ttl}]"

    return f"{query}: {price:,.2f} {'TL' if '.IS' in symbol else 'USD'} [TTL: {ttl}]"

if __name__ == "__main__":
    mcp.run()
