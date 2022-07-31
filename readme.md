
# Proof-of-concept connected wheelchair

This project demonstrates a connected-wheelchair, capable of detecting whether it is standing upright or fallen over. In case the wheelchair has fallen over, it alerts a medical respondent via email. If the issue is solved, it informs the medical respondent that aid is no longer required. 

It functions as a proof-of-concept for the master thesis: An Edge Computing Reference Architecture for Healthcare by Lucas de Geus.

The paper is available [here](paper.pdf)


## Components

The project consists of three components:
- An constrained edge device (Arduino Uno)
- An smart device functioning as a gateway (HP Elitebook)
- A cloud (AWS)

The __constrained edge device__ has a tilt switch that detects whether it has fallen over. It has a red LED and piezo (sound device) to alert people nearby that the wheelchair has fallen over, both are activated if the wheelchair falls over, and an alert is send to the smart device. Furthermore, it has a button to turn of the LED and piezo, which is also used to send a message to the smart device that there is no longer a need for medical aid. Lastly, it has another button and a green-LED, which are used to reset the wheelchair. If the reset button is pressed, the device is reset and the green-LED will blink for 3 seconds, the end of the blinking indicates that the reset is complete.

The __smart device__, in this case a HP-Elitebook laptop, runs a python script and functions as a gateway between the edge device and the cloud. To communicate with the edge device it listens to its serial port and waits for messages. As soon as a message is received, it forwards this messages over MQTT to AWS IoT Core and adds the required authenhication (X.509 certificates).

The __cloud (AWS)__ is subscribed to a MQTT-topic on which the smart device published its messages. If the certificates are verified and correct, AWS IoT Core send the data received to a AWS Lambda function, which in turn sends an email containing the patients ID, location, required aid, and time of accident to a medical respondent.

The functioning of the proof-of-concept is demonstrated in POC_CONNECTED.avi and POC_DISCONNECTED.avi. Showing one set-up where the constrained device is connected to the cloud via a gateway smart device, and a set-up where the constrained device is working standalone, running on a 9V battery and no connection to any other device.

## Installation
It is advised to first set up the cloud environment, as the certificates that are generated are required for the other components.

### Cloud
For the cloud environment we need multiple AWS Services:
- Simple Email Service (SES)
- Lambda
- IoT Core

#### AWS SES
To send emails using AWS services atleast two verified identities are required (atleast one receiver/sender). To create such identities go to AWS SES -> Verified Identities -> Create Identity. Make sure to confirm the identities via mail.

#### Lambda
Create a Lambda function and copy the code available in this repository (cloud/lambda_function.py). Once created, make sure Lambda has the right to use SES and send mails. In case you have no existing policy for this, follow the following [guide](https://aws.amazon.com/premiumsupport/knowledge-center/lambda-send-email-ses/).

#### IoT Core
First, create a "Thing" from AWS IoT > Manage > All Devices > Things > Create Things. Press "Create single thing", enter "wheelchair" for the "Thing Name", and press next. Choose "Auto-generate a new certificate". Press "Next" and "Create thing".

Now __make sure__ to download all certificates and key file (device certificate, public key file, private key file) and copy and save the content of the RSA 2048 bit key: Amazon Root CA1 to text file names root.pem.

Next, create a rule from AWS IoT > Manage > Message Routing > Rules > Create rule. Name the rule "forwardmail", use SQL-version 2016-03-23 and add the following SQL statement: 

SELECT * FROM 'services/alerting'

press "Next". In the section "Rule Actions", choose the action "Send a message to a Lambda function" and pick the previously created lambda function. Press "Next" and "Create".


Your AWS services should now do the following: wait for messages being published to the MQTT-topic services/alerting, if a message arrives forward it to lambda, lambda sends an email to a medical respondent.

### Constrained edge device
The setup of the constrained edge devices has two parts:
- Setting up the hardware
- Setting up the operating system and software

#### Hardware
In this project a Arduino Uno was used and all instructions will be based on this board. Make sure the circuit is the same as shown in the cirtcuit-figure (constrained_device/CIRCUIT.PNG). Steps:
1. Connect power and ground from breadboard to the Arduino (on 5v and GND). 
2. Connect one lead of the tilt switch to 5V and the other to a 10 Kilohm to ground. Connect the junction where the lead and resistor meet to analog pin 1. The tilt-switch is kept in place by an unconnected wire going over it, this can also be replaced by other solution (glue, ductape etc.).
3. Connect the anodes of the red/green LED to digital pins 10/11 and connect them to ground through 220 ohm resistors.
4. Connect the RESOLVER-button to 5V via one lead, and the other to a 220 ohm to ground. Connect the junction of the lead and resistor to digital pin 2.
5. Connect the RESET-button to 5V via one lead, and the other to a 220 ohm to ground. Connect the junction of the lead and resistor to digital pin 4.
6. Connect one end of the piezo to ground and the other to digital pin 8.

#### Software
We use freeRTOS on the arduino board, mainly because it provides an easy way of running multiple tasks and it operates well with AWS-stack.

Perform the following steps in the given order:
1. Download freeRTOS for AVR, preferably version 10.4.6-5 ([here] https://www.arduino.cc/reference/en/libraries/freertos/)
2. Download and set-up the Arduino IDE [guide](https://docs.arduino.cc/software/ide-v1/tutorials/Windows). Make sure that in the IDE->Tools the correct board is selected and the PORT is COM7.
3. From the IDE, go to Sketch->Include Library->Add .ZIP libary and select the downloaded freeRTOS for AVR.
4. Connect the PC and Arduino board using the USB-cable. 
5. Import the _main.ino_ file available in the repository (constrained_device/main.cpp) and upload it to the board.

### Smart device
The smart device runs a python script to connect the edge and cloud. 
1. Create virtual environment [guide](https://docs.python.org/3/library/venv.html)
2. Clone the smart_device folder
3. Install the required packages (available in smart_device/requirements.txt)
4. Place the downloaded certificates from the Cloud-steps in the _certificates_ folder.
5. Update the constants.py file, make sure you change ENDPOINT, PATH_TO_CERTIFICATE, PATH_TO_PRIVATE_KEY, and PATH_TO_AMAZON_ROOT_CA_1.
6. Run the script (python3 main.py). -- Make sure COM7 is free!


### Contact
Mail: lucasdegeus1999@gmail.com
