import random
import numpy as np
from math import log2
import os
import matplotlib.pyplot as plt


# 用来验证归一化熵对于互斥锁申请时间影响的，但是没啥用
# 废弃了，唉，他妈的


# 带标签的规则生成函数
def add_lock_labels_to_rules(rules):
    room_assignments = {room: 0 for room in Room}

    labeled_rules = []
    for rule in rules:
        home_label = Home
        room_label = min(room_assignments, key=room_assignments.get)
        room_assignments[room_label] += 1

        device_types = []
        device_names = []
        for action in rule["Action"]:
            device_name = action[0]
            if device_name in device_type_mapping:
                device_types.append(device_type_mapping[device_name])
                device_names.append(device_name)

        device_types = list(set(device_types))
        device_names = list(set(device_names))

        labeled_rule = rule.copy()
        labeled_rule["Home"] = home_label
        labeled_rule["Room"] = [room_label]
        labeled_rule["DeviceType"] = device_types
        labeled_rule["DeviceName"] = device_names

        labeled_rules.append(labeled_rule)

    return labeled_rules

# 规则集合



ldm = [
    {"score": 3, "Trigger": ["NetatmoWeatherStation", 2], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "if Netatmo Weather Station(11) is Windy, close MiJia Curtains(1,2)", "triggerType": 2},
    {"score": 3, "Trigger": ["Location", 1], "Condition": [], "Action": [["iRobotRoomba", 0]],
     "description": "if i leave home, start the iRobot(7)", "triggerType": 3},
    {"score": 4, "Trigger": ["time", "190000"], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "if 7p.m.,close MiJia Curtains(1,2)", "triggerType": 0},
    {"score": 2, "Trigger": ["time", "70000"], "Condition": [], "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],
     "description": "if 7a.m.,open MiJia Curtains(1,2)", "triggerType": 0},
    {"score": 4, "Trigger": ["RingDoorbell", 2], "Condition": [], "Action": [["YeelightBulb", 0]],
     "description": "if doorbell rings(6), open the Yeelight Bulb(3)", "triggerType": 3},
    {"score": 5, "Trigger": ["SmartThingsDoorSensor", 2], "Condition": [], "Action": [["Notification", 0]],
     "description": "if door opened(4),notify me.", "triggerType": 3},
    {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
                ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "if door opened(5), when after 7p.m., open the lamps(12,13,14,15,16)", "triggerType": 3},
    {"score": 5, "Trigger": ["Location", 1], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 1], ["YeelightCeilingLamp2", 1], ["YeelightCeilingLamp3", 1],
                ["YeelightCeilingLamp5", 1], ["YeelightCeilingLamp6", 1]],
     "description": "if i leave home, close all lamps(12,13,14,15,16)", "triggerType": 3},
    {"score": 3, "Trigger": ["AlexaVoiceAssistance", 2], "Condition": [],
     "Action": [["YeelightBulb", 0], ["PhilipsHueLight", 0]], "description": "tell alexa to open hue lights(3,9)",
     "triggerType": 3},
    {"score": 3, "Trigger": ["AlexaVoiceAssistance", 3], "Condition": [],
     "Action": [["YeelightBulb", 1], ["PhilipsHueLight", 1]], "description": "tell alexa to close hue lights(3,9)",
     "triggerType": 3},
    {"score": 4, "Trigger": ["MideaAirConditioner", 0], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "if air conditioner(10) is opened, close curtains(1,2)", "triggerType": 1},
    {"score": 2, "Trigger": ["temperature", 30], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "if temperature is over 30, open the air conditioner(10)", "triggerType": 2},
    {"score": 1, "Trigger": ["temperature", 15], "Condition": [], "Action": [["MideaAirConditioner", 1]],
     "description": "if temperature is under 15, close the air conditioner(10)", "triggerType": 2},
    {"score": 5, "Trigger": ["NetatmoWeatherStation", 3], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]], "description": "if rain(11), close the curtains(1,2)",
     "triggerType": 2},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 4], "Condition": [],
     "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]], "description": "if sun(12), open the curtains(1,2)",
     "triggerType": 2},
    {"score": 3, "Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action": [["WemoSmartPlug", 0]],
     "description": "if motion(19) detected, open the wemo smart plug(17).", "triggerType": 2},
    {"score": 5, "Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action": [["WyzeCamera", 1]],
     "description": "if motion detected(19), open the camera(18)", "triggerType": 2},
    {"score": 2, "Trigger": ["humidity", 30], "Condition": [], "Action": [["MijiaPurifier", 0]],
     "description": "if humidity is under 30, open the purifier", "triggerType": 2},
    {"score": 1, "Trigger": ["humidity", 60], "Condition": [], "Action": [["MijiaPurifier", 1]],
     "description": "if humidity is over 60, close the purifier", "triggerType": 2},
]

whd = [
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": ["MijiaCurtain1", 1], "Action": [["YeelightBulb", 0]],
     "description": "If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)",
     "triggerType": 2},
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": ["MijiaCurtain2", 1], "Action": [["YeelightBulb", 0]],
     "description": "If wemo is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3)",
     "triggerType": 2},
    {"score": 3, "Trigger": ["MijiaDoorLock", 1], "Condition": [], "Action": [["YeelightBulb", 1]],
     "description": "If door(5) is locked, after 10sec, turn off the Yeelight Bulb(3)", "triggerType": 1},
    {"score": 2, "Trigger": ["WyzeCamera", 2], "Condition": [],
     "Action": [["PhilipsHueLight", 0], ["MijiaProjector", 0]],
     "description": "If motion(18) is detected by Wyze Camera, turn on Philips Hue Light(9) and Mijia Projecter(23)",
     "triggerType": 2},
    {"score": 4, "Trigger": ["time", "110000"], "Condition": ["WyzeCamera", 2],
     "Action": [["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1", 1], ["YeelightCeilingLamp2", 1],
                ["YeelightCeilingLamp3", 1], ["YeelightCeilingLamp5", 1], ["YeelightCeilingLamp6", 1]],
     "description": "When 11pm - 5am every clock, if last motion(18) detected past over 2 hours, close Philips light(9),Wemo Plug(17), Lamps(12-16)",
     "triggerType": 0},
    {"score": 5, "Trigger": ["MijiaDoorLock", 1], "Condition": [], "Action": [["WyzeCamera", 0], ["Notification", 0]],
     "description": "If door(5) is unlocked between 11pm-4am, record a short vedio clip(18) and turn on notification(18)",
     "triggerType": 0},
    {"score": 3, "Trigger": ["temperature", 35], "Condition": [],
     "Action": [["WemoSmartPlug", 0], ["MideaAirConditioner", 0]],
     "description": "If room temperature(11) is over 86$^\circ$F ,when between 8am-9pm, open Wemo Smart Plug(17) and Air Conditioner(10)",
     "triggerType": 2},
    {"score": 3, "Trigger": ["temperature", 13], "Condition": [], "Action": [["MideaAirConditioner", 1]],
     "description": "If room temperature is between 60 and 80$ ^\circ$F, turn off Air Conditioner", "triggerType": 2},
    {"score": 5, "Trigger": ["AlexaVoiceAssistance", 4], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
                ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "Tell Alexa(8) to open a certain Yeelight Ceiling Lamp(12-16)", "triggerType": 3},
    {"score": 5, "Trigger": ["AlexaVoiceAssistance", 5], "Condition": [],
     "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],
     "description": "Tell Alexa(8) to open/close a certain Curtain(1-2)", "triggerType": 3},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0]],
     "description": "If PIR motion senser(19) detects person, turn on Yeelight Ceiling Lamp (12-13)", "triggerType": 2},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor2", 2], "Condition": [],
     "Action": [["YeelightCeilingLamp3", 0], ["YeelightCeilingLamp5", 0]],
     "description": "If PIR motion senser(20) detects person, turn on Yeelight Ceiling Lamp (13-14)", "triggerType": 2},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor3", 2], "Condition": [],
     "Action": [["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "If PIR motion senser(21) detects person, turn on Yeelight Ceiling Lamp (15-16)", "triggerType": 2},
    {"score": 3, "Trigger": ["SmartLifePIRmotionsensor1", 3], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 1], ["YeelightCeilingLamp2", 1]],
     "description": "Every 30 minutes check PIR motion sensor(19), if 1h since last person detected, close lamp (12-13)",
     "triggerType": 2},
    {"score": 3, "Trigger": ["SmartLifePIRmotionsensor2", 3], "Condition": [],
     "Action": [["YeelightCeilingLamp3", 1], ["YeelightCeilingLamp5", 1]],
     "description": "Every 30 minutes check PIR motion sensor(20), if 1h since last person detected, close lamp (13-14)",
     "triggerType": 2},
    {"score": 3, "Trigger": ["SmartLifePIRmotionsensor3", 3], "Condition": [],
     "Action": [["YeelightCeilingLamp5", 1], ["YeelightCeilingLamp6", 1]],
     "description": "Every 30 minutes check PIR motion sensor21, if 1h since last person detected, close lamp 15\&16",
     "triggerType": 2},
    {"score": 2, "Trigger": ["MijiaCurtain1", 0], "Condition": [], "Action": [["YeelightCeilingLamp5", 1]],
     "description": "If curtain(1) is open when between 8am and 5pm, turn off Yeelight(15)", "triggerType": 3},
    {"score": 2, "Trigger": ["MijiaCurtain2", 0], "Condition": [], "Action": [["YeelightCeilingLamp6", 1]],
     "description": "If curtain(2) is open when between 8am and 5pm, turn off Yeelight(16)", "triggerType": 3},
    {"score": 4, "Trigger": ["time", "0"], "Condition": ["time", "000000"],
     "Action": [["YeelightBulb", 1], ["PhilipsHueLight", 1], ["WemoSmartPlug", 1], ["YeelightCeilingLamp1", 1],
                ["YeelightCeilingLamp2", 1], ["YeelightCeilingLamp3", 1], ["YeelightCeilingLamp5", 1],
                ["YeelightCeilingLamp6", 1], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1], ["MijiaPurifier", 1],
                ["MijiaProjector", 1]],
     "description": "When 12pm, turn off all the light(3,9,12-16) and plug(17) and Mijia projecter(23), Mijia purifier(22), curtain(1-2).",
     "triggerType": 0},
    {"score": 3, "Trigger": ["time", "80000"], "Condition": [], "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],
     "description": "When sunshine and 8am-5pm, open curtain(1-2)", "triggerType": 0},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action": [["iRobotRoomba", 2]],
     "description": "If person detected by PIR motion(19), dock robot(7)", "triggerType": 2},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor2", 2], "Condition": [], "Action": [["iRobotRoomba", 2]],
     "description": "If person detected by PIR motion(20), dock robot(7)", "triggerType": 2},
    {"score": 4, "Trigger": ["SmartLifePIRmotionsensor3", 2], "Condition": [], "Action": [["iRobotRoomba", 2]],
     "description": "If person detected by PIR motion(21), dock robot(7)", "triggerType": 2}
]

wzf = [
    {"score": 2, "Trigger": ["MijiaCurtain1", 1], "Condition": [], "Action": [["YeelightCeilingLamp5", 0]],
     "description": "If curtain(1) off, when motion sensor(21) detect person, then Lamp(15) switch on.",
     "triggerType": 1},
    {"score": 2, "Trigger": ["MijiaCurtain2", 1], "Condition": [], "Action": [["YeelightCeilingLamp6", 0]],
     "description": "If  curtain(2) off, when motion sensor(21) detect person, then Lamp(16) switch on",
     "triggerType": 1},
    {"score": 1, "Trigger": ["MijiaDoorLock", 1], "Condition": [], "Action": [["YeelightCeilingLamp3", 0]],
     "description": "If door(5) unlock, when night, then lamp(14) on", "triggerType": 1},
    {"score": 3, "Trigger": ["MijiaDoorLock", 1], "Condition": [],
     "Action": [["RingDoorbell", 0], ["AlexaVoiceAssistance", 0], ["YeelightCeilingLamp5", 0],
                ["YeelightCeilingLamp6", 0]], "description": "If door(5) unlock, then lights(6,8,11,17-18) switch on",
     "triggerType": 1},
    {"score": 5, "Trigger": ["MijiaDoorLock", 0], "Condition": ["SmartThingsDoorSensor", 0],
     "Action": [["WyzeCamera", 3]], "description": "If door(5) lock, when door sensor(4) open, then wyze(18) alert",
     "triggerType": 1},
    {"score": 3, "Trigger": ["MijiaDoorLock", 0], "Condition": [], "Action": [["iRobotRoomba", 0]],
     "description": "If door(5) lock, when fri, then iRobot(7) cleaning a room", "triggerType": 1},
    {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
     "Action": [["WemoSmartPlug", 1], ["MijiaPurifier", 1]],
     "description": "If door(5) lock, wemo(17) and purifier(22) switch off", "triggerType": 1},
    {"score": 4, "Trigger": ["iRobotRoomba", 0], "Condition": [], "Action": [["WyzeCamera", 4]],
     "description": "If iRobot(7) robot started, then wyze(18) disable motion detection", "triggerType": 3},
    {"score": 0, "Trigger": ["humidity", 40], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "If weather station(11) detect humidity drops below, then air conditioner(10) switch on",
     "triggerType": 2},
    {"score": 1, "Trigger": ["NetatmoWeatherStation", 2], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "If weather station(11) detect wind speed rise, curtain(1,2) switch off", "triggerType": 3},
    {"score": 2, "Trigger": ["SmartLifePIRmotionsensor1", 2], "Condition": [], "Action": [["WyzeCamera", 5]],
     "description": "If sensor(19) detect person, wyze(18) enable motion detection", "triggerType": 2},
    {"score": 5, "Trigger": ["SmartLifePIRmotionsensor2", 2], "Condition": [], "Action": [["WyzeCamera", 5]],
     "description": "If PIR Motion Sensor(20) detects person, enable Camera(18) motion detection", "triggerType": 2},
    {"score": 3, "Trigger": ["WyzeCamera", 2], "Condition": [], "Action": [["PhilipsHueLight", 0]],
     "description": "If Camera(18) detects person, open Light(9)", "triggerType": 3},
    {"score": 3, "Trigger": ["MijiaPurifier", 0], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]], "description": "If open Purifier(22), close Curtain (1-2)",
     "triggerType": 1},
    {"score": 1, "Trigger": ["NetatmoWeatherStation", 5], "Condition": [], "Action": [["MijiaPurifier", 1]],
     "description": "If Weather Station(11) detects rain stop, turn off Purifier(22)", "triggerType": 3},
    {"score": 3, "Trigger": ["RingDoorbell", 2], "Condition": [], "Action": [["MijiaProjector", 0]],
     "description": "If Doorbell(6) rings, mute Projector (23)", "triggerType": 3},
    {"score": 5, "Trigger": ["WyzeCamera", 2], "Condition": [], "Action": [["MijiaProjector", 1]],
     "description": "If Camera(18) detect person, unmute Projector(23)", "triggerType": 3},
]

zxh = [
    {"score": 2, "Trigger": ["WemoSmartPlug", 0], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "If wemo is open, close curtain(1) and curtain(2)", "triggerType": 2},
    {"score": 2, "Trigger": ["MijiaCurtain1", 1], "Condition": [], "Action": [["YeelightBulb", 0]],
     "description": "When the curtain is closed, please turn on the bulb.", "triggerType": 1},
    {"score": 3, "Trigger": ["SmartThingsDoorSensor", 2], "Condition": [],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "After 7 pm, I come to the room, when I open the door, the curtain should be closed",
     "triggerType": 2},
    {"score": 1, "Trigger": ["temperature", 30], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "When the temperature is over 30°C, the Midea Air Conditioner should be open.", "triggerType": 2},
    {"score": 4, "Trigger": ["Location", 1], "Condition": [], "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "When I leave the room, the curtain should be closed.", "triggerType": 3},
    {"score": 5, "Trigger": ["time", "90000"], "Condition": [], "Action": [["MijiaProjector", 0]],
     "description": "Every Tuesday 9 am, the Mijia Projector should be open for a conference.", "triggerType": 0},
    {"score": 1, "Trigger": ["temperature", -5], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "When the temperature is below -5°C, the Mijia Air Conditioner should be open.", "triggerType": 2},
    {"score": 5, "Trigger": ["time", "230000"], "Condition": [], "Action": [["MijiaProjector", 1]],
     "description": "After 11 pm every Sunday, the projector should be closed for  a maintenance status",
     "triggerType": 0},
    {"score": 1, "Trigger": ["temperature", 20], "Condition": [], "Action": [["MijiaDoorLock", 0]],
     "description": "When the temperature is over 20°C in summar, the door should be open for ventilating.",
     "triggerType": 2},
    {"score": 4, "Trigger": ["Location", 1], "Condition": ["time", "220000"], "Action": [["YeelightBulb", 1]],
     "description": "After we leave the room, about 10 pm everyday, the bulb should be closed.", "triggerType": 3},
    {"score": 4, "Trigger": ["Location", 1], "Condition": ["time", "220000"],
     "Action": [["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "After we leave the room, about 10 pm everyday, the curtain should be closed.", "triggerType": 3},
    {"score": 4, "Trigger": ["time", "90000"], "Condition": [], "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],
     "description": "Before we come to the room to study, about 9 am everyday, the curtain should be open.",
     "triggerType": 0},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 3], "Condition": [],
     "Action": [["MijiaCurtain1", 0], ["MijiaCurtain2", 0]],
     "description": "If it is raining in winter, the curtain should be open for more light.", "triggerType": 3},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 3], "Condition": [], "Action": [["YeelightBulb", 0]],
     "description": "If it is raining after 5 pm, the bulb should be open for more light.", "triggerType": 3},
    {"score": 4, "Trigger": ["Location", 1], "Condition": ["time", "220000"], "Action": [["WemoSmartPlug", 1]],
     "description": "After we leave the room, about 10 pm everyday, the smart plug should be closed.",
     "triggerType": 3},
    {"score": 3, "Trigger": ["time", "90000"], "Condition": [], "Action": [["WemoSmartPlug", 0]],
     "description": "Before we come to the room to study, about 9 am everyday, the smart plug should be open.",
     "triggerType": 0},
    {"score": 5, "Trigger": ["time", "90000"], "Condition": [],
     "Action": [["YeelightBulb", 0], ["MijiaCurtain1", 1], ["MijiaCurtain2", 1]],
     "description": "Every Tuesday 9 am there is a conference, keep thebulb on and curtain off", "triggerType": 0},
    {"score": 2, "Trigger": ["time", "90000"], "Condition": [], "Action": [["Notification", 0]],
     "description": "Get the weather forecast every day at 9 am", "triggerType": 0},
    {"score": 5, "Trigger": ["time", "90000"], "Condition": [], "Action": [["WyzeCamera", 0]],
     "description": "Every Tuesday 9 am there is a conference, keep camera on to record the conference.",
     "triggerType": 0},
    {"score": 4, "Trigger": ["Location", 1], "Condition": [], "Action": [["WyzeCamera", 1]],
     "description": "When I leave the room, the camera should be closed.", "triggerType": 3}
]

zyk = [
    {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
                ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3},
    {"score": 5, "Trigger": ["MijiaCurtain1", 0], "Condition": [], "Action": [["MijiaCurtain2", 0]],
     "description": "if Curtain(1) open ,then Curtain(2) open", "triggerType": 1},
    {"score": 5, "Trigger": ["MijiaCurtain1", 1], "Condition": [], "Action": [["MijiaCurtain2", 1]],
     "description": "if Curtain(1) close ,then Curtain(2) close", "triggerType": 1},
    {"score": 4, "Trigger": ["SmartThingsDoorSensor", 2], "Condition": [],
     "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
                ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
     "description": "if smartThings Door Sensor (4) Any new motion ,then turn on Yeelight (12-16)", "triggerType": 2},
    {"score": 3, "Trigger": ["MijiaCurtain2", 0], "Condition": [], "Action": [["MideaAirConditioner", 1]],
     "description": "if Curtain(2) open ,then turn off Midea Air Conditioner(10)", "triggerType": 1},
    {"score": 3, "Trigger": ["MijiaDoorLock", 0], "Condition": [], "Action": [["WyzeCamera", 0]],
     "description": "if Mijia Door Lock(5) locked,then turn on Wyze Camera(18)", "triggerType": 1},
    {"score": 1, "Trigger": ["RingDoorbell", 2], "Condition": [], "Action": [["AlexaVoiceAssistance", 6]],
     "description": "if Ring Doorbell（6） new ring detected,then Alexa Voice Assistance（8） sing a song",
     "triggerType": 3},
    {"score": 2, "Trigger": ["iRobotRoomba", 0], "Condition": [], "Action": [["MijiaPurifier", 0]],
     "description": "if iRobot Roomba(7) Robot Started ,then Mijia Purifier(22) Start", "triggerType": 1},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 6], "Condition": [], "Action": [["MijiaPurifier", 0]],
     "description": "if Netatmo Weather Station(11) Air pressure rises above,then Mijia Purifier(22) Start",
     "triggerType": 3},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 5], "Condition": [], "Action": [["MijiaPurifier", 0]],
     "description": "if Netatmo Weather Station(11) rain no longer detected,then Mijia Purifier(22) Start",
     "triggerType": 3},
    {"score": 2, "Trigger": ["NetatmoWeatherStation", 7], "Condition": [],
     "Action": [["MijiaPurifier", 0], ["MideaAirConditioner", 0]],
     "description": "if Netatmo Weather Station(11) carbon dioxide rise above ,then Mijia Purifier(22) and Midea Air Conditioner(10) Start",
     "triggerType": 3},
    {"score": 2, "Trigger": ["temperature", 25], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "if Netatmo Weather Station(11) temperature rises above ,then Midea Air Conditioner(10) Start",
     "triggerType": 2},
    {"score": 2, "Trigger": ["temperature", 15], "Condition": [], "Action": [["MideaAirConditioner", 0]],
     "description": "if Netatmo Weather Station(11) temperature drops below ,then Midea Air Conditioner(10) Start",
     "triggerType": 2},
    {"score": 3, "Trigger": ["NetatmoWeatherStation", 8], "Condition": [], "Action": [["WyzeCamera", 0]],
     "description": "if Netatmo Weather Station(11) noise level drops below ,then Wyze Camera（18） Start",
     "triggerType": 3},
    {"score": 5, "Trigger": ["WyzeCamera", 2], "Condition": [], "Action": [["AlexaVoiceAssistance", 7]],
     "description": "if Wyze Camera（18）Smoke alarm is detected ,then  Alexa Voice Assistance（8） alarm",
     "triggerType": 3},
    {"score": 5, "Trigger": ["WyzeCamera", 6], "Condition": [], "Action": [["AlexaVoiceAssistance", 7]],
     "description": "if Wyze Camera（18）CO alarm is detected ,then  Alexa Voice Assistance（8） alarm", "triggerType": 3},
    {"score": 2, "Trigger": ["iRobotRoomba", 1], "Condition": [], "Action": [["WemoSmartPlug", 1]],
     "description": "if iRobot Roomba(7) Job Complete ,then Wemo Smart Plug（17）Turn off", "triggerType": 1},
    {"score": 1, "Trigger": ["YeelightBulb", 0], "Condition": [], "Action": [["MijiaCurtain1", 0]],
     "description": "When turn on the bulb, please close the curtain.", "triggerType": 1},
    {"score": 1, "Trigger": ["YeelightBulb", 1], "Condition": [], "Action": [["MijiaCurtain1", 1]],
     "description": "When turn off the bulb, please open the curtain.", "triggerType": 1},
    {"score": 1, "Trigger": ["NetatmoWeatherStation", 5], "Condition": [], "Action": [["MijiaPurifier", 1]],
     "description": "If Weather Station(11) detects rain stop, turn off Purifier(22)", "triggerType": 3},
    {"score": 3, "Trigger": ["RingDoorbell", 2], "Condition": [], "Action": [["MijiaProjector", 0]],
     "description": "If Doorbell(6) rings, mute Projector (23)", "triggerType": 3},

]

device_type_mapping = {
    "Smoke": "sensor",
    "Location": "sensor",
    "WaterLeakage": "sensor",
    "MijiaCurtain1": "curtain",
    "MijiaCurtain2": "curtain",
    "YeelightBulb": "bulb",
    "SmartThingsDoorSensor": "sensor",
    "MijiaDoorLock": "lock",
    "RingDoorbell": "sensor",
    "iRobotRoomba": "appliance",
    "AlexaVoiceAssistance": "voice_assistance",
    "PhilipsHueLight": "bulb",
    "MideaAirConditioner": "appliance",
    "NetatmoWeatherStation": "weather_station",
    "YeelightCeilingLamp1": "bulb",
    "YeelightCeilingLamp2": "bulb",
    "YeelightCeilingLamp3": "bulb",
    "YeelightCeilingLamp5": "bulb",
    "YeelightCeilingLamp6": "bulb",
    "WemoSmartPlug": "plug",
    "WyzeCamera": "camera",
    "SmartLifePIRmotionsensor1": "sensor",
    "SmartLifePIRmotionsensor2": "sensor",
    "SmartLifePIRmotionsensor3": "sensor",
    "MijiaPurifier": "appliance",
    "MijiaProjector": "appliance",
    "Notification": "notification"
}

Home = ["home"]
Room = ["room1", "room2", "room3", "room4", "room5", "room6"]
DeviceType = [
    "bulb", "sensor", "lock", "plug", "appliance", "camera",
    "voice_assistance", "curtain", "notification", "weather_station"
]
DeviceName = list(device_type_mapping.keys())

all_rules = ldm + whd + wzf + zxh + zyk
labeled_rules = add_lock_labels_to_rules(all_rules)

# Group rules by size
random.seed(32)
rule_groups = []
remaining_rules = labeled_rules.copy()

group_sizes = [10, 20, 30,  40,  50]
previous_group = []

for size in group_sizes:
    current_group = random.sample(remaining_rules, size - len(previous_group))
    previous_group += current_group
    rule_groups.append(previous_group.copy())
    remaining_rules = [rule for rule in remaining_rules if rule not in current_group]

# 计算函数
def calculate_lock_uniformity(lock_usage):
    lock_usage = np.array(lock_usage)
    total_usage = lock_usage.sum()
    num_locks = len(lock_usage)

    if total_usage == 0 or num_locks == 0:
        return {"Normalized Entropy": 0}

    probabilities = lock_usage / total_usage
    entropy = -np.sum([p * log2(p) for p in probabilities if p > 0])
    max_entropy = log2(num_locks)
    normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0

    return {"Normalized Entropy": normalized_entropy}

def count_lock_usage(group, locks, lock_type):
    lock_usage = {lock: 0 for lock in locks}
    for rule in group:
        if lock_type == "device_type":
            used_locks = rule.get("DeviceType", [])
        elif lock_type == "device_name":
            used_locks = rule.get("DeviceName", [])
        elif lock_type == "room":
            used_locks = rule.get("Room", [])
        else:
            used_locks = []

        for lock in used_locks:
            if lock in lock_usage:
                lock_usage[lock] += 1

    return list(lock_usage.values())

# 初始化数据存储
device_type_entropies = []
device_name_entropies = []
room_entropies = []

device_type_times = []
device_name_times = []
room_times = []
# 路径配置
base_path = r"/Detector/Mutex/CS/Size/Data"

for group, size in zip(rule_groups, group_sizes):
    # 计算 device_type 的归一化熵
    device_type_usage = count_lock_usage(group, DeviceType, "device_type")
    device_type_metrics = calculate_lock_uniformity(device_type_usage)
    device_type_entropies.append(device_type_metrics["Normalized Entropy"])

    # # 计算 device_name 的归一化熵
    # device_name_usage = count_lock_usage(group, DeviceName, "device_name")
    # device_name_metrics = calculate_lock_uniformity(device_name_usage)
    # device_name_entropies.append(device_name_metrics["Normalized Entropy"])

    # 计算 room 的归一化熵
    room_usage = count_lock_usage(group, Room, "room")
    room_metrics = calculate_lock_uniformity(room_usage)
    room_entropies.append(room_metrics["Normalized Entropy"])

    # 加载 device_type 和 device_name 平均时间
    device_type_file = os.path.join(base_path, f"device_type_lock_groups_{size}.txt")
    device_name_file = os.path.join(base_path, f"device_name_lock_groups_{size}.txt")
    room_file = os.path.join(base_path, f"room_lock_groups_{size}.txt")

    if os.path.exists(device_type_file):
        with open(device_type_file, "r") as f:
            values = [float(line.strip()) for line in f if line.strip()]
            device_type_times.append(np.mean(values))
    else:
        device_type_times.append(0)

    if os.path.exists(device_name_file):
        with open(device_name_file, "r") as f:
            values = [float(line.strip()) for line in f if line.strip()]
            device_name_times.append(np.mean(values))
    else:
        device_name_times.append(0)

    if os.path.exists(room_file):
        with open(room_file, "r") as f:
            values = [float(line.strip()) for line in f if line.strip()]
            room_times.append(np.mean(values))
    else:
        room_times.append(0)

# 绘制对比图
fig, ax1 = plt.subplots(figsize=(12, 6))

# 配置颜色
device_type_color = "red"
room_color = "purple"

# 归一化熵曲线
ax1.set_xlabel("Number of Rules", fontsize=12)
ax1.set_ylabel("Normalized Entropy", fontsize=12, color="tab:blue")
ax1.plot(group_sizes, device_type_entropies, marker="o", linestyle="-", color=device_type_color, label="Device Type Entropy")
ax1.plot(group_sizes, room_entropies, marker="s", linestyle="-", color=room_color, label="Room Entropy")
ax1.tick_params(axis="y", labelcolor="tab:blue")
ax1.grid(axis="x", linestyle="--", alpha=0.6)

# 平均时间曲线
ax2 = ax1.twinx()
ax2.set_ylabel("Average Time (s)", fontsize=12, color="tab:red")
ax2.plot(group_sizes, device_type_times, marker="^", linestyle="-.", color=device_type_color, label="Device Type Time")
ax2.plot(group_sizes, room_times, marker="d", linestyle="-.", color=room_color, label="Room Time")
ax2.tick_params(axis="y", labelcolor="tab:red")

# 图例统一放置
fig.legend(loc="upper left", fontsize=10, bbox_to_anchor=(0.1, 0.95))

# 图表标题和格式
plt.title("Comparison of Normalized Entropy and Average Time Across Lock Types", fontsize=14)
plt.tight_layout()
plt.show()

# 打印各 size 下的归一化熵
print("Size | DeviceType Entropy | Room Entropy")
for size, dt_entropy, r_entropy in zip(group_sizes, device_type_entropies, room_entropies):
    print(f"{size:<4} | {dt_entropy:<18.4f} | {r_entropy:<.4f}")

