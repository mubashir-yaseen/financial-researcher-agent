import httpx
from bs4 import BeautifulSoup
from typing import List, Dict
import urllib.parse

class FreeSearch:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://duckduckgo.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }

    def search(self, query: str, max_results: int = 8) -> List[Dict]:
        """
        Executes a DuckDuckGo search. Uses httpx for better compatibility.
        """
        results = []
        try:
            # We use the 'lite' version as it's the most stable for scraping
            url = "https://lite.duckduckgo.com/lite/"
            
            with httpx.Client(headers=self.headers, follow_redirects=True, timeout=20.0) as client:
                data = {"q": query}
                response = client.post(url, data=data)
                
                # If POST fails or returns nothing, try a simple GET on the html endpoint
                if response.status_code != 200 or "result-url" not in response.text:
                    url_html = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"
                    response = client.get(url_html)
                
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Try Lite parsing first (table based)
                for tr in soup.find_all("tr"):
                    a_tag = tr.find("a", class_="result-url")
                    if a_tag:
                        title = a_tag.text.strip()
                        href = a_tag.get("href", "")
                        
                        # Snippet is usually in the next tr
                        snippet = ""
                        next_tr = tr.find_next_sibling("tr")
                        if next_tr:
                            snippet_td = next_tr.find("td", class_="result-snippet")
                            if snippet_td:
                                snippet = snippet_td.text.strip()
                        
                        # Cleanup redirect
                        if "uddg=" in href:
                            href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                        elif href.startswith("//"):
                            href = "https:" + href

                        results.append({
                            "title": title,
                            "url": href,
                            "snippet": snippet
                        })
                        if len(results) >= max_results:
                            break
                            
                # Fallback to standard HTML parsing if lite failed
                if not results:
                    for res in soup.find_all("div", class_="result"):
                        title_tag = res.find("a", class_="result__a")
                        snippet_tag = res.find("a", class_="result__snippet")
                        if title_tag:
                            title = title_tag.text.strip()
                            href = title_tag.get("href", "")
                            snippet = snippet_tag.text.strip() if snippet_tag else ""
                            
                            if "uddg=" in href:
                                href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
                            
                            results.append({
                                "title": title,
                                "url": href,
                                "snippet": snippet
                            })
                            if len(results) >= max_results:
                                break

        except Exception as e:
            print(f"Search error: {e}")
            
        return results

    def fetch_url_content(self, url: str) -> str:
        try:
            with httpx.Client(headers=self.headers, timeout=10.0) as client:
                response = client.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                text = " ".join([p.text for p in soup.find_all("p")])
                return text[:1000]
        except Exception:
            return ""
