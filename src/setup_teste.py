#!/usr/bin/env python3
"""
Script para popular o banco de dados com tomadas e enviar dados de teste
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Outlet
from influxdb import InfluxDBClient
import time
import random
from datetime import datetime

def popular_banco():
    """Cria tomadas no banco PostgreSQL"""

    DATABASE_URL = "postgresql://admin:password123@db/smart_lan"
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = SessionLocal()

    # Criar tomadas se não existirem
    tomadas = [
        {"name": "Tomada 1", "location": "Sala Principal"},
        {"name": "Tomada 2", "location": "Sala Principal"},
        {"name": "Tomada 3", "location": "Sala de Reuniões"}
    ]

    for tomada in tomadas:
        existing = db.query(Outlet).filter(Outlet.name == tomada["name"]).first()
        if not existing:
            outlet = Outlet(name=tomada["name"], location=tomada["location"])
            db.add(outlet)
            print(f"Criada {tomada['name']} - {tomada['location']}")

    db.commit()
    db.close()
    print("Tomadas criadas no banco!")

def enviar_dados_teste():
    """Envia dados de teste no formato esperado pelo dashboard"""

    # Conectar ao InfluxDB
    client = InfluxDBClient(host='influxdb', port=8086, database='consumo_watts')

    print("Conectando ao InfluxDB...")

    # Verificar se o banco existe
    databases = client.get_list_database()
    db_names = [db['name'] for db in databases]

    if 'consumo_watts' not in db_names:
        client.create_database('consumo_watts')
        print("Banco 'consumo_watts' criado!")

    client.switch_database('consumo_watts')

    print("Enviando dados de teste no formato correto...")

    tomadas = [1, 2, 3]  # outlet IDs

    for minuto in range(10):  # 10 minutos de dados
        timestamp = datetime.now()

        for outlet_id in tomadas:
            watts = random.uniform(50, 200)

            # Formatar dados no formato esperado pelo dashboard
            # measurement: 'consumo', field: 'value', tag: 'outlet'
            json_body = [
                {
                    "measurement": "consumo",
                    "tags": {
                        "outlet": str(outlet_id)
                    },
                    "time": timestamp.isoformat(),
                    "fields": {
                        "value": watts
                    }
                }
            ]

            client.write_points(json_body)
            print(f"{timestamp.strftime('%H:%M:%S')} - Outlet {outlet_id}: {watts:.1f}W")

        time.sleep(1)

    print("\n Dados de teste enviados com sucesso!")
    print(" Acesse o dashboard: http://localhost:8000/dashboard")
    print(" Usuário: admin | Senha: admin123")

if __name__ == "__main__":
    popular_banco()
    enviar_dados_teste()