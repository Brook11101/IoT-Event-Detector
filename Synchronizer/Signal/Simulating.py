import copy
import numpy as np

from Synchronizer.Signal import RuleSet

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

def runRules(office, triggers, rules, rule_id_start):
    """
    - 根据当前触发器 triggers 在所有规则中找到可执行的规则。
    - 随机顺序执行可执行规则，如果 condition 不满足则标记为 skipped，否则 run。
    - 修改 office 状态并记录日志到 execution_logs.txt。返回本次新增的 logs + 下一个可用 rule_id。
    """
    triggerIdMap = {}
    epoch = 0
    logs = []
    current_time = int(office["time"])
    actions_buffer = []
    actionIdMap = {}

    # 初始化 triggerIdMap
    for trig in triggers:
        triggerIdMap[str(trig)] = 0

    # 以追加模式写日志
    with open("execution_logs.txt", "a", encoding="utf-8") as logfile:
        # 在这里我们限制多轮触发次数，避免无限触发
        while triggers and epoch < 5:
            potential_rules = findPotentialRules(triggers, rules)
            # 随机打乱这些可能执行的规则
            potential_rules = np.random.choice(potential_rules, len(potential_rules), replace=False)

            for rule in potential_rules:
                # 如果有 condition，需要判断是否满足
                if rule['Condition']:
                    cond_dev, cond_state = rule['Condition'][0], rule['Condition'][1]
                    # time类型和普通设备状态做不同判断
                    if ((cond_dev == 'time' and int(cond_state) != current_time)
                        or (cond_dev != 'time' and office[cond_dev] != cond_state)):
                        # 条件不满足 => skipped
                        log_entry = makeLogEntry(
                            rule, rule_id_start, "skipped", current_time,
                            triggerIdMap.get(str(rule["Trigger"]), 0)
                        )
                        logs.append(log_entry)
                        logfile.write(str(log_entry)+"\n")
                        rule_id_start += 1
                        continue

                # 条件满足或无条件 => run
                log_entry = makeLogEntry(
                    rule, rule_id_start, "run", current_time,
                    triggerIdMap.get(str(rule["Trigger"]), 0)
                )
                logs.append(log_entry)
                logfile.write(str(log_entry)+"\n")

                # 执行动作
                for act in rule["Action"]:
                    office[act[0]] = act[1]
                    actions_buffer.append(act)
                    actionIdMap[str(act)] = rule_id_start

                rule_id_start += 1

            # 本轮执行完，把 actions_buffer 当做下一轮的 triggers
            triggers = actions_buffer
            triggerIdMap = actionIdMap
            actions_buffer = []
            actionIdMap = {}
            epoch += 1

        # 回填 ancestor 信息（仅在本批 logs 内做追溯）
        for log_item in logs:
            if log_item["ancestor"] == "":
                ancestor_id = log_item["triggerId"]
                for item in logs:
                    if item["id"] == ancestor_id:
                        log_item["ancestor"] = item["ancestor"]

    return logs, rule_id_start

def makeLogEntry(rule, cur_id, status, current_time, trigger_id):
    """
    生成一条日志字典，包含id、status、time、triggerId、ancestor等字段
    """
    temp = copy.copy(rule)
    temp["id"] = cur_id
    temp["status"] = status
    temp["time"] = current_time

    # 判断 triggerId 和 ancestor
    if trigger_id == 0:
        temp["triggerId"] = cur_id  # 说明是一个新触发
        temp["ancestor"] = cur_id
    else:
        temp["triggerId"] = trigger_id
        temp["ancestor"] = ""
    return temp

def findPotentialRules(triggers, rules):
    """
    从所有规则里选出 Trigger 在当前 triggers 里的规则
    """
    potential_rules = []
    for rule in rules:
        if rule["Trigger"] in triggers:
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
    with open("execution_logs.txt", "w", encoding="utf-8"):
        pass

    # 从 1 开始给规则分配ID
    rule_id = 1

    for _ in range(times):
        print('随机改变场景')
        triggers = updateOfficeStatus(office)

        print('触发规则')
        # 每轮会将新日志追加到 execution_logs.txt
        logs, rule_id = runRules(office, triggers, rules, rule_id)

    print("== Simulation Done. Logs written to execution_logs.txt. ==")
