# IoT Lights with Python, AWS, Alexa, and Raspberry Pi
### Background
I have an old painting that can be lit with LED lights. After using numerous
remote and battery powered lights I decided to build
my own IoT LED lights that would response to Alexa. A fully blog and tutorial
can be found in my [Medium article](https://www.medium.com).

The code should be well documented for a more technical look than the
blog article touches upon. Some of the code for sessions in the Lambda
function will be commented out. No data will be stored in sessions for
this project, but I have left it there as reference if a developer decides
to implement it.

The three directories correspond to where that code will be used. Likely, the
only code that will be run by a developer's device will be on the
Raspberry Pi. However, I find it helpful to maintain the environment variables
on your development computer for reference. I will **only** be reviewing
the set up and deploy for code here. **The commands will be for Linux.**
For a full tutorial of setting up please visit the [blog](https://www.medium.com).

## Requirements
You will need the following for the running the code of this project.
* A virtual environment set up. I recommend [virtualenv](https://pypi.python.org/pypi/virtualenv)
and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/)
* Raspberry Pi Zero W with Rasperian installed and a 5 V power supply
* An Amazon Developer account (preferably made under the same Amazon account tied to your Echo)
Additionally, you will want to also have the following to physically set up
the lights.
* A strand of SMD5050 LED RGB Lights
* 12V power supply for the lights
* Three N-Channel MOSFETS (I used P30N06LE)
* A breadboard and jumper wires (PCB board and solder if you want to make it more permanent after breadboarding)
* Amazon Echo Dot

## Setup
From the command line clone and cd in to the directory and create a .env file
for environment variables.
```
$ git clone https://github.com/altonelli/my_painting.git
$ cd ~/<path_to_repos>/my_painting
$ touch .env
```
Edit the .env file to look like the following and set up your virtual
environment to source the file.
```
#General AWS credentials for Pi
AWS_IOT_CERTIFICATE_FILENAME="~/<path_to_credentials>/XXXXX-certificate.pem.crt"
AWS_IOT_PRIVATE_KEY_FILENAME="~/<path_to_credentials>/XXXXX-private.pem.key"
AWS_IOT_PUBLIC_KEY_FILENAME="~/<path_to_credentials>/XXXXX-public.pem.key"
AWS_IOT_ROOT_CA_FILENAME="~/<path_to_credentials>/root-ca.pem"
#IoT Information
AWS_IOT_MQTT_HOST="XXXXX.iot.us-east-1.amazonaws.com"
AWS_IOT_MQTT_PORT=8883
AWS_IOT_MQTT_PORT_UPDATE=8443
AWS_IOT_MQTT_CLIENT_ID="my_painting"
AWS_IOT_MY_THING_NAME="my_painting"
#Alexa Skill Information
AWS_ALEXA_SKILLS_KIT_ID="amzn1.ask.skill.XXXXX"
```

## AWS Lambda

## Raspberry Pi
I recommend also setting up a virtual environment for the Raspberry Pi. I did
so because I was developing and testing on it, but I recommend doing so
especially if you are going to be reusing the Pi.

### The pigpio library
You'll need the C pigpio library to use the Python pigpio library. Run
the following command.
```
$ sudo apt-get install pigpio
```
With your virtual environment set up, install all dependencies.
```
$ pip install -r raspberry_pi/requirements.txt
```
To use the pigpio library, a pigpio daemon has to be set up. To do this
run the following command after starting up the Pi.
```
$ sudo pigpiod
```
If you ever need to destroy the daemon, run
```
$ sudo killall pigpiod
```
You will likely want the daemon to start on boot. To do so, run
```
$ sudo systemctl enable pigpiod
```

### Running the Python script
You will likely want to run the code on the so that you can close your
terminal or ssh client and allow the code to continue to run. Run it in the
background with nohup.
```
$ nohup python ./raspberry_pi/shadow_client.py &
```

## Contributing
If you would like to contribute, whether to add a feature or correct a bug,
feel free to fork the repo and make a PR.