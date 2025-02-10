import copy
import numpy as np
from Synchronizer.CV import RuleSet

# 用于多次循环场景的次数
times = 1

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
    "AlexaVoiceAssistance": ["open", "close", "openhuelights", "closehuelights",
                             "openLamps", "openCutrain", "singsong", "alarm"],
    "PhilipsHueLight": ["open", "close"],
    "MideaAirConditioner": ["open", "close"],
    "NetatmoWeatherStation": ["open", "close", "windy", "rain", "sun", "unrain",
                              "AirPressureRises", "CarbonDioxideRise", "noise"],
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

def changeStatus(device):
    """
    随机给定设备分配一个新的状态索引
    """
    status_count = len(deviceStatus[device])
    return np.random.randint(0, status_count)

def updateOfficeStatus(office):
    """
    随机改变 office 内所有设备的状态，并返回实际发生改变的设备及其新状态列表。
    例如：[['MijiaCurtain1', 1], ['Smoke', 0], ...]
    """
    old_office = copy.copy(office)
    devices = list(deviceStatus.keys())

    for dev in devices:
        office[dev] = changeStatus(dev)

    ans = []
    for dev in office:
        if office[dev] != old_office[dev]:
            ans.append([dev, office[dev]])

    return ans

def runRules(office, Triggers, rules, id):
    # triggers = [[“time”：xx]， [“temxxx”：xx]]
    # [{id,status,time,rules, "triggerId", "actionIds", "ancestor"}]
    # 维护一个家庭状态， 维护一个Triggers 和 tirggerId,
    # 找到所有当前可能执行的规则，随机挑选执行，判断condition是否满足，如果不满足就是skipped，如果满足就修改office状态，把action加入到新的Triggers并给出triggerId。

    triggerId = {}
    epoch = 0
    logs = []
    time = int(office["time"])
    Actions = []
    actionId = {}
    logfile = open(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt", "a", encoding="utf-8")
    rulesCountPerEpoch = []


    for i in range(len(Triggers)):
        triggerId[str(Triggers[i])] = 0

    while len(Triggers) != 0 and epoch < 10:
        potentialRules = findPotentialRules(Triggers, rules)
        # 随机打乱，不放回抽样
        # potentialRules = np.random.choice(potentialRules, len(potentialRules), False)
        round_rule_count = len(potentialRules)
        rulesCountPerEpoch.append(round_rule_count)

        for rule in potentialRules:
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
                logs.append(temp)

                # 添加新的Action
                for item in rule["Action"]:
                    # 动作执行，修改房间状态
                    office[item[0]] = item[1]
                    Actions.append(item)
                    actionId[str(item)] = id
            id += 1

        Triggers = Actions
        triggerId = actionId
        Actions = []
        actionId = {}
        epoch += 1

    for log in logs:
        if log["ancestor"] == "":
            for i in range(len(logs)):
                if logs[i]["id"] == log["triggerId"]:
                    log["ancestor"] = logs[i]["ancestor"]


    start_idx = 0
    for idx, count in enumerate(rulesCountPerEpoch):
        end_idx = start_idx + count
        # 写这一轮
        for j in range(start_idx, end_idx):
            logfile.write(str(logs[j]) + "\n")

        # 轮次间插入空行
        logfile.write("\n")
        start_idx = end_idx

    logfile.close()
    return logs, id

def findPotentialRules(Triggers, rules):
    """
    用于筛选：触发器(Triggers)里出现的 => 哪些规则可执行
    """
    potential_rules = []
    for rule in rules:
        if rule["Trigger"] in Triggers:
            potential_rules.append(rule)
    return potential_rules


if __name__ == '__main__':
    # 初始场景
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

    rules = RuleSet.get_all_rules()

    # 初始化日志文件（清空）
    with open(r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt", "w", encoding="utf-8"):
        pass

    # 从 1 开始给规则分配ID
    rule_id = 1

    for _ in range(times):
        print('随机改变场景')
        triggers = updateOfficeStatus(office)

        print('触发规则')
        # 每轮会将新日志追加到 static_logs.txt
        logs, rule_id = runRules(office, triggers, rules, rule_id)

    print("== Simulation Done. Logs written to static_logs.txt. ==")
