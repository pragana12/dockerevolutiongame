import json
import websocket
import time
import sqlite3
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

STATUS_FILE = "status.json"
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

roleta_ids = [
    # "XxxtremeLigh0001",
    "PorROU0000000001"
    #"vctlz20yfnmp1ylr" (aparentemente ruim)
    #"lkcbrbdckjxajdol" (aparentemente ruim)
    #"01rb77cq1gtenhmo"  (aparentemente ruim)
    #"f1f4rm9xgh4j3u2z"  (aparentemente ruim)
    #"7nyiaws9tgqrzaz3" (aparentemente ruim)
    #"mvrcophqscoqosd6" ( verificar id)
    #"RedDoorRoulette1"  connection.kickout
    #"lr6t4k3lcd4qgyrk" connection.kickout
    #"AmericanTable001" connection.kickout

]

def get_websocket_urls_from_supabase():
    """Busca URLs do websocket no Supabase filtradas por provedor='evolution'"""
    try:
        # Verifica credenciais
        if not SUPABASE_URL or not SUPABASE_KEY:
            logging.error("Credenciais do Supabase não configuradas")
            return []
            
        # Cria cliente Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logging.info("Conexão com Supabase estabelecida")
        
        # Consulta dados
        response = supabase.table('websocketurl')\
            .select('url')\
            .eq('provedor', 'evolution')\
            .execute()
            
        logging.info(f"Resposta do Supabase: {response}")
        
        # Verifica se há dados
        if not response.data:
            logging.warning("Nenhum dado retornado do Supabase")
            return []
            
        # Extrai URLs
        urls = [record['url'] for record in response.data]
        logging.info(f"URLs encontradas: {urls}")

        if not urls:
            raise Exception("Nenhuma URL encontrada no Supabase")
                
        base_url = None
        # Tenta conectar em cada URL até encontrar uma que funcione
        for url in urls:
            if connect_to_websocket(url, roleta_ids[0]):
                base_url = url
                logging.info(f"Conectado com sucesso na URL: {url}")
                break
                
        if not base_url:
            raise Exception("Nenhuma URL válida encontrada")
            base_url = urls[0]
        
        return base_url
        
    except Exception as e:
        logging.error(f"Erro ao buscar URLs no Supabase: {str(e)}", exc_info=True)
        return []


def init_db():
    conn = sqlite3.connect('roletas.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS resultados
                 (gametoken TEXT PRIMARY KEY,
                  arialabel TEXT,
                  initialresults TEXT,
                  data TEXT)''')
    
    conn.commit()
    return conn

def substitute_roleta_id(url, roleta_id):
    return url.replace("{id_roleta}", roleta_id)

aria_labels = {
    "PorROU0000000001": "ROLETA AO VIVO",
    "7x0b1tgh7agmf6hv": "IMMERSIVE ROULETTE",
    "vctlz20yfnmp1ylr": "ROULETTE",
    "48z5pjps3ntvqc1b": "AUTO ROULETTE",
    "lkcbrbdckjxajdol": "SPEED ROULETTE",
    "wzg6kdkad1oe7m5k": "VIP ROULETTE",
    "01rb77cq1gtenhmo": "AUTO ROULETTE VIP",
    "DoubleBallRou001": "DOUBLE BALL ROULETTE",
    "f1f4rm9xgh4j3u2z": "AUTO ROULETTE LA PARTAGE",
    "7nyiaws9tgqrzaz3": "FOOTBALL STUDIO ROULETTE",
    "lr6t4k3lcd4qgyrk": "GRAND CASINO ROULETTE",
    "mrpuiwhx5slaurcy": "Hippodrome Grand Casino",
    "mvrcophqscoqosd6": "CASINO MALTA ROULETTE",
    "RedDoorRoulette1": "Red Door Roulette",
    "AmericanTable001": "American Roulette",
    "SpeedAutoRo00001": "Speed Auto Roulette",
    "p675txa7cdt6za26": "Roulette in Spanish"
}

def get_aria_label(roleta_id):
    return aria_labels.get(roleta_id, "Aria Label Padrão")

def connect_to_websocket(url, roleta_id):
    """Tenta conectar ao websocket e retorna se foi bem sucedido"""
    try:
        ws = websocket.WebSocket()
        base_url_connect = substitute_roleta_id(url, roleta_id)
        ws.connect(base_url_connect)
        msg = ws.recv()
        parse_msg = json.loads(msg)
        
        if 'type' in parse_msg and parse_msg['type'] == 'connection.kickout':
            raise websocket.WebSocketException(f"Erro: {parse_msg['args']['reason']}")
            
        return True
    except Exception as e:
        logging.warning(f"Falha ao conectar na URL {url}: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/roleta_websocket.log'),
            logging.StreamHandler()
        ]
    )
    
    conn = init_db()
    
    base_url = get_websocket_urls_from_supabase()

    while True:
        try:
            game_info = []
            for roleta_id in roleta_ids:
                try:
                    url = substitute_roleta_id(base_url, roleta_id)
                    check_resultado = None
                    reconnect_attempts = 0
                    success = False

                    ws = websocket.WebSocket()
                    ws.connect(url)

                    while True:
                        msg = ws.recv()
                        parse_msg = json.loads(msg)

                        if 'type' in parse_msg and parse_msg['type'] == 'roulette.recentResults':
                            resultado = parse_msg["args"]["recentResults"][0:10]
                            def remove_after_x(item):
                                if 'x' in item:
                                    return item.split('x')[0]
                                return item

                            cleaned_results = [[remove_after_x(item[0])] for item in resultado]
                            resultado = cleaned_results

                            resultado_ = [int(x) for sublist in resultado for x in sublist]

                            if resultado_ != check_resultado:
                                check_resultado = resultado_

                                game = {
                                    "Game Token": roleta_id,
                                    "Aria Label": get_aria_label(roleta_id).title(),
                                    "Initial Results": resultado_,
                                }
                                print(game)
                                game_info.append(game)
                                success = True
                                break

                except Exception as e:
                    print(f"Erro ao conectar ou receber dados da roleta {roleta_id}: {e}")
                    logging.error(f"Erro ao conectar ou receber dados da roleta {roleta_id}: {e}")
                    continue
                    
            if game_info:
                game = game_info[0]
                game["Initial Results"] = [int(x) for x in game["Initial Results"]]
                
                c = conn.cursor()
                c.execute('''INSERT OR REPLACE INTO resultados
                             (gametoken, arialabel, initialresults, data)
                             VALUES (?, ?, ?, ?)''',
                         (game["Game Token"],
                          game["Aria Label"],
                          ','.join(map(str, game["Initial Results"])),
                          datetime.now().isoformat()))
                conn.commit()

            time.sleep(1)

        except Exception as e:
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            
            if 'last_error_time' not in globals():
                last_error_time = now
                time_since_last_error = "Primeiro erro"
            else:
                time_since_last_error = str(now - last_error_time)
            
            last_error_time = now
            
            log_message = f"[{current_time}] Erro: {e} | Tempo desde último erro: {time_since_last_error}\n"
            logging.error(log_message)
            
            print(f"Erro: {e}")
            print('RECONECTANDO!!')
            logging.error(f"Erro: {e}", exc_info=True)
            urls = get_websocket_urls_from_supabase()
            time.sleep(1)
            continue
