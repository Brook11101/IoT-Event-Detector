import ast

from conda_build.api import check

from Synchronizer.CV.UserTemplate import getUserTemplate


def read_nocv_logs(filename):
    """
    读取 `nocv_logs.txt` 并解析成规则列表，保留执行顺序。
    """
    logs = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            log_entry = ast.literal_eval(line.strip())  # 解析 JSON 格式的日志
            logs.append(log_entry)
    return logs


def detectRaceCondition(logs):
    conflict_dict = {
        "AC": [],  # Action Conflict
        "UC": [],  # Unexpected Conflict
        "CBK": [],  # Condition Block
        "CP": []  # Condition Pass
    }

    logged_pairs = set()  # 记录已检测的 conflict pair

    for i in range(len(logs)):
        current_rule = logs[i]
        current_actions = current_rule["Action"]
        cur_rule_id = current_rule["id"]

        # Condition Block (CBK)
        if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
            cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
            for j in range(i - 1, -1, -1):
                former_rule = logs[j]
                frm_rule_id = former_rule["id"]
                former_actions = former_rule["Action"]

                for former_act in former_actions:
                    if former_act[0] == cond_dev:
                        pair_cbk = (frm_rule_id, cur_rule_id)
                        if pair_cbk not in logged_pairs:
                            logged_pairs.add(pair_cbk)
                            conflict_dict["CBK"].append(pair_cbk)
                        break
                else:
                    continue
                break

        # 其他 Race Condition 只在 `run` 规则里检测
        if current_rule['status'] == 'run':
            # Action Conflict / Unexpected Conflict
            for j in range(i - 1, -1, -1):
                former_rule = logs[j]
                frm_rule_id = former_rule["id"]
                former_actions = former_rule["Action"]

                for latter_act in current_actions:
                    for former_act in former_actions:
                        if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                            if former_rule["ancestor"] == current_rule["ancestor"]:
                                pair_ac = (frm_rule_id, cur_rule_id)
                                if pair_ac not in logged_pairs:
                                    logged_pairs.add(pair_ac)
                                    conflict_dict["AC"].append(pair_ac)
                            else:
                                pair_uc = (frm_rule_id, cur_rule_id)
                                if pair_uc not in logged_pairs:
                                    logged_pairs.add(pair_uc)
                                    conflict_dict["UC"].append(pair_uc)

            # Condition Pass (CP)
            if current_rule.get('Condition'):
                cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):
                    former_rule = logs[j]
                    frm_rule_id = former_rule["id"]
                    if [cond_dev, cond_state] in former_rule["Action"]:
                        pair_cp = (frm_rule_id, cur_rule_id)
                        if pair_cp not in logged_pairs:
                            logged_pairs.add(pair_cp)
                            conflict_dict["CP"].append(pair_cp)
                        break

    return conflict_dict


def check_rcs(user_template_dict, conflict_dict):
    check_result = {  # 记录顺序不一致的冲突
        "AC": [],
        "UC": [],
        "CBK": [],
        "CP": []
    }

    mismatch_count = 0  # 统计顺序不一致的冲突数量

    for conflict_type in user_template_dict:
        expected_pairs = set(user_template_dict[conflict_type])
        nocv_pairs = set(conflict_dict[conflict_type])

        for pair in nocv_pairs:
            reversed_pair = (pair[1], pair[0])
            if reversed_pair in expected_pairs:  # 顺序发生颠倒
                check_result[conflict_type].append(pair)
                mismatch_count += 1

    return check_result, mismatch_count


def main():
    # 读取 `nocv_logs.txt`
    nocv_logs = read_nocv_logs("nocv_logs.txt")

    # 从 `nocv_logs.txt` 检测 Race Condition
    conflict_dict = detectRaceCondition(nocv_logs)

    user_template = getUserTemplate()

    # 比较两者的顺序是否一致
    conflict_result, mismatch_count = check_rcs(user_template, conflict_dict)

    # 输出最终结果
    print("=== Final Check Conflict Results ===")
    print(f"Total Mismatched Conflicts: {mismatch_count}")
    print("Detailed Mismatched Conflicts:")
    for conflict_type, mismatches in conflict_result.items():
        print(f"{conflict_type}: {mismatches}")

    return conflict_result, mismatch_count


if __name__ == "__main__":
    main()
