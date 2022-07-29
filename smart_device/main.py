# IMPORTS
from awscrt import io, mqtt, auth, http
from awsiot import mqtt_connection_builder
import time as t
import json
import constants as c
import serial
import requests
from datetime import datetime



# OPEN CONNECTION TO SERIAL LINE
serial_monitor = serial.Serial(c.PORT, c.BAUDRATE, timeout=1)


# SETUP AWS RESOURCES
event_loop_group = io.EventLoopGroup(1)
host_resolver = io.DefaultHostResolver(event_loop_group)
client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=c.ENDPOINT,
            cert_filepath=c.PATH_TO_CERTIFICATE,
            pri_key_filepath=c.PATH_TO_PRIVATE_KEY,
            client_bootstrap=client_bootstrap,
            ca_filepath=c.PATH_TO_AMAZON_ROOT_CA_1,
            client_id=c.CLIENT_ID,
            clean_session=False,
            keep_alive_secs=6
            )

connect_future = mqtt_connection.connect()
connect_future.result()

# FUNCTION TO CREATE MQTT-MESSAGE BODIES
def create_body(m_type):
    p_location = requests.get('https://ipinfo.io').json()['loc']
    body_data = {
        'type' : m_type, # Type of request, must be ALERT or FIXED
        'patient_id' : c.PATIENT_ID, # ID of the patient, dummy variable 1 is used.
        'patient_location' : p_location, 
        'timestamp' : datetime.timestamp(datetime.now()) # Send current timestamp
    }
    return body_data  

# LISTEN TO SERIAL INPUT
while True:
    try:
        byte_message = serial_monitor.readline()    
        if (byte_message != b'\x0A' or byte_message != ""):
            message = byte_message.decode().strip()
            # If a message is received from the Arduino, add additional information and forward it to the cloud
            if (message in ["ALERT", "FIXED"]):
                mqtt_message = create_body(message) # Add information to message
                mqtt_connection.publish(topic=c.TOPIC, payload=json.dumps(mqtt_message), qos=mqtt.QoS.AT_LEAST_ONCE) # Publish to MQTT-topic
                print("Published an " + message)
    except KeyboardInterrupt: # Disconnect MQTT connection when script is exited
        print("Disconneting MQTT")
        disconnect_future = mqtt_connection.disconnect()
        disconnect_future.result()




