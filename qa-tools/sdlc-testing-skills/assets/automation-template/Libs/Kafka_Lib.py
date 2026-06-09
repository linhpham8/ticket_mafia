from base64 import decode
from multiprocessing.sharedctypes import Value
import os, ssl, json
from typing_extensions import Self

from kafka import KafkaProducer, KafkaConsumer
from kafka.client_async import KafkaClient
from kafka.consumer import group
from kafka.structs import TopicPartition

from robot.api.deco import keyword
from robot.output import stdoutlogsplitter
from sys import stdout, __stdout__
from robot.api import logger
from robot.api.deco import not_keyword

bootstrap_servers = ['confluent-kafka-tw-1.int.onemount.dev:9093', 'confluent-kafka-tw-2.int.onemount.dev:9093', 'confluent-kafka-tw-3.int.onemount.dev:9093',
        'confluent-kafka-sg-4.int.onemount.dev:9093', 'confluent-kafka-sg-5.int.onemount.dev:9093 ', 'confluent-kafka-sg-6.int.onemount.dev:9093']

my_topic = "b2b-integration-log-tracking-event-qc"
my_group = '0'
   

class Kafka_Lib(object):
    """
    Khai báo certificate để truy cập vào kafka
    Library | Kafka_Lib | omd-qc-clients.int.onemount.dev-cert.pem | omd-qc-clients.int.onemount.dev-key.pem |  
    Thư viện chưa được hoàn hảo, mọi người có thể improve thêm :v
    """
    ROBOT_LIBRARY_SCOPE = "GLOBAL"
    ROBOT_LIBRARY_DOC_FORMAT = "ROBOT"

    def __init__(self, cert_file_name, key_file_name):

        super().__init__()
        self.cert_file_name = cert_file_name
        self.key_file_name = key_file_name

    def Kafka_ssl_contexts(self):

        KAFKA_CER = os.getenv('KAFKA_CER')

        context = ssl.SSLContext(protocol=ssl.PROTOCOL_TLS)
        context.load_cert_chain(certfile = KAFKA_CER + self.cert_file_name,
                                keyfile = KAFKA_CER + self.key_file_name)   
        return context

    @keyword('Kafka_send_message')      
    def Kafka_send_message(self, topics: str, key: str, message: str):

        """ Kafka_send_message : Gửi messgae lên kafka
        - ``arg``: topics | key | message 
        - ``Ex``: Kafka_send_message | topics=b2b-integration-log-tracking-event-qc | key=auto | message={id:1}
        - ``Return ``Response message Data json    
        """

        producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                        security_protocol='SSL',
                        ssl_context=self.Kafka_ssl_contexts())

        future = producer.send(topics, value=bytes(message, 'UTF-8'), key=bytes(key, 'UTF-8'))
        result = future.get(timeout=5)
        producer.flush()
        print(result)
        data = {}
        for index, value in enumerate(result):
          data[result._fields[index]] = value
        print(json.dumps(data))
        return json.dumps(data)

    @keyword('Kafka_get_message')
    def Kafka_get_message(self, topics: str, **kwargs):

        """ Kafka_get_message : Lấy message từ kafka theo 1 số điều kiện nhật định offset hoặc messageId, phần này chưa được tối ưu lắm.
        - ``arg``: topics | key | **kwargs  
        - ``Ex``: Kafka Get Message | topics=b2b-integration-log-tracking-event-qc | offset=12345
        - ``Ex``: Kafka Get Message | topics=b2b-integration-log-tracking-event-qc | messageId=bd846147-a9b6-4090-b26f-8fd3f7f975ba
        - ``Return ``Response message Data json    
        """

        consumer = KafkaConsumer(my_topic, bootstrap_servers=bootstrap_servers,
                                security_protocol="SSL",
                                auto_offset_reset='earliest',
                                ssl_context=self.Kafka_ssl_contexts())
        data = []
        consumer.subscribe([topics])
        for key, value in kwargs.items():
            print(key, value)
        try:
            if key == 'messageId':
                for message in consumer:
                    # if message.offset == int(set_offset):                            
                        if str(value) in message.value.decode("utf-8"):
                        # if '2022100721685' in str(message.value):
                            # print(message.value.decode("utf-8"))
                            print("Finding... : "+ str(value))
                            data = message.value.decode("utf-8")
                            break

            elif key == 'offset':
                for message in consumer:
                    if str(value) == str(message.offset):
                        print("Finding... : "+ str(value))
                        data = message.value.decode("utf-8")
                        break
            
        except Exception as err:

            print(repr(err))
        finally:

            consumer.close()
        
        print(json.loads(data))
        return json.loads(data)
       

# run = Kafka_Lib()
# run.Kafka_send_message("b2b-integration-log-tracking-event-qc","key", "message")
# run.Kafka_get_message('b2b-integration-log-tracking-event-qc', messageId='bd846147-a9b6-4090-b26f-8fd3f7f975ba')