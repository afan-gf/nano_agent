import requests
import re
from typing import Dict, Any, List
from urllib.parse import quote
from bs4 import BeautifulSoup

class SearchEngine:
    """
    Search engine for retrieving up-to-date information from Baidu and Google
    """
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        self.timeout = config.get("search_timeout", 10)
    
    def _extract_main_content(self, html: str) -> str:
        """
        Extract main content from HTML page
        """
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Try to find main content areas
            content_selectors = [
                'article',
                'main',
                '[role="main"]',
                '.content',
                '.post-content',
                '.entry-content',
                '.article-content',
                '.main-content',
                '#content',
                '#main'
            ]
            
            content = None
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = elements[0]
                    break
            
            # Fallback to body if no specific content area found
            if content is None:
                content = soup.find('body')
            
            if content:
                # Extract text and clean it
                text = content.get_text(separator=' ', strip=True)
                # Compress whitespace
                text = re.sub(r'\s+', ' ', text).strip()
                # Limit length to prevent overly long responses
                return text[:10000]
            
            return "Failed to extract content from the page"
        except Exception as e:
            return f"Error extracting content: {str(e)}"
    
    def _clean_content_text(self, text: str) -> str:
        """
        Clean content text by removing special newline characters and extra whitespace
        """
        if not text:
            return ""
        
        # Remove various types of newline characters and normalize whitespace
        # This includes \n, \r, \t, and other special whitespace characters
        text = re.sub(r'[\r\n\t]+', ' ', text)
        # Compress multiple spaces into single space
        text = re.sub(r'\s+', ' ', text)
        # Strip leading and trailing whitespace
        text = text.strip()
        return text
    
    def _search_baidu(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search using Baidu search
        """
        try:
            # Try to use baidusearch package first
            try:
                from baidusearch.baidusearch import search as baidu_search
                results = baidu_search(query, num_results)
                processed_results = []
                
                for item in results:
                    if isinstance(item, dict):
                        title = item.get('title', '')
                        abstract = item.get('abstract', '')
                        url = item.get('url', '')
                    else:
                        # Handle string URLs
                        title = f"Result for: {query}"
                        abstract = ""
                        url = str(item)
                    
                    # Clean the content text
                    title = self._clean_content_text(title)
                    abstract = self._clean_content_text(abstract)
                    
                    processed_results.append({
                        'title': title,
                        'content': abstract,
                        'url': url
                    })
                
                return processed_results[:num_results]
            except ImportError:
                # Fallback to web scraping if package not available
                pass
            
            # Fallback to web scraping
            search_url = f"https://www.baidu.com/s?wd={quote(query)}&rn={num_results}"
            response = self.session.get(search_url, timeout=self.timeout)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find search result items
            result_items = soup.find_all('div', class_='result')
            
            for item in result_items[:num_results]:
                try:
                    title_elem = item.find('h3') or item.find('a')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link_elem = title_elem.find('a') if title_elem.name != 'a' else title_elem
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        # Extract abstract/content
                        content_elem = item.find('div', class_='c-abstract') or item.find('span', class_='content-right_2s-R')
                        content = content_elem.get_text(strip=True) if content_elem else ''
                        
                        # Clean the content text
                        title = self._clean_content_text(title)
                        content = self._clean_content_text(content)
                        
                        if title or content:
                            results.append({
                                'title': title,
                                'content': content,
                                'url': url
                            })
                except Exception:
                    continue
            
            return results
        except Exception as e:
            return [{'title': 'Search Error', 'content': f'Baidu search failed: {str(e)}', 'url': ''}]
    
    def _search_google(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Search using Google search
        """
        try:
            # Try to use googlesearch-python package first
            try:
                import googlesearch
                results = []
                
                search_results = googlesearch.search(query, num_results=num_results, advanced=True)
                for result in search_results:
                    if hasattr(result, 'title') and hasattr(result, 'description') and hasattr(result, 'url'):
                        # SearchResult object
                        title = result.title
                        content = result.description
                        url = result.url
                    else:
                        # String URL
                        title = f"Result for: {query}"
                        content = ""
                        url = str(result)
                    
                    # Clean the content text
                    title = self._clean_content_text(title)
                    content = self._clean_content_text(content)
                    
                    results.append({
                        'title': title,
                        'content': content,
                        'url': url
                    })
                
                return results
            except ImportError:
                # Fallback to web scraping if package not available
                pass
            
            # Fallback to web scraping (note: Google is hard to scrape, this is just a basic attempt)
            search_url = f"https://www.google.com/search?q={quote(query)}&num={num_results}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            # Find search result items
            result_items = soup.find_all('div', class_='g')
            
            for item in result_items[:num_results]:
                try:
                    title_elem = item.find('h3')
                    if title_elem:
                        title = title_elem.get_text(strip=True)
                        link_elem = item.find('a')
                        url = link_elem.get('href', '') if link_elem else ''
                        
                        # Extract snippet
                        content_elem = item.find('span', class_='aCOpRe') or item.find('div', class_='VwiC3b')
                        content = content_elem.get_text(strip=True) if content_elem else ''
                        
                        # Clean the content text
                        title = self._clean_content_text(title)
                        content = self._clean_content_text(content)
                        
                        if title or content:
                            results.append({
                                'title': title,
                                'content': content,
                                'url': url
                            })
                except Exception:
                    continue
            
            return results
        except Exception as e:
            return [{'title': 'Search Error', 'content': f'Google search failed: {str(e)}', 'url': ''}]
    
    async def search(self, query: str, engine: str = "baidu", num_results: int = 5) -> str:
        """
        Perform web search using specified search engine
        """
        try:
            # mock search
            #return f"found info for query: {query}"
            if engine.lower() == "google":
                results = self._search_google(query, num_results)
            else:
                # Default to Baidu
                results = self._search_baidu(query, num_results)
            
            if not results:
                return f"No results found for query: {query}"
            
            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                content = result.get('content', 'No content')
                url = result.get('url', 'No URL')
                
                # Try to get detailed content if available and needed
                if url and not content and i <= 2:  # Only for top results
                    try:
                        response = self.session.get(url, timeout=5)
                        content = self._extract_main_content(response.text)
                        # Clean the extracted content
                        content = self._clean_content_text(content)
                    except:
                        content = "Failed to retrieve content"
                
                formatted_result = f"{i}. {title}\n   {content[:500]}...\n   URL: {url}\n"
                formatted_results.append(formatted_result)
            
            print("=======web search result:\n".join(formatted_results))
            return "\n".join(formatted_results)
        except Exception as e:
            return f"Search failed: {str(e)}"