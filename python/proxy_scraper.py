import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import random
import os
from typing import List, Dict, Optional


class ProxyScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        self.proxies_by_source = {}

    def _get_random_user_agent(self) -> str:
        return random.choice(self.user_agents)

    def _make_request(self, url: str) -> Optional[requests.Response]:
        headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }
        try:
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException:
            return None

    def save_proxies_to_txt(self, proxies: List[Dict[str, str]], source_name: str) -> None:
        """Salva proxies no formato IP:PORTA em arquivo .txt"""
        os.makedirs('./lists', exist_ok=True)
        clean_name = source_name.replace(' ', '_').replace('.', '_').replace('/', '_')
        filename = f"./lists/{clean_name}.txt"
        
        with open(filename, 'w') as f:
            for proxy in proxies:
                f.write(f"{proxy['ip']}:{proxy['port']}\n")

    def scrape_proxyscrape(self) -> List[Dict[str, str]]:
        url = "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all"
        response = self._make_request(url)
        proxies = []
        if response:
            for line in response.text.splitlines():
                if ':' in line:
                    ip, port = line.strip().split(':')
                    proxies.append({'ip': ip, 'port': port, 'type': 'http', 'source': 'ProxyScrape'})
        self.proxies_by_source['ProxyScrape'] = proxies
        return proxies

    def scrape_free_proxy_list(self) -> List[Dict[str, str]]:
        url = "https://free-proxy-list.net/"
        response = self._make_request(url)
        proxies = []
        if response:
            try:
                tables = pd.read_html(response.text)
                df = tables[0]
                for _, row in df.iterrows():
                    proxies.append({
                        'ip': str(row['IP Address']),
                        'port': str(row['Port']),
                        'type': 'https' if row['Https'] == 'yes' else 'http',
                        'country': row['Country'],
                        'anonymity': row['Anonymity'],
                        'source': 'Free Proxy List'
                    })
            except Exception:
                pass
        self.proxies_by_source['Free Proxy List'] = proxies
        return proxies

    def scrape_proxy_list_download(self) -> List[Dict[str, str]]:
        types = ['http', 'https', 'socks4', 'socks5']
        proxies = []
        for proxy_type in types:
            url = f"https://www.proxy-list.download/api/v1/get?type={proxy_type}"
            response = self._make_request(url)
            if response:
                for line in response.text.splitlines():
                    if ':' in line:
                        ip, port = line.strip().split(':')
                        proxies.append({'ip': ip, 'port': port, 'type': proxy_type, 'source': 'Proxy List Download'})
        self.proxies_by_source['Proxy List Download'] = proxies
        return proxies

    def scrape_hidemy_name(self) -> List[Dict[str, str]]:
        url = "https://hidemy.name/en/proxy-list/"
        response = self._make_request(url)
        proxies = []
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'proxy__t'})
            if table:
                rows = table.find_all('tr')[1:]
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
        url = "https://spys.one/en/free-proxy-list/"
        response = self._make_request(url)
        proxies = []
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'width': '100%'})
            if table:
                rows = table.find_all('tr')[2:]
                for row in rows:
                    cols = row.find_all('td')
                    if len(cols) >= 10:
                        ip = cols[0].text.strip().split(':')[0]
                        port = cols[1].text.strip()
                        proxies.append({
                            'ip': ip,
                            'port': port,
                            'type': cols[2].text.strip().lower(),
                            'country': cols[3].text.strip(),
                            'anonymity': cols[4].text.strip(),
                            'source': 'Spys.One'
                        })
        self.proxies_by_source['Spys.One'] = proxies
        return proxies

    def scrape_openproxy_space(self) -> List[Dict[str, str]]:
        url = "https://openproxy.space/api/proxies"
        response = self._make_request(url)
        proxies = []
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
                pass
        self.proxies_by_source['OpenProxy.Space'] = proxies
        return proxies

    def scrape_speedx_list(self) -> List[Dict[str, str]]:
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
                        proxies.append({'ip': ip, 'port': port, 'type': proxy_type, 'source': 'SpeedX'})
        self.proxies_by_source['SpeedX Proxy List'] = proxies
        return proxies

    def scrape_all_sources(self) -> List[Dict[str, str]]:
        """Coleta proxies de todas as fontes e salva em arquivos separados"""
        sources = [
            ('ProxyScrape', self.scrape_proxyscrape),
            ('Free Proxy List', self.scrape_free_proxy_list),
            ('Proxy List Download', self.scrape_proxy_list_download),
            ('HideMy.Name', self.scrape_hidemy_name),
            ('Spys.One', self.scrape_spys_one),
            ('OpenProxy.Space', self.scrape_openproxy_space),
            ('SpeedX Proxy List', self.scrape_speedx_list)
        ]
        
        all_proxies = []
        for name, method in sources:
            try:
                proxies = method()
                self.save_proxies_to_txt(proxies, name)
                all_proxies.extend(proxies)
            except Exception as e:
                print(f"Erro ao coletar de {name}: {str(e)}")
        
        return all_proxies

    def test_proxy(self, ip: str, port: str, proxy_type: str, test_url: str = "http://www.google.com") -> bool:
        proxy_url = f"{ip}:{port}"
        proxies = {
            "http": f"{proxy_type}://{proxy_url}",
            "https": f"{proxy_type}://{proxy_url}"
        }
        try:
            response = requests.get(test_url, proxies=proxies, timeout=self.timeout)
            return response.status_code == 200
        except Exception:
            return False
