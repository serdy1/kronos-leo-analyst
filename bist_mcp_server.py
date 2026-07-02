import yfinance as yf
import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, time
import pytz
from mcp.server.fastmcp import FastMCP

# Konfigürasyon
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BIST-Scanner-v6")
mcp = FastMCP("BIST Intelligence Terminal v6.0")

# TRT Timezone
TRT = pytz.timezone('Europe/Istanbul')

def is_bist_trading_hours():
    """BIST işlem saatleri (09:55 - 18:10 TRT) kontrolü."""
    now = datetime.now(TRT)
    if now.weekday() >= 5: # Hafta sonu
        return False
    current_time = now.time()
    return time(9, 55) <= current_time <= time(18, 10)

def scrape_bigpara(symbol: str):
    """Fallback 1: Bigpara scraping."""
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
    """Fallback 2: Mynet scraping."""
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
    """Triple-Source Redundancy & Volatility Guard."""
    prices = []
    
    # Source 1: yfinance
    try:
        ticker = yf.Ticker(symbol)
        yf_price = ticker.fast_info.last_price
        if yf_price and yf_price > 0:
            prices.append(yf_price)
    except Exception as e:
        logger.error(f"yfinance error for {symbol}: {e}")

    # Source 2 & 3 (Only for BIST symbols)
    if ".IS" in symbol:
        bp_price = scrape_bigpara(symbol)
        if bp_price: prices.append(bp_price)
        
        mn_price = scrape_mynet(symbol)
        if mn_price: prices.append(mn_price)

    if not prices:
        return None

    # Volatility Guard: Anomali kontrolü (Medyan kullanarak sapmaları filtrele)
    prices.sort()
    median_price = prices[len(prices)//2]
    
    # Sanity Cross-check: Eğer bir kaynak medyan fiyattan %10'dan fazla sapıyorsa onu ele
    valid_prices = [p for p in prices if 0.9 * median_price <= p <= 1.1 * median_price]
    
    return sum(valid_prices) / len(valid_prices) if valid_prices else median_price

@mcp.tool()
async def get_market_data(ticker: str) -> str:
    """
    Self-healing Telemetry System v6.0
    Triple-Source Redundancy: yfinance -> Bigpara -> Mynet
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
        "GOLD": "GC=F"
    }
    
    query = ticker.upper().strip()
    symbol = mapping.get(query, query if ".IS" in query or "=" in query else f"{query}.IS")
    
    # Fixed USD/TRY Decoupling (Highest Senior Boss Requirement)
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
