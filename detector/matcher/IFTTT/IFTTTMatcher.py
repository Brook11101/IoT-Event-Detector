import configparser
import copy
import logging
import os
import json
import numpy as np

devices = 20
cyctime = 8
epoch = 1500

users = 5
rules = 20
npyPath = "./"+str(devices)+"/" +str(cyctime) + "/npy/"
devicePath = npyPath + "randomDeviceList.npy"
# rulePath = "./resources/Rules/"

conflict_path = "conflicts_IFTTT"+str(devices)+"_"+str(cyctime)+"_"+str(epoch)+".csv"

def changeTime(time):
    time = int(time)
    hour = int(time/10000)
    time = time%10000
    minute = int(time/100)
    time = time%100
    second = time
    minute += 5
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


def updateOfficeStatus(office, devicesStatus):
    old_office = copy.copy(office)

    office["time"] = changeTime(office["time"] )

    devices = list(devicesStatus.keys())
    for device in devices:
        if len(devicesStatus[device]) != 0:
            office[device] = np.random.choice(devicesStatus[device], 1)[0]
        else:
            office[device] = ''

    ans = []
    for item in list(office.keys()):
        if office[item] != old_office[item]:
            ans.append([item, office[item]])
    return ans






def getDeviceStatus(deviceList):
    triggerStatus = {}
    actionStatus = {}
    statusMap = {}
    for device in devicesList:
        path = "./resources/TA_Popular/"+str(device)+"/"
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
                tmp[actionStatus[device][item[0]-2]] = []
                for i in range(1, len(item)):
                    tmp[actionStatus[device][item[0]-2]].append(triggerStatus[device][item[i]-2])



        statusMap[device] = tmp


    return triggerStatus, actionStatus, statusMap



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

    while len(Triggers) != 0 and eporch < 10:
        potientialRules = findPotientialRules(Triggers, rules)
        potientialRules = np.random.choice(potientialRules, len(potientialRules), False)

        for rule in potientialRules:
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
                    office[item[0]] = item[1]
                    Actions.append(item)
                    actionId[str(item)] = id

            id += 1
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

def findPotientialRules(Triggers, rules):
    potientialRules = []
    for rule in rules:
        if rule["Trigger"] in Triggers:
            potientialRules.append(rule)
    return potientialRules

def TriggerToNum(device, Trigger, devicesStatus):
    list = devicesStatus[device]
    for i in range(len(list)):
        if Trigger == list[i]:
            return i
    return len(list)


def ConflictsToFile(office, devicesStatus, conflict, type):
    with open(conflict_path, "a", encoding='utf-8') as f:
        # 环境
        office_data = ""
        office_keys = list(office.keys())
        for key in office_keys:
            if key == "time" :
                office_data += str(office[key])+","
            else:
                office_data += str(TriggerToNum(key, office[key], devicesStatus))+","

        # user1, user2
        user_data = str(conflict[0]['user']) + "," + str(conflict[1]['user']) + ","

        # 规则：triggerMode,formerTriggerType,latterTriggerType,formerDescription,latterDescription,

        conflict[0]["description"] = conflict[0]["description"].replace(",", ".")
        conflict[1]["description"] = conflict[1]["description"].replace(",", ".")
        conflict[0]["description"] = conflict[0]["description"].replace("\n", "")
        conflict[1]["description"] = conflict[1]["description"].replace("\n", "")

        data = ""
        data += str(conflict[0]["description"]) + ","
        data += str(conflict[1]["description"]) + ","

        # exection,score1,score2
        exection_data = ""
        if conflict[0]["score"] > conflict[1]["score"]:
            exection_data += str(0)
        elif conflict[0]["score"]<conflict[1]["score"]:
            exection_data += str(1)
        else:
            exection_data += str(1)

        exection_data += "\n"

        f.write(office_data+data+type+","+user_data+exection_data)

def detector(logs, office, devicesStatus):

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
                            # ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "Condition Bypass")
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
                            ConflictsToFile(office, devicesStatus, [logs[i], logs[j]], "Condition Bypass")
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
                                ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "Condition Block")

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
                                    ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "Action Conflict")
                            # unexpected Conflict:相同的设备的Action，不同的status，不在同一个祖宗上
                            elif Latter[0] == former[0] and Latter[1] != former[1] :
                                unexpectedConflictNum += 1
                                if logs[i]['user'] != logs[j]['user']:
                                    UsersunexpectedConflictNum += 1
                                    criFile.write("unexpected Conflict\n")
                                    criFile.write(str(logs[j]) + "\n")
                                    criFile.write(str(logs[i]) + "\n\n")
                                    ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "unexpected Conflict")
                # Condition Contradictory：没有，在用户构建的规则中，没有能够导致condition Contradictory的规则。如果有，那就是If door(4) is open, when curtain(1) or curtain(2) is closed, open the Yeelight Bulb(3) ，和If door(4) is open, when curtain(1) or curtain(2) is opened, open the xxx。
                if len(logs[i]['Condition']) != 0 and len(logs[j]["Condition"]) != 0 and logs[i]['Condition'][0] ==logs[j]['Condition'][0] \
                        and logs[i]['Condition'][1] !=logs[j]['Condition'][1] :
                    ConditionContradictoryNum += 1
                    if logs[i]['user'] != logs[j]['user']:
                        UsersConditionContradictoryNum += 1
                        criFile.write("Condition Contradictory\n")
                        criFile.write(str(logs[j]) + "\n")
                        criFile.write(str(logs[i]) + "\n\n")
                        ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "Condition Contradictory")

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
                            ConflictsToFile(office, devicesStatus, [logs[j], logs[i]], "Conditon Pass")


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

def setOffice(devicesList, devicesStatus):
    # office = {
    #     "MijiaCurtain1": 0,
    #     "MijiaCurtain2": 0,
    #     "YeelightBulb": 0,
    #     "SmartThingsDoorSensor": 0,
    #     "MijiaDoorLock": 0,
    #     "RingDoorbell": 0,
    #     "iRobotRoomba": 0,
    #     "AlexaVoiceAssistance": 0,
    #     "PhilipsHueLight": 0,
    #     "MideaAirConditioner": 0,
    #     "NetatmoWeatherStation": 0,
    #     "YeelightCeilingLamp1": 0,
    #     "YeelightCeilingLamp2": 0,
    #     "YeelightCeilingLamp3": 0,
    #     "YeelightCeilingLamp5": 0,
    #     "YeelightCeilingLamp6": 0,
    #     "WemoSmartPlug": 0,
    #     "WyzeCamera": 0,
    #     "SmartLifePIRmotionsensor1": 0,
    #     "SmartLifePIRmotionsensor2": 0,
    #     "SmartLifePIRmotionsensor3": 0,
    #     "MijiaPurifier": 0,
    #     "MijiaProjector": 0,
    #     "Notification": 0,
    # }
    office = {"time": "000000"}
    for device in devicesList:
        if len(devicesStatus[device]) != 0:
            office[device] = np.random.choice(devicesStatus[device], 1)[0]
        else:
            office[device] = ''
    return office

def setRules(statusMap):

    # {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
    #     #  "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
    #     #             ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
    #     #  "description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3, "user":"ldm"}

    # applet_name, applet_description, applet_Trigger, applet_Action, applet_TD, applet_AD, applet_number

    rules = []

    for user in range(users):
        path = npyPath + "/randomRulesList"+ str(user) +".npy"
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

def setDeviceStatus(devicesList):
    # deviceStatus = {
    #     "Smoke": ["unsmoke", "smoke"],
    #     "Location": ["home", "away"]}
    # Action---Trigger
    # 在Rule端要把Action的内容换成一个或者多个Trigger，随机化Trigger；如果Action中没有对应的Trigger，把第二个数字设置为一个较大的数
    # deviceStatus中放Trigger。
    #
    deviceStatus = {}
    for device in devicesList:
        deviceStatus[device] = []
        path = "./resources/TA_Popular/"+device +"/Trigger.csv"
        file = open(path, "r", encoding='utf-8')
        lines = file.readlines()
        for line in lines:
            line = line.split(',')
            if line[0] == 'trigger' or line[1] == 'trigger_description':
                continue
            deviceStatus[device].append(line[0])
        file.close()
    return deviceStatus

if __name__ == '__main__':

    devicesList = np.load(devicePath)
    devicesStatus = setDeviceStatus(devicesList)
    office = setOffice(devicesList, devicesStatus)
    triggerStatus, actionStatus, statusMap = getDeviceStatus(devicesList)
    rules = setRules(statusMap)

    # 初始化文件
    logfile = open("logs.txt", "w", encoding="utf-8")
    logfile.close()
    criFile = open("CRIs.txt", "w", encoding="utf-8")
    criFile.close()
    conflictFile = open(conflict_path, "w", encoding='utf-8')
    conflictFile.close()


    id = 1
    ALNum, ARnNum, ARtNum, ACNum, uCNum, CBsNum, CPNum, CBkNum, CCNum = 0, 0, 0, 0, 0, 0, 0, 0, 0
    UALNum, UARnNum, UARtNum, UACNum, UuCNum, UCBsNum, UCPNum, UCBkNum, UCCNum = 0, 0, 0, 0, 0, 0, 0, 0, 0
    for i in range(epoch):

        Triggers = updateOfficeStatus(office, devicesStatus)

        logs, id = runRules(office, Triggers, rules, id)

        ActionLoopNum, ActionRepetitionNum, ActionRevertNum, ActionConflictNum, unexpectedConflictNum, ConditionBypassNum, \
        ConditionPassNum, ConditionBlockNum, ConditionContradictoryNum, UsersActionLoopNum, UsersActionRepetitionNum, \
        UsersActionRevertNum, UsersActionConflictNum, UsersunexpectedConflictNum, UsersConditionBypassNum, UsersConditionPassNum, \
        UsersConditionBlockNum, UsersConditionContradictoryNum = detector(logs, office, devicesStatus)

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

        print(ALNum, ARnNum, ARtNum, ACNum, uCNum, CBsNum, CPNum, CBkNum, CCNum)
        # print(UALNum, UARnNum, UARtNum, UACNum, UuCNum, UCBsNum, UCPNum, UCBkNum, UCCNum)
        # print(ALNum)
        # print(ARnNum)
        # print(ARtNum)
        # print(ACNum)
        # print(uCNum)
        # print(CBsNum)
        # print(CPNum)
        # print(CBkNum)
        # print(CCNum)






