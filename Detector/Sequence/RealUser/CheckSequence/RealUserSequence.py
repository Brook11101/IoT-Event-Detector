import copy
import logging
from multiprocessing.sharedctypes import synchronized

import numpy as np
from datetime import datetime

times = 1
conflict_file = "conflicts_RealUser_"+str(times)+".csv"

trigger_type = ["data", "switch", "sensor", "command"]

ldm = [
    {"score":3,"Trigger":["NetatmoWeatherStation", 2], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if Netatmo Weather Station(11) is Windy, close MiJia Curtains(1,2)", "triggerType":2},
    {"score":3,"Trigger":["Location", 1], "Condition": [], "Action":[["iRobotRoomba", 0]],"description":"if i leave home, start the iRobot(7)", "triggerType":3},
    {"score":4,"Trigger":["time", "190000"] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if 7p.m.,close MiJia Curtains(1,2)", "triggerType":0},
    {"score":2,"Trigger":["time", "70000"] , "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"if 7a.m.,open MiJia Curtains(1,2)", "triggerType":0},
    {"score":4,"Trigger":["RingDoorbell", 2] , "Condition": [], "Action":[["YeelightBulb", 0]],"description":"if doorbell rings(6), open the Yeelight Bulb(3)", "triggerType":3},
    {"score":5,"Trigger":["SmartThingsDoorSensor", 2] , "Condition": [], "Action":[["Notification", 0]],"description":"if door opened(4),notify me.", "triggerType":3},
    {"score":4,"Trigger":["MijiaDoorLock", 0] , "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0],["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0]],"description":"if door opened(5), when after 7p.m., open the lamps(12,13,14,15,16)", "triggerType":3},
    {"score":5,"Trigger":["Location", 1] , "Condition": [], "Action":[["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1]],"description":"if i leave home, close all lamps(12,13,14,15,16)", "triggerType":3},
    {"score":3,"Trigger":["AlexaVoiceAssistance", 2] , "Condition": [], "Action":[["YeelightBulb", 0], ["PhilipsHueLight", 0]],"description":"tell alexa to open hue lights(3,9)", "triggerType":3},
    {"score":3,"Trigger":["AlexaVoiceAssistance", 3] , "Condition": [], "Action":[["YeelightBulb", 1], ["PhilipsHueLight", 1]],"description":"tell alexa to close hue lights(3,9)", "triggerType":3},
    {"score":4,"Trigger":["MideaAirConditioner", 0] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if air conditioner(10) is opened, close curtains(1,2)", "triggerType":1},
    {"score":2,"Trigger":["temperature", 30] , "Condition": [], "Action":[["MideaAirConditioner", 0]],"description":"if temperature is over 30, open the air conditioner(10)", "triggerType":2},
    {"score":1,"Trigger":["temperature", 15], "Condition": [], "Action":[["MideaAirConditioner", 1]], "description":"if temperature is under 15, close the air conditioner(10)", "triggerType":2},
    {"score":5,"Trigger":["NetatmoWeatherStation", 3] , "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],"description":"if rain(11), close the curtains(1,2)", "triggerType":2},
    {"score":2,"Trigger":["NetatmoWeatherStation", 4], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"if sun(12), open the curtains(1,2)", "triggerType":2},
    {"score":3,"Trigger":["SmartLifePIRmotionsensor1", 2] , "Condition": [], "Action":[["WemoSmartPlug", 0]],"description":"if motion(19) detected, open the wemo smart plug(17).", "triggerType":2},
    {"score":5,"Trigger":["SmartLifePIRmotionsensor1", 2] , "Condition": [], "Action":[["WyzeCamera", 1]],"description":"if motion detected(19), open the camera(18)", "triggerType":2},
    {"score":2,"Trigger":["humidity", 30] , "Condition": [], "Action":[["MijiaPurifier", 0]],"description":"if humidity is under 30, open the purifier", "triggerType":2},
    {"score":1,"Trigger":["humidity", 60], "Condition": [], "Action":[["MijiaPurifier", 1]],"description":"if humidity is over 60, close the purifier", "triggerType":2},
]

whd = [
    {"score":2,"Trigger":["WemoSmartPlug", 0], "Condition": ["MijiaCurtain1", 1], "Action":[["YeelightBulb", 0]], "description":"If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)", "triggerType":2},
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": ["MijiaCurtain2", 1],"Action": [["YeelightBulb", 0]],"description": "If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)","triggerType": 2},
    {"score":3,"Trigger":["MijiaDoorLock", 1], "Condition": [], "Action":[["YeelightBulb", 1]], "description":"If door(5) is locked, after 10sec, turn off the Yeelight Bulb(3)", "triggerType":1},
    {"score":2,"Trigger":["WyzeCamera", 2], "Condition": [], "Action":[["PhilipsHueLight", 0], ["MijiaProjector", 0]], "description":"If motion(18) is detected by Wyze Camera, turn on Philips Hue Light(9) and Mijia Projecter(23)", "triggerType":2 },
    {"score":4,"Trigger":["time", "110000"], "Condition": ["WyzeCamera", 2], "Action":[["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1]], "description":"When 11pm - 5am every clock, if last motion(18) detected past over 2 hours, close Philips light(9),Wemo Plug(17), Lamps(12-16)", "triggerType":0},
    {"score":5,"Trigger":["MijiaDoorLock", 1], "Condition": [], "Action":[["WyzeCamera", 0], ["Notification", 0]], "description":"If door(5) is unlocked between 11pm-4am, record a short vedio clip(18) and turn on notification(18)", "triggerType":0 },
    {"score":3,"Trigger":["temperature", 35], "Condition": [], "Action":[["WemoSmartPlug", 0], ["MideaAirConditioner", 0]], "description":"If room temperature(11) is over 86$^\circ$F ,when between 8am-9pm, open Wemo Smart Plug(17) and Air Conditioner(10)", "triggerType":2 },
    {"score":3,"Trigger":["temperature", 13], "Condition": [], "Action":[["MideaAirConditioner", 1]], "description":"If room temperature is between 60 and 80$ ^\circ$F, turn off Air Conditioner", "triggerType":2 },
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
    {"score":4,"Trigger":["time", "0"], "Condition": ["time", "000000"], "Action":[["YeelightBulb",1], ["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1",1], ["YeelightCeilingLamp2",1],["YeelightCeilingLamp3",1],["YeelightCeilingLamp5",1],["YeelightCeilingLamp6",1], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1], ["MijiaPurifier", 1], ["MijiaProjector", 1]],"description":"When 12pm, turn off all the light(3,9,12-16) and plug(17) and Mijia projecter(23), Mijia purifier(22), curtain(1-2).", "triggerType":0},
    {"score":3,"Trigger":["time", "80000"], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],"description":"When sunshine and 8am-5pm, open curtain(1-2)", "triggerType":0},
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
    {"score":0,"Trigger": ["humidity", 40], "Condition": [], "Action": [["MideaAirConditioner", 0 ]], "description":"If weather station(11) detect humidity drops below, then air conditioner(10) switch on", "triggerType":2},
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
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]], "description": "If wemo is open, close curtain(1) and curtain(2)","triggerType": 2},
    {"score":2,"Trigger":["MijiaCurtain1", 1], "Condition": [], "Action":[["YeelightBulb", 0 ]], "description":"When the curtain is closed, please turn on the bulb.", "triggerType":1},
    {"score":3,"Trigger":["SmartThingsDoorSensor", 2], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"After 7 pm, I come to the room, when I open the door, the curtain should be closed", "triggerType":2},
    {"score":1,"Trigger":["temperature", 30] , "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"When the temperature is over 30°C, the Midea Air Conditioner should be open.", "triggerType":2},
    {"score":4,"Trigger":["Location", 1], "Condition": [], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"When I leave the room, the curtain should be closed.", "triggerType":3},
    {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["MijiaProjector", 0 ]], "description":"Every Tuesday 9 am, the Mijia Projector should be open for a conference.", "triggerType":0},
    {"score":1,"Trigger":["temperature", -5], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"When the temperature is below -5°C, the Mijia Air Conditioner should be open.", "triggerType":2},
    {"score":5,"Trigger":["time", "230000"], "Condition": [], "Action":[["MijiaProjector", 1 ]], "description":"After 11 pm every Sunday, the projector should be closed for  a maintenance status", "triggerType":0},
    {"score":1,"Trigger":["temperature", 20], "Condition": [], "Action":[["MijiaDoorLock", 0 ]], "description":"When the temperature is over 20°C in summar, the door should be open for ventilating.", "triggerType":2},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["YeelightBulb", 1 ]], "description":"After we leave the room, about 10 pm everyday, the bulb should be closed.", "triggerType":3},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"After we leave the room, about 10 pm everyday, the curtain should be closed.", "triggerType":3},
    {"score":4,"Trigger":["time", "90000"], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0 ]], "description":"Before we come to the room to study, about 9 am everyday, the curtain should be open.", "triggerType":0},
    {"score":2,"Trigger":["NetatmoWeatherStation", 3], "Condition": [], "Action":[["MijiaCurtain1", 0], ["MijiaCurtain2", 0 ]], "description":"If it is raining in winter, the curtain should be open for more light.", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 3], "Condition": [], "Action":[["YeelightBulb", 0 ]], "description":"If it is raining after 5 pm, the bulb should be open for more light.", "triggerType":3},
    {"score":4,"Trigger":["Location", 1], "Condition": ["time", "220000"], "Action":[["WemoSmartPlug", 1 ]], "description":"After we leave the room, about 10 pm everyday, the smart plug should be closed.", "triggerType":3},
    {"score":3,"Trigger":["time", "90000"], "Condition": [], "Action":[["WemoSmartPlug", 0 ]], "description":"Before we come to the room to study, about 9 am everyday, the smart plug should be open.", "triggerType":0},
    {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["YeelightBulb", 0], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1 ]], "description":"Every Tuesday 9 am there is a conference, keep thebulb on and curtain off", "triggerType":0},
    {"score":2,"Trigger":["time", "90000"], "Condition": [], "Action":[["Notification", 0 ]], "description":"Get the weather forecast every day at 9 am", "triggerType":0},
    {"score":5,"Trigger":["time", "90000"], "Condition": [], "Action":[["WyzeCamera", 0 ]], "description":"Every Tuesday 9 am there is a conference, keep camera on to record the conference.", "triggerType":0},
    {"score":4,"Trigger":["Location", 1], "Condition": [], "Action":[["WyzeCamera", 1 ]], "description":"When I leave the room, the camera should be closed.", "triggerType":3}
]

zyk = [
    {"score": 4, "Trigger": ["MijiaDoorLock", 0],"Condition": [],"Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],"description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3},
    {"score":5,"Trigger":["MijiaCurtain1", 0], "Condition": [], "Action":[["MijiaCurtain2", 0 ]], "description":"if Curtain(1) open ,then Curtain(2) open", "triggerType":1},
    {"score":4,"Trigger":["SmartThingsDoorSensor", 2], "Condition": [], "Action":[["YeelightCeilingLamp1",0], ["YeelightCeilingLamp2",0],["YeelightCeilingLamp3",0],["YeelightCeilingLamp5",0],["YeelightCeilingLamp6",0 ]], "description":"if smartThings Door Sensor (4) Any new motion ,then turn on Yeelight (12-16)", "triggerType":2},
    {"score":3,"Trigger":["MijiaCurtain2", 0], "Condition": [], "Action":[["MideaAirConditioner", 1 ]], "description":"if Curtain(2) open ,then turn off Midea Air Conditioner(10)", "triggerType":1},
    {"score":3,"Trigger":["MijiaDoorLock", 0], "Condition": [], "Action":[["WyzeCamera", 0 ]], "description":"if Mijia Door Lock(5) locked,then turn on Wyze Camera(18)", "triggerType":1},
    {"score":1,"Trigger":["RingDoorbell", 2], "Condition": [], "Action":[["AlexaVoiceAssistance", 6 ]], "description":"if Ring Doorbell（6） new ring detected,then Alexa Voice Assistance（8） sing a song", "triggerType":3},
    {"score":2,"Trigger":["iRobotRoomba", 0], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if iRobot Roomba(7) Robot Started ,then Mijia Purifier(22) Start", "triggerType":1},
    {"score":2,"Trigger":["NetatmoWeatherStation", 6], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if Netatmo Weather Station(11) Air pressure rises above,then Mijia Purifier(22) Start", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 5], "Condition": [], "Action":[["MijiaPurifier", 0 ]], "description":"if Netatmo Weather Station(11) rain no longer detected,then Mijia Purifier(22) Start", "triggerType":3},
    {"score":2,"Trigger":["NetatmoWeatherStation", 7], "Condition": [], "Action":[["MijiaPurifier", 0], ["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) carbon dioxide rise above ,then Mijia Purifier(22) and Midea Air Conditioner(10) Start", "triggerType":3},
    {"score":2,"Trigger":["temperature", 25], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) temperature rises above ,then Midea Air Conditioner(10) Start", "triggerType":2},
    {"score":2,"Trigger":["temperature", 15], "Condition": [], "Action":[["MideaAirConditioner", 0 ]], "description":"if Netatmo Weather Station(11) temperature drops below ,then Midea Air Conditioner(10) Start", "triggerType":2},
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

def changeTime(time):
    time = int(time)
    hour = int(time/10000)
    time = time%10000
    minute = int(time/100)
    time = time%100
    second = time
    minute += 10
    hour = (int(minute/60) + hour)%24
    minute = minute%60
    return str(hour*10000 + minute*100 + second)

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

    # office["time"] = changeTime(office["time"])
    # office["temperature"] = changeValue(office["temperature"])
    # office["humidity"] = changeValue(office["humidity"])
    # office["illumination"] = changeValue(office["illumination"])

    devices = list(deviceStatus.keys())
    for item in devices:
        office[item] = changeStatus(item)

    ans = []
    for item in list(office.keys()):
        if office[item] != old_office[item]:
            ans.append([item, office[item]])
    return ans

def runRules(office, Triggers, rules, id):
    # triggers = [[“time”：xx]， [“temxxx”：xx]]
    # [{id,status,time,rules, "triggerId", "actionIds", "ancestor"}]
    # 维护一个家庭状态， 维护一个Triggers 和 tirggerId,
    # 找到所有当前可能执行的规则，随机挑选执行，判断condition是否满足，如果不满足就是skipped，如果满足就修改office状态，把action加入到新的Triggers并给出triggerId。

    triggerId = {}
    eporch = 0
    logs = []
    time = int(office["time"])
    Actions = []
    actionId = {}
    logfile = open("logs.txt", "a", encoding="utf-8")


    for i in range(len(Triggers)):
        triggerId[str(Triggers[i])] = 0

    while len(Triggers) != 0 and eporch < 1:
        potientialRules = findPotientialRules(Triggers, rules)
        # 随机打乱，不放回抽样
        potientialRules = np.random.choice(potientialRules, len(potientialRules), False)

        for rule in potientialRules:
            # 条件不满足，跳过执行
            if len(rule['Condition'])  != 0 and ((rule['Condition'][0] == 'time' and int(rule['Condition'][1]) != int(office["time"])) or office[rule['Condition'][0]] != rule['Condition'][1]):
                temp = copy.copy(rule)
                temp["id"] = id
                temp["status"] = "skipped"
                temp["time"] = time
                if triggerId[str(rule["Trigger"])] == 0:
                    temp["triggerId"] = id
                else:
                    temp["triggerId"] = triggerId[str(rule["Trigger"])]
                temp["actionIds"] = []
                temp["ancestor"] = ""
                temp["triggerTime"] = int(datetime.now().timestamp())
                logs.append(temp)
            else:
                # 生成记录
                temp = copy.copy(rule)
                temp["id"] = id
                temp["status"] = "run"
                temp["time"] = time
                # 没有triggerId就用当前的id，说明是一个新触发的trigger
                if triggerId[str(rule["Trigger"])] == 0:
                    temp["triggerId"] = id
                    temp["ancestor"] = id
                else:
                    temp["triggerId"] = triggerId[str(rule["Trigger"])]
                    temp["ancestor"] = ""
                temp["actionIds"] = []
                temp["triggerTime"] = int(datetime.now().timestamp())
                logs.append(temp)

                # 添加新的Action
                for item in rule["Action"]:
                    # 动作执行，修改房间状态
                    office[item[0]] = item[1]
                    Actions.append(item)
                    actionId[str(item)] = id
            id += 1
        # 攻防转换
        Triggers = Actions
        triggerId = actionId
        Actions = []
        actionId = {}
        eporch += 1


    for log in logs:
        if log["ancestor"] == "":
            for i in range(len(logs)):
                if logs[i]["id"] == log["triggerId"]:
                    log["ancestor"] = logs[i]["ancestor"]

    for log in logs:
        logfile.write(str(log)+"\n")
    logfile.close()
    return logs, id

# 基于并发控制执行规则
def runSyncRules(office, Triggers, rules, syncid):
    # triggers = [[“time”：xx]， [“temxxx”：xx]]
    # [{id,status,time,rules, "triggerId", "actionIds", "ancestor"}]
    # 维护一个家庭状态， 维护一个Triggers 和 tirggerId,
    # 找到所有当前可能执行的规则，随机挑选执行，判断condition是否满足，如果不满足就是skipped，如果满足就修改office状态，把action加入到新的Triggers并给出triggerId。

    triggerId = {}
    eporch = 0
    logs = []
    time = int(office["time"])
    Actions = []
    actionId = {}
    synclogfile = open("synclogs.txt", "a", encoding="utf-8")
    concurrlogfile = open("concurrlogs.txt", "a", encoding="utf-8")


    for i in range(len(Triggers)):
        triggerId[str(Triggers[i])] = 0

    while len(Triggers) != 0 and eporch < 10:
        potientialRules = findPotientialRules(Triggers, rules)

        for rule in potientialRules:
            # 条件不满足，跳过执行
            if len(rule['Condition'])  != 0 and ((rule['Condition'][0] == 'time' and int(rule['Condition'][1]) != int(office["time"])) or office[rule['Condition'][0]] != rule['Condition'][1]):
                temp = copy.copy(rule)
                temp["id"] = syncid
                temp["status"] = "skipped"
                temp["time"] = time
                if triggerId[str(rule["Trigger"])] == 0:
                    temp["triggerId"] = syncid
                else:
                    temp["triggerId"] = triggerId[str(rule["Trigger"])]
                temp["actionIds"] = []
                temp["ancestor"] = ""
                temp["triggerTime"] = int(datetime.now().timestamp())
                logs.append(temp)
            else:
                # 生成记录
                temp = copy.copy(rule)
                temp["id"] = syncid
                temp["status"] = "run"
                temp["time"] = time
                # 没有triggerId就用当前的id，说明是一个新触发的trigger
                if triggerId[str(rule["Trigger"])] == 0:
                    temp["triggerId"] = syncid
                    temp["ancestor"] = syncid
                else:
                    temp["triggerId"] = triggerId[str(rule["Trigger"])]
                    temp["ancestor"] = ""
                temp["actionIds"] = []
                temp["triggerTime"] = int(datetime.now().timestamp())
                logs.append(temp)

                # 添加新的Action
                for item in rule["Action"]:
                    # 动作执行，修改房间状态
                    office[item[0]] = item[1]
                    Actions.append(item)
                    actionId[str(item)] = syncid
            syncid += 1
        # 攻防转换
        Triggers = Actions
        triggerId = actionId
        Actions = []
        actionId = {}
        eporch += 1

    for log in logs:
        if log["ancestor"] == "":
            for i in range(len(logs)):
                if logs[i]["id"] == log["triggerId"]:
                    log["ancestor"] = logs[i]["ancestor"]

    for log in logs:
        synclogfile.write(str(log)+"\n")
    synclogfile.close()

    # 打乱 logs，模拟并发无序执行。但是后面用Java多线程来做并发无序。
    shuffled_logs = list(np.random.permutation(logs))  # 打乱顺序
    for log in shuffled_logs:
        concurrlogfile.write(str(log) + "\n")  # 追加到并发日志文件

    return logs, syncid

def findPotientialRules(Triggers, rules):
    potientialRules = []
    for rule in rules:
        if rule["Trigger"] in Triggers:
            potientialRules.append(rule)
    return potientialRules

def ConflictsToFile(office, conflict, type):
    with open(conflict_file, "a", encoding='utf-8') as f:
        # 环境
        office_data = ""
        office_keys = list(office.keys())
        for key in office_keys:
            office_data += str(office[key])+","

        # user1, user2
        user_data = str(conflict[0]['user']) + "," + str(conflict[1]['user']) + ","

        # 规则：triggerMode,formerTriggerType,latterTriggerType,formerDescription,latterDescription,

        conflict[0]["description"] = conflict[0]["description"].replace(",", ".")
        conflict[1]["description"] = conflict[1]["description"].replace(",", ".")

        data = "0,"
        data += str(conflict[0]["description"]) + ","
        data += str(conflict[1]["description"]) + ","

        # exection,score1,score2
        execution_data = ""
        if conflict[0]["score"]>conflict[1]["score"]:
            execution_data += str(0)
        elif conflict[0]["score"]<conflict[1]["score"]:
            execution_data += str(1)
        else:
            execution_data += "null"

        execution_data += "\n"

        f.write(office_data+data+type+","+user_data+execution_data)



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


def detector(logs, office):

    # 从前往后遍历，双指针遍历，为了对比两个数据集，
    # Action Loop:前面是否有相同的Action，且在一条链上
    # Action Repetition：前面是否有相同的Action，且在一个祖宗上
    # Action Revert：前面是否有相同的设备的Action，不同的status，且在一条链上
    # Action Conflict:前面是否有相同的设备的Action，不同的status，且在一个祖宗上
    # unexpected Conflict:相同的设备的Action，不同的status，不在同一个祖宗上
    # Condition Bypass：skipped的规则，前面或者后面有没有相同的Action
    # Condition Pass：If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) run的规则前面有没有关闭curtain12的rule
    # Condition Block：If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) skipped的规则，前面有没有规则的修改curtain12的rule
    # Condition Contradictory：没有，在用户构建的规则中，没有能够导致condition Contradictory的规则。如果有，那就是If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) ，和If door(4) is open, when curtain(1) or curtain(2) is opened, open the xxx。
    criFile = open("CRIs.txt", "a", encoding="utf-8")
    ActionLoopNum = 0
    ActionRepetitionNum = 0
    ActionRevertNum = 0
    ActionConflictNum = 0
    unexpectedConflictNum = 0
    ConditionBypassNum = 0
    ConditionPassNum = 0
    ConditionBlockNum = 0
    ConditionContradictoryNum = 0
    UsersActionLoopNum = 0
    UsersActionRepetitionNum = 0
    UsersActionRevertNum = 0
    UsersActionConflictNum = 0
    UsersunexpectedConflictNum = 0
    UsersConditionBypassNum = 0
    UsersConditionPassNum = 0
    UsersConditionBlockNum = 0
    UsersConditionContradictoryNum = 0

    for i in range(len(logs)):
        LatterActions = logs[i]["Action"]
        if logs[i]['status'] == 'skipped':
            # Condition Bypass：skipped的规则，前面或者后面有没有相同的Action
            for j in range(i-1, -1, -1):
                formerActions = logs[j]["Action"]
                for Latter in LatterActions:
                    if Latter in formerActions:
                        ConditionBypassNum += 1
                        if logs[i]['user'] != logs[j]['user']:
                            UsersConditionBypassNum += 1
                        criFile.write("Condition Bypass\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) + "\n\n")
                        ConflictsToFile(office, [logs[j], logs[i]], "Condition Bypass")
            for j in range(i+1, len(logs)):
                formerActions = logs[j]["Action"]
                for Latter in LatterActions:
                    if Latter in formerActions:
                        ConditionBypassNum += 1
                        if logs[i]['user'] != logs[j]['user']:
                            UsersConditionBypassNum += 1
                        criFile.write("Condition Bypass\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) + "\n\n")
                        ConflictsToFile(office, [logs[i], logs[j]], "Condition Bypass")
            if len(logs[i]['Condition']) != 0:
                # Condition Block：If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) skipped的规则，前面有没有规则的修改curtain12的rule
                for j in range(i - 1, -1, -1):
                    formerActions = logs[j]["Action"]
                    Latter = logs[i]["Condition"]
                    for former in formerActions:
                        if Latter[0] == former[0]:
                            ConditionBlockNum += 1
                            if logs[i]['user'] != logs[j]['user']:
                                UsersConditionBlockNum += 1
                            criFile.write("Condition Block\n")
                            criFile.write(str(logs[j]) + "\n")
                            criFile.write(str(logs[i]) + "\n\n")
                            ConflictsToFile(office, [logs[j], logs[i]], "Condition Block")

        else:
            front = logs[i]["triggerId"]
            for j in range(i-1, -1, -1):
                formerActions = logs[j]["Action"]

                for Latter in LatterActions:
                    # Action Loop:前面是否有相同的Action，且在一条链上
                    if Latter in formerActions and logs[j]["id"] == front:
                        ActionLoopNum += 1
                        if logs[i]['user'] != logs[j]['user']:
                            UsersActionLoopNum += 1
                        criFile.write("Action Loop\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) +"\n\n")

                    # Action Repetition：前面是否有相同的Action，且在一个祖宗上
                    elif Latter in formerActions and logs[j]["ancestor"] == logs[i]["ancestor"] :
                        ActionRepetitionNum += 1
                        if logs[i]['user'] != logs[j]['user']:
                            UsersActionRepetitionNum += 1
                        criFile.write("Action Repetition\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) + "\n\n")
                    else:

                        for former in formerActions:
                            # Action Revert：前面是否有相同的设备的Action，不同的status，且在一条链上
                            if Latter[0] == former[0] and logs[j]["id"] == front:
                                ActionRevertNum += 1
                                if logs[i]['user'] != logs[j]['user']:
                                    UsersActionRevertNum += 1
                                criFile.write("Action Revert\n")
                                criFile.write(str(logs[j]) + "\n")
                                criFile.write(str(logs[i]) + "\n\n")


                            # Action Conflict:前面是否有相同的设备的Action，不同的status，且在一个祖宗上
                            elif Latter[0] == former[0] and logs[j]["ancestor"] == logs[i]["ancestor"]:
                                ActionConflictNum += 1
                                if logs[i]['user'] != logs[j]['user']:
                                    UsersActionConflictNum += 1
                                criFile.write("Action Conflict\n")
                                criFile.write(str(logs[j]) + "\n")
                                criFile.write(str(logs[i]) + "\n\n")
                                ConflictsToFile(office, [logs[j], logs[i]], "Action Conflict")
                            # unexpected Conflict:相同的设备的Action，不同的status，不在同一个祖宗上
                            elif Latter[0] == former[0] and Latter[1] != former[1] :
                                unexpectedConflictNum += 1
                                if logs[i]['user'] != logs[j]['user']:
                                    UsersunexpectedConflictNum += 1
                                criFile.write("unexpected Conflict\n")
                                criFile.write(str(logs[j]) + "\n")
                                criFile.write(str(logs[i]) + "\n\n")
                                ConflictsToFile(office, [logs[j], logs[i]], "unexpected Conflict")
                # Condition Contradictory：没有，在用户构建的规则中，没有能够导致condition Contradictory的规则。如果有，那就是If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) ，和If door(4) is open, when curtain(1) or curtain(2) is opened, open the xxx。
                if len(logs[i]['Condition']) != 0 and len(logs[j]["Condition"]) != 0 and logs[i]['Condition'][0] ==logs[j]['Condition'][0] \
                        and logs[i]['Condition'][1] !=logs[j]['Condition'][1] :
                    ConditionContradictoryNum += 1
                    if logs[i]['user'] != logs[j]['user']:
                        UsersConditionContradictoryNum += 1
                    criFile.write("Condition Contradictory\n")
                    criFile.write(str(logs[j]) + "\n")
                    criFile.write(str(logs[i]) + "\n\n")
                    ConflictsToFile(office, [logs[j], logs[i]], "Condition Contradictory")

                if logs[j]["id"] == front:
                    front = logs[j]["triggerId"]
            if len(logs[i]['Condition']) != 0 :
                # Condition Pass：If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) run的规则前面有没有关闭curtain12的rule
                for j in range(i - 1, -1, -1):
                    formerActions = logs[j]["Action"]
                    Latter = logs[i]['Condition']
                    if Latter in formerActions:
                        ConditionPassNum += 1
                        if logs[i]['user'] != logs[j]['user']:
                            UsersConditionPassNum += 1
                        criFile.write("Conditon Pass\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) + "\n\n")
                        ConflictsToFile(office, [logs[j], logs[i]], "Conditon Pass")


    # print(ActionLoopNum)
    # print(ActionRepetitionNum)
    # print(ActionRevertNum)
    # print(ActionConflictNum)
    # print(unexpectedConflictNum)
    # print(ConditionBypassNum)
    # print(ConditionPassNum)
    # print(ConditionBlockNum)
    criFile.close()

    return ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum, ConditionBypassNum, \
           ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum, UsersActionLoopNum, UsersActionRepetitionNum, \
           UsersActionRevertNum, UsersActionConflictNum, UsersunexpectedConflictNum, UsersConditionBypassNum,UsersConditionPassNum,\
           UsersConditionBlockNum, UsersConditionContradictoryNum

if __name__ == '__main__':
    # home
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

    # 初始化文件
    logfile = open("logs.txt", "w", encoding="utf-8")
    logfile.close()
    synclogfile = open("synclogs.txt", "w", encoding="utf-8")
    synclogfile.close()
    concurrlogfile = open("concurrlogs.txt", "w", encoding="utf-8")
    concurrlogfile.close()
    criFile = open("CRIs.txt", "w", encoding="utf-8")
    criFile.close()
    conflictFile = open(conflict_file, "w", encoding='utf-8')
    conflictFile.close()

    id = 1
    syncid = 1
    ALNum, ARnNum, ARtNum, ACNum, uCNum, CBsNum, CPNum, CBkNum, CCNum = 0, 0, 0, 0, 0, 0, 0, 0, 0
    UALNum, UARnNum, UARtNum, UACNum, UuCNum, UCBsNum, UCPNum, UCBkNum, UCCNum = 0, 0, 0, 0, 0, 0, 0, 0, 0
    for i in range(times):
        logging.info('随机改变场景')  # 普通日志信息
        Triggers = updateOfficeStatus(office)

        # logging.info('乱序并发触发规则')  # 普通日志信息
        # logs, id = runRules(office, Triggers, rules, id)

        # # 检测随机模拟并发执行生成的日志
        # logging.critical('冲突检查乱序执行日志')
        # (
        #     ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum,
        #     ConditionBypassNum, ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum, UsersActionLoopNum,
        #     UsersActionRepetitionNum, UsersActionRevertNum, UsersActionConflictNum, UsersunexpectedConflictNum,
        #     UsersConditionBypassNum, UsersConditionPassNum, UsersConditionBlockNum, UsersConditionContradictoryNum
        # ) = detector(logs, office)

        # logging.critical(
        #     '乱序执行检测结果: '
        #     'ActionLoopNum=%s, ActionRepetitionNum=%s, ActionRevertNum=%s, ActionConflictNum=%s, unexpectedConflictNum=%s, '
        #     'ConditionBypassNum=%s, ConditionPassNum=%s, ConditionBlockNum=%s, ConditionContradictoryNum=%s, '
        #     'UsersActionLoopNum=%s, UsersActionRepetitionNum=%s, UsersActionRevertNum=%s, UsersActionConflictNum=%s, '
        #     'UsersunexpectedConflictNum=%s, UsersConditionBypassNum=%s, UsersConditionPassNum=%s, '
        #     'UsersConditionBlockNum=%s, UsersConditionContradictoryNum=%s',
        #     ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum,
        #     ConditionBypassNum, ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum,
        #     UsersActionLoopNum, UsersActionRepetitionNum, UsersActionRevertNum, UsersActionConflictNum,
        #     UsersunexpectedConflictNum, UsersConditionBypassNum, UsersConditionPassNum,
        #     UsersConditionBlockNum, UsersConditionContradictoryNum
        # )

        # 生成顺序执行时的规则日志
        logging.info('顺序执行触发规则')
        synclogs, syncid = runSyncRules(office, Triggers, rules, syncid)

        # 检测顺序执行生成的日志
        logging.critical('冲突检查顺序执行日志')
        (
            ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum,
            ConditionBypassNum, ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum, UsersActionLoopNum,
            UsersActionRepetitionNum, UsersActionRevertNum, UsersActionConflictNum, UsersunexpectedConflictNum,
            UsersConditionBypassNum, UsersConditionPassNum, UsersConditionBlockNum, UsersConditionContradictoryNum
        ) = detector(synclogs, office)

        logging.critical(
            '顺序执行检测结果: '
            'ActionLoopNum=%s, ActionRepetitionNum=%s, ActionRevertNum=%s, ActionConflictNum=%s, unexpectedConflictNum=%s, '
            'ConditionBypassNum=%s, ConditionPassNum=%s, ConditionBlockNum=%s, ConditionContradictoryNum=%s, '
            'UsersActionLoopNum=%s, UsersActionRepetitionNum=%s, UsersActionRevertNum=%s, UsersActionConflictNum=%s, '
            'UsersunexpectedConflictNum=%s, UsersConditionBypassNum=%s, UsersConditionPassNum=%s, '
            'UsersConditionBlockNum=%s, UsersConditionContradictoryNum=%s',
            ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum,
            ConditionBypassNum, ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum,
            UsersActionLoopNum, UsersActionRepetitionNum, UsersActionRevertNum, UsersActionConflictNum,
            UsersunexpectedConflictNum, UsersConditionBypassNum, UsersConditionPassNum,
            UsersConditionBlockNum, UsersConditionContradictoryNum
        )

        # 累计统计数据
        ALNum += ActionLoopNum
        ARnNum += ActionRepetitionNum
        ARtNum += ActionRevertNum
        ACNum += ActionConflictNum
        uCNum += unexpectedConflictNum
        CBsNum += ConditionBypassNum
        CPNum += ConditionPassNum
        CBkNum += ConditionBlockNum
        CCNum += ConditionContradictoryNum

        UALNum += UsersActionLoopNum
        UARnNum += UsersActionRepetitionNum
        UARtNum += UsersActionRevertNum
        UACNum += UsersActionConflictNum
        UuCNum += UsersunexpectedConflictNum
        UCBsNum += UsersConditionBypassNum
        UCPNum += UsersConditionPassNum
        UCBkNum += UsersConditionBlockNum
        UCCNum += UsersConditionContradictoryNum

        # 每轮结束后用红线分隔，并输出统计结果
        logging.critical('统计结果 (第 {} 次迭代)'.format(i + 1))
        logging.critical(
            'ALNum: {}, ARnNum: {}, ARtNum: {}, ACNum: {}, uCNum: {}, CBsNum: {}, CPNum: {}, CBkNum: {}, CCNum: {}'.format(
                ALNum, ARnNum, ARtNum, ACNum, uCNum, CBsNum, CPNum, CBkNum, CCNum))
        logging.critical(
            'UALNum: {}, UARnNum: {}, UARtNum: {}, UACNum: {}, UuCNum: {}, UCBsNum: {}, UCPNum: {}, UCBkNum: {}, UCCNum: {}'.format(
                UALNum, UARnNum, UARtNum, UACNum, UuCNum, UCBsNum, UCPNum, UCBkNum, UCCNum))
        print('\n')

