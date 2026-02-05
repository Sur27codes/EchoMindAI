
import requests

def search_wikimedia(query):
    print(f"--- Searching Wikimedia for: '{query}' ---")
    try:
        # Wikimedia Commons API
        url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrnamespace": 6, # File namespace
            "gsrsearch": f"{query} filetype:bitmap",
            "gsrlimit": 3,
            "prop": "imageinfo",
            "iiprop": "url|mime",
            "iiurlheight": 600
        }
        
        headers = {
            "User-Agent": "EchoMindAI/1.0 (Integration Test)"
        }
        
        res = requests.get(url, params=params, headers=headers).json()
        
        pages = res.get("query", {}).get("pages", {})
        if not pages:
            print("❌ No results found.")
            return

        for page_id, page in pages.items():
            if "imageinfo" in page:
                info = page["imageinfo"][0]
                print(f"✅ Found: {info['url']}")
                
    except Exception as e:
        print(f"❌ Error: {e}")

search_wikimedia("Nike Logo")
search_wikimedia("Tokyo Skyline")
search_wikimedia("Tesla Model S")
