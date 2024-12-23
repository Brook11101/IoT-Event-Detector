import copy
import Apriori
from numpy.random import seed
from numpy.random import randint
import numpy as np
import configparser


users = 5
times = 40
npyPath = "../Datasets/IFTTTDataset/Environment/0/npy/"
devicePath = npyPath + "randomDeviceList.npy"

all_rules = []

type = ["data", "switch", "sensor", "command"]

ldm = [
    {"score":3,"Trigger":["NetatmoWeatherStation", 2], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if Netatmo Weather Station(11) is Windy, close MiJia Curtains(1,2)", "triggerType":2},
    {"score":3,"Trigger":["Location", 1], "Condition": [], "Action":[["iRobotRoomba", 0]],"description":"if i leave home, start the iRobot(7)", "triggerType":3},
    # {"score":4,"Trigger":["time", "190000"] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if 7p.m.,close MiJia Curtains(1,2)", "triggerType":0},
    # {"score":2,"Trigger":["time", "70000"] , "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"if 7a.m.,open MiJia Curtains(1,2)", "triggerType":0},
    {"score":4,"Trigger":["RingDoorbell", 2] , "Condition": [], "Action":[["YeelightBulb", 0]],"description":"if doorbell rings(6), open the Yeelight Bulb(3)", "triggerType":3},
    {"score":5,"Trigger":["SmartThingsDoorSensor", 2] , "Condition": [], "Action":[["Notification", 0]],"description":"if door opened(4),notify me.", "triggerType":3},
    {"score":4,"Trigger":["MijiaDoorLock", 0] , "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0],["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0]],"description":"if door opened(5), when after 7p.m., open the lamps(12,13,14,15,16)", "triggerType":3},
    {"score":5,"Trigger":["Location", 1] , "Condition": [], "Action":[["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1]],"description":"if i leave home, close all lamps(12,13,14,15,16)", "triggerType":3},
    {"score":3,"Trigger":["AlexaVoiceAssistance", 2] , "Condition": [], "Action":[["YeelightBulb", 0], ["PhilipsHueLight", 0]],"description":"tell alexa to open hue lights(3,9)", "triggerType":3},
    {"score":3,"Trigger":["AlexaVoiceAssistance", 3] , "Condition": [], "Action":[["YeelightBulb", 1], ["PhilipsHueLight", 1]],"description":"tell alexa to close hue lights(3,9)", "triggerType":3},
    {"score":4,"Trigger":["MideaAirConditioner", 0] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if air conditioner(10) is opened, close curtains(1,2)", "triggerType":1},
    # {"score":2,"Trigger":["temperature", 30] , "Condition": [], "Action":[["MideaAirConditioner", 0]],"description":"if temperature is over 30, open the air conditioner(10)", "triggerType":2},
    # {"score":1,"Trigger":["temperature", 15], "Condition": [], "Action":[["MideaAirConditioner", 1]], "description":"if temperature is under 15, close the air conditioner(10)", "triggerType":2},
    {"score":5,"Trigger":["NetatmoWeatherStation", 3] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if rain(11), close the curtains(1,2)", "triggerType":2},
    {"score":2,"Trigger":["NetatmoWeatherStation", 4], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"if sun(12), open the curtains(1,2)", "triggerType":2},
    {"score":3,"Trigger":["SmartLifePIRmotionsensor1", 2] , "Condition": [], "Action":[["WemoSmartPlug", 0]],"description":"if motion(19) detected, open the wemo smart plug(17).", "triggerType":2},
    {"score":5,"Trigger":["SmartLifePIRmotionsensor1", 2] , "Condition": [], "Action":[["WyzeCamera", 1]],"description":"if motion detected(19), open the camera(18)", "triggerType":2},
    # {"score":2,"Trigger":["humidity", 30] , "Condition": [], "Action":[["MijiaPurifier", 0]],"description":"if humidity is under 30, open the purifier", "triggerType":2},
    # {"score":1,"Trigger":["humidity", 60], "Condition": [], "Action":[["MijiaPurifier", 1]],"description":"if humidity is over 60, close the purifier", "triggerType":2},
]

whd = [
    {"score":2,"Trigger":["WemoSmartPlug", 0], "Condition": ["MijiaCurtain1", 1], "Action":[["YeelightBulb", 0]], "description":"If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)", "triggerType":2},
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": ["MijiaCurtain2", 1],
     "Action": [["YeelightBulb", 0]],
     "description": "If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)",
     "triggerType": 2},

    {"score":3,"Trigger":["MijiaDoorLock", 1], "Condition": [], "Action":[["YeelightBulb", 1]], "description":"If door(5) is locked, after 10sec, turn off the Yeelight Bulb(3)", "triggerType":1},
    {"score":2,"Trigger":["WyzeCamera", 2], "Condition": [], "Action":[["PhilipsHueLight", 0], ["MijiaProjector", 0]], "description":"If motion(18) is detected by Wyze Camera, turn on Philips Hue Light(9) and Mijia Projecter(23)", "triggerType":2 },
    {"score":4,"Trigger":["time", "110000"], "Condition": ["WyzeCamera", 2], "Action":[["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1]], "description":"When 11pm - 5am every clock, if last motion(18) detected past over 2 hours, close Philips light(9),Wemo Plug(17), Lamps(12-16)", "triggerType":0},
    {"score":5,"Trigger":["MijiaDoorLock", 1], "Condition": [], "Action":[["WyzeCamera", 0], ["Notification", 0]], "description":"If door(5) is unlocked between 11pm-4am, record a short vedio clip(18) and turn on notification(18)", "triggerType":0 },
    # {"score":3,"Trigger":["temperature", 35], "Condition": [], "Action":[["WemoSmartPlug", 0], ["MideaAirConditioner", 0]], "description":"If room temperature(11) is over 86$^\circ$F ,when between 8am-9pm, open Wemo Smart Plug(17) and Air Conditioner(10)", "triggerType":2 },
    # {"score":3,"Trigger":["temperature", 13], "Condition": [], "Action":[["MideaAirConditioner", 1]], "description":"If room temperature is between 60 and 80$ ^\circ$F, turn off Air Conditioner", "triggerType":2 },
    {"score":5,"Trigger":["AlexaVoiceAssistance", 4], "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0],["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0]],"description":"Tell Alexa(8) to open a certain Yeelight Ceiling Lamp(12-16)", "triggerType":3 },
    {"score":5,"Trigger":["AlexaVoiceAssistance", 5], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"Tell Alexa(8) to open/close a certain Curtain(1-2)", "triggerType":3 },
    {"score":4,"Trigger":["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0]],"description":"If PIR motion senser(19) detects person, turn on Yeelight Ceiling Lamp (12-13)", "triggerType":2 },
    {"score":4,"Trigger":["SmartLifePIRmotionsensor2", 2], "Condition": [], "Action":[["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0]],"description":"If PIR motion senser(20) detects person, turn on Yeelight Ceiling Lamp (13-14)", "triggerType":2 },
    {"score":4,"Trigger":["SmartLifePIRmotionsensor3", 2], "Condition": [], "Action":[["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0]],"description":"If PIR motion senser(21) detects person, turn on Yeelight Ceiling Lamp (15-16)", "triggerType":2 },
    {"score":3,"Trigger":["SmartLifePIRmotionsensor1", 3], "Condition": [], "Action":[["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1]],"description":"Every 30 minutes check PIR motion sensor(19), if 1h since last person detected, close lamp (12-13)", "triggerType":2 },
    {"score":3,"Trigger":["SmartLifePIRmotionsensor2", 3], "Condition": [], "Action":[["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1]],"description":"Every 30 minutes check PIR motion sensor(20), if 1h since last person detected, close lamp (13-14)", "triggerType":2 },
    {"score":3,"Trigger":["SmartLifePIRmotionsensor3", 3], "Condition": [], "Action":[["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1]],"description":"Every 30 minutes check PIR motion sensor21, if 1h since last person detected, close lamp 15\&16", "triggerType":2},
    {"score":2,"Trigger":["MijiaCurtain1", 0], "Condition": [], "Action":[["YeelightCeilingLamp5", 1]],"description":"If curtain(1) is open when between 8am and 5pm, turn off Yeelight(15)", "triggerType":3},
    {"score":2,"Trigger":["MijiaCurtain2", 0], "Condition": [], "Action":[["YeelightCeilingLamp6", 1]],"description":"If curtain(2) is open when between 8am and 5pm, turn off Yeelight(16)", "triggerType":3},
    # {"score":4,"Trigger":["time", "0"], "Condition": ["time", "000000"], "Action":[["YeelightBulb",1], ["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1], ["MijiaPurifier", 1], ["MijiaProjector", 1]],"description":"When 12pm, turn off all the light(3,9,12-16) and plug(17) and Mijia projecter(23), Mijia purifier(22), curtain(1-2).", "triggerType":0},
    # {"score":3,"Trigger":["time", "80000"], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"When sunshine and 8am-5pm, open curtain(1-2)", "triggerType":0},
    {"score":4,"Trigger":["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action":[["iRobotRoomba", 2]],"description":"If person detected by PIR motion(19), dock robot(7)", "triggerType":2},
    {"score":4,"Trigger":["SmartLifePIRmotionsensor2", 2], "Condition": [], "Action":[["iRobotRoomba", 2]],"description":"If person detected by PIR motion(20), dock robot(7)", "triggerType":2},
    {"score":4,"Trigger":["SmartLifePIRmotionsensor3", 2], "Condition": [], "Action":[["iRobotRoomba", 2]],"description":"If person detected by PIR motion(21), dock robot(7)", "triggerType":2}
]

wzf = [
    {"score":2,"Trigger":["MijiaCurtain1", 1], "Condition": [], "Action":[["YeelightCeilingLamp5", 0]], "description":"If curtain(1) off, when motion sensor(21) detect person, then Lamp(15) switch on.", "triggerType":1},
    {"score":2,"Trigger": ["MijiaCurtain2", 1], "Condition": [], "Action": [["YeelightCeilingLamp6", 0 ]], "description":"If  curtain(2) off, when motion sensor(21) detect person, then Lamp(16) switch on", "triggerType":1},
    {"score":1,"Trigger": ["MijiaDoorLock", 1], "Condition": [], "Action": [["YeelightCeilingLamp3", 0 ]], "description":"If door(5) unlock, when night, then lamp(14) on", "triggerType":1},
    {"score":3,"Trigger": ["MijiaDoorLock", 1], "Condition": [], "Action": [["RingDoorbell", 0], ["AlexaVoiceAssistance", 0], ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0 ]], "description":"If door(5) unlock, then lights(6,8,11,17-18) switch on", "triggerType":1},
    {"score":5,"Trigger": ["MijiaDoorLock", 0], "Condition": ["SmartThingsDoorSensor", 0], "Action": [["WyzeCamera", 3 ]], "description":"If door(5) lock, when door sensor(4) open, then wyze(18) alert", "triggerType":1},
    {"score":3,"Trigger": ["MijiaDoorLock", 0], "Condition": [], "Action": [["iRobotRoomba", 0 ]], "description":"If door(5) lock, when fri, then iRobot(7) cleaning a room", "triggerType":1},
    {"score":4,"Trigger": ["MijiaDoorLock", 0], "Condition": [], "Action": [["WemoSmartPlug", 1], ["MijiaPurifier", 1 ]], "description":"If door(5) lock, wemo(17) and purifier(22) switch off", "triggerType":1},
    {"score":4,"Trigger": ["iRobotRoomba", 0], "Condition": [], "Action": [["WyzeCamera", 4 ]], "description":"If iRobot(7) robot started, then wyze(18) disable motion detection", "triggerType":3},
    # {"score":0,"Trigger": ["humidity", 40], "Condition": [], "Action": [["MideaAirConditioner", 0 ]], "description":"If weather station(11) detect humidity drops below, then air conditioner(10) switch on", "triggerType":2},
    {"score":1,"Trigger": ["NetatmoWeatherStation", 2], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"If weather station(11) detect wind speed rise, curtain(1,2) switch off", "triggerType":3},
    {"score":2,"Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action": [["WyzeCamera", 5 ]], "description":"If sensor(19) detect person, wyze(18) enable motion detection", "triggerType":2},
    {"score":5,"Trigger": ["SmartLifePIRmotionsensor2", 2], "Condition": [], "Action": [["WyzeCamera", 5 ]], "description":"If PIR Motion Sensor(20) detects person, enable Camera(18) motion detection", "triggerType":2},
    {"score":3,"Trigger": ["WyzeCamera", 2], "Condition": [], "Action": [["PhilipsHueLight", 0 ]], "description":"If Camera(18) detects person, open Light(9)", "triggerType":3},
    {"score":3,"Trigger": ["MijiaPurifier", 0], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"If open Purifier(22), close Curtain (1-2)", "triggerType":1},
    {"score":1,"Trigger": ["NetatmoWeatherStation", 5], "Condition": [], "Action": [["MijiaPurifier", 1 ]], "description":"If Weather Station(11) detects rain stop, turn off Purifier(22)", "triggerType":3},
    {"score":3,"Trigger": ["RingDoorbell", 2], "Condition": [], "Action": [["MijiaProjector", 0 ]], "description":"If Doorbell(6) rings, mute Projector (23)", "triggerType":3},
    {"score":5,"Trigger": ["WyzeCamera", 2], "Condition": [], "Action": [["MijiaProjector", 1 ]], "description":"If Camera(18) detect person, unmute Projector(23)", "triggerType":3},
]

zxh = [
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "If wemo is open, close curtain(1) and curtain(2)",
     "triggerType": 2},
    {"score":2,"Trigger":["MijiaCurtain1", 1], "Condition": [], "Action":[["YeelightBulb", 0 ]], "description":"When the curtain is closed, please turn on the bulb.", "triggerType":1},
    {"score":3,"Trigger":["SmartThingsDoorSensor", 2], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"After 7 pm, I come to the room, when I open the door, the curtain should be closed", "triggerType":2},
    # {"score":1,"Trigger":["temperature", 30] , "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"When the temperature is over 30°C, the Midea Air Conditioner should be open.", "triggerType":2},
    {"score":4,"Trigger":["Location", 1], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"When I leave the room, the curtain should be closed.", "triggerType":3},
    # {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["MijiaProjector", 0 ]], "description":"Every Tuesday 9 am, the Mijia Projector should be open for a conference.", "triggerType":0},
    # {"score":1,"Trigger":["temperature", -5], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"When the temperature is below -5°C, the Mijia Air Conditioner should be open.", "triggerType":2},
    # {"score":5,"Trigger":["time", "230000"], "Condition": [], "Action":[["MijiaProjector", 1 ]], "description":"After 11 pm every Sunday, the projector should be closed for  a maintenance status", "triggerType":0},
    # {"score":1,"Trigger":["temperature", 20], "Condition": [], "Action":[["MijiaDoorLock", 0 ]], "description":"When the temperature is over 20°C in summar, the door should be open for ventilating.", "triggerType":2},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["YeelightBulb", 1 ]], "description":"After we leave the room, about 10 pm everyday, the bulb should be closed.", "triggerType":3},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"After we leave the room, about 10 pm everyday, the curtain should be closed.", "triggerType":3},
    # {"score":4,"Trigger":["time", "90000"], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0 ]], "description":"Before we come to the room to study, about 9 am everyday, the curtain should be open.", "triggerType":0},
    {"score":2,"Trigger":["NetatmoWeatherStation", 3], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0 ]], "description":"If it is raining in winter, the curtain should be open for more light.", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 3], "Condition": [], "Action":[["YeelightBulb", 0 ]], "description":"If it is raining after 5 pm, the bulb should be open for more light.", "triggerType":3},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["WemoSmartPlug", 1 ]], "description":"After we leave the room, about 10 pm everyday, the smart plug should be closed.", "triggerType":3},
    # {"score":3,"Trigger":["time", "90000"], "Condition": [], "Action":[["WemoSmartPlug", 0 ]], "description":"Before we come to the room to study, about 9 am everyday, the smart plug should be open.", "triggerType":0},
    # {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["YeelightBulb", 0], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"Every Tuesday 9 am there is a conference, keep thebulb on and curtain off", "triggerType":0},
    # {"score":2,"Trigger":["time", "90000"], "Condition": [], "Action":[["Notification", 0 ]], "description":"Get the weather forecast every day at 9 am", "triggerType":0},
    # {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["WyzeCamera", 0 ]], "description":"Every Tuesday 9 am there is a conference, keep camera on to record the conference.", "triggerType":0},
    {"score":4,"Trigger":["Location", 1], "Condition": [], "Action":[["WyzeCamera", 1 ]], "description":"When I leave the room, the camera should be closed.", "triggerType":3}
]

zyk = [
    {"score": 4, "Trigger": ["MijiaDoorLock", 0],"Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
                ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3},
    {"score":5,"Trigger":["MijiaCurtain1", 0], "Condition": [], "Action":[["MijiaCurtain2", 0 ]], "description":"if Curtain(1) open ,then Curtain(2) open", "triggerType":1},
    {"score":4,"Trigger":["SmartThingsDoorSensor", 2], "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0],["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0 ]], "description":"if smartThings Door Sensor (4) Any new motion ,then turn on Yeelight (12-16)", "triggerType":2},
    {"score":3,"Trigger":["MijiaCurtain2", 0], "Condition": [], "Action":[["MideaAirConditioner", 1 ]], "description":"if Curtain(2) open ,then turn off Midea Air Conditioner(10)", "triggerType":1},
    {"score":3,"Trigger":["MijiaDoorLock", 0], "Condition": [], "Action":[["WyzeCamera", 0 ]], "description":"if Mijia Door Lock(5) locked,then turn on Wyze Camera(18)", "triggerType":1},
    {"score":1,"Trigger":["RingDoorbell", 2], "Condition": [], "Action":[["AlexaVoiceAssistance", 6 ]], "description":"if Ring Doorbell（6） new ring detected,then Alexa Voice Assistance（8） sing a song", "triggerType":3},
    {"score":2,"Trigger":["iRobotRoomba", 0], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if iRobot Roomba(7) Robot Started ,then Mijia Purifier(22) Start", "triggerType":1},
    {"score":2,"Trigger":["NetatmoWeatherStation", 6], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if Netatmo Weather Station(11) Air pressure rises above,then Mijia Purifier(22) Start", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 5], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if Netatmo Weather Station(11) rain no longer detected,then Mijia Purifier(22) Start", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 7], "Condition": [], "Action":[["MijiaPurifier", 0], ["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) carbon dioxide rise above ,then Mijia Purifier(22) and Midea Air Conditioner(10) Start", "triggerType":3},
    # {"score":2,"Trigger":["temperature", 25], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) temperature rises above ,then Midea Air Conditioner(10) Start", "triggerType":2},
    # {"score":2,"Trigger":["temperature", 15], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) temperature drops below ,then Midea Air Conditioner(10) Start", "triggerType":2},
    {"score":3,"Trigger":["NetatmoWeatherStation", 8], "Condition": [], "Action":[["WyzeCamera", 0 ]], "description":"if Netatmo Weather Station(11) noise level drops below ,then Wyze Camera（18） Start", "triggerType":3},
    {"score":5,"Trigger":["WyzeCamera", 2], "Condition": [], "Action":[["AlexaVoiceAssistance", 7 ]], "description":"if Wyze Camera（18）Smoke alarm is detected ,then  Alexa Voice Assistance（8） alarm", "triggerType":3},
    {"score":5,"Trigger":["WyzeCamera", 6], "Condition": [], "Action":[["AlexaVoiceAssistance", 7 ]], "description":"if Wyze Camera（18）CO alarm is detected ,then  Alexa Voice Assistance（8） alarm", "triggerType":3},
    {"score":2,"Trigger":["iRobotRoomba", 1], "Condition": [], "Action":[["WemoSmartPlug", 1 ]], "description":"if iRobot Roomba(7) Job Complete ,then Wemo Smart Plug（17）Turn off", "triggerType":1},
    {"score":1, "Trigger": ["YeelightBulb", 0], "Condition": [], "Action": [["MijiaCurtain1", 0]],
     "description": "When turn on the bulb, please close the curtain.", "triggerType": 1},
]

deviceStatus = {
    "Smoke":["unsmoke", "smoke"],
    "Location" : ["home", "away"],
    "WaterLeakage" : ["unleak", "leak"],
    "MijiaCurtain1" : ["open", "close"],
    "MijiaCurtain2" : ["open", "close"],
    "YeelightBulb" : ["open", "close"],
    "SmartThingsDoorSensor" : ["open", "close", "detect", "undetect"],
    "MijiaDoorLock" : ["open", "close"],
    "RingDoorbell" : ["open", "close", "ring"],
    "iRobotRoomba" : ["open", "close", "dock"],
    "AlexaVoiceAssistance" : ["open", "close","openhuelights","closehuelights", "openLamps", "openCutrain", "singsong", "alarm"],
    "PhilipsHueLight" : ["open", "close"],
    "MideaAirConditioner" : ["open", "close"],
    "NetatmoWeatherStation" : ["open", "close", "windy", "rain", "sun", "unrain", "AirPressureRises", "CarbonDioxideRise", "noise"],
    "YeelightCeilingLamp1" : ["open", "close"],
    "YeelightCeilingLamp2" : ["open", "close"],
    "YeelightCeilingLamp3" : ["open", "close"],
    "YeelightCeilingLamp5" : ["open", "close"],
    "YeelightCeilingLamp6" : ["open", "close"],
    "WemoSmartPlug" : ["open", "close"],
    "WyzeCamera" : ["open", "close", "detect", "alert", "disable", "enable", "COalarm"],
    "SmartLifePIRmotionsensor1" : ["open", "close", "detect", "undetect"],
    "SmartLifePIRmotionsensor2" : ["open", "close", "detect", "undetect"],
    "SmartLifePIRmotionsensor3" : ["open", "close", "detect", "undetect"],
    "MijiaPurifier" : ["open", "close"],
    "MijiaProjector" : ["open", "close"],
    "Notification" : ["notify"]
}

def create_records(rules, office):
  file = open("records.txt", "w", encoding='utf-8')
  Triggers = updateOfficeStatus(office)
  potientialRules = findPotientialRules(Triggers, rules)

  exectionRules = potientialRules

  mergeArray = mergeRules(exectionRules)
  file.write(str(mergeArray) +"\n")

  return mergeArray

def mergeRules(rules):
  rulesNum = len(rules)
  indexs = []
  ans = []

  for i in range(rulesNum):
    indexs.append(i)

  while len(indexs) != 0:
    index = np.random.choice(indexs)
    if len(rules[index]) == 0:
      indexs.remove(index)
      continue
    else:
      ans.append(rules[index][0])
      rules[index].pop(0)
  return ans

def create_rules():
  rules = []
  ruleNum = 10

  seed(1)
  values = randint(0, 24, 4*ruleNum)
  for ruleIndex in range(ruleNum):
    rule = []
    rule.append([values[ruleIndex*4]%24 + 1, values[ruleIndex * 4 + 1] % 5])
    rule.append([ruleIndex + 100, 0])
    rule.append([values[ruleIndex * 4 + 2] % 24 +1, values[ruleIndex * 4 + 3] % 5])
    rules.append(rule)
  return rules

def create_tables(mergeArrays):
  trigger_records = []
  action_records = []

  # get trigger_records
  for record in mergeArrays:
    temp_trigger = []
    for item in record:
      if item[1] == 1:
        temp = copy.copy(temp_trigger)
        temp.append(str(item[0])+","+str(item[1]))
        trigger_records.append(temp)
      else:
        temp_trigger.append(str(item[0])+","+str(item[1]))

  # get action_records
  for record in mergeArrays:
    temp_action = []
    for item in reversed(record):
      if item[1] == 1 :
        temp = copy.copy(temp_action)
        temp.append(str(item[0])+","+str(item[1]))
        action_records.append(temp)
      else:
        temp_action.append(str(item[0])+","+str(item[1]))
  with open("trigger_records.txt","w", encoding="utf-8") as f:
    f.write(str(trigger_records))

  with open("action_records.txt", "w", encoding="utf-8") as f:
    f.write(str(action_records))
  return trigger_records,action_records

def getSubRecord(rule, trigger_records):
  ans = []
  for item in trigger_records:
    if item[-1] == rule:
      ans.append(item)
  return ans


def setDeviceStatus(devicesList):
    deviceStatus = {}
    for device in devicesList:
      deviceStatus[device] = []
      path = "../resources/TA_Popular/" + device + "/Trigger.csv"
      file = open(path, "r", encoding='utf-8')
      lines = file.readlines()
      for line in lines:
        line = line.split(',')
        if line[0] == 'trigger' or line[1] == 'trigger_description':
          continue
        deviceStatus[device].append(line[0])
      file.close()
    return deviceStatus


def setOffice(devicesList, devicesStatus):
  office = {"time": "000000"}
  for device in devicesList:
    if len(devicesStatus[device]) != 0:
      office[device] = np.random.choice(devicesStatus[device], 1)[0]
    else:
      office[device] = ''
  return office

def getDeviceStatus(deviceList):
  triggerStatus = {}
  actionStatus = {}
  statusMap = {}
  for device in devicesList:
    path = "../resources/TA_Popular/" + str(device) + "/"
    triggerPath = path + "Trigger.csv"
    actionPath = path + "Action.csv"
    statePath = path + "state.ini"
    with open(triggerPath, "r", encoding="utf-8") as f:
      triggers = []
      lines = f.readlines()
      for line in lines:
        line = line.split(',')
        if line[0] == 'trigger' or line[1] == 'trigger_description':
          continue
        elif line[0] != "":
          triggers.append(line[0])
      triggerStatus[device] = triggers
    with open(actionPath, "r", encoding="utf-8") as f:
      actions = []
      lines = f.readlines()
      for line in lines:
        line = line.split(',')
        if line[0] == 'action' or line[1] == 'action_description':
          continue
        elif line[0] != "":
          actions.append(line[0])
      actionStatus[device] = actions

    config = configparser.ConfigParser()
    config.read(statePath)
    p_default = config['DEFAULT']
    p_default = eval('[' + p_default['ATlist'] + ']')

    tmp = {}
    if len(p_default) != 0:
      for item in p_default:
        tmp[actionStatus[device][item[0] - 2]] = []
        for i in range(1, len(item)):
          tmp[actionStatus[device][item[0] - 2]].append(triggerStatus[device][item[i] - 2])

    statusMap[device] = tmp

  return triggerStatus, actionStatus, statusMap

def setRules(statusMap):

  # {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
  #     #  "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
  #     #             ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
  #     #  "description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3, "user":"ldm"}

  # applet_name, applet_description, applet_Trigger, applet_Action, applet_TD, applet_AD, applet_number

  rules = []

  for user in range(users):
    path = npyPath + "/randomRulesList" + str(user) + ".npy"
    ruleList = np.load(path)
    for item in ruleList:
      rule = {}
      rule["score"] = np.random.randint(6, size=1)[0]
      rule["Trigger"] = [item[4], item[2]]
      rule["Condition"] = []
      if item[3] in statusMap[item[5]].keys():
        rule["Action"] = []
        for tmp in statusMap[item[5]][item[3]]:
          rule["Action"].append([item[5], tmp])
      else:
        rule["Action"] = [[item[5], item[3]]]

      rule["description"] = item[1]
      rule["triggerType"] = 0
      rule["user"] = user
      rules.append(rule)
  return rules

def changeTime(time):
  time = int(time)
  hour = int(time / 10000)
  time = time % 10000
  minute = int(time / 100)
  time = time % 100
  second = time
  minute += 5
  hour = (int(minute / 60) + hour) % 24
  minute = minute % 60
  return str(hour * 10000 + minute * 100 + second)

def changeValue(val):
  # 0:不变， 1：up， 2：down
  ans = np.random.randint(0, 3, 1)
  if ans == 1:
    val += 1
  elif ans == 2:
    val -= 1
  return val

def changeStatus(device):
  status = len(deviceStatus[device])
  return np.random.randint(0, status, 1)[0]

def updateOfficeStatus(office):
  old_office = copy.copy(office)

  office["time"] = changeTime(office["time"])
  office["temperature"] = changeValue(office["temperature"])
  office["humidity"] = changeValue(office["humidity"])
  office["illumination"] = changeValue(office["illumination"])

  devices = list(deviceStatus.keys())
  for item in devices:
    office[item] = changeStatus(item)

  ans = []
  for item in list(office.keys()):
    if office[item] != old_office[item]:
      ans.append([[item, office[item]],0])

  return ans

# def updateOfficeStatus(office, devicesStatus):
#   old_office = copy.copy(office)
#
#   office["time"] = changeTime(office["time"])
#
#   devices = list(devicesStatus.keys())
#   for device in devices:
#     if len(devicesStatus[device]) != 0:
#       office[device] = np.random.choice(devicesStatus[device], 1)[0]
#     else:
#       office[device] = ''
#
#   ans = []
#   for item in list(office.keys()):
#     if office[item] != old_office[item]:
#       ans.append([[item, office[item]],0])
#   return ans
#
# def runRules(office, Triggers, rules, id):
#   # triggers = [[“time”：xx]， [“temxxx”：xx]]
#   # [{id,status,time,rules, "triggerId", "actionIds", "ancestor"}]
#   # 维护一个家庭状态， 维护一个Triggers 和 tirggerId,
#   # 找到所有当前可能执行的规则，随机挑选执行，判断condition是否满足，如果不满足就是skipped，如果满足就修改office状态，把action加入到新的Triggers并给出triggerId。
#
#   triggerId = {}
#   eporch = 0
#   logs = []
#   time = int(office["time"])
#   Actions = []
#   actionId = {}
#   logfile = open("logs.txt", "a", encoding="utf-8")
#
#   for i in range(len(Triggers)):
#     triggerId[str(Triggers[i])] = 0
#
#   while len(Triggers) != 0 and eporch < 10:
#     potientialRules = findPotientialRules(Triggers, rules)
#     potientialRules = np.random.choice(potientialRules, len(potientialRules), False)
#
#     for rule in potientialRules:
#       if len(rule['Condition']) != 0 and (
#               (rule['Condition'][0] == 'time' and int(rule['Condition'][1]) != int(office["time"])) or office[
#         rule['Condition'][0]] != rule['Condition'][1]):
#         temp = copy.copy(rule)
#         temp["id"] = id
#         temp["status"] = "skipped"
#         temp["time"] = time
#         if triggerId[str(rule["Trigger"])] == 0:
#           temp["triggerId"] = id
#         else:
#           temp["triggerId"] = triggerId[str(rule["Trigger"])]
#         temp["actionIds"] = []
#         temp["ancestor"] = ""
#         logs.append(temp)
#       else:
#         # 生成记录
#         temp = copy.copy(rule)
#         temp["id"] = id
#         temp["status"] = "run"
#         temp["time"] = time
#         if triggerId[str(rule["Trigger"])] == 0:
#           temp["triggerId"] = id
#           temp["ancestor"] = id
#         else:
#           temp["triggerId"] = triggerId[str(rule["Trigger"])]
#           temp["ancestor"] = ""
#         temp["actionIds"] = []
#         logs.append(temp)
#
#         # 添加新的Action
#         for item in rule["Action"]:
#           office[item[0]] = item[1]
#           Actions.append(item)
#           actionId[str(item)] = id
#
#       id += 1
#     Triggers = Actions
#     triggerId = actionId
#     Actions = []
#     actionId = {}
#     eporch += 1
#
#   for log in logs:
#     if log["ancestor"] == "":
#       for i in range(len(logs)):
#         if logs[i]["id"] == log["triggerId"]:
#           log["ancestor"] = logs[i]["ancestor"]
#
#   for log in logs:
#     logfile.write(str(log) + "\n")
#   logfile.close()
#   return logs, id

def findPotientialRules(Triggers, rules):
  potientialRules = []
  for rule in rules:
    if rule[0] in Triggers:
      if rule not in all_rules:
        all_rules.append(rule)
      potientialRules.append(copy.copy(rule))
  return potientialRules

def getRules():
  rules = []
  for rule in ldm:
    rule["user"] = "ldm"
    rules.append(rule)

  for rule in whd:
    rule["user"] = "whd"
    rules.append(rule)

  for rule in wzf:
    rule["user"] = "wzf"
    rules.append(rule)

  for rule in zxh:
    rule["user"] = "zxh"
    rules.append(rule)

  for rule in zyk:
    rule["user"] = "zyk"
    rules.append(rule)
  return rules

if __name__ == "__main__":

  # rules = create_rules()
  # print(rules)

  # devicesList = np.load(devicePath)
  # devicesStatus = setDeviceStatus(devicesList)
  # office = setOffice(devicesList, devicesStatus)
  # triggerStatus, actionStatus, statusMap = getDeviceStatus(devicesList)
  # rules = setRules(statusMap)

  office = {
    "time": "000000",
    "temperature": 20,
    "humidity": 50,
    "illumination": 50,
    "Smoke": 0,
    "Location": 0,
    "WaterLeakage": 0,
    "MijiaCurtain1": 0,
    "MijiaCurtain2": 0,
    "YeelightBulb": 0,
    "SmartThingsDoorSensor": 0,
    "MijiaDoorLock": 0,
    "RingDoorbell": 0,
    "iRobotRoomba": 0,
    "AlexaVoiceAssistance": 0,
    "PhilipsHueLight": 0,
    "MideaAirConditioner": 0,
    "NetatmoWeatherStation": 0,
    "YeelightCeilingLamp1": 0,
    "YeelightCeilingLamp2": 0,
    "YeelightCeilingLamp3": 0,
    "YeelightCeilingLamp5": 0,
    "YeelightCeilingLamp6": 0,
    "WemoSmartPlug": 0,
    "WyzeCamera": 0,
    "SmartLifePIRmotionsensor1": 0,
    "SmartLifePIRmotionsensor2": 0,
    "SmartLifePIRmotionsensor3": 0,
    "MijiaPurifier": 0,
    "MijiaProjector": 0,
    "Notification": 0,
  }
  # get all rules
  rules = getRules()

  # 初始化文件
  # logfile = open("logs.txt", "w", encoding="utf-8")
  # logfile.close()

  # id = 1
  # for i in range(12):
    # Triggers = updateOfficeStatus(office, devicesStatus)
    # logs, id = runRules(office, Triggers, rules, id)
    # print(logs)



  rules_new = []
  for rule in rules:
    rules_new.append([[rule['Trigger'],0], [rule['description'],1], [rule['Action'],0]])

  rules = rules_new


  # rules = [
  #   [[6, 1], [100, 0], [13, 3]],
  #   [[10, 1], [101, 0], [6, 0]],
  #   [[1, 1], [102, 0], [2, 2]],
  #   [[8, 3], [103, 0], [7, 3]],
  #   [[21, 0], [104, 0], [19, 0]],
  #   [[12, 0], [105, 0], [15, 3]],
  #   [[5, 3], [106, 0], [24, 4]],
  #   [[18, 3], [107, 0], [1, 2]],
  #   [[14, 4], [108, 0], [10, 2]],
  #   [[23, 1], [109, 0], [1, 2]]
  # ]
  mergeArrays = []
  accuracy = 0
  for i in range(times):
    # mergeArray = create_records(rules, office, devicesStatus)
    mergeArray = create_records(rules, office)
    # print(mergeArray)
    mergeArrays.append(mergeArray)

    trigger_records, action_records = create_tables(mergeArrays)

    num_true = 0
    for item in rules:
        trigger = str(item[0][0]) +"," + str(item[0][1])
        rule = str(item[1][0]) +"," + str(item[1][1])
        action = str(item[2][0]) +"," + str(item[2][1])
    #   # 假设我们想找'100,0'这个规则的trigger
        dataset_trigger = getSubRecord(rule, trigger_records)
        dataset_action = getSubRecord(rule, action_records)
    #   # print(dataset)
    #
    #
        trigger_list = Apriori.get_target_rule(rule, dataset_trigger)
        action_list = Apriori.get_target_rule(rule, dataset_action)
    #
        trigger_flag = 0
        for pair in trigger_list:
          for item in pair:
            if trigger in item:
              num_true += 1
              trigger_flag = 1
          if trigger_flag == 1:
            break
        action_flag = 0
        for pair in action_list:
          for item in pair:
            if action in item:
              num_true += 1
              action_flag = 1
          if action_flag == 1:
            break
        # for item in target_list:
        #   print(item)
    # print(len(mergeArrays))
    accuracy = num_true/(2*len(rules))
    print(accuracy)

  # unrunRules = []
  # for rule in rules:
  #   if rule not in all_rules:
  #     unrunRules.append(rule[1][0])
  #
  #
  #
  # rule0List = np.load(npyPath+"randomRulesList0.npy")
  # temp = []
  # for item in rule0List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # rule0List = temp
  #
  # rule1List = np.load(npyPath + "randomRulesList1.npy")
  # temp = []
  # for item in rule1List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # rule1List = temp
  #
  # rule2List = np.load(npyPath + "randomRulesList2.npy")
  # temp = []
  # for item in rule2List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # rule2List = temp
  #
  # rule3List = np.load(npyPath + "randomRulesList3.npy")
  # temp = []
  # for item in rule3List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # rule3List = temp
  #
  # rule4List = np.load(npyPath + "randomRulesList4.npy")
  # temp = []
  # for item in rule4List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # rule4List = temp
  #
  # rule5List = np.load(npyPath + "randomRulesList5.npy")
  # temp = []
  # for item in rule5List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  # # rule5List = temp
  #
  # rule6List = np.load(npyPath + "randomRulesList6.npy")
  # # temp = []
  # for item in rule6List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  #
  #
  # rule7List = np.load(npyPath + "randomRulesList7.npy")
  # # temp = []
  # for item in rule7List:
  #   if item[0] in unrunRules:
  #     continue
  #   temp.append(item)
  #
  #
  # add_rules = temp
  #
  # index = 0
  #
  # while len(rule0List) < 20:
  #     rule0List.append(add_rules[index])
  #     index += 1
  # np.save(npyPath + "randomRulesList0.npy", rule0List)
  # while len(rule1List) < 20:
  #     rule1List.append(add_rules[index])
  #     index += 1
  # np.save(npyPath + "randomRulesList1.npy", rule1List)
  # while len(rule2List) < 20:
  #     rule2List.append(add_rules[index])
  #     index += 1
  # np.save(npyPath + "randomRulesList2.npy", rule2List)
  # while len(rule3List) < 20:
  #     rule3List.append(add_rules[index])
  #     index += 1
  # np.save(npyPath + "randomRulesList3.npy", rule3List)
  # while len(rule4List) < 20:
  #     rule4List.append(add_rules[index])
  #     index += 1
  # np.save(npyPath + "randomRulesList4.npy", rule4List)
  # # while len(rule5List) < 20:
  # #     rule5List.append(add_rules[index])
  # #     index += 1
  #
  # # print(mergeArrays)

