import ssl
import os

from kafka import KafkaProducer


def send_message(topics: str, mes: str, key='autotest'):
    context = ssl.create_default_context(purpose=ssl.Purpose.CLIENT_AUTH,
                                         cafile='C:/Kafka/kafka-int-ca.crt')
    context.load_cert_chain(certfile='C:/Kafka/salestools_worker_clients.int.vinid.dev.cer',
                            keyfile='C:/Kafka/salestools-worker-clients.int.vinid.dev.key',
                            password=os.environ['KAFKA_PASSWORD'])          #os.environ['KAFKAPASSWORD']

    p = KafkaProducer(bootstrap_servers=['vep-kafka-1.int.vinid.dev:9093', 'vep-kafka-2.int.vinid.dev:9093',
                                         'vep-kafka-3.int.vinid.dev:9093'],
                      security_protocol='SSL',
                      ssl_context=context)
    # ssl_cafile='C:/Users/haltn8/projects/Kafka/kafka-int-ca.crt',
    # ssl_certfile='C:/Users/haltn8/projects/Kafka/salestools_worker_clients.int.vinid.dev.cer',
    # ssl_keyfile='C:/Users/haltn8/projects/Kafka/salestools-worker-clients.int.vinid.dev.key',
    # ssl_password='uHFFDE7Hx8LaJQ6j')
    future = p.send(topics, key = bytes(key, 'UTF-8'), value = bytes(mes, 'UTF-8'))
    result = future.get(timeout=60)
    p.flush()
    print(result)


if __name__ == "__main__":
    send_message('c1.b2b-platform.shipment-event.qc', 'iklm1vccvccv1111')
