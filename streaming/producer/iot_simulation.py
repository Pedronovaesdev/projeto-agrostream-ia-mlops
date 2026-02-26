import pandas as pd
import json
import time
import uuid
import sys
from confluent_kafka import Producer


KAFKA_BROKER = 'localhost:9092'
TOPIC_NAME = 'raw-sensor-data'
GREENHOUSE_ID = 'GH-001' 

def receipt_callback(err, msg):
    """Função de callback para confirmar se a mensagem foi entregue ao Kafka."""
    if err is not None:
        print(f"❌ Falha ao entregar mensagem: {err}")
    else:
        print(f"✅ Evento entregue ao tópico {msg.topic()} | Partição: {msg.partition()} | Offset: {msg.offset()}")

def run_simulator():
    print("🚜 A iniciar o Simulador IoT AgroStream...")
    
    conf = {
        'bootstrap.servers': KAFKA_BROKER,
        'client.id': 'iot-sensor-simulator',
        'acks': 'all', 
        'enable.idempotence': True 
    }
    
    try:
        producer = Producer(conf)
    except Exception as e:
        print(f"Erro ao conectar ao Kafka: {e}")
        sys.exit(1)

    try:
        df = pd.read_csv('../../data/data.csv', sep=',', decimal=',')
        df = df.dropna(subset=['greenhous_temperature_celsius', 'greenhouse_humidity_percentage'])
    except FileNotFoundError:
        print("❌ Erro: Ficheiro CSV não encontrado. Verifica o caminho.")
        sys.exit(1)

    print(f"📊 Dados carregados. A iniciar envio de {len(df)} eventos...\n")

    try:
        for index, row in df.iterrows():
            event_payload = {
                "eventId": str(uuid.uuid4()),
                "greenhouseId": GREENHOUSE_ID,
                "timestamp": row['created'],
                "temperature": row['greenhous_temperature_celsius'],
                "humidity": row['greenhouse_humidity_percentage'],
                "illuminance": row['greenhouse_illuminance_lux'],
                "co2": row['greenhouse_equivalent_co2_ppm'],
                "external_temperature": row['online_temperature_celsius'],
                "external_humidity": row['online_humidity_percentage']
            }

            json_data = json.dumps(event_payload)

            producer.produce(
                topic=TOPIC_NAME,
                key=GREENHOUSE_ID.encode('utf-8'),
                value=json_data.encode('utf-8'),
                callback=receipt_callback
            )
            producer.poll(0)

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n🛑 Simulação interrompida pelo utilizador.")
    finally:
        print("A esvaziar a fila de mensagens do produtor...")
        producer.flush()
        print("Desligado.")

if __name__ == '__main__':
    run_simulator()