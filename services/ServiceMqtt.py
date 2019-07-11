from racing.calculations import car_status_speed, race_positions, car_position, race_events
import paho.mqtt.client as mqtt
import json


class ServiceMqtt:
    def __init__(self, host: str = 'broker', port: int = 1883, topic: str = 'carCoordinates'):
        self._topic = topic
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_publish = self.on_publish
        self.client.on_log = self.on_log
        self.client.connect(host, port, 60)
        self.client.loop_forever()

    def on_message(self, client, userdata, message):
        msg = json.loads(str(message.payload.decode("utf-8")))
        car_speed_payload = car_status_speed(msg)
        self.client.publish('carStatus', car_speed_payload)
        race_positions()
        race_position_payload = car_position(msg)
        self.client.publish('carStatus', race_position_payload)
        event_payload = race_events(msg)
        if event_payload:
            self.client.publish('events', event_payload)

    def on_publish(self, client, userdata, result):
        print("Message published...")

    def on_log(self, client, userdata, level, buf):
        print("log: ", buf)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to broker")
            client.subscribe(self._topic)
        else:
            print("Connection failed")
