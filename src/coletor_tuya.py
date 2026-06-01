import time
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Outlet
from influxdb import InfluxDBClient
import tinytuya
from sqlalchemy.sql import text
from sqlalchemy.exc import OperationalError

# Conecta ao InfluxDB configurado no seu docker-compose
influx_client = InfluxDBClient(host='influxdb', port=8086, database='consumo_watts')

def coletar_dados_locais():
    db: Session = SessionLocal()
    try:
        # Puxa as tomadas cadastradas que possuem ID e IP preenchidos
        outlets = db.query(Outlet).filter(Outlet.tuya_device_id != None, Outlet.tuya_api_secret != None).all()
        
        for outlet in outlets:
            try:
                # Inicializa a conexão local direta usando o IP e a Local Key salvos
                d = tinytuya.OutletDevice(
                    dev_id=outlet.tuya_device_id,
                    address=outlet.tuya_api_secret,  # Coluna onde salvamos o IP
                    local_key=outlet.tuya_api_key    # Coluna onde salvamos a Local Key
                )
                d.set_version(3.5) # Versão do protocolo Tuya local
                
                # Faz a requisição direta na tomada dentro do seu Wi-Fi
                data = d.status()
                
                if 'dps' in data:
                    # 🔍 LINHA DE DEBUG: Vai printar no terminal exatamente as chaves que a sua tomada possui
                    print(f"🔍 [DEBUG DPS] Chaves recebidas de '{outlet.name}': {data['dps']}")
                    
                    # Correção para buscar tanto se a chave for Texto ('19') quanto Número (19)
                    raw_power = data['dps'].get('19', data['dps'].get(19, 0))
                    watts = float(raw_power) / 10.0
                    
                    print(f"⚡ [LOCAL] Tomada '{outlet.name}' -> Consumo Atual: {watts} W")
                    
                    # CORREÇÃO DE ALINHAMENTO COM O DASHBOARD:
                    json_body = [
                        {
                            "measurement": "consumo",  # Ajustado de 'energia' para 'consumo'
                            "tags": {
                                "outlet": str(outlet.id)  # Ajustado de 'outlet_id' para 'outlet'
                            },
                            "fields": {
                                "value": watts
                            }
                        }
                    ]
                    influx_client.write_points(json_body)
                else:
                    print(f"⚠️ Resposta inválida da tomada {outlet.name}: {data}")
                    
            except Exception as e:
                print(f"❌ Falha de comunicação local com {outlet.name} (IP: {outlet.tuya_api_secret}): {e}")
                
    finally:
        db.close()

def aguardar_banco():
    print("⏳ Verificando conexão com o banco de dados...")
    tentativas = 10
    for i in range(tentativas):
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            print("✅ Banco de dados pronto e aceitando conexões!")
            return True
        except OperationalError:
            print(f"⚠️ Banco ainda inicializando... Tentativa {i+1}/{tentativas}. Aguardando 3 segundos...")
            time.sleep(3)
    raise Exception("❌ Não foi possível conectar ao banco de dados após várias tentativas.")

if __name__ == "__main__":
    # Garante que o banco está estável antes de avançar
    aguardar_banco()
    
    print("🚀 Coletor Local Tuya Ativo (Lendo a cada 7 segundos)...")
    while True:
        coletar_dados_locais()
        time.sleep(7)