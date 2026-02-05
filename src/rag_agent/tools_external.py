"""
External Tools for World Knowledge (Weather, News, Travel, Shopping, Flights).
"""
from typing import Optional
import requests
from langchain_core.tools import tool
from duckduckgo_search import DDGS
from functools import lru_cache
import warnings
import logging

# GLOBALLY Suppress the noisy "package renamed" warning from duckduckgo_search
warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")
warnings.filterwarnings("ignore", category=UserWarning, module="duckduckgo_search")
logging.getLogger("duckduckgo_search").setLevel(logging.ERROR)

# Direct DDGS usage replaces LangChain wrapper

# --- CACHED IMPLEMENTATIONS ---

# @lru_cache(maxsize=32) -- REMOVED FOR LIVE UPDATES
def _fetch_weather(city_name: str) -> str:
    try:
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_res = requests.get(geo_url).json()
        
        if not geo_res.get("results"):
            return f"Error: Could not find location '{city_name}'"
            
        location = geo_res["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        name = location["name"]
        country = location.get("country", "")
        
        # 2. Weather Data
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,apparent_temperature&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
        w_res = requests.get(weather_url).json()
        
        if "error" in w_res:
            return f"Error fetching weather: {w_res['reason']}"
            
        current = w_res["current"]
        daily = w_res["daily"]
        
        # Mapping WMO codes to text (Simplified)
        wmo_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm"
        }
        
        # Icon Map
        icon_map = {
            0: "☀️", 1: "🌤️", 2: "⛅", 3: "☁️",
            45: "🌫️", 48: "🌫️",
            51: "🌦️", 53: "🌧️", 55: "🌧️",
            61: "🌧️", 63: "🌧️", 65: "⛈️",
            71: "🌨️", 73: "🌨️", 75: "❄️",
            95: "⚡"
        }
        
        curr_cond = wmo_map.get(current["weather_code"], "Unknown")
        curr_icon = icon_map.get(current["weather_code"], "🌡️")
        
        # Helper for C/F
        def fmt_temp(c_val):
            f_val = (c_val * 9/5) + 32
            return f"{c_val}°C <span style='opacity:0.5; font-size: 0.8em;'>/ {f_val:.1f}°F</span>"

        # Build Forecast Items HTML
        forecast_html = ""
        for i in range(len(daily["time"])):
            date = daily["time"][i]
            # Simple Date Format (2025-01-01 -> Jan 01)
            try:
                d_obj = datetime.strptime(date, "%Y-%m-%d")
                date_str = d_obj.strftime("%a, %b %d")
            except:
                date_str = date
                
            max_t = daily["temperature_2m_max"][i]
            min_t = daily["temperature_2m_min"][i]
            max_f = (max_t * 9/5) + 32
            min_f = (min_t * 9/5) + 32
            
            code = daily["weather_code"][i]
            cond = wmo_map.get(code, "-")
            icon = icon_map.get(code, "🌡️")
            
            forecast_html += f"""<div class="forecast-item">
<div class="forecast-date">{date_str}</div>
<div class="forecast-icon">{icon}</div>
<div class="forecast-temp">{max_t}° <span style="opacity:0.5; font-size:0.8em">{max_f:.0f}°F</span></div>
<div class="forecast-desc">{cond}</div>
</div>"""

        # Apparent Temp
        app_c = current.get('apparent_temperature', current['temperature_2m'])
        app_f = (app_c * 9/5) + 32

        # Build Main Card HTML
        card_html = f"""<section class="weather-card">
<div class="weather-header">
<div class="weather-main">
<div class="weather-icon-big" style="font-size: 4rem;">{curr_icon}</div>
<div class="weather-temp-big">{current['temperature_2m']}°C <br><span style="font-size:0.5em; opacity:0.7">{((current['temperature_2m'] * 9/5) + 32):.1f}°F</span></div>
<div class="weather-meta">
<div class="weather-condition">{curr_cond}</div>
<div class="weather-location">📍 {name}, {country}</div>
</div>
</div>
</div>
<div class="weather-stats-grid">
<div class="weather-stat-item">
<span class="stat-label">Humidity</span>
<span class="stat-value">{current['relative_humidity_2m']}%</span>
</div>
<div class="weather-stat-item">
<span class="stat-label">Wind</span>
<span class="stat-value">{current['wind_speed_10m']} <span style="font-size:0.7em">km/h</span></span>
</div>
<div class="weather-stat-item">
<span class="stat-label">Feels Like</span>
<span class="stat-value">{app_c:.1f}° <span style="font-size:0.7em; opacity:0.7">/ {app_f:.1f}°F</span></span>
</div>
</div>
<div class="weather-forecast-scroll">
{forecast_html}
</div>
</section>"""
        return card_html
    except Exception as e:
        return f"Error: {e}"

# @lru_cache(maxsize=32) -- REMOVED FOR LIVE UPDATES
def _fetch_news(topic: str) -> str:
    try:
        query = f"{topic}"
        results = []
        with DDGS() as ddgs:
            # Use 'news' backend which returns {date, title, body, url, image, source}
            news_gen = ddgs.news(query, max_results=6)
            for r in news_gen:
                title = r.get('title', 'No Title')
                link = r.get('url', r.get('href', '#'))
                body = r.get('body', 'No description.')
                image = r.get('image', '')
                source = r.get('source', 'Unknown')
                date = r.get('date', '')

                # Format as a visual card
                card = f"### {title}\n"
                if image:
                    card += f"![{title}]({image})\n"
                card += f"**Source**: {source} ({date})\n\n"
                card += f"{body}\n\n"
                card += f"[**Read Full Article**]({link})"
                results.append(card)
        
        if not results: return "No news found."
        return f"**Latest News for '{topic}':**\n\n---\n\n" + "\n\n---\n\n".join(results)
    except Exception as e:
        error_msg = str(e)
        if "ratelimit" in error_msg.lower() or "429" in error_msg:
             return f"**News Error**: The news engine is currently rate limited. Please try again in 5-10 seconds."
        return f"**News Search Failed**: {error_msg}"

# @lru_cache(maxsize=32) -- REMOVED FOR LIVE UPDATES
def _fetch_news_archive(topic: str, time_range: str = 'd') -> str:
    """
    Fetch news with a specific time range.
    time_range: 'd' (day), 'w' (week), 'm' (month), 'y' (year)
    """
    try:
        query = f"news about {topic}"
        results = []
        range_map = {'d': 'Past Day', 'w': 'Past Week', 'm': 'Past Month', 'y': 'Past Year'}
        range_desc = range_map.get(time_range, 'Recent')
        
        with DDGS() as ddgs:
            # timelimit: d, w, m, y
            for r in ddgs.text(query, timelimit=time_range, max_results=7):
                results.append(f"[{r['title']}]({r['href']}): {r['body']}")
        
        if not results: return f"No {range_desc} news found for '{topic}'."
        return f"**{range_desc} News for '{topic}':**\n\n" + "\n\n".join(results)
    except Exception as e:
        error_msg = str(e)
        if "ratelimit" in error_msg.lower() or "429" in error_msg:
             return f"**Archive Error**: Rate limited. Please try again later."
        return f"**Archive Search Failed**: {error_msg}"

import random

# Real Browser Headers to bypass anti-bot checks
BROWSER_HEADERS = [
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
    {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0"},
    {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"},
    {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
]

def _search_ddg(query_or_list: str | list, header: str) -> str:
    # Silence the annoying "renamed to ddgs" warning
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="duckduckgo_search")
    
    try:
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import time 
        
        queries = [query_or_list] if isinstance(query_or_list, str) else query_or_list
        results = []
        
        # Prioritize HTML (Stealth) - 'api' and 'lite' are often deprecated/throttled
        backends = ["html"]

        def run_single_query(q):
            local_res = []
            # Rotate UA for each attempt
            ua = random.choice(BROWSER_HEADERS)
            
            for backend in backends:
                try:
                    # Pass UA to DDGS (if supported) or just rely on backend behavior
                    # Note: DDGS constructor doesn't formally verify 'headers' in all versions
                    # but we can try passing it if the library allows, or just rely on the retry logic.
                    # Current DDGS versions often auto-manage headers, but retries are key.
                    with DDGS(headers=ua) as ddgs:
                        # Fetch results using specific backend
                        for r in ddgs.text(q, max_results=14, backend=backend):
                            local_res.append(f"[{r['title']}]({r['href']}): {r['body']}")
                    
                    if local_res: 
                        break # Backend worked!
                except Exception as inner_e:
                    # Gentle backoff if rate limited
                    if "ratelimit" in str(inner_e).lower() or "429" in str(inner_e):
                         time.sleep(2.0) # Increase wait
                    elif "timeout" in str(inner_e).lower():
                         time.sleep(1.0)
                    continue
            
            return local_res

        # Parallel Execution
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_query = {executor.submit(run_single_query, q): q for q in queries}
            for future in as_completed(future_to_query):
                results.extend(future.result())
                if len(results) >= 25: break 
                    
        if not results: 
            # Differentiate between "no results found" and "search failed completely"
            return (f"**{header}:**\n\n(Note: Live search returned no results from any browser channel. "
                    "This might be due to strict rate limiting or no relevant content found. "
                    "Answering based on internal knowledge.)")
                    
        # Dedup by URL
        seen_urls = set()
        unique_results = []
        for r in results:
            try:
                # Robust URL extraction
                if "](" in r and "):" in r:
                    url = r.split("](")[1].split(")")[0]
                else:
                    url = str(hash(r)) # Fallback for unique ID

                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)
            except:
                continue
        
        return f"**{header}:**\n\n" + "\n\n".join(unique_results[:15])

    except Exception as e:
        error_msg = str(e)
        if "ratelimit" in error_msg.lower() or "429" in error_msg:
             return f"**Search Error**: The search engine is currently rate limiting requests. Please try again in a few seconds."
        return f"**Search Failed**: {error_msg}. (I will generate a response based on my training data instead.)"

def _generate_dalle_image(prompt: str) -> str:
    """Internal helper to generate DALL-E 3 images."""
    try:
        import os
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return "Error: OpenAI API Key not found."
            
        client = OpenAI(api_key=api_key)
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        revised = response.data[0].revised_prompt
        return f"![Generated Image]({image_url})\n\n*(AI Generated Visualization: {revised})*"
    except Exception as e:
        return f"Error generating image: {e}"

# @lru_cache(maxsize=32) -- REMOVED FOR LIVE UPDATES
def _find_images(query: str) -> str:
    """Try finding real images using robust search."""
    try:
        results = []
        ua = random.choice(BROWSER_HEADERS)
        
        # 1. Primary: DDGS Images (Best Quality but Rate Limited)
        try:
            from duckduckgo_search import DDGS 
            with DDGS(headers=ua) as ddgs:
                search_res = ddgs.images(query, max_results=5)
                for r in search_res:
                    img_url = r.get('image', '')
                    if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        results.append(img_url)
        except Exception:
            pass # Silent fail to fallback
        
        if results:
            return "\n".join(list(set(results))[:3])
            
        # 2. Secondary: Wikimedia Commons API (Robust, Public, No Rate Limit)
        try:
            # print(f"DEBUG: Falling back to Wikimedia for '{query}'...")
            api_url = "https://commons.wikimedia.org/w/api.php"
            params = {
                "action": "query", "format": "json", "generator": "search",
                "gsrnamespace": 6, "gsrsearch": f"{query} filetype:bitmap",
                "gsrlimit": 5, "prop": "imageinfo", "iiprop": "url", "iiurlheight": 600
            }
            wiki_res = requests.get(api_url, params=params, headers={"User-Agent": "EchoMindAI/1.0"}).json()
            pages = wiki_res.get("query", {}).get("pages", {})
            for pid, page in pages.items():
                if "imageinfo" in page:
                    results.append(page["imageinfo"][0]["url"])
        except Exception:
            pass

        if results:
            # Format nicely
            unique = list(set(results))
            return "\n".join([f"![{query}]({url})" for url in unique[:2]]) # Return markdown directly if from Wiki

        # 3. Final Fallback: AI Generation (DALL-E 3)
        # "make sure image is generated properly" -> We generate it if we can't find it.
        # print("DEBUG: No real images found. Generating AI image...")
        return _generate_dalle_image(f"A high quality photo-realistic image of {query}")

    except Exception as e:
        return f"Image Error: {e}"

@tool
def get_stock_price(ticker: str) -> str:
    """
    Get real-time stock price, stats, and 'Buy' links.
    Smartly finds the ticker if a company name is provided (e.g. 'Adani Green' -> 'ADANIGREEN.NS').
    """
    try:
        import yfinance as yf
        from duckduckgo_search import DDGS
        import time

        clean_ticker = ticker.upper().replace("$", "").strip()
        
        # 1. SMART TICKER LOOKUP
        # 1. Fallback: Search for Ticker if input is a company name or robust fallback
        if " " in clean_ticker or len(clean_ticker) > 3:
            
            # 1a. HARDCODED FALLBACKS (Robustness against DDGS Rate Limits)
            # Common queries that might fail search
            stock_map = {
                "tata": "TATASTEEL.NS",
                "tata motors": "TATASTEEL.NS",
                "tata steel": "TATASTEEL.NS",
                "tata power": "TATAPOWER.NS",
                "adani": "ADANIENT.NS",
                "adani group": "ADANIENT.NS",
                "adani green": "ADANIGREEN.NS",
                "reliance": "RELIANCE.NS",
                "reliance industries": "RELIANCE.NS",
                "tesla": "TSLA",
                "apple": "AAPL",
                "microsoft": "MSFT",
                "google": "GOOGL",
                "amazon": "AMZN",
                "facebook": "META",
                "meta": "META",
                "netflix": "NFLX"
            }
            
            lower_input = clean_ticker.lower().strip()
            # Partial match check (e.g. "tata stocks" -> matches "tata")
            found_in_map = False
            for key, val in stock_map.items():
                if key in lower_input:
                    clean_ticker = val
                    found_in_map = True
                    break
            
            if not found_in_map:
                try:
                    # Search for "Yahoo Finance ticker for [Name]"
                    # We try 2 queries: one specific for Yahoo, one general
                    queries = [f"Yahoo Finance ticker {clean_ticker}", f"stock symbol for {clean_ticker}", f"{clean_ticker} share price"]
                    
                    with DDGS() as ddgs:
                        for i, q in enumerate(queries):
                            try:
                                results = list(ddgs.text(q, max_results=3))
                                if results:
                                    # Combine text to search in
                                    blob = " ".join([r['title'] + " " + r['body'] for r in results])
                                    
                                    # Regex to find Ticker-like patterns:
                                    # 1. Indian: WORD.NS or WORD.BO
                                    import re
                                    indian_match = re.search(r'\b([A-Z0-9]{3,12}\.(?:NS|BO))\b', blob, re.IGNORECASE)
                                    if indian_match:
                                        clean_ticker = indian_match.group(1).upper()
                                        break
                                    
                                    # 2. US: (AAPL) or "Symbol: AAPL"
                                    us_match = re.search(r'(?:\(|Symbol:\s?|Code:\s?)([A-Z]{2,5})(?:\)| )', blob)
                                    if us_match:
                                        candidate = us_match.group(1).upper()
                                        # Verify it's not a common word
                                        if candidate not in ["THE", "FOR", "AND", "STOCK", "INC", "LTD", "CORP"] and len(candidate) >= 2:
                                            clean_ticker = candidate
                                            break
                            except Exception as inner_e:
                                print(f"Search query '{q}' failed: {inner_e}")
                                continue
                except Exception as e:
                    print(f"Ticker lookup failed: {e}")

        # 2. FETCH DATA
        stock = yf.Ticker(clean_ticker)
        
        # Safely fetch price to trigger fallback if needed
        price = None
        info = None
        
        try:
            info = stock.fast_info
            price = info.last_price
        except:
            price = None
        
        # Retry with .NS (NSE India) as a hard fallback if US ticker fails
        if price is None and ".NS" not in clean_ticker:
             try:
                 # Heuristic: try removing spaces and adding .NS
                 heuristic_ticker = clean_ticker.replace(" ", "").upper() + ".NS"
                 stock = yf.Ticker(heuristic_ticker)
                 info = stock.fast_info
                 price = info.last_price
                 if price: clean_ticker = heuristic_ticker
             except:
                 pass

        if price is None:
             # FALLBACK: Real-Time Web Search
             # If exact ticker lookup fails, we search the web for the price/news immediately.
             fallback_query = f"share price of {ticker}"
             return _search_ddg(fallback_query, f"Real-Time Search Results for '{ticker}' (Live Data Unavailable)")

        prev_close = info.previous_close
        open_price = info.open if hasattr(info, 'open') else prev_close # Fallback
        day_high = info.day_high if hasattr(info, 'day_high') else price
        day_low = info.day_low if hasattr(info, 'day_low') else price
        
        change = price - prev_close
        pct_change = (change / prev_close) * 100
        
        # Color & Sign
        color = '#4caf50' if change >= 0 else '#ff5252'
        emoji = "📈" if change >= 0 else "📉"
        sign = "+" if change >= 0 else ""
        
        # Yahoo Link
        yahoo_link = f"https://finance.yahoo.com/quote/{clean_ticker}"

        # 3. RICH HTML CARD
        # Fetch history for dynamic chart
        try:
            # User wants "previous ups and downs" -> 1 Year history is better
            hist = stock.history(period="1y")
            chart_data = [] # List of dicts for Plotly
            
            if not hist.empty:
                for date, row in hist.iterrows():
                    chart_data.append({
                        "Date": date.strftime("%Y-%m-%d"),
                        "Close": round(row['Close'], 2)
                    })
                
                # RECOVERY: If price was failed (None) but we have history, use the last close!
                if price is None:
                    price = chart_data[-1]['Close']
                    # Approximate generic stats if missing
                    if prev_close is None: prev_close = price
                    if open_price is None: open_price = price
                    if day_high is None: day_high = price
                    if day_low is None: day_low = price
                    if change is None: change = 0.0
                    if pct_change is None: pct_change = 0.0
            
            import json
            # Payload for specialized Plotly Chart
            payload = {
                "type": "line",
                "x": "Date",
                "y": "Close",
                "data": chart_data,
                "title": f"Price Trend (1 Year): {clean_ticker}"
            }
            # Use the NEW standard tag that triggers st.plotly_chart
            chart_embed = f"<!-- CHART_TOOL_JSON: {json.dumps(payload)} -->"

        except Exception as e:
            print(f"Chart gen failed: {e}")
            chart_embed = ""

        if price is None:
             # FALLBACK: Real-Time Web Search
             # If exact ticker lookup fails AND no history found, we search the web.
             fallback_query = f"share price of {ticker}"
             return _search_ddg(fallback_query, f"Real-Time Search Results for '{ticker}' (Live Data Unavailable)")

        # Re-calc change if we recovered price from history
        if change is None or (change == 0 and prev_close != price):
             change = price - prev_close
             pct_change = (change / prev_close) * 100
             
        color = "#4caf50" if change >= 0 else "#ff5252"
        arrow = "▲" if change >= 0 else "▼"
        sign = "+" if change >= 0 else ""
        
        # Yahoo Link
        yahoo_link = f"https://finance.yahoo.com/quote/{clean_ticker}"


        return f"""
<div class="financial-card" style="font-family: sans-serif; padding: 20px; border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(0,0,0,0.2)); width: 100%; max-width: 400px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);">
    
    <!-- Header -->
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <div>
            <div style="font-size: 1.1rem; font-weight: bold; letter-spacing: 0.5px;">{clean_ticker}</div>
            <div style="font-size: 0.8rem; color: #aaa;">Real-Time Market Data</div>
        </div>
        <div style="font-size: 1.5rem;">{emoji}</div>
    </div>

    <!-- Main Price -->
    <div style="margin-bottom: 20px;">
        <span style="font-size: 2.5rem; font-weight: 700; color: #fff;">${price:,.2f}</span>
        <div style="color: {color}; font-weight: 600; font-size: 1rem; margin-top: 5px;">
            {sign}{change:,.2f} ({sign}{pct_change:.2f}%)
        </div>
    </div>

    <!-- Stats Grid -->
    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; font-size: 0.9rem;">
        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
            <div style="color: #666; font-size: 0.8rem;">Open</div>
            <div style="color: #ddd;">${open_price:,.2f}</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
            <div style="color: #666; font-size: 0.8rem;">High</div>
            <div style="color: #ddd;">${day_high:,.2f}</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
            <div style="color: #666; font-size: 0.8rem;">Low</div>
            <div style="color: #ddd;">${day_low:,.2f}</div>
        </div>
        <div style="background: rgba(255,255,255,0.03); padding: 8px; border-radius: 6px;">
            <div style="color: #666; font-size: 0.8rem;">Prev Close</div>
            <div style="color: #ddd;">${prev_close:,.2f}</div>
        </div>
    </div>

    <!-- Action Button -->
    <a href="{yahoo_link}" target="_blank" style="display: block; width: 100%; padding: 12px; background: {color}; color: white; text-align: center; border-radius: 8px; text-decoration: none; font-weight: bold; transition: opacity 0.2s;">
        Buy / Trade on Yahoo Finance ↗
    </a>
</div>
<!-- END_FINANCIAL_CARD -->
{chart_embed}
"""
    except Exception as e:
        return f"Stock Error: {e}"

# --- TOOLS ---

@tool
def get_weather(city_name: str) -> str:
    """
    Get the current weather and forecast for a specific city.
    Usage: get_weather("London") or get_weather("Tokyo, Japan")
    """
    return _fetch_weather(city_name)

@tool
def get_global_news(topic: str) -> str:
    """
    Search for the latest news on a specific topic or region.
    """
    return _fetch_news(topic)

@tool
def find_hotels(query: str) -> str:
    """
    Find hotels, availability, and rates for a location.
    """
    # Clean query to avoid redundancy (e.g. "hotels in Austin hotels")
    clean_q = query.lower().replace("hotels", "").replace("hotel", "").strip()
    clean_q = clean_q or query # Fallback if empty
    
    # Robust Retry Strategy
    queries = [
        f"hotels in {clean_q} with rates and images",
        f"top 10 hotels in {clean_q} 2025",
        f"luxury and budget hotels in {clean_q}",
        f"booking.com {clean_q} hotels"
    ]

    primary_results = _search_ddg(queries, f"Hotel Search Results for '{query}'")
    
    # If the specialized search returns "no results", try a very basic text search
    if "no results" in primary_results.lower() or "returned no results" in primary_results.lower():
         return _search_ddg(f"{query} accommodations", f"General Lodging Search: '{query}'")
         
    return primary_results

@tool
def find_flights(origin: str, destination: str, date: str = "soon") -> str:
    """
    Find flights, prices, and airlines.
    Usage: find_flights("New York", "London", "next friday")
    """
    queries = [
        f"flights from {origin} to {destination} {date} booking",
        f"cheap flights {origin} to {destination} skyscanner",
        f"kayak flights {origin} {destination}"
    ]
    # We construct a synthetic 'Booking' table helper
    return (f"**Flight Search: {origin} -> {destination}**\n\n"
            "| Booking | Link |\n| :---: | :---: |\n"
            f"| ✈️ Google Flights | [Search Now](https://www.google.com/travel/flights?q=flights+from+{origin}+to+{destination}+on+{date}) |\n"
            f"| 🛶 Kayak | [Search Now](https://www.kayak.com/flights/{origin}-{destination}) |\n"
            f"| 🛫 Skyscanner | [Search Now](https://www.skyscanner.com/transport/flights/{origin}/{destination}) |\n"
            "\n" + _search_ddg(queries, "Recent Flight Info"))

@tool
def search_products(item: str, location: Optional[str] = None) -> str:
    """
    Search for shopping items with optional local availability.
    Usage: search_products("PlayStation 5") or search_products("organic coffee", "Austin TX")
    """
    if location:
        queries = [
            f"where to buy {item} in {location}",
            f"{item} shops in {location} with ratings",
            f"price of {item} in {location}",
            f"{item} inventory near {location}"
        ]
        header = f"Shopping Results for '{item}' in {location}"
    else:
        # Global/Online search
        queries = [
            f"buy {item} price",
            f"{item} reviews and ratings",
            f"best price for {item}",
            f"where to buy {item} online"
        ]
        header = f"Shopping Results for '{item}'"
        
    return _search_ddg(queries, header)

@tool
def get_map_location(place_name: str) -> str:
    """
    Get the map coordinates and a direct map link for any place in the world.
    Usage: get_map_location("Eiffel Tower")
    """
    try:
        # Reuse Open-Meteo Geocoding for "Mapping"
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={place_name}&count=1&language=en&format=json"
        headers = {'User-Agent': 'EchoMindAI/1.0'} # Good practice
        geo_res = requests.get(geo_url, headers=headers).json()
        
        if not geo_res.get("results"):
            return f"Error: Could not find location '{place_name}' on the map."
            
        loc = geo_res["results"][0]
        lat = loc["latitude"]
        lon = loc["longitude"]
        name = loc["name"]
        country = loc.get("country", "")
        
        # Generate Map Links
        osm_link = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=12/{lat}/{lon}"
        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
        
        return f"""
### 📍 Location: {name}, {country}
**Coordinates**: `{lat}, {lon}`

| [**🌍 Open in Google Maps**]({google_maps_link}) | [🗺️ OpenStreetMap]({osm_link}) |
| :---: | :---: |
"""
    except Exception as e:
        return f"Error finding map location: {e}"

@tool
def find_relevant_links(query: str) -> str:
    """
    Find relevant web links (URLs) for any topic, resource, or request.
    Usage: find_relevant_links("official python documentation") or find_relevant_links("download link for VS Code")
    """
    try:
        # We explicitly ask for links in the search
        queries = [
            f"{query} official website",
            f"{query} download link",
            f"{query} homepage"
        ]
        
        # Use our robust search
        return _search_ddg(queries, f"Links found for '{query}'")
    except Exception as e:
        return f"Error finding links: {e}"

@tool
def get_images(query: str) -> str:
    """
    Find or generate images for a specific item, place, or product.
    If real images are not found or search fails, AI will generate one automatically.
    Usage: get_images('iphone 15 pro max titanium') or get_images('Eiffel Tower at night')
    """
    # 0. HARDCODED IMAGE FALLBACKS (Guaranteed Visuals for Demo)
    # This ensures "Tata", "Tesla", "Apple" etc always have a high-quality logo/product shot.
    image_map = {
        "tata": "https://upload.wikimedia.org/wikipedia/commons/8/8e/Tata_logo.svg",
        "tata motors": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tata_logo.svg/1200px-Tata_logo.svg.png",
        "tata steel": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Tata_logo.svg/1920px-Tata_logo.svg.png",
        "adani": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Adani_2012_logo.png/1200px-Adani_2012_logo.png",
        "adani group": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Adani_2012_logo.png/1200px-Adani_2012_logo.png",
        "tesla": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/1200px-Tesla_Motors.svg.png",
        "apple": "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg",
        "iphone": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/IPhone_15_Pro_Blue_Titanium.jpg/640px-IPhone_15_Pro_Blue_Titanium.jpg",
        "google": "https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg",
        "microsoft": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Microsoft_logo.svg/1200px-Microsoft_logo.svg.png",
        "amazon": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg",
        "facebook": "https://upload.wikimedia.org/wikipedia/commons/6/6c/Facebook_Logo_2023.png",
        "netflix": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Netflix_2015_logo.svg/1200px-Netflix_2015_logo.svg.png",
        "echo mind": "https://raw.githubusercontent.com/survaghasiya/EchoMindAI/main/assets/logo.png" # Example
    }
    
    clean_q = query.lower().strip()
    for key, url in image_map.items():
        if key in clean_q:
            return f"![{key}]({url})"

    return _find_images(query)

@tool
def generate_ai_image(description: str) -> str:
    """
    Generate a new, unique image using AI (DALL-E 3) based on a detailed text description.
    Use this when you need to create an image, visualize a concept, or when a specific real-world photo isn't found.
    Usage: generate_ai_image("A futuristic city on Mars at sunset")
    """
    return _generate_dalle_image(description)
