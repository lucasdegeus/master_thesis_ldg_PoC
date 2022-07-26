## Constants
PORT = 'COM7' # Serial port used by Arduino
BAUDRATE = 9600 # Default baud rate of Arduino Uno (9600 bits per second)
PATIENT_ID = 1 # Dummy constant, in real-world application this should be variable

# AWS CONSTANTS
ENDPOINT = "YOUR_AWS_IOT_ENDPOINT" # AWS_IOT MQTT endpoint, found in the AWS Console: AWS IoT > Settings > Device data endpoint
CLIENT_ID = "testDevice" # Device client_id
PATH_TO_CERTIFICATE = "PATH_TO_YOUR_CERTIFICATE" # File should be downloaded when creating an AWS IoT Thing
PATH_TO_PRIVATE_KEY = "PATH_TO_YOUR_PRIVATE_KEY" # File should be downloaded when creating an AWS IoT Thing
PATH_TO_AMAZON_ROOT_CA_1 = "PATH_TO_YOUR_AWS_ROOT" # AWS PUBLIC ROOT .pem, https://www.amazontrust.com/repository/AmazonRootCA1.pem
TOPIC = "services/alerting" # TOPIC WHERE MQTT-MESSAGES ARE PUBLISHED TO