import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import random
import os
import time
from typing import List, Dict, Optional, Union
from io import StringIO


class ProxyScraper:
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        self.proxies_by_source = {}
        self.session = requests.Session()

    def _get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def _make_request(self, url: str) -> Optional[requests.Response]:
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    print(f"Failed to fetch {url} after {self.max_retries} attempts: {str(e)}")
                    return None
                time.sleep(1)

    def save_proxies(self, proxies: List[Dict[str, str]], source_name: str, output_format: str = 'txt') -> None:
        """Save proxies to files organized by type and format"""
        os.makedirs('./lists', exist_ok=True)
        clean_name = source_name.replace(' ', '_').replace('.', '_').replace('/', '_')
        
        # Organize proxies by type
        proxies_by_type = {}
        for proxy in proxies:
            ptype = proxy.get('type', 'http').lower()
            if ptype not in proxies_by_type:
                proxies_by_type[ptype] = []
            proxies_by_type[ptype].append(proxy)
        
        # Save in requested format
        for ptype, proxy_list in proxies_by_type.items():
            filename = f"./lists/{clean_name}_{ptype}.{output_format}"
            
            if output_format == 'txt':
                with open(filename, 'w') as f:
                    for proxy in proxy_list:
                        f.write(f"{ptype}://{proxy['ip']}:{proxy['port']}\n")
            
            elif output_format == 'json':
                with open(filename, 'w') as f:
                    json.dump(proxy_list, f, indent=2)
            
            print(f"Saved {len(proxy_list)} {ptype} proxies to {filename}")

    def scrape_proxyscrape(self) -> List[Dict[str, str]]:
        """Scrape proxies from ProxyScrape API"""
        urls = [
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=10000&country=all",
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=10000&country=all"
        ]
        
        proxies = []
        for url in urls:
            response = self._make_request(url)
            if response:
                for line in response.text.splitlines():
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        ptype = 'http' if 'http' in url else 'socks4' if 'socks4' in url else 'socks5'
                        proxies.append({
                            'ip': ip,
                            'port': port,
                            'type': ptype,
                            'source': 'ProxyScrape'
                        })
        
        self.proxies_by_source['ProxyScrape'] = proxies
        return proxies

    def scrape_free_proxy_list(self) -> List[Dict[str, str]]:
        """Scrape proxies from Free-Proxy-List.net"""
        url = "https://free-proxy-list.net/"
        proxies = []
        
        response = self._make_request(url)
        if response:
            try:
                tables = pd.read_html(StringIO(response.text))
                df = tables[0]
                
                required_columns = ['IP Address', 'Port', 'Https', 'Country', 'Anonymity']
                if all(col in df.columns for col in required_columns):
                    for _, row in df.iterrows():
                        proxies.append({
                            'ip': str(row['IP Address']),
                            'port': str(row['Port']),
                            'type': 'https' if row['Https'] == 'yes' else 'http',
                            'country': row['Country'],
                            'anonymity': row['Anonymity'],
                            'source': 'Free Proxy List'
                        })
            except Exception as e:
                print(f"Error parsing Free Proxy List: {str(e)}")
        
        self.proxies_by_source['Free Proxy List'] = proxies
        return proxies

    def scrape_proxy_list_download(self) -> List[Dict[str, str]]:
        """Scrape proxies from Proxy-List.Download"""
        types = ['http', 'https', 'socks4', 'socks5']
        proxies = []
        
        for proxy_type in types:
            url = f"https://www.proxy-list.download/api/v1/get?type={proxy_type}"
            response = self._make_request(url)
            if response:
                for line in response.text.splitlines():
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        proxies.append({
                            'ip': ip,
                            'port': port,
                            'type': proxy_type,
                            'source': 'Proxy List Download'
                        })
        
        self.proxies_by_source['Proxy List Download'] = proxies
        return proxies

    def scrape_hidemy_name(self) -> List[Dict[str, str]]:
        """Scrape proxies from HideMy.Name"""
        url = "https://hidemy.name/en/proxy-list/"
        proxies = []
        
        response = self._make_request(url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'proxy__t'})
            
            if table:
                rows = table.find_all('tr')[1:]  # Skip header
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 6:
                        proxies.append({
                            'ip': cols[0].text.strip(),
                            'port': cols[1].text.strip(),
                            'country': cols[2].text.strip(),
                            'type': cols[4].text.strip().lower(),
                            'anonymity': cols[5].text.strip(),
                            'source': 'HideMy.Name'
                        })
        
        self.proxies_by_source['HideMy.Name'] = proxies
        return proxies

    def scrape_spys_one(self) -> List[Dict[str, str]]:
        """Scrape proxies from Spys.One"""
        url = "https://spys.one/en/free-proxy-list/"
        proxies = []
        
        response = self._make_request(url)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'width': '100%'})
            
            if table:
                rows = table.find_all('tr')[2:]  # Skip headers
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 10:
                        ip_port = cols[0].text.strip().split(':')
                        if len(ip_port) == 2:
                            proxies.append({
                                'ip': ip_port[0],
                                'port': cols[1].text.strip(),
                                'type': cols[2].text.strip().lower(),
                                'country': cols[3].text.strip(),
                                'anonymity': cols[4].text.strip(),
                                'source': 'Spys.One'
                            })
        
        self.proxies_by_source['Spys.One'] = proxies
        return proxies

    def scrape_openproxy_space(self) -> List[Dict[str, str]]:
        """Scrape proxies from OpenProxy.Space API"""
        url = "https://openproxy.space/api/proxies"
        proxies = []
        
        response = self._make_request(url)
        if response:
            try:
                data = response.json()
                for proxy in data.get('proxies', []):
                    proxies.append({
                        'ip': proxy.get('ip'),
                        'port': str(proxy.get('port')),
                        'type': proxy.get('protocol', '').lower(),
                        'country': proxy.get('country'),
                        'source': 'OpenProxy.Space'
                    })
            except json.JSONDecodeError:
                print("Error decoding OpenProxy.Space JSON")
        
        self.proxies_by_source['OpenProxy.Space'] = proxies
        return proxies

    def scrape_speedx_list(self) -> List[Dict[str, str]]:
        """Scrape proxies from SpeedX GitHub lists"""
        base_urls = [
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt"
        ]
        
        proxies = []
        for url in base_urls:
            proxy_type = 'http' if 'http' in url else 'socks4' if 'socks4' in url else 'socks5'
            response = self._make_request(url)
            if response:
                for line in response.text.splitlines():
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        proxies.append({
                            'ip': ip,
                            'port': port,
                            'type': proxy_type,
                            'source': 'SpeedX'
                        })
        
        self.proxies_by_source['SpeedX'] = proxies
        return proxies

    def scrape_all_sources(self, output_format: str = 'txt') -> List[Dict[str, str]]:
        """Scrape from all available sources and save results"""
        sources = [
            ('ProxyScrape', self.scrape_proxyscrape),
            ('Free Proxy List', self.scrape_free_proxy_list),
            ('Proxy List Download', self.scrape_proxy_list_download),
            ('HideMy.Name', self.scrape_hidemy_name),
            ('Spys.One', self.scrape_spys_one),
            ('OpenProxy.Space', self.scrape_openproxy_space),
            ('SpeedX', self.scrape_speedx_list)
        ]
        
        all_proxies = []
        print("\nStarting proxy scraping...")
        for name, method in sources:
            try:
                start_time = time.time()
                proxies = method()
                self.save_proxies(proxies, name, output_format)
                all_proxies.extend(proxies)
                elapsed = time.time() - start_time
                print(f"✓ {name}: {len(proxies)} proxies ({elapsed:.2f}s)")
            except Exception as e:
                print(f"✗ {name}: Error - {str(e)}")
        
        total_proxies = sum(len(v) for v in self.proxies_by_source.values())
        print(f"\nTotal proxies collected: {total_proxies}")
        return all_proxies

    def test_proxy(self, ip: str, port: str, proxy_type: str, test_url: str = "http://www.google.com") -> bool:
        """Test if a proxy is working"""
        proxy_url = f"{proxy_type}://{ip}:{port}"
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }
        
        try:
            start_time = time.time()
            response = requests.get(test_url, proxies=proxies, timeout=self.timeout)
            elapsed = time.time() - start_time
            if response.status_code == 200:
                print(f"✓ {proxy_url} works! Response time: {elapsed:.2f}s")
                return True
        except Exception as e:
            print(f"✗ {proxy_url} failed: {str(e)}")
        
        return False

    def get_proxies_by_source(self, source: str) -> List[Dict[str, str]]:
        """Get proxies from a specific source"""
        return self.proxies_by_source.get(source, [])

    def get_all_proxies(self) -> List[Dict[str, str]]:
        """Get all collected proxies"""
        return [proxy for proxies in self.proxies_by_source.values() for proxy in proxies]


if __name__ == "__main__":
    scraper = ProxyScraper(timeout=15)
    
    # Example usage:
    print("1. Scrape all sources and save to files")
    print("2. Test a specific proxy")
    choice = input("Choose an option: ")
    
    if choice == "1":
        scraper.scrape_all_sources()
    elif choice == "2":
        ip = input("Enter IP: ")
        port = input("Enter Port: ")
        ptype = input("Enter Type (http/socks4/socks5): ")
        scraper.test_proxy(ip, port, ptype)
    else:
        print("Invalid option")
