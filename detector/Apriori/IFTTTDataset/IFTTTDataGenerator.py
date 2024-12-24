import copy
from detector.Apriori import Apriori
from numpy.random import seed
from numpy.random import randint
import numpy as np
import configparser


numOfUser = 10
# numOfDevice = 20/30/40/50
numOfDevice = 50
npyPath = "../../Datasets/IFTTTDataset/"+str(numOfDevice)+"/0/npy/"
devicePath = npyPath + "randomDeviceList.npy"
times = 40
Records = str(numOfDevice)+  "IFTTTRecords.txt"
TriggerRecords = str(numOfDevice)+"IFTTTTriggerRecords.txt"
ActionRecords = str(numOfDevice)+"IFTTTActionRecords.txt"
ACCFile = str(numOfDevice)+"IFTTTACC.txt"
all_rules = []


def setDeviceStatus(devicesList):
    deviceStatus = {}
    for device in devicesList:
        deviceStatus[device] = []
        path = "../../Datasets/TA_Popular/" + device + "/Trigger.csv"
        file = open(path, "r", encoding='utf-8')
        lines = file.readlines()
        for line in lines:
            line = line.split(',')
            if line[0] == 'trigger' or line[1] == 'trigger_description':
                continue
            deviceStatus[device].append(line[0])
        file.close()
    return deviceStatus


# 基于第一步得到的device status列表，为房间中所有设备生成初始状态
def setOffice(devicesList, devicesStatus):
    office = {"time": "000000"}
    for device in devicesList:
        if len(devicesStatus[device]) != 0:
            office[device] = np.random.choice(devicesStatus[device], 1)[0]
        else:
            office[device] = ''
    return office

def getDeviceStatus(deviceList):
    # statusMap用于分析设备action动作与trigger的关联，判断某个动作执行后哪些规则会被触发，key是action，value是trigger
    triggerStatus = {}
    actionStatus = {}
    statusMap = {}
    for device in devicesList:
        path = "../../Datasets/TA_Popular/" + str(device) + "/"
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

        # statusMap内层字典是动作与触发状态的组合
        tmp = {}
        if len(p_default) != 0:
            for item in p_default:
                tmp[actionStatus[device][item[0] - 2]] = []
                for i in range(1, len(item)):
                    tmp[actionStatus[device][item[0] - 2]].append(triggerStatus[device][item[i] - 2])
        statusMap[device] = tmp
    return triggerStatus, actionStatus, statusMap

# 基于DeviceList得到的statusMap，将文件中的规则转换成可用的字典形式
def setRules(statusMap):

    # {"score": 4, "Trigger": ["MijiaDoorLock", 0], "Condition": [],
    #     #  "Action": [["YeelightCeilingLamp1", 0], ["YeelightCeilingLamp2", 0], ["YeelightCeilingLamp3", 0],
    #     #             ["YeelightCeilingLamp5", 0], ["YeelightCeilingLamp6", 0]],
    #     #  "description": "if door opened(5), open the lamps(12,13,14,15,16)", "triggerType": 3, "user":"ldm"}

    # applet_name, applet_description, applet_Trigger, applet_Action, applet_TD, applet_AD, applet_number

    rules = []

    for user in range(numOfUser):
        path = npyPath + "/randomRulesList" + str(user) + ".npy"
        ruleList = np.load(path)
        for item in ruleList:
            rule = {}
            rule["score"] = np.random.randint(6, size=1)[0]
            rule["Trigger"] = [item[4], item[2]]
            rule["Condition"] = []
            if item[3] in statusMap[item[5]].keys():
                rule["Action"] = []
                # 提取该action对应的所有trigger，在statusMap中
                for tmp in statusMap[item[5]][item[3]]:
                  rule["Action"].append([item[5], tmp])
            else:
                rule["Action"] = [[item[5], item[3]]]

            rule["description"] = item[1]
            rule["triggerType"] = 0
            rule["user"] = user
            rules.append(rule)
    #       最终这样做的目的就是将一个规则的action直接转化成其他可能的规则的trigger（action设备上的状态切换），trigger-action-trigger的形式
    #       由action到trigger的转化是由statusMap建立的映射来实现的
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

def updateOfficeStatus(office, devicesStatus):
    old_office = copy.copy(office)

    office["time"] = changeTime(office["time"])

    devices = list(devicesStatus.keys())
    for device in devices:
        if len(devicesStatus[device]) != 0:
            # 随机扰动设备状态
            # Trigger设备状态发生了变化
            office[device] = np.random.choice(devicesStatus[device], 1)[0]
        else:
            office[device] = ''

    ans = []
    for item in list(office.keys()):
        # 判断设备状态是否发生了不一致，认为规则被触发
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

# rules乱序执行生成历史记录，这里模拟大量规则随机执行并生成执行记录可能对我有用，相当于设定了逻辑上的执行规则
def mergeRules(rules):
    rulesNum = len(rules)
    indexs = []
    ans = []

    for i in range(rulesNum):
        indexs.append(i)

    # 生成规则所有的执行记录。乱序选择规则，然后把规则的动作执行完
    while len(indexs) != 0:
        index = np.random.choice(indexs)
        if len(rules[index]) == 0:
            indexs.remove(index)
            continue
        else:
            # 因此，取的是rules[index][0]，取开头的即可
            ans.append(rules[index][0])
            # 通过这样的方式把一条规则打散了，抽取成trigger、description、action的部分依次加入。中间为1的是description
            # description分隔了trigger和action（虽然action也是trigger）
            rules[index].pop(0)
    return ans

def create_records(rules, office, devicesStatus):
    file = open(Records, "w", encoding='utf-8')
    Triggers = updateOfficeStatus(office, devicesStatus)
    potientialRules = findPotientialRules(Triggers, rules)
    # 找到了要执行的规则
    exectionRules = potientialRules
    # 用随机数把规则进行乱序执行
    mergeArray = mergeRules(exectionRules)
    file.write(str(mergeArray) +"\n")
    # 把当前一轮一次执行的规则都记录下来
    return mergeArray

# 由历史记录生成trigger_record和action_record，从而用于后续Apriori推理
# 是基于mergeArrays进行records抽取的，因此规则执行的次数越多，得到的rule record越多，抽出的trigger/action records也越多，推理的更加准确
def create_tables(mergeArrays):
    # 在mergeArays里面，这个字典每一个key对应的字典里面，每一轮记录是一个执行规则trigger、description、action打散后的结果
    trigger_records = []
    action_records = []

    # get trigger_records

    # 这里处理的是每一轮的执行，生成其trigger/action records，并全部汇总
    for record in mergeArrays:
        temp_trigger = []
        for item in record:
            # 遇到1的标志说明遇到了description
            if item[1] == 1:
                temp = copy.copy(temp_trigger)
                temp.append(str(item[0])+","+str(item[1]))
                # 原理就是在这个规则description之前，即代表规则执行前，收到的所有trigger都可能是导致该规则触发的trigger
                # 相当于给每一个规则把之前触发的trigger都记录下来了，用于匹配
                trigger_records.append(temp)
            else:
                temp_trigger.append(str(item[0])+","+str(item[1]))

    # get action_records
    for record in mergeArrays:
        temp_action = []
        # 因为action在后，所以要进行reverse，拿到的首先是action
        for item in reversed(record):
            # 遇到1的标志说明遇到了description
            if item[1] == 1 :
                temp = copy.copy(temp_action)
                temp.append(str(item[0])+","+str(item[1]))
                # 记录下该规则发生前的所有action的record
                action_records.append(temp)
            else:
                temp_action.append(str(item[0])+","+str(item[1]))
    #    这种trigger和action的记录相当于是重复记录，trigger_records和action_records的每一个item都包含了重复项
    with open(TriggerRecords,"w", encoding="utf-8") as f:
        f.write(str(trigger_records))

    with open(ActionRecords, "w", encoding="utf-8") as f:
        f.write(str(action_records))
    return trigger_records,action_records

# 获取rule对应的记录
def getSubRecord(rule, trigger_records):
    ans = []
    # 根据规则去找到所有的trigger records
    for item in trigger_records:
        if item[-1] == rule:
            ans.append(item)
    return ans

if __name__ == "__main__":


    devicesList = np.load(devicePath)
    devicesStatus = setDeviceStatus(devicesList)
    office = setOffice(devicesList, devicesStatus)
    triggerStatus, actionStatus, statusMap = getDeviceStatus(devicesList)
    rules = setRules(statusMap)

    rules_new = []
    for rule in rules:
        rules_new.append([[rule['Trigger'], 0], [rule['description'], 1], [rule['Action'], 0]])
    rules = rules_new
    # print(rules)

    accfile = open(ACCFile, "w", encoding="utf-8")

    mergeArrays = []
    accuracy = 0
    for i in range(times):
        mergeArray = create_records(rules, office, devicesStatus)
        mergeArrays.append(mergeArray)
        trigger_records, action_records = create_tables(mergeArrays)
        num_true = 0
        for item in rules:
            trigger = str(item[0][0]) + "," + str(item[0][1])
            rule = str(item[1][0]) + "," + str(item[1][1])
            action = str(item[2][0]) + "," + str(item[2][1])
            #   # 假设我们想找'100,0'这个规则的trigger
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
            # if trigger_flag==1 & action_flag ==1:
            #     print(rule)
        accuracy = num_true / (2 * len(rules))
        print(accuracy)
        accfile.write(str(accuracy) + "\n")

    accfile.close()
