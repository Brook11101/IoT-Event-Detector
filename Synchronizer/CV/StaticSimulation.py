import copy
import numpy as np
from Synchronizer.CV import RuleSet

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
    """随机给定设备分配一个新的状态索引"""
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

def runRules(office, Triggers, rules, id, log_file_path):
    """
    执行规则，生成静态日志，并写入日志文件
    """
    triggerId = {}
    epoch = 0
    logs = []
    time = int(office["time"])
    Actions = []
    actionId = {}

    rulesCountPerEpoch = []

    for i in range(len(Triggers)):
        triggerId[str(Triggers[i])] = 0

    while len(Triggers) != 0 and epoch < 10:
        potentialRules = findPotentialRules(Triggers, rules)
        # 随机打乱，不放回抽样
        potentialRules = np.random.choice(potentialRules, len(potentialRules), False)

        round_rule_count = len(potentialRules)
        rulesCountPerEpoch.append(round_rule_count)

        for rule in potentialRules:
            # 条件不满足，跳过执行
            if len(rule['Condition']) != 0 and (
                    (rule['Condition'][0] == 'time' and int(rule['Condition'][1]) != int(office["time"])) or office[
                rule['Condition'][0]] != rule['Condition'][1]):
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

    with open(log_file_path, "a", encoding="utf-8") as logfile:
        start_idx = 0
        for count in rulesCountPerEpoch:
            end_idx = start_idx + count
            for j in range(start_idx, end_idx):
                logfile.write(str(logs[j]) + "\n")
            logfile.write("\n")
            start_idx = end_idx

    return logs, id

def findPotentialRules(Triggers, rules):
    """用于筛选触发器 (Triggers) 里出现的 => 哪些规则可执行"""
    return [rule for rule in rules if rule["Trigger"] in Triggers]

def run_static_simulation(times=5, log_file_path=r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\CV\Data\static_logs.txt"):
    """
    运行规则模拟，生成静态日志
    :param times: 运行实验的次数
    :param log_file_path: 结果日志文件的路径
    """
    office = {
        "time": "000000",
        "temperature": 20,
        "humidity": 50,
        "illumination": 50,
        **{device: 0 for device in deviceStatus.keys()}  # 设备初始状态
    }

    rules = RuleSet.get_all_rules()

    # 初始化日志文件（清空）
    with open(log_file_path, "w", encoding="utf-8"):
        pass

    rule_id = 1

    for _ in range(times):
        print('随机改变场景')
        triggers = updateOfficeStatus(office)

        print('触发规则')
        logs, rule_id = runRules(office, triggers, rules, rule_id, log_file_path)

    print(f"=={rule_id} Simulation Done. Logs written to {log_file_path} ==")

    return rule_id

run_static_simulation()
