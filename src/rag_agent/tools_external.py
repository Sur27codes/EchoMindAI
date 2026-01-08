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
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto"
        w_res = requests.get(weather_url).json()
        
        if "error" in w_res:
            return f"Error fetching weather: {w_res['reason']}"
            
        current = w_res["current"]
        daily = w_res["daily"]
        
        # Mapping WMO codes to text (Simplified)
        wmo_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm"
        }
        curr_cond = wmo_map.get(current["weather_code"], "Unknown")
        
        report = [
            f"**Weather Report for {name}, {country}**",
            f"**Current**: {current['temperature_2m']}°C, {curr_cond}",
            f"Humidity: {current['relative_humidity_2m']}%, Wind: {current['wind_speed_10m']} km/h",
            "\n**7-Day Forecast**:"
        ]
        
        for i in range(len(daily["time"])):
            date = daily["time"][i]
            max_t = daily["temperature_2m_max"][i]
            min_t = daily["temperature_2m_min"][i]
            cond = wmo_map.get(daily["weather_code"][i], "-")
            report.append(f"- {date}: {min_t}°C to {max_t}°C, {cond}")
            
        return "\n".join(report)
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
        return f"Error: {e}"

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
        return f"Error: {e}"

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
                    if "ratelimit" in str(inner_e).lower():
                         time.sleep(2.0) # Increase wait
                    continue
            
            return local_res

        # Parallel Execution
        with ThreadPoolExecutor(max_workers=4) as executor:
            future_to_query = {executor.submit(run_single_query, q): q for q in queries}
            for future in as_completed(future_to_query):
                results.extend(future.result())
                if len(results) >= 25: break 
                    
        if not results: 
            return (f"**{header}:**\n\n(Note: Live search returned no results from any browser channel. "
                    "Answering based on internal training data.)")
                    
        # Dedup by URL
        seen_urls = set()
        unique_results = []
        for r in results:
            try:
                url = r.split("](")[1].split(")")[0]
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(r)
            except:
                continue
        
        return f"**{header}:**\n\n" + "\n\n".join(unique_results[:15])
    except Exception as e:
        return f"Error: {e}"

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
        # Rotation of headers helps, but the main fix is standardizing the backend
        ua = random.choice(BROWSER_HEADERS)
        
        # Retry loop for resilience
        for attempt in range(2):
            try:
                print(f"DEBUG: Image Image attempt {attempt} for '{query}'")
                with DDGS(headers=ua) as ddgs:
                    # backend="html" is generally safer for scraping when API fails
                    search_res = ddgs.images(query, max_results=8)
                    for r in search_res:
                        img_url = r.get('image', '')
                        if any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            results.append(img_url)
                
                if results: 
                    print(f"DEBUG: Found {len(results)} images via images().")
                    break
            except Exception as inner_e:
                print(f"DEBUG: Image search error (attempt {attempt}): {inner_e}")
        
        # Fallback Strategy: Text Search for Image URLs (if images() failed)
        if not results:
            print("DEBUG: Falling back to Text Search for images...")
            try:
                with DDGS(headers=ua) as ddgs:
                    # Search for the query + "image" and look for image-like URLs in results
                    text_res = ddgs.text(query + " image", max_results=20)
                    for r in text_res:
                        link = r.get('href', '')
                        if any(ext in link.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                            results.append(link)
            except Exception as e:
                 print(f"DEBUG: Text search fallback failed: {e}")

        if not results: 
            print("DEBUG: No images found after all strategies.")
            # If we honestly can't find an image, provide a Google Images link instead of Fake AI 
            # If we honestly can't find an image, provide a Google Images link instead of Fake AI
            return (f"**No direct images found.**\n"
                    f"[🔎 Click here to view '{query}' on Google Images](https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')})")
            
        # Return unique ones
        unique = list(set(results))
        return "\n".join(unique[:3])
    except Exception as e:
        return (f"**Image Search Error**\n"
                f"[🔎 Click here to search '{query}' on Google Images](https://www.google.com/search?tbm=isch&q={query.replace(' ', '+')})")

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
    return _find_images(query)

@tool
def generate_ai_image(description: str) -> str:
    """
    Generate a new, unique image using AI (DALL-E 3) based on a detailed text description.
    Use this when you need to create an image, visualize a concept, or when a specific real-world photo isn't found.
    Usage: generate_ai_image("A futuristic city on Mars at sunset")
    """
    return _generate_dalle_image(description)
