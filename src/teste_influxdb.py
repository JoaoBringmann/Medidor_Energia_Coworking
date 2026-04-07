#!/usr/bin/env python3
"""
Script de teste para enviar dados ao InfluxDB
Este script simula dados de consumo de energia para testar os gráficos
"""

from influxdb import InfluxDBClient
import time
import random
from datetime import datetime

def enviar_dados_teste():
    """Envia dados de teste para o InfluxDB"""

    client = InfluxDBClient(host='influxdb', port=8086, database='consumo_watts')

    print("Conectando ao InfluxDB...")

    databases = client.get_list_database()
    db_names = [db['name'] for db in databases]

    if 'consumo_watts' not in db_names:
        client.create_database('consumo_watts')
        print("Banco 'consumo_watts' criado!")

    client.switch_database('consumo_watts')

    print("Enviando dados de teste...")

    tomadas = ['tomada_1', 'tomada_2', 'tomada_3']

    for minuto in range(10):
        timestamp = datetime.now()

        for tomada in tomadas:
            watts = random.uniform(50, 200)

            json_body = [
                {
                    "measurement": "consumo_energia",
                    "tags": {
                        "tomada": tomada,
                        "local": "coworking_sala_principal"
                    },
                    "time": timestamp.isoformat(),
                    "fields": {
                        "watts": watts,
                        "kwh_acumulado": watts * (minuto + 1) / 60
                    }
                }
            ]

            client.write_points(json_body)
            print(f"{timestamp.strftime('%H:%M:%S')} - {tomada}: {watts:.1f}W")

        time.sleep(1)

    print("\n Dados de teste enviados com sucesso!")
    print(" Verifique no Grafana: http://localhost:3000")
    print(" Usuário: admin | Senha: admin123")

if __name__ == "__main__":
    enviar_dados_teste()