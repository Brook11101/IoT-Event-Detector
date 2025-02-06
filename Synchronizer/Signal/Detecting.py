
def detectRaceCondition(logs):
    """
    仅统计/记录 4 类冲突：
      - Action Conflict (AC)
      - Unexpected Conflict (UC)
      - Condition Block (CBK)
      - Condition Pass (CP)

    并且避免重复日志：如果同一对 (former_rule.RuleId, latter_rule.RuleId, conflict_type)
    已记录过，就不再重复输出或计数。
    """

    action_conflict_count = 0      # AC
    unexpected_conflict_count = 0  # UC
    condition_block_count = 0      # CBK
    condition_pass_count = 0       # CP

    # 用来去重的集合：存储 (former_rule.RuleId, latter_rule.RuleId, conflict_type)
    logged_pairs = set()

    with open("race_condition.txt", "a", encoding="utf-8") as rc_file:
        for i in range(len(logs)):
            current_rule = logs[i]
            current_actions = current_rule["Action"]
            cur_rule_id = current_rule["RuleId"]    # 使用 RuleId 而非 id

            # ========== 1) Condition Block (CBK) ========== #
            # 如果当前规则被 skipped 且有 Condition，则检查前面有没有修改对应设备
            if current_rule['status'] == 'skipped' and current_rule.get('Condition'):
                cond_dev, _ = current_rule['Condition'][0], current_rule['Condition'][1]
                for j in range(i - 1, -1, -1):
                    former_rule = logs[j]
                    frm_rule_id = former_rule["RuleId"]
                    former_actions = former_rule["Action"]

                    for former_act in former_actions:
                        if former_act[0] == cond_dev:
                            # 构造一个标识元组 (前者RuleId, 后者RuleId, "CBK")
                            pair_cbk = (frm_rule_id, cur_rule_id, "CBK")

                            if pair_cbk not in logged_pairs:
                                logged_pairs.add(pair_cbk)
                                condition_block_count += 1

                                rc_file.write("Condition Block\n")
                                rc_file.write(str(former_rule) + "\n")
                                rc_file.write(str(current_rule) + "\n\n")
                            # 找到后即可 break，避免重复记录
                            break
                    else:
                        # 内层 actions 没 break 就继续
                        continue
                    # 如果内层 break 表示已记录一次 -> 跳出 j-loop
                    break

            # ========== 2) 其他三个冲突只在 'run' 规则里检测 ========== #
            if current_rule['status'] == 'run':
                # ---- (A) Action Conflict / Unexpected Conflict ----
                # 往前对比是否相同设备不同状态
                front_id = current_rule["triggerId"]   # 用于追溯同一链，但你也可以按需删除

                for j in range(i - 1, -1, -1):
                    former_rule = logs[j]
                    frm_rule_id = former_rule["RuleId"]
                    former_actions = former_rule["Action"]

                    for latter_act in current_actions:
                        for former_act in former_actions:
                            # 设备相同 & 状态不同
                            if latter_act[0] == former_act[0] and latter_act[1] != former_act[1]:
                                # 决定是 AC 还是 UC
                                if former_rule["ancestor"] == current_rule["ancestor"]:
                                    # 同祖先 -> Action Conflict
                                    pair_ac = (frm_rule_id, cur_rule_id, "AC")
                                    if pair_ac not in logged_pairs:
                                        logged_pairs.add(pair_ac)
                                        action_conflict_count += 1

                                        rc_file.write("Action Conflict\n")
                                        rc_file.write(str(former_rule) + "\n")
                                        rc_file.write(str(current_rule) + "\n\n")
                                else:
                                    # 不同祖先 -> unexpected Conflict
                                    pair_uc = (frm_rule_id, cur_rule_id, "UC")
                                    if pair_uc not in logged_pairs:
                                        logged_pairs.add(pair_uc)
                                        unexpected_conflict_count += 1

                                        rc_file.write("unexpected Conflict\n")
                                        rc_file.write(str(former_rule) + "\n")
                                        rc_file.write(str(current_rule) + "\n\n")

                    # 如果需要基于 "triggerId" 来追溯同一条链，可以在这里更新 front_id
                    # 但对 AC/UC 的判断其实不一定要依赖 front_id

                    if former_rule["id"] == front_id:
                        front_id = former_rule["triggerId"]

                # ---- (B) Condition Pass (CP) ----
                # 如果当前 rule 有 condition，检查前面是否有 [cond_dev, cond_state] 的动作
                if current_rule.get('Condition'):
                    cond_dev, cond_state = current_rule['Condition'][0], current_rule['Condition'][1]
                    for j in range(i - 1, -1, -1):
                        former_rule = logs[j]
                        frm_rule_id = former_rule["RuleId"]
                        if [cond_dev, cond_state] in former_rule["Action"]:
                            pair_cp = (frm_rule_id, cur_rule_id, "CP")
                            if pair_cp not in logged_pairs:
                                logged_pairs.add(pair_cp)
                                condition_pass_count += 1

                                rc_file.write("Condition Pass\n")
                                rc_file.write(str(former_rule) + "\n")
                                rc_file.write(str(current_rule) + "\n\n")
                            break  # 只要找到一次即可（避免多次重复计入）

    return (
        action_conflict_count,      # AC
        unexpected_conflict_count,  # UC
        condition_pass_count,       # CP
        condition_block_count       # CBK
    )


if __name__ == "__main__":
    import os
    import ast


    # 读取execution_logs.txt
    logs = []
    with open("execution_logs.txt", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                # 用ast.literal_eval将字符串(形如"{'key': value, ...}")解析成dict
                log_entry = ast.literal_eval(line)
                logs.append(log_entry)

        # 初始化日志文件（清空）
        with open("race_condition.txt", "w", encoding="utf-8"):
            pass

    # 调用检测函数
    (
        ac_count,
        uc_count,
        cp_count,
        cbk_count
    ) = detectRaceCondition(logs)

    # 控制台打印结果，便于查看
    print("=== Final Detection Counts ===")
    print(f"Action Conflict: {ac_count}")
    print(f"Unexpected Conflict: {uc_count}")
    print(f"Condition Pass: {cp_count}")
    print(f"Condition Block: {cbk_count}")