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

deviceStatus = {
    "Smoke": ["unsmoke", "smoke"],
    "Location": ["home", "away"],
    "WaterLeakage": ["unleak", "leak"],
    "MijiaCurtain1": ["open", "close"],
    "MijiaCurtain2": ["open", "close"],
    "YeelightBulb": ["open", "close"],
    "SmartThingsDoorSensor": ["open", "close", "detect", "undetect"],
    "MijiaDoorLock": ["open", "close"],
    "RingDoorbell": ["open", "close", "ring"],
    "iRobotRoomba": ["open", "close", "dock"],
    "AlexaVoiceAssistance": ["open", "close", "openhuelights", "closehuelights", "openLamps", "openCutrain", "singsong",
                             "alarm"],
    "PhilipsHueLight": ["open", "close"],
    "MideaAirConditioner": ["open", "close"],
    "NetatmoWeatherStation": ["open", "close", "windy", "rain", "sun", "unrain", "AirPressureRises",
                              "CarbonDioxideRise", "noise"],
    "YeelightCeilingLamp1": ["open", "close"],
    "YeelightCeilingLamp2": ["open", "close"],
    "YeelightCeilingLamp3": ["open", "close"],
    "YeelightCeilingLamp5": ["open", "close"],
    "YeelightCeilingLamp6": ["open", "close"],
    "WemoSmartPlug": ["open", "close"],
    "WyzeCamera": ["open", "close", "detect", "alert", "disable", "enable", "COalarm"],
    "SmartLifePIRmotionsensor1": ["open", "close", "detect", "undetect"],
    "SmartLifePIRmotionsensor2": ["open", "close", "detect", "undetect"],
    "SmartLifePIRmotionsensor3": ["open", "close", "detect", "undetect"],
    "MijiaPurifier": ["open", "close"],
    "MijiaProjector": ["open", "close"],
    "Notification": ["notify"]
}

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

DeviceName = ["Smoke", "Location", "WaterLeakage", "MijiaCurtain1", "MijiaCurtain2", "YeelightBulb",
              "SmartThingsDoorSensor", "MijiaDoorLock", "RingDoorbell", "iRobotRoomba", "AlexaVoiceAssistance",
              "PhilipsHueLight", "MideaAirConditioner", "NetatmoWeatherStation", "YeelightCeilingLamp1",
              "YeelightCeilingLamp2", "YeelightCeilingLamp3", "YeelightCeilingLamp5", "YeelightCeilingLamp6",
              "WemoSmartPlug", "WyzeCamera", "SmartLifePIRmotionsensor1", "SmartLifePIRmotionsensor2",
              "SmartLifePIRmotionsensor3", "MijiaPurifier", "MijiaProjector", "Notification"]


# 带标签的规则生成函数
def add_lock_labels_to_rules(rules):
    labeled_rules = []
    for rule in rules:
        device_names = []
        # 将 Action 设备作为需要申请的锁
        for action in rule["Action"]:
            device_name = action[0]
            if device_name in device_type_mapping:
                device_names.append(device_name)

        # 去重，确保唯一性
        device_names = list(set(device_names))

        # 添加 TotalLock 标签，包括 Trigger 设备、Condition 设备和 Action 设备
        total_device_names = set(device_names)  # Start with Action devices

        # 提取 Trigger 设备名称
        if "Trigger" in rule:
            trigger_devices = rule["Trigger"][0]
            total_device_names.add(trigger_devices)

        # # 提取 Condition 设备名称
        # if "Condition" in rule:
        #     condition_devices = rule["Condition"][0]
        #     total_device_names.update(condition_devices)

        # Step 4: 添加 Lock 和 TotalLock 标签到规则
        labeled_rule = rule.copy()
        labeled_rule["Lock"] = device_names
        labeled_rule["TotalLock"] = list(total_device_names)  # TotalLock 标签包含所有相关设备
        labeled_rules.append(labeled_rule)

    return labeled_rules


# 为规则添加 RuleId
def add_ruleid_to_rules(rules):
    for index, rule in enumerate(rules, start=1):
        rule["RuleId"] = index
    return rules


def get_all_rules():
    return add_ruleid_to_rules(add_lock_labels_to_rules(ldm + whd + wzf + zxh + zyk))


def group_rules():
    """
    返回5组分好类的规则：group1, group2, group3, group4, group5
    每组均含有所有无冲突规则，以及若干有冲突规则 ID
    """

    # -----------------------
    # (1) 获取全部 100 条规则（已带 RuleId）
    # -----------------------
    all_rules = get_all_rules()
    all_rule_ids = {r['RuleId'] for r in all_rules}

    # -----------------------
    # (2) 写死的分组 ID (冲突规则部分)
    #
    #    这些 ID 来自于你手工挑选，用于构造
    #    group1 ~ group5 的递增冲突场景。
    # -----------------------
    G1_conflict_ids = {
        5, 9, 10, 11, 13, 22, 25, 27, 28, 29, 45, 46, 68, 84, 86, 94, 95
    }
    G2_new_add = {23, 24, 47, 50, 53, 54, 78, 79, 85, 93}
    G3_new_add = {36, 37, 38, 52, 56, 57, 60, 62, 64, 70, 76, 82, 98, 99}
    G4_new_add = {21, 39, 43, 44, 49, 61, 71, 72, 74, 81, 96, 97}
    G5_new_add = {20, 55, 59}  # 补齐其余剩下的冲突规则

    # -----------------------
    # (3) 我们假设冲突规则的全集(参与冲突)就是
    #     上述集合的并集(如果你已经检测好还有其他ID，可手动再加)
    # -----------------------
    conflict_involved_ids = set().union(
        G1_conflict_ids, G2_new_add, G3_new_add, G4_new_add, G5_new_add
    )

    # -----------------------
    # (4) “无冲突”规则 ID = 全部规则ID - 参与冲突的ID
    #     这些“无冲突”规则会被加到每个分组中，以模拟真实环境
    # -----------------------
    no_conflict_ids = all_rule_ids - conflict_involved_ids

    # -----------------------
    # (5) 构造最终分组 ID
    #     group1_conflict_set: G1
    #     group2_conflict_set: group1_conflict_set ∪ G2
    #     ...
    #     group5_conflict_set: group4_conflict_set ∪ G5
    # -----------------------
    group1_conflict_set = G1_conflict_ids
    group2_conflict_set = group1_conflict_set.union(G2_new_add)
    group3_conflict_set = group2_conflict_set.union(G3_new_add)
    group4_conflict_set = group3_conflict_set.union(G4_new_add)
    group5_conflict_set = group4_conflict_set.union(G5_new_add)

    # -----------------------
    # (6) 将每组的“冲突规则 ID” + “无冲突规则 ID” 转为规则对象
    # -----------------------
    def rules_by_ids(rules, ids_set):
        return [r for r in rules if r['RuleId'] in ids_set]

    group1 = rules_by_ids(all_rules, group1_conflict_set.union(no_conflict_ids))
    group2 = rules_by_ids(all_rules, group2_conflict_set.union(no_conflict_ids))
    group3 = rules_by_ids(all_rules, group3_conflict_set.union(no_conflict_ids))
    group4 = rules_by_ids(all_rules, group4_conflict_set.union(no_conflict_ids))
    group5 = rules_by_ids(all_rules, group5_conflict_set.union(no_conflict_ids))

    # 返回这5个分组列表
    return group1, group2, group3, group4, group5


def group_rules_conflict_only():
    """
    返回 5 组仅包含冲突规则的列表，每组只包含其对应的冲突 ID 集，
    不再添加无冲突规则。
    """
    all_rules = get_all_rules()

    G1_conflict_ids = {
        5, 9, 10, 11, 13, 22, 25, 27, 28, 29, 45, 46, 68, 84, 86, 94, 95
    }
    G2_new_add = {23, 24, 47, 50, 53, 54, 78, 79, 85, 93}
    G3_new_add = {36, 37, 38, 52, 56, 57, 60, 62, 64, 70, 76, 82, 98, 99}
    G4_new_add = {21, 39, 43, 44, 49, 61, 71, 72, 74, 81, 96, 97}
    G5_new_add = {20, 55, 59}

    group1_conflict_set = G1_conflict_ids
    group2_conflict_set = group1_conflict_set.union(G2_new_add)
    group3_conflict_set = group2_conflict_set.union(G3_new_add)
    group4_conflict_set = group3_conflict_set.union(G4_new_add)
    group5_conflict_set = group4_conflict_set.union(G5_new_add)

    def rules_by_ids(rules, ids_set):
        return [r for r in rules if r['RuleId'] in ids_set]

    group1 = rules_by_ids(all_rules, group1_conflict_set)
    group2 = rules_by_ids(all_rules, group2_conflict_set)
    group3 = rules_by_ids(all_rules, group3_conflict_set)
    group4 = rules_by_ids(all_rules, group4_conflict_set)
    group5 = rules_by_ids(all_rules, group5_conflict_set)

    return group1, group2, group3, group4, group5


# 获取分组
Group1, Group2, Group3, Group4, Group5 = group_rules_conflict_only()
