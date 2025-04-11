#!/usr/bin/env python3
import os
import time
from typing import List, Dict
from colorama import init, Fore, Style
from proxy_scraper import ProxyScraper

init(autoreset=True)

class ProxyWizard:
    def __init__(self):
        self.scraper = ProxyScraper(timeout=10)
        self.source_status = {}
        self.sources = {
            '1': ('ProxyScrape', self.scraper.scrape_proxyscrape),
            '2': ('Free Proxy List', self.scraper.scrape_free_proxy_list),
            '3': ('Proxy List Download', self.scraper.scrape_proxy_list_download),
            '4': ('HideMy.Name', self.scraper.scrape_hidemy_name),
            '5': ('Spys.One', self.scraper.scrape_spys_one),
            '6': ('OpenProxy.Space', self.scraper.scrape_openproxy_space),
            '7': ('SpeedX', self.scraper.scrape_speedx_list)
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def show_status(self):
        self.clear_screen()
        print(Fore.CYAN + "PROXY SOURCE STATUS")
        print(Fore.YELLOW + "="*40)
        for idx, (name, _) in self.sources.items():
            status = self.source_status.get(name, "Not checked")
            color = Fore.GREEN if status == "Online" else Fore.RED if "Error" in status else Fore.YELLOW
            print(f"{idx}. {name.ljust(20)}: {color}{status}")
        print(Fore.YELLOW + "="*40 + Style.RESET_ALL)

    def check_sources(self):
        for idx, (name, method) in self.sources.items():
            try:
                start = time.time()
                proxies = method()
                elapsed = time.time() - start
                if proxies:
                    self.source_status[name] = f"Online ({len(proxies)} proxies, {elapsed:.2f}s)"
                else:
                    self.source_status[name] = Fore.YELLOW + "Online (No proxies)"
            except Exception as e:
                self.source_status[name] = Fore.RED + f"Error: {str(e)}"

    def scrape_all(self):
        self.clear_screen()
        print(Fore.CYAN + "SCRAPING ALL SOURCES")
        print(Fore.YELLOW + "="*40)
        
        total = 0
        for idx, (name, method) in self.sources.items():
            if "Error" in self.source_status.get(name, ""):
                print(Fore.RED + f"[SKIP] {name} (Offline)")
                continue
            
            try:
                start = time.time()
                proxies = method()
                elapsed = time.time() - start
                count = len(proxies)
                total += count
                print(Fore.GREEN + f"[OK] {name.ljust(20)}: {count} proxies ({elapsed:.2f}s)")
                self.scraper.save_proxies(proxies, name, 'txt')
            except Exception as e:
                print(Fore.RED + f"[FAIL] {name}: {str(e)}")
        
        print(Fore.YELLOW + "="*40)
        print(Fore.CYAN + f"TOTAL PROXIES COLLECTED: {total}")
        input("\nPress Enter to continue...")

    def run(self):
        self.check_sources()
        while True:
            self.show_status()
            print("\n1. Rescan source status")
            print("2. Scrape all available")
            print("3. Scrape specific source")
            print("0. Exit\n")
            
            choice = input(Fore.YELLOW + "Select option: " + Style.RESET_ALL)
            
            if choice == '1':
                self.check_sources()
            elif choice == '2':
                self.scrape_all()
            elif choice == '3':
                self.scrape_selected()
            elif choice == '0':
                break
            else:
                print(Fore.RED + "Invalid option!")
                time.sleep(1)

    def scrape_selected(self):
        while True:
            self.show_status()
            print("\nSelect source number (0 to cancel)")
            choice = input(Fore.YELLOW + "> " + Style.RESET_ALL)
            
            if choice == '0':
                break
            elif choice in self.sources:
                name, method = self.sources[choice]
                if "Error" in self.source_status.get(name, ""):
                    print(Fore.RED + f"\n{name} is currently unavailable")
                    time.sleep(2)
                    continue
                
                self.clear_screen()
                print(Fore.CYAN + f"SCRAPING: {name}")
                print(Fore.YELLOW + "="*40)
                
                try:
                    start = time.time()
                    proxies = method()
                    elapsed = time.time() - start
                    count = len(proxies)
                    print(Fore.GREEN + f"\nSuccess: {count} proxies ({elapsed:.2f}s)")
                    self.scraper.save_proxies(proxies, name, 'txt')
                    print(Fore.CYAN + f"Saved to ./lists/{name.replace(' ', '_')}_*.txt")
                except Exception as e:
                    print(Fore.RED + f"\nError: {str(e)}")
                
                input("\nPress Enter to continue...")
                break
            else:
                print(Fore.RED + "Invalid source!")
                time.sleep(1)


if __name__ == "__main__":
    wizard = ProxyWizard()
    try:
        wizard.run()
    except KeyboardInterrupt:
        print(Fore.RED + "\nOperation cancelled")
    except Exception as e:
        print(Fore.RED + f"\nError: {str(e)}")
