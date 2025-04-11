import os
import time
from colorama import init, Fore, Style
from typing import List, Dict
from proxy_scraper import ProxyScraper

init(autoreset=True)

class ProxyScraperWizard:
    def __init__(self):
        self.scraper = ProxyScraper(timeout=15)
        self.proxies_by_source = {}

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def display_header(self):
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
        print(Fore.GREEN + " Wizard para Coleta de Proxies de Diversas Fontes")
        print(Fore.YELLOW + "=" * 60 + Style.RESET_ALL)
        print()

    def main_menu(self):
        while True:
            self.display_header()
            print(Fore.WHITE + "MENU PRINCIPAL:")
            print(Fore.CYAN + "1. Coletar proxies de fonte específica")
            print(Fore.CYAN + "2. Coletar proxies de todas as fontes")
            print(Fore.CYAN + "3. Visualizar proxies coletados")
            print(Fore.CYAN + "4. Testar um proxy específico")
            print(Fore.RED + "0. Sair")
            print()

            choice = input(Fore.YELLOW + "Escolha uma opção: " + Style.RESET_ALL)

            if choice == "1":
                self.collect_specific_source()
            elif choice == "2":
                self.collect_all_sources()
            elif choice == "3":
                self.view_proxies()
            elif choice == "4":
                self.test_single_proxy()
            elif choice == "0":
                print(Fore.GREEN + "\nSaindo do wizard...")
                break
            else:
                print(Fore.RED + "\nOpção inválida! Tente novamente.")
                time.sleep(1)

    def collect_specific_source(self):
        self.display_header()
        print(Fore.CYAN + "COLETAR PROXIES DE FONTE ESPECÍFICA" + Style.RESET_ALL)
        print()

        sources = {
            "1": ("ProxyScrape", self.scraper.scrape_proxyscrape),
            "2": ("Free_Proxy_List", self.scraper.scrape_free_proxy_list),
            "3": ("Proxy_List_Download", self.scraper.scrape_proxy_list_download),
            "4": ("HideMy_Name", self.scraper.scrape_hidemy_name),
            "5": ("Spys_One", self.scraper.scrape_spys_one),
            "6": ("OpenProxy_Space", self.scraper.scrape_openproxy_space),
            "7": ("SpeedX_Proxy_List", self.scraper.scrape_speedx_list)
        }

        for key, (name, _) in sources.items():
            print(Fore.CYAN + f"{key}. {name.replace('_', ' ')}")

        print(Fore.RED + "0. Voltar")
        print()

        choice = input(Fore.YELLOW + "Escolha a fonte desejada: " + Style.RESET_ALL)

        if choice == "0":
            return
        elif choice in sources:
            name, method = sources[choice]
            display_name = name.replace('_', ' ')
            print(Fore.YELLOW + f"\nColetando proxies de {display_name}..." + Style.RESET_ALL)

            try:
                proxies = method()
                self.proxies_by_source[display_name] = proxies
                self.scraper.save_proxies_to_txt(proxies, name)
                print(Fore.GREEN + f"\nColeta concluída! {len(proxies)} proxies obtidos de {display_name}.")
                print(Fore.GREEN + f"Proxies salvos em ./lists/{name}.txt" + Style.RESET_ALL)
            except Exception as e:
                print(Fore.RED + f"\nErro ao coletar de {display_name}: {e}" + Style.RESET_ALL)

            input("\nPressione Enter para continuar...")
        else:
            print(Fore.RED + "\nOpção inválida!" + Style.RESET_ALL)
            time.sleep(1)

    def collect_all_sources(self):
        self.display_header()
        print(Fore.CYAN + "COLETANDO PROXIES DE TODAS AS FONTES" + Style.RESET_ALL)
        print(Fore.YELLOW + "\nEsta operação pode demorar alguns minutos..." + Style.RESET_ALL)
        
        try:
            all_proxies = self.scraper.scrape_all_sources()
            total = sum(len(proxies) for proxies in self.scraper.proxies_by_source.values())
            print(Fore.GREEN + f"\nColeta completa! Total de {total} proxies obtidos de todas as fontes.")
            print(Fore.GREEN + "Arquivos salvos no diretório ./lists/" + Style.RESET_ALL)
        except Exception as e:
            print(Fore.RED + f"\nErro durante a coleta: {e}" + Style.RESET_ALL)
        
        input("\nPressione Enter para continuar...")

    def view_proxies(self):
        self.display_header()
        print(Fore.CYAN + "PROXIES COLETADOS POR FONTE" + Style.RESET_ALL)
        print()

        if not self.proxies_by_source:
            print(Fore.YELLOW + "Nenhuma fonte de proxy foi coletada ainda." + Style.RESET_ALL)
        else:
            for source, proxies in self.proxies_by_source.items():
                print(Fore.GREEN + f"{source} - {len(proxies)} proxies" + Style.RESET_ALL)
                for proxy in proxies[:5]:
                    print(f"{proxy['ip']}:{proxy['port']} ({proxy['type']})")
                if len(proxies) > 5:
                    print(Fore.YELLOW + f"... e mais {len(proxies) - 5} não exibidos" + Style.RESET_ALL)
                print()

        input("Pressione Enter para continuar...")

    def test_single_proxy(self):
        self.display_header()
        print(Fore.CYAN + "TESTAR PROXY ESPECÍFICO" + Style.RESET_ALL)
        print()

        ip = input("IP do proxy: ").strip()
        port = input("Porta do proxy: ").strip()
        ptype = input("Tipo (http/socks4/socks5): ").strip().lower()

        print(Fore.YELLOW + f"\nTestando {ip}:{port} ({ptype})..." + Style.RESET_ALL)
        is_working = self.scraper.test_proxy(ip, port, ptype)

        if is_working:
            print(Fore.GREEN + "\nSucesso! O proxy está funcionando." + Style.RESET_ALL)
        else:
            print(Fore.RED + "\nFalha. O proxy não respondeu corretamente." + Style.RESET_ALL)

        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        wizard = ProxyScraperWizard()
        wizard.main_menu()
    except KeyboardInterrupt:
        print(Fore.RED + "\nOperação cancelada pelo usuário." + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"\nErro fatal: {e}" + Style.RESET_ALL)
