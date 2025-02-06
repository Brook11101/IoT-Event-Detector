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
    "AlexaVoiceAssistance": ["open", "close","openhuelights","closehuelights",
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
    - 根据当前触发器 triggers 在所有规则中找到可能执行的规则。
    - 随机顺序执行可执行规则，如果 condition 不满足则标记为 skipped，否则 run。
    - 修改 office 状态并记录日志。返回本轮执行的日志数组 logs 和下一个可用 rule_id。
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

    with open("execution_logs.txt", "a", encoding="utf-8") as logfile:
        while triggers and epoch < 1:
            potential_rules = findPotentialRules(triggers, rules)
            # 随机打乱这些可能执行的规则
            potential_rules = np.random.choice(potential_rules, len(potential_rules), replace=False)

            for rule in potential_rules:
                # 如果有 condition，需要判断是否满足
                if rule['Condition']:
                    cond_dev, cond_state = rule['Condition'][0], rule['Condition'][1]
                    # time类型和普通设备状态做不同判断
                    if (
                        (cond_dev == 'time' and int(cond_state) != current_time)
                        or (cond_dev != 'time' and office[cond_dev] != cond_state)
                    ):
                        # 条件不满足
                        log_entry = makeLogEntry(
                            rule, rule_id_start, "skipped", current_time,
                            triggerIdMap.get(str(rule["Trigger"]), 0)
                        )
                        logs.append(log_entry)
                        logfile.write(str(log_entry)+"\n")
                        rule_id_start += 1
                        continue
                # 如果走到这里，说明条件满足或没有条件 => run
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

        # 回填 ancestor 信息
        for log_item in logs:
            if log_item["ancestor"] == "":
                # 根据其 triggerId 找到祖先
                ancestor_id = log_item["triggerId"]
                # 在 logs 里找到那条id==ancestor_id的记录，再把那条记录的 ancestor 填给自己
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

def detector(logs):
    """
    检测并统计各种冲突/现象：
    1. Action Loop
    2. Action Repetition
    3. Action Revert
    4. Action Conflict
    5. unexpected Conflict
    6. Condition Bypass
    7. Condition Pass
    8. Condition Block
    9. Condition Contradictory
    """

    ActionLoopNum = 0
    ActionRepetitionNum = 0
    ActionRevertNum = 0
    ActionConflictNum = 0
    unexpectedConflictNum = 0
    ConditionBypassNum = 0
    ConditionPassNum = 0
    ConditionBlockNum = 0
    ConditionContradictoryNum = 0

    with open("race_condition.txt", "a", encoding="utf-8") as rc_file:
        for i in range(len(logs)):
            LatterActions = logs[i]["Action"]

            # === 如果当前规则是 skipped 的 ===
            if logs[i]['status'] == 'skipped':
                # Condition Bypass：skipped的规则，前后有没有相同的Action
                for j in range(i-1, -1, -1):
                    formerActions = logs[j]["Action"]
                    for LatterAct in LatterActions:
                        if LatterAct in formerActions:
                            ConditionBypassNum += 1
                            # rc_file.write("Condition Bypass\n")
                            # rc_file.write(str(logs[j]) + "\n")
                            # rc_file.write(str(logs[i]) + "\n\n")
                for j in range(i+1, len(logs)):
                    formerActions = logs[j]["Action"]
                    for LatterAct in LatterActions:
                        if LatterAct in formerActions:
                            ConditionBypassNum += 1
                            # rc_file.write("Condition Bypass\n")
                            # rc_file.write(str(logs[j]) + "\n")
                            # rc_file.write(str(logs[i]) + "\n\n")

                # Condition Block：(示例中只判断单条件)
                if logs[i]['Condition']:
                    for j in range(i - 1, -1, -1):
                        formerActions = logs[j]["Action"]
                        cond_dev, _ = logs[i]['Condition'][0], logs[i]['Condition'][1]
                        for former in formerActions:
                            if cond_dev == former[0]:
                                ConditionBlockNum += 1
                                rc_file.write("Condition Block\n")
                                rc_file.write(str(logs[j]) + "\n")
                                rc_file.write(str(logs[i]) + "\n\n")

            # === 如果当前规则是 run 的 ===
            else:
                # 从后往前找同链/同祖宗等信息
                front_id = logs[i]["triggerId"]
                for j in range(i-1, -1, -1):
                    formerActions = logs[j]["Action"]

                    for LatterAct in LatterActions:
                        # Action Loop: 前面是否有相同的 Action，且在一条链上 (id == front_id)
                        if LatterAct in formerActions and logs[j]["id"] == front_id:
                            ActionLoopNum += 1
                            # rc_file.write("Action Loop\n")
                            # rc_file.write(str(logs[j]) + "\n")
                            # rc_file.write(str(logs[i]) +"\n\n")

                        # Action Repetition: 前面是否有相同的 Action，且在一个祖宗上
                        elif LatterAct in formerActions and logs[j]["ancestor"] == logs[i]["ancestor"]:
                            ActionRepetitionNum += 1
                            # rc_file.write("Action Repetition\n")
                            # rc_file.write(str(logs[j]) + "\n")
                            # rc_file.write(str(logs[i]) + "\n\n")
                        else:
                            # 遍历 formerActions 判断是否同设备不同状态
                            for formerAct in formerActions:
                                # Action Revert: 相同设备 & 不同状态 & 在一条链上
                                if (LatterAct[0] == formerAct[0]
                                    and logs[j]["id"] == front_id
                                    and LatterAct[1] != formerAct[1]):
                                    ActionRevertNum += 1
                                    # rc_file.write("Action Revert\n")
                                    # rc_file.write(str(logs[j]) + "\n")
                                    # rc_file.write(str(logs[i]) + "\n\n")

                                # Action Conflict: 相同设备 & 不同状态 & 在同一祖宗上
                                elif (LatterAct[0] == formerAct[0]
                                      and logs[j]["ancestor"] == logs[i]["ancestor"]
                                      and LatterAct[1] != formerAct[1]):
                                    ActionConflictNum += 1
                                    rc_file.write("Action Conflict\n")
                                    rc_file.write(str(logs[j]) + "\n")
                                    rc_file.write(str(logs[i]) + "\n\n")

                                # unexpected Conflict: 相同设备 & 不同状态 & 不在同一个祖宗
                                elif (LatterAct[0] == formerAct[0]
                                      and LatterAct[1] != formerAct[1]
                                      and logs[j]["ancestor"] != logs[i]["ancestor"]):
                                    unexpectedConflictNum += 1
                                    rc_file.write("unexpected Conflict\n")
                                    rc_file.write(str(logs[j]) + "\n")
                                    rc_file.write(str(logs[i]) + "\n\n")

                    # Condition Contradictory:
                    # 如果当前 rule 和之前 rule 的 condition 是同设备但状态相反，即互斥
                    if (logs[i].get('Condition')
                        and logs[j].get('Condition')
                        and len(logs[i]['Condition']) == 2
                        and len(logs[j]['Condition']) == 2):
                        if (logs[i]['Condition'][0] == logs[j]['Condition'][0]
                            and logs[i]['Condition'][1] != logs[j]['Condition'][1]):
                            ConditionContradictoryNum += 1
                            # rc_file.write("Condition Contradictory\n")
                            # rc_file.write(str(logs[j]) + "\n")
                            # rc_file.write(str(logs[i]) + "\n\n")

                    # 更新前置链条: 把 j 条 rule 的 triggerId 继续往上追溯
                    if logs[j]["id"] == front_id:
                        front_id = logs[j]["triggerId"]

                # Condition Pass: 如果当前 rule 有 condition,
                # 检查前面有没有修改该条件的动作(或满足其动作).
                if logs[i]['Condition']:
                    cond_dev, cond_state = logs[i]['Condition'][0], logs[i]['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        formerActions = logs[j]["Action"]
                        if [cond_dev, cond_state] in formerActions:
                            ConditionPassNum += 1
                            rc_file.write("Condition Pass\n")
                            rc_file.write(str(logs[j]) + "\n")
                            rc_file.write(str(logs[i]) + "\n\n")

    return (ActionConflictNum, unexpectedConflictNum, ConditionPassNum, ConditionBlockNum)

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
    with open("race_condition.txt", "w", encoding="utf-8"):
        pass

    # 累加各类冲突检测数量
    total_AC = total_uC = 0
    total_CP = 0
    total_CB_b = 0

    rule_id = 1

    for _ in range(times):
        print('随机改变场景')
        triggers = updateOfficeStatus(office)

        print('触发规则')
        logs, rule_id = runRules(office, triggers, rules, rule_id)

        print('冲突检查')
        (
            ActionConflictNum,
            unexpectedConflictNum,
            ConditionPassNum,
            ConditionBlockNum,
        ) = detector(logs)

        # 累加
        total_AC += ActionConflictNum
        total_uC += unexpectedConflictNum
        total_CP += ConditionPassNum
        total_CB_b += ConditionBlockNum

    # 打印最终的检测统计
    print("=== 检测结果统计 ===")
    print(f"Action Conflict: {total_AC}")
    print(f"unexpected Conflict: {total_uC}")
    print(f"Condition Pass: {total_CP}")
    print(f"Condition Block: {total_CB_b}")
