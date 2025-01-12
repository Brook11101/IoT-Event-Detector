import time
from time import sleep
import random
import redis
import threading
from ExecuteOrder import XiaomiCloudConnector


class RedisMutexLock:
    def __init__(self, client, lock_name):
        """
        初始化 Redis 可重入锁
        :param client: Redis 客户端连接对象
        :param lock_name: 锁的名称
        """
        self.client = client
        self.lock_name = lock_name

    def acquire(self):
        """
        获取锁，持续重试直到成功。
        """
        while True:
            if self.client.set(self.lock_name, "locked", nx=True):
                print(f"Thread {threading.get_ident()} acquired lock: {self.lock_name}")
                return True

    def release(self):
        """
        释放锁。
        """
        self.client.delete(self.lock_name)
        print(f"Thread {threading.get_ident()} released lock: {self.lock_name}")


def initLock():
    client = redis.StrictRedis(host="114.55.74.144", port=6379, password='whd123456', decode_responses=True)
    # 创建 Redis 可重入锁字典
    device_type_lock_dict = {}
    # 遍历 Home 数组，为每个元素创建一个锁，并存储到字典中
    for device_type_name in DeviceType:
        device_type_lock_dict[device_type_name] = RedisMutexLock(client, device_type_name)
    return device_type_lock_dict


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
Room = ["room1", "room2", "room3","room4","room5","room6"]
DeviceType = [
    "bulb",  # 灯具
    "sensor",  # 传感器
    "lock",  # 门锁
    "plug",  # 智能插头
    "appliance",  # 智能家电
    "camera",  # 摄像头
    "voice_assistance",  # 语音助手
    "curtain",  # 智能窗帘
    "notification",  # 通知设备
    "weather_station"  # 天气设备
]
DeviceName = ["Smoke", "Location", "WaterLeakage", "MijiaCurtain1", "MijiaCurtain2", "YeelightBulb",
              "SmartThingsDoorSensor", "MijiaDoorLock", "RingDoorbell", "iRobotRoomba", "AlexaVoiceAssistance",
              "PhilipsHueLight", "MideaAirConditioner", "NetatmoWeatherStation", "YeelightCeilingLamp1",
              "YeelightCeilingLamp2", "YeelightCeilingLamp3", "YeelightCeilingLamp5", "YeelightCeilingLamp6",
              "WemoSmartPlug", "WyzeCamera", "SmartLifePIRmotionsensor1", "SmartLifePIRmotionsensor2",
              "SmartLifePIRmotionsensor3", "MijiaPurifier", "MijiaProjector", "Notification"]


# 带标签的规则生成函数
def add_lock_labels_to_rules(rules):
    # 统计规则分配到的房间，用于均匀分配
    room_assignments = {room: 0 for room in Room}

    labeled_rules = []
    for rule in rules:
        # Step 1: Home 标签
        home_label = Home

        # Step 2: Room 标签 - 随机均匀分配
        room_label = min(room_assignments, key=room_assignments.get)
        room_assignments[room_label] += 1

        # Step 3: DeviceType 标签
        device_types = []
        device_names = []
        for action in rule["Action"]:
            device_name = action[0]
            if device_name in device_type_mapping:
                device_types.append(device_type_mapping[device_name])
                device_names.append(device_name)

        # 去重，确保唯一性
        device_types = list(set(device_types))
        device_names = list(set(device_names))

        # Step 4: 添加标签到规则
        labeled_rule = rule.copy()
        labeled_rule["Home"] = home_label
        labeled_rule["Room"] = [room_label]
        labeled_rule["DeviceType"] = device_types
        labeled_rule["DeviceName"] = device_names

        labeled_rules.append(labeled_rule)

    return labeled_rules


# 模拟规则执行的线程函数
def apply_lock(connector, rule, device_type_lock_dict, time_differences):
    # Step 1: 获取需要申请的锁并排序
    locks_to_acquire = sorted(rule["DeviceType"])  # 确保按字典序排序

    # Step 2: 开始计时
    start_time = time.time()

    # Step 3: 按顺序申请所有锁
    acquired_locks = []
    try:
        for lock_name in locks_to_acquire:
            device_type_lock_dict[lock_name].acquire()
            acquired_locks.append(lock_name)  # 记录已成功获取的锁

        # Step 4: 记录成功获取锁的时间
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Rule:  {rule['description']}    acquired all locks in {elapsed_time:.6f} seconds.")
        time_differences.append(elapsed_time)

        # 真实执行规则
        # value = str(random.randint(0, 100))
        # print(value)
        # response = connector.create_order("cn", value)
        # while True:
        #     status = connector.query_status("cn")
        #     print(status)
        #     status_dict = json.loads(status.decode('utf-8'))
        #     brightness = status_dict['result'][0]['value']
        #     if str(brightness) == str(value):  # 如果状态与发送的 value 一致
        #         print(f"Rule:  {rule['description']}   execute over.")
        #         break

        # 模拟执行规则占用时间
        sleep(random.uniform(1.5, 2.0))

    finally:
        # Step 5: 释放所有已获取的锁
        for lock_name in acquired_locks:
            device_type_lock_dict[lock_name].release()


# 多轮执行并保存结果
def execute_rules(connector, rounds, output_file):
    all_rules = ldm + whd + wzf + zxh + zyk
    labeled_rules = add_lock_labels_to_rules(all_rules)
    device_type_lock_dict = initLock()

    with open(output_file, "w") as file:
        for round_num in range(1, rounds + 1):
            time_differences = []
            threads = []

            for rule in labeled_rules:
                thread = threading.Thread(target=apply_lock,
                                          args=(connector, rule, device_type_lock_dict, time_differences))
                threads.append(thread)
                thread.start()

            for thread in threads:
                thread.join()

            avg_time = sum(time_differences) / len(time_differences) if time_differences else 0
            file.write(f"Round {round_num}: Average time to acquire locks: {avg_time:.6f} seconds\n")
            print(f"Round {round_num} completed. Average time: {avg_time:.6f} seconds.")


# 多轮执行并记录结果
def execute_rules_for_groups(connector, rule_groups, rounds, base_output_dir):
    device_type_lock_dict = initLock()
    for group_idx, rules in enumerate(rule_groups):
        group_size = len(rules)
        output_file = f"{base_output_dir}/device_type_lock_groups_{group_size}.txt"

        with open(output_file, "w") as file:
            for round_num in range(1, rounds + 1):
                time_differences = []
                threads = []

                for rule in rules:
                    thread = threading.Thread(target=apply_lock,
                                              args=(connector, rule, device_type_lock_dict, time_differences))
                    threads.append(thread)
                    thread.start()

                print(f"当前的活动线程数量: {threading.active_count()}")

                for thread in threads:
                    thread.join()

                avg_time = sum(time_differences) / len(time_differences) if time_differences else 0
                file.write(f"{avg_time:.6f}\n")
                print(
                    f"Group {group_idx + 1} - Size {group_size} - Round {round_num} completed. Average time: {avg_time:.6f} seconds.")


if __name__ == "__main__":
    all_rules = ldm + whd + wzf + zxh + zyk
    labeled_rules = add_lock_labels_to_rules(all_rules)
    random.seed(32)

    rule_groups = [
        random.sample(labeled_rules, 5),
        random.sample(labeled_rules, 10),
        random.sample(labeled_rules, 15),
        random.sample(labeled_rules, 20),
        random.sample(labeled_rules, 25),
        random.sample(labeled_rules, 30),
        random.sample(labeled_rules, 35),
        random.sample(labeled_rules, 40),
        random.sample(labeled_rules, 45),
        random.sample(labeled_rules, 50),
        random.sample(labeled_rules, 60),
        random.sample(labeled_rules, 80),
        labeled_rules  # 全部规则
    ]

    rounds = 20
    output_base_dir = r"E:\\研究生信息收集\\论文材料\\IoT-Event-Detector\\Detector\\Mutex\\Atomicity\\MiJia\\Unit\\Data"

    username = "2844532281"
    password = "whd123456"

    connector = XiaomiCloudConnector(username, password)
    print("Logging in...")
    logged = connector.login()
    if logged:
        print("Login successful.")
        execute_rules_for_groups(connector, rule_groups, rounds, output_base_dir)
    else:
        print("Unable to log in.")
