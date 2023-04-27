import PySimpleGUI as sg
import time
import threading
import paho.mqtt.client as mqtt
import logging
from threading import Thread
import json
from appJar import gui

# TODO: choose proper MQTT broker address
MQTT_BROKER = 'mqtt.item.ntnu.no'
MQTT_PORT = 1883

# TODO: choose proper topics for communication
MQTT_TOPIC_INPUT = 'ttm4115/team_x/command'
MQTT_TOPIC_OUTPUT = 'ttm4115/team_x/answer'

def countdown(minutes):
    seconds = minutes * 60
    while seconds > 0:
        time.sleep(1)
        seconds -= 1
        minutes, sec = divmod(seconds, 60)
        time_left = f'{minutes:02d}:{sec:02d}'
        window['-TIMER-'].update(value=time_left)
        if event == sg.WIN_CLOSED:
            break

layout = [[sg.T("")],
    [sg.T("Enter Unit number:"), sg.Input(size=(2,1), key='UnitNumber')],
    [sg.T("")],
    [sg.T("Enter time estimates for subtasks: ")],
    [sg.T("Individual RAT"),sg.T(""),sg.T(""),sg.T(""), sg.Input(size=(2,1), key='TimeInduvidualRat')],
    [sg.T("Team RAT"),sg.T(""),sg.T(""),sg.T(""), sg.Input(size=(2,1), key='timeTeamRat')],
    [sg.T("Unit part 1"),sg.T(""),sg.T(""),sg.T(""), sg.Input(size=(2,1), key='TimeUnitPart1')],
    [sg.T("Unit part 2"),sg.T(""),sg.T(""),sg.T(""), sg.Input(size=(2,1), key='TimeUnitPart2')],
    [sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.Button('Start RAT')],
    [sg.T("")],
    [sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.T(""),sg.Text('Time Left:'), sg.Text(size=(10,1), key='-TIMER-')],
    #[sg.Text("Time remaining: ", font=("Helvetica", 10), justification='center', key='-TIMER-')],
    [sg.T("")],
    [sg.T("Teams"),sg.T(""),sg.T(""),sg.T(""),sg.T("Progression"),sg.T(""),sg.T(""),sg.T(""),sg.T("Needs help")],    
    [sg.T(""),sg.T("01"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR01-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam01')],
    [sg.T(""),sg.T("02"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR02-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam02')],
    [sg.T(""),sg.T("03"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR03-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam03')],
    [sg.T(""),sg.T("04"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR04-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam04')],
    [sg.T(""),sg.T("05"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR05-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam05')],
    [sg.T(""),sg.T("06"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR06-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam06')],
    [sg.T(""),sg.T("07"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR07-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam07')],
    [sg.T(""),sg.T("08"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR08-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam08')],
    [sg.T(""),sg.T("09"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR09-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam09')],
    [sg.T(""),sg.T("10"),sg.T(""),sg.T(""),sg.ProgressBar(10, orientation='h', size=(11, 20), key='-PROGRESSBAR10-'),sg.T(""),sg.T(""),sg.T(""), sg.Checkbox('', enable_events=True, key='helpTeam10')],
    [sg.T("")]]

window = sg.Window('Multiple Checkboxes and Progress Bar', layout)
# Add MQTT code for retreiving number of minutes in disposal from TA

minutes = 15
seconds = 0 

class ManagerComponent:
    """
    The component to send voice commands.
    """
    def on_connect(self, client, userdata, flags, rc):
        # we just log that we are connected
        self._logger.debug('MQTT connected to {}'.format(client))

    def on_message(self, client, userdata, msg):
        pass

    def __init__(self):
        # get the logger object for the component
        self._logger = logging.getLogger(__name__)
        print('logging under name {}.'.format(__name__))
        self._logger.info('Starting Component')

        # create a new MQTT client
        self._logger.debug('Connecting to MQTT broker {} at port {}'.format(MQTT_BROKER, MQTT_PORT))
        self.mqtt_client = mqtt.Client()
        # callback methods
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        # Connect to the broker
        self.mqtt_client.connect(MQTT_BROKER, MQTT_PORT)
        # start the internal loop to process MQTT messages
        self.mqtt_client.loop_start()

        self.create_gui()

    def create_gui(self):

        def publish_command(command):
            payload = json.dumps(command)
            self._logger.info(command)
            self.mqtt_client.publish(MQTT_TOPIC_INPUT, payload=payload, qos=2)

        def on_startRat_pressed(unitNumber,timeInduvidualRat,timeTeamRat,timeUnitPart1,timeUnitPart2):
            name = "Unit " + unitNumber
            command = {"command": "new_unit", "name": name, "timeInduvidualRat": timeInduvidualRat,"timeTeamRat": timeTeamRat,"timeUnitPart1": timeUnitPart1,"timeUnitPart2": timeUnitPart2}
            publish_command(command)      

    def on_message(self, client, userdata, msg):
        """
        Processes incoming MQTT messages.
        We assume the payload of all received MQTT messages is an UTF-8 encoded
        string, which is formatted as a JSON object. The JSON object contains
        a field called `command` which identifies what the message should achieve.
        As a reaction to a received message, we can for example do the following:
        * create a new state machine instance to handle the incoming messages,
        * route the message to an existing state machine session,
        * handle the message right here,
        * throw the message away.
        """
        self._logger.debug('Incoming message to topic {}'.format(msg.topic))
        # encdoding from bytes to string. This
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception as err:
            self._logger.error('Message sent to topic {} had no valid JSON. Message ignored. {}'.format(msg.topic, err))
            return
        command = payload.get('command')
        self._logger.debug('Command in message is {}'.format(command))
        if command == 'new_timer':
            try:
                print(type(self))
                timer_name = payload.get('name')
                duration = int(payload.get('duration'))
                # create a new instance of the timer logic state machine
                timer_stm = TimerLogic.create_machine(timer_name, duration, self)
                # add the machine to the driver to start it
                self.stm_driver.add_machine(timer_stm)
            except Exception as err:
                self._logger.error('Invalid arguments to command. {}'.format(err))

    def stop(self):
        """
        Stop the component.
        """
        # stop the MQTT client
        self.mqtt_client.loop_stop()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Start RAT':
        unitNumber = int(values['UnitNumber'])
        timeInduvidualRat = int(values['TimeInduvidualRat'])
        timeTeamRat = int(values['TimeTeamRat'])
        timeUnitPart1 = int(values['TimeUnitPart1'])
        timeUnitPart2 = int(values['TimeUnitPart2'])
        countdown_thread = threading.Thread(target=countdown, args=(minutes,))
        countdown_thread.start()
        ManagerComponent.on_startRat_pressed(unitNumber,timeInduvidualRat,timeTeamRat,timeUnitPart1,timeUnitPart2)

    

# logging.DEBUG: Most fine-grained logging, printing everything
# logging.INFO:  Only the most important informational log items
# logging.WARN:  Show only warnings and errors.
# logging.ERROR: Show only error messages.
debug_level = logging.DEBUG
logger = logging.getLogger(__name__)
logger.setLevel(debug_level)
ch = logging.StreamHandler()
ch.setLevel(debug_level)
formatter = logging.Formatter('%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

t = ManagerComponent()       

window.close()
