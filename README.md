
# Proxy Scraper Wizard 🕵️‍♂️

Este projeto é um módulo Python completo para **coleta, visualização, teste e exportação de proxies gratuitos** de múltiplas fontes públicas.

---

## 📦 Estrutura do Projeto

```
proxy_scraper/
├── proxy_scraper.py      # Módulo com funções de scraping e teste
├── proxy_wizard.py       # Interface interativa (wizard)
├── requirements.txt      # (opcional) Dependências do projeto
└── README.md             # Instruções de uso
```

---

## 🚀 Como Usar

### 1. Instalar Dependências

```bash
pip install requests beautifulsoup4 pandas colorama
```

Ou crie o arquivo `requirements.txt` com:

```
requests
beautifulsoup4
pandas
colorama
```

E instale com:

```bash
pip install -r requirements.txt
```

---

### 2. Executar o Wizard

```bash
python proxy_wizard.py
```

---

## 🎯 Funcionalidades

### ✅ Coleta de Proxies
- ProxyScrape
- Free Proxy List
- Proxy List Download
- HideMy.Name
- Spys.One
- OpenProxy.Space
- SpeedX Proxy GitHub

### ✅ Visualização
- Exibe quantidade e amostras por fonte coletada

### ✅ Teste Individual
- Permite testar um proxy manualmente:
  - Informe IP, porta e tipo (http/socks4/socks5)

---

## ✨ Exemplo de uso manual com o módulo

```python
from proxy_scraper import ProxyScraper

scraper = ProxyScraper(timeout=10)

proxies = scraper.scrape_free_proxy_list()

for proxy in proxies[:5]:
    print(proxy)

# Testar um proxy manual
result = scraper.test_proxy("8.8.8.8", "8080", "http")
print("Proxy válido" if result else "Proxy inválido")
```

---

## 🔐 Avisos

- Sites de proxies podem mudar sua estrutura sem aviso prévio.
- Scraping em alta frequência pode ser bloqueado.
- Use com responsabilidade e apenas em conformidade com a lei.

---

## 📌 Melhorias Futuras

- Suporte a verificação assíncrona (`asyncio`)
- Sistema de pontuação de proxies
- Interface gráfica (GUI) com PyQt ou Tkinter
