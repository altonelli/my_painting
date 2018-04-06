# IoT Lights with Python, AWS, Alexa, and Raspberry Pi

### Background
I have an old painting that can be lit with LED lights. After using numerous remote and battery powered lights I decided to build my own IoT LED lights that would response to Alexa. A fully blog and tutorial can be found in my [Medium article](https://medium.com/@arthurltonelli/building-an-iot-device-with-alexa-aws-python-and-raspberry-pi-274d941ef3c3). I hope this is helpful for any level of developer.

The code should be well documented for a more technical look than the blog article touches upon. The three directories correspond to where that code will be used. Likely, the only code that will be run by a developer's device will be on the Raspberry Pi. However, I find it helpful to maintain the environment variables on your development computer for reference. I will **only** be reviewing the set up and deploy for code here. **The commands will be for Linux.** For a full tutorial of setting up the Amazon Services and the lights please visit the [blog](https://medium.com/@arthurltonelli/building-an-iot-device-with-alexa-aws-python-and-raspberry-pi-274d941ef3c3).

## Requirements
You will need the following for the running the code of this project.
* Raspberry Pi Zero W with Rasperian installed and a 5 V power supply
* An Amazon Developer account (preferably made under the same Amazon account tied to your Echo)
* A virtual environment set up. I recommend [virtualenv](https://pypi.python.org/pypi/virtualenv) and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
Additionally, you will want to also have the following to physically set up the lights.
* A strand of SMD5050 LED RGB Lights
* 12V power supply for the lights
* Three N-Channel MOSFETS (I used P30N06LE)
* A breadboard and jumper wires (PCB board and solder if you want to make it more permanent after breadboarding)
* An Amazon Echo Device

## Setup
From the command line clone the repo, cd into the directory, and create a .env file for environment variables.
```
$ git clone https://github.com/altonelli/my_painting.git
$ cd ~/<path_to_repo>/my_painting
$ touch .env
```
Edit the .env file to look like the following.
```
#General AWS credentials for Pi
export AWS_IOT_CERTIFICATE_FILENAME="~/<path_to_credentials>/XXXXX-certificate.pem.crt"
export AWS_IOT_PRIVATE_KEY_FILENAME="~/<path_to_credentials>/XXXXX-private.pem.key"
export AWS_IOT_PUBLIC_KEY_FILENAME="~/<path_to_credentials>/XXXXX-public.pem.key"
export AWS_IOT_ROOT_CA_FILENAME="~/<path_to_credentials>/root-ca.pem"
#IoT Information
export AWS_IOT_MQTT_HOST="XXXXX.iot.us-east-1.amazonaws.com"
export AWS_IOT_MQTT_PORT=8883
export AWS_IOT_MQTT_PORT_UPDATE=8443
export AWS_IOT_MQTT_CLIENT_ID="my_painting"
export AWS_IOT_MY_THING_NAME="my_painting"
#Alexa Skill Information
export AWS_ALEXA_SKILLS_KIT_ID="amzn1.ask.skill.XXXXX"
```

### AWS Lambda
There is a bit of set up in AWS. Again look at [this blog](https://medium.com/@arthurltonelli/building-an-iot-device-with-alexa-aws-python-and-raspberry-pi-part-ii-8ad84f24a3ee) for a detailed walk through.
When inside the Lambda function console, zip and upload the code.
```
$ cd ~/<path_to_repo>/lambda_function/
$ zip -r lambda_function.zip .
```
Then select upload in the console and upload the zip folder.

### Raspberry Pi
You will have to copy the certificates and keys to the Raspberry Pi once you have created them through AWS IoT. Then ssh to the Pi.
```
$ scp ~/<path_to_certs>/XXXXX-certificate.pem.crt pi@raspberrypi:~/.credentials/XXXXX-certificate.pem.crt
$ scp ~/<path_to_certs>/XXXXX-private.pem.key pi@raspberrypi:~/.credentials/XXXXX-private.pem.key
$ scp ~/<path_to_certs>/XXXXX-public.pem.key pi@raspberrypi:~/.credentials/XXXXX-public.pem.key
$ scp ~/<path_to_certs>/root-ca.pem pi@raspberrypi:~/.credentials/root-ca.pem
$ ssh pi@192.168.pi.ip
```
I recommend setting up a virtual environment for the Raspberry Pi.
Again, clone the repo, touch the .env file and edit it like above.
```
pi@raspberrypi:$ git clone https://github.com/altonelli/my_painting.git
pi@raspberrypi:$ cd ~/<path_to_repo>/my_painting
pi@raspberrypi:$ touch .env
pi@raspberrypi:$ vi .env
```
With a virtualenv activated source the .env file (or add this to your postactivate file)
```
pi@raspberrypi:$ source ~/<path_to_repo>/.env
```
Finally install all dependencies.
```
pi@raspberrypi:$ pip install -r raspberry_pi/requirements.txt
```

### The Pigpio library
You'll need the C pigpio library to use the Python pigpio library on the Pi. Run the following command.
```
pi@raspberrypi:$ sudo apt-get install pigpio
```
To use the pigpio library, a pigpio daemon has to be set up. To do this
run the following command after starting up the Pi.
```
pi@raspberrypi:$ sudo pigpiod
```
If you ever need to destroy the daemon, run
```
pi@raspberrypi:$ sudo killall pigpiod
```
You will likely want the daemon to start on boot. To do so, run
```
pi@raspberrypi:$ sudo systemctl enable pigpiod
```

## Running the script

### AWS Lambda
Saving the function should enable it to be used.

### Raspberry Pi
Ensure that the Raspberry Pi has red wired to GPIO port 4, blue wired to port 17, and green wired to port 22. GPIO ports are different from the physical pin numbers.

You will likely want to run the code on the so that you can close your terminal or ssh client and allow the code to continue to run. Run it in the background with nohup.
```
pi@raspberrypi:$ nohup python ./raspberry_pi/shadow_client.py &
```

## Built With
* [Alexa Skill Kit](developer.amazon.com/alexa/console/ask/)
* [AWS Lambda](console.aws.amazon.com/lambda/home)
* [AWS IoT](console.aws.amazon.com/iot/home)
* [AWS IoT Python SDK](https://github.com/aws/aws-iot-device-sdk-python)
* [Pigpio](http://abyz.me.uk/rpi/pigpio/)

## Contributing
If you would like to contribute, whether to add a feature or correct a bug, feel free to fork the repo and make a PR.

## Acknowledgments
* The [Amazon "Color Expert" demo app](https://github.com/awslabs/serverless-application-model/tree/master/examples/apps/alexa-skills-kit-color-expert-python) was helpful to write the core of the skill.
* [Jay Proulx's tutorial](https://medium.com/@jay_proulx/headless-raspberry-pi-zero-w-setup-with-ssh-and-wi-fi-8ddd8c4d2742) was helpful in setting up the Raspberry Pi.
* [David Ordnung's tutorial](https://dordnung.de/raspberrypi-ledstrip/) was used in setting of the LED lights.
