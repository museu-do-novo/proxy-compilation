def save_proxies_to_txt(self, proxies: List[Dict[str, str]], source_name: str) -> None:
    """Salva proxies no formato tipo://ip:porta em arquivos organizados"""
    os.makedirs('./lists', exist_ok=True)
    clean_name = source_name.replace(' ', '_').replace('.', '_').replace('/', '_')
    
    # Verifica e garante que cada proxy tenha um tipo
    validated_proxies = []
    for proxy in proxies:
        if 'type' not in proxy:
            # Tenta determinar o tipo com base na fonte
            if 'socks4' in source_name.lower():
                proxy['type'] = 'socks4'
            elif 'socks5' in source_name.lower():
                proxy['type'] = 'socks5'
            elif 'https' in source_name.lower():
                proxy['type'] = 'https'
            else:
                proxy['type'] = 'http'  # Padrão seguro
        
        validated_proxies.append(proxy)
    
    # Organiza por tipo para criar arquivos separados
    proxies_by_type = {}
    for proxy in validated_proxies:
        ptype = proxy['type'].lower()
        if ptype not in proxies_by_type:
            proxies_by_type[ptype] = []
        proxies_by_type[ptype].append(proxy)
    
    # Salva em arquivos
    for ptype, proxy_list in proxies_by_type.items():
        filename = f"./lists/{clean_name}_{ptype}.txt"
        with open(filename, 'w') as f:
            for proxy in proxy_list:
                # Garante o formato tipo://ip:porta
                line = f"{ptype}://{proxy['ip']}:{proxy['port']}"
                
                # Adiciona metadados como comentários (opcional)
                metadata = []
                if 'country' in proxy:
                    metadata.append(f"country={proxy['country']}")
                if 'anonymity' in proxy:
                    metadata.append(f"anon={proxy['anonymity']}")
                if 'source' in proxy:
                    metadata.append(f"src={proxy['source']}")
                
                if metadata:
                    line += f"  # {' '.join(metadata)}"
                
                f.write(line + "\n")
