#!/usr/bin/env python3
import os
import time
from typing import List, Dict
from colorama import init, Fore, Style
from proxy_scraper import ProxyScraper

init(autoreset=True)

class ProxyWizard:
    def __init__(self):
        self.scraper = ProxyScraper(timeout=15)
        self.proxy_stats = {}
        self.test_urls = {
            'http': 'http://httpbin.org/ip',
            'https': 'https://httpbin.org/ip',
            'socks4': 'https://httpbin.org/ip',
            'socks5': 'https://httpbin.org/ip'
        }
        self.selected_test_url = 'https://www.google.com'
        self.current_proxy = None

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self, title):
        self.clear_screen()
        print(Fore.CYAN + r"""
  ____                          ____                                  
 |  _ \ _ __ _____  ___   _    / ___| _ __   ___  ___ _ __ ___  ___ 
 | |_) | '__/ _ \ \/ / | | |   \___ \| '_ \ / _ \/ __| '__/ _ \/ __|
 |  __/| | | (_) >  <| |_| |    ___) | |_) |  __/ (__| | |  __/\__ \
 |_|   |_|  \___/_/\_\\__, |___|____/| .__/ \___|\___|_|  \___||___/
                       |___/_____|    |_|                            
        """)
        print(Fore.YELLOW + "=" * 60)
        print(Fore.GREEN + f" {title.center(58)} ")
        print(Fore.YELLOW + "=" * 60 + Style.RESET_ALL)
        print()

    def main_menu(self):
        while True:
            self.display_header("Proxy Management Wizard")
            print(Fore.WHITE + "MAIN MENU:")
            print(Fore.CYAN + "1. Scrape Proxies")
            print(Fore.CYAN + "2. Proxy Analysis Tools")
            print(Fore.CYAN + "3. Proxy Tester")
            print(Fore.CYAN + "4. Settings")
            print(Fore.RED + "0. Exit")
            print()

            choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL)

            if choice == "1":
                self.scrape_menu()
            elif choice == "2":
                self.analysis_menu()
            elif choice == "3":
                self.testing_menu()
            elif choice == "4":
                self.settings_menu()
            elif choice == "0":
                print(Fore.GREEN + "\nExiting wizard...")
                break
            else:
                print(Fore.RED + "\nInvalid option! Try again.")
                time.sleep(1)

    def scrape_menu(self):
        while True:
            self.display_header("Proxy Scraping")
            print(Fore.WHITE + "SCRAPE OPTIONS:")
            print(Fore.CYAN + "1. Scrape from all sources")
            print(Fore.CYAN + "2. Scrape from specific source")
            print(Fore.CYAN + "3. View scraped proxies")
            print(Fore.RED + "0. Back to main menu")
            print()

            choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL)

            if choice == "1":
                self.scrape_all_sources()
            elif choice == "2":
                self.scrape_specific_source()
            elif choice == "3":
                self.view_proxies()
            elif choice == "0":
                return
            else:
                print(Fore.RED + "\nInvalid option!")
                time.sleep(1)

    def scrape_all_sources(self):
        self.display_header("Scraping All Sources")
        print(Fore.YELLOW + "This may take several minutes...\n" + Style.RESET_ALL)
        
        proxies = self.scraper.scrape_all_sources()
        self.update_stats(proxies)
        
        input("\nPress Enter to continue...")

    def scrape_specific_source(self):
        sources = {
            "1": ("ProxyScrape", self.scraper.scrape_proxyscrape),
            "2": ("Free Proxy List", self.scraper.scrape_free_proxy_list),
            "3": ("Proxy List Download", self.scraper.scrape_proxy_list_download),
            "4": ("HideMy.Name", self.scraper.scrape_hidemy_name),
            "5": ("Spys.One", self.scraper.scrape_spys_one),
            "6": ("OpenProxy.Space", self.scraper.scrape_openproxy_space),
            "7": ("SpeedX", self.scraper.scrape_speedx_list)
        }

        while True:
            self.display_header("Scrape Specific Source")
            print(Fore.WHITE + "SELECT SOURCE:")
            for key, (name, _) in sources.items():
                print(Fore.CYAN + f"{key}. {name}")
            print(Fore.RED + "0. Back")
            print()

            choice = input(Fore.YELLOW + "Choose a source: " + Style.RESET_ALL)

            if choice == "0":
                return
            elif choice in sources:
                name, method = sources[choice]
                self.display_header(f"Scraping from {name}")
                print(Fore.YELLOW + f"Scraping proxies from {name}..." + Style.RESET_ALL)
                
                try:
                    proxies = method()
                    self.update_stats(proxies)
                    print(Fore.GREEN + f"\nSuccessfully scraped {len(proxies)} proxies from {name}")
                except Exception as e:
                    print(Fore.RED + f"\nError scraping {name}: {str(e)}")
                
                input("\nPress Enter to continue...")
                return
            else:
                print(Fore.RED + "\nInvalid option!")
                time.sleep(1)

    def update_stats(self, proxies: List[Dict[str, str]]):
        """Update statistics about collected proxies"""
        stats = {
            'total': len(proxies),
            'by_type': {},
            'by_country': {},
            'by_anonymity': {}
        }

        for proxy in proxies:
            # Count by type
            ptype = proxy.get('type', 'unknown')
            stats['by_type'][ptype] = stats['by_type'].get(ptype, 0) + 1

            # Count by country
            country = proxy.get('country', 'unknown')
            stats['by_country'][country] = stats['by_country'].get(country, 0) + 1

            # Count by anonymity
            anonymity = proxy.get('anonymity', 'unknown')
            stats['by_anonymity'][anonymity] = stats['by_anonymity'].get(anonymity, 0) + 1

        self.proxy_stats = stats

    def view_proxies(self):
        self.display_header("View Collected Proxies")
        
        if not self.scraper.proxies_by_source:
            print(Fore.YELLOW + "No proxies have been collected yet." + Style.RESET_ALL)
        else:
            print(Fore.WHITE + "PROXY STATISTICS:")
            print(f"Total proxies: {Fore.GREEN}{self.proxy_stats.get('total', 0)}")
            
            print("\n" + Fore.WHITE + "BY TYPE:")
            for ptype, count in self.proxy_stats.get('by_type', {}).items():
                print(f"{ptype.ljust(10)}: {Fore.CYAN}{count}")
            
            print("\n" + Fore.WHITE + "BY COUNTRY (Top 5):")
            sorted_countries = sorted(self.proxy_stats.get('by_country', {}).items(), 
                                    key=lambda x: x[1], reverse=True)[:5]
            for country, count in sorted_countries:
                print(f"{country.ljust(15)}: {Fore.CYAN}{count}")
            
            print("\n" + Fore.WHITE + "Press Enter to view sample proxies...")
            input()
            
            self.display_header("Sample Proxies")
            for source, proxies in self.scraper.proxies_by_source.items():
                print(Fore.GREEN + f"\n{source} ({len(proxies)} proxies):" + Style.RESET_ALL)
                for proxy in proxies[:3]:  # Show first 3 as sample
                    print(f"{proxy.get('type', 'unknown')}://{proxy['ip']}:{proxy['port']} "
                          f"({proxy.get('country', 'unknown')})")
        
        input("\nPress Enter to continue...")

    def analysis_menu(self):
        while True:
            self.display_header("Proxy Analysis Tools")
            print(Fore.WHITE + "ANALYSIS TOOLS:")
            print(Fore.CYAN + "1. Filter proxies by type")
            print(Fore.CYAN + "2. Filter proxies by country")
            print(Fore.CYAN + "3. Find fastest proxies")
            print(Fore.CYAN + "4. Check proxy anonymity levels")
            print(Fore.RED + "0. Back to main menu")
            print()

            choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL)

            if choice == "1":
                self.filter_by_type()
            elif choice == "2":
                self.filter_by_country()
            elif choice == "3":
                self.find_fastest()
            elif choice == "4":
                self.check_anonymity()
            elif choice == "0":
                return
            else:
                print(Fore.RED + "\nInvalid option!")
                time.sleep(1)

    def filter_by_type(self):
        self.display_header("Filter by Proxy Type")
        
        if not self.proxy_stats.get('by_type'):
            print(Fore.YELLOW + "No proxy data available. Please scrape proxies first.")
            input("\nPress Enter to continue...")
            return
        
        print(Fore.WHITE + "Available proxy types:")
        for i, ptype in enumerate(self.proxy_stats['by_type'].keys(), 1):
            print(f"{i}. {ptype}")
        
        try:
            choice = int(input(Fore.YELLOW + "\nSelect type to filter: " + Style.RESET_ALL))
            selected_type = list(self.proxy_stats['by_type'].keys())[choice-1]
            
            filtered = []
            for proxies in self.scraper.proxies_by_source.values():
                for proxy in proxies:
                    if proxy.get('type', '').lower() == selected_type.lower():
                        filtered.append(proxy)
            
            self.display_header(f"Proxies of type: {selected_type}")
            print(f"Found {Fore.GREEN}{len(filtered)}{Style.RESET_ALL} proxies")
            
            if filtered:
                print("\nSample proxies:")
                for proxy in filtered[:5]:
                    print(f"{proxy['ip']}:{proxy['port']} "
                          f"(Source: {proxy.get('source', 'unknown')})")
                
                save = input("\nSave these proxies to file? (y/n): ").lower()
                if save == 'y':
                    self.scraper.save_proxies(filtered, f"filtered_{selected_type}", 'txt')
                    print(Fore.GREEN + f"Saved to ./lists/filtered_{selected_type}.txt")
            
        except (ValueError, IndexError):
            print(Fore.RED + "Invalid selection!")
        
        input("\nPress Enter to continue...")

    def testing_menu(self):
        while True:
            self.display_header("Proxy Testing")
            print(Fore.WHITE + "TESTING OPTIONS:")
            print(Fore.CYAN + "1. Test specific proxy")
            print(Fore.CYAN + "2. Batch test proxies")
            print(Fore.CYAN + "3. Set test URL")
            print(Fore.CYAN + "4. Current proxy: " + 
                  (Fore.GREEN + f"{self.current_proxy}" if self.current_proxy else Fore.RED + "None"))
            print(Fore.RED + "0. Back to main menu")
            print()

            choice = input(Fore.YELLOW + "Choose an option: " + Style.RESET_ALL)

            if choice == "1":
                self.test_single_proxy()
            elif choice == "2":
                self.batch_test()
            elif choice == "3":
                self.set_test_url()
            elif choice == "4":
                self.set_current_proxy()
            elif choice == "0":
                return
            else:
                print(Fore.RED + "\nInvalid option!")
                time.sleep(1)

    def test_single_proxy(self):
        self.display_header("Test Single Proxy")
        
        print(Fore.WHITE + "Enter proxy details:")
        ip = input("IP: ").strip()
        port = input("Port: ").strip()
        ptype = input("Type (http/socks4/socks5): ").strip().lower()
        
        print(Fore.YELLOW + f"\nTesting {ptype}://{ip}:{port}..." + Style.RESET_ALL)
        
        result = self.scraper.test_proxy(ip, port, ptype, self.selected_test_url)
        
        if result:
            print(Fore.GREEN + "\nProxy is working!")
            use = input("Set as current proxy? (y/n): ").lower()
            if use == 'y':
                self.current_proxy = f"{ptype}://{ip}:{port}"
        else:
            print(Fore.RED + "\nProxy is not working")
        
        input("\nPress Enter to continue...")

    def settings_menu(self):
        while True:
            self.display_header("Settings")
            print(Fore.WHITE + "CURRENT SETTINGS:")
            print(Fore.CYAN + f"1. Test URL: {Fore.YELLOW}{self.selected_test_url}")
            print(Fore.CYAN + f"2. Timeout: {Fore.YELLOW}{self.scraper.timeout}s")
            print(Fore.RED + "0. Back to main menu")
            print()

            choice = input(Fore.YELLOW + "Choose setting to change: " + Style.RESET_ALL)

            if choice == "1":
                self.selected_test_url = input("Enter new test URL: ").strip()
                print(Fore.GREEN + "Test URL updated!")
                time.sleep(1)
            elif choice == "2":
                try:
                    new_timeout = int(input("Enter new timeout (seconds): "))
                    self.scraper.timeout = new_timeout
                    print(Fore.GREEN + "Timeout updated!")
                    time.sleep(1)
                except ValueError:
                    print(Fore.RED + "Invalid timeout value!")
                    time.sleep(1)
            elif choice == "0":
                return
            else:
                print(Fore.RED + "\nInvalid option!")
                time.sleep(1)

    def run(self):
        try:
            self.main_menu()
        except KeyboardInterrupt:
            print(Fore.RED + "\nOperation cancelled by user")
        except Exception as e:
            print(Fore.RED + f"\nFatal error: {str(e)}")


if __name__ == "__main__":
    wizard = ProxyWizard()
    wizard.run()
