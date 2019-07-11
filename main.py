from services.ServiceMqtt import ServiceMqtt
import threading


t1 = threading.Thread(target=ServiceMqtt)
t1.start()

