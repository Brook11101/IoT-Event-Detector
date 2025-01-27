import RuleSet


def find_rule_conflicts(rules):
    """
    检查规则集中的规则是否存在冲突，并返回一个字典，记录每个规则的冲突规则。
    """
    conflicts = {}  # 最终存储冲突对的字典

    # 遍历规则集中的每一条规则
    for current_rule in rules:
        current_rule_id = current_rule['RuleId']
        trigger_and_condition_status = {}

        # 创建状态映射（statusMap），记录当前规则所有 Trigger 和 Condition 的设备及其状态
        # 1. Trigger 设备状态映射
        if "Trigger" in current_rule:
            trigger_device = current_rule["Trigger"][0]
            trigger_state = current_rule["Trigger"][1]
            trigger_and_condition_status[trigger_device] = trigger_state

        # 2. Condition 设备状态映射
        if "Condition" in current_rule and current_rule["Condition"]:
            condition_device = current_rule["Condition"][0]
            condition_state = current_rule["Condition"][1]
            trigger_and_condition_status[condition_device] = condition_state

        # 遍历其他规则，判断它们的 Action 设备是否与当前规则的 Trigger 或 Condition 设备冲突
        for other_rule in rules:
            other_rule_id = other_rule['RuleId']
            # 忽略小于id的规则，这些规则本来就是先启动的
            if other_rule_id <= current_rule_id:  # 忽略与自己冲突的情况
                continue

            # 检查其他晚于自己启动的规则的 Action 设备，是否会影响到自己的触发条件
            for action in other_rule["Action"]:
                action_device = action[0]
                # 如果其他规则的 Action 设备在当前规则的 Trigger 或 Condition 中，并且状态不同，则冲突
                if action_device in trigger_and_condition_status:
                    current_state = trigger_and_condition_status[action_device]
                    # 如果当前状态与其他规则的 Action 状态不匹配，则认为发生了冲突
                    action_state = action[1]  # 获取 Action 状态（例如 "open", "close"）
                    if current_state != action_state:
                        if current_rule_id not in conflicts:
                            conflicts[current_rule_id] = set()
                        conflicts[current_rule_id].add(other_rule_id)
    return conflicts

# print(find_rule_conflicts(RuleSet.get_all_rules()))


rule_conflict_map = {
    5: {46},
    9: {86, 95, 46, 94},
    10: {86, 95, 46, 94},
    11: {27, 84, 13},
    20: {96, 97, 38, 39, 71, 72, 74, 49, 24, 29},
    21: {96, 38, 39, 71, 72, 74, 49, 81, 24, 29},
    22: {68},
    23: {78, 47, 79, 50, 53, 54, 85, 25, 93},
    24: {78, 47, 79, 50, 53, 54, 85, 25, 93},
    25: {68},
    28: {86, 95, 46, 94},
    29: {86, 95, 46, 94},
    36: {64, 98, 38, 70, 76, 52, 56, 60, 62},
    37: {64, 38, 70, 76, 82, 52, 56, 60, 62},
    43: {72, 97, 71},
    44: {72, 81, 71},
    45: {68},
    46: {68},
    55: {93, 85, 78, 79},
    56: {57, 99},
    59: {93, 85, 78, 79},
    60: {96, 74},
    61: {72, 97, 71},
    81: {98},
    82: {97}
}
