import copy
from Detector.Apriori import Apriori
from numpy.random import seed
from numpy.random import randint
import numpy as np
import configparser

times = 50
Records = "RealUserRecords.txt"
TriggerRecords = "RealUserTriggerRecords.txt"
ActionRecords = "RealUserActionRecords.txt"
ACCFile = "RealUserACC.txt"
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


all_rules = []

# 获取所有的Rule
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

# 改变时间的状态
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

# 数值型参数的修改
def changeValue(val):
    # 0:不变， 1：up， 2：down
    ans = np.random.randint(0, 3, 1)
    if ans == 1:
        val += 1
    elif ans == 2:
        val -= 1
    return val

# 状态型参数的修改
def changeStatus(device):
  status = len(deviceStatus[device])
  return np.random.randint(0, status, 1)[0]

# 随机改变room的状态
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

# 获取将要执行的规则列表
def findPotientialRules(Triggers, rules):
    potientialRules = []
    for rule in rules:
        if rule[0] in Triggers:
            if rule not in all_rules:
                all_rules.append(rule)
            potientialRules.append(copy.copy(rule))
    return potientialRules

# rules乱序执行生成历史记录
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


# 生成由用户规则产生的历史记录
def create_records(rules, office):
    file = open(Records, "w", encoding='utf-8')
    Triggers = updateOfficeStatus(office)
    potientialRules = findPotientialRules(Triggers, rules)
    exectionRules = potientialRules
    mergeArray = mergeRules(exectionRules)
    file.write(str(mergeArray) +"\n")
    return mergeArray

# 由历史记录生成trigger_record和action_record
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
    with open(TriggerRecords,"w", encoding="utf-8") as f:
        f.write(str(trigger_records))

    with open(ActionRecords, "w", encoding="utf-8") as f:
        f.write(str(action_records))
    return trigger_records,action_records

# 获取rule对应的记录
def getSubRecord(rule, trigger_records):
    ans = []
    for item in trigger_records:
        if item[-1] == rule:
            ans.append(item)
    return ans

if __name__ == "__main__":
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

    rules = getRules()


    rules_new = []
    for rule in rules:
        rules_new.append([[rule['Trigger'], 0], [rule['description'], 1], [rule['Action'], 0]])
    rules = rules_new


    accfile = open(ACCFile, "w", encoding="utf-8")


    mergeArrays = []
    accuracy = 0
    for i in range(times):
        mergeArray = create_records(rules, office)
        mergeArrays.append(mergeArray)
        trigger_records, action_records = create_tables(mergeArrays)
        num_true = 0
        for item in rules:
            trigger = str(item[0][0]) + "," + str(item[0][1])
            rule = str(item[1][0]) + "," + str(item[1][1])
            action = str(item[2][0]) + "," + str(item[2][1])
            # 获取规则的records
            dataset_trigger = getSubRecord(rule, trigger_records)
            dataset_action = getSubRecord(rule, action_records)

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
        accuracy = num_true / (2 * len(rules))
        print(accuracy)
        accfile.write(str(accuracy)+"\n")

    accfile.close()





