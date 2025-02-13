import time
import redis
from Synchronizer.CV import RuleSet
import json

# Redis 连接配置（请根据实际情况修改）
redis_host = '114.55.74.144'
redis_port = 6379
redis_db = 0
redis_password = 'whd123456'

# 创建 Redis 客户端
redis_client = redis.StrictRedis(
    host=redis_host,
    port=redis_port,
    db=redis_db,
    password=redis_password,
    decode_responses=True
)

def create_streams():
    """
    为 RuleSet 中每个设备创建对应的 Redis Stream（命名为 Stream_<设备名>）
    通过添加一条初始化消息来确保 stream 存在，消费者在处理时可以忽略包含 'status' 字段的消息
    """
    for device in RuleSet.DeviceName:
        stream_name = f"Stream_{device}"
        # 如果 stream 不存在，则添加一条初始化消息进行创建
        if not redis_client.exists(stream_name):
            init_id = redis_client.xadd(stream_name, {"status": "stream_created"})
            print(f"Stream '{stream_name}' 创建成功，初始化消息 ID: {init_id}")
        else:
            print(f"Stream '{stream_name}' 已存在，跳过创建。")

def clear_stream(stream_name):
    """
    清空指定的 Redis Stream 的所有消息
    实现方式：直接删除该 stream 对应的 key
    如果后续需要使用该 stream，请在删除后调用 create_streams() 重新创建
    """
    try:
        result = redis_client.delete(stream_name)
        if result:
            print(f"Stream '{stream_name}' 已清空。")
        else:
            print(f"Stream '{stream_name}' 不存在或已清空。")
    except Exception as e:
        print(f"删除 Stream '{stream_name}' 时发生错误: {e}")

def clear_all_streams():
    """
    清空 RuleSet 中所有设备对应的 Redis Stream 的消息
    遍历 RuleSet.DeviceName 中的每个设备，删除对应的 stream
    """
    for device in RuleSet.DeviceName:
        stream_name = f"Stream_{device}"
        clear_stream(stream_name)


def send_message(rule_name, stream, key, id):
    """
    向指定的 Redis Stream 发送消息，支持最多 3 次重试，并返回消息的偏移量。

    :param rule_name: 规则线程的名称（作为 Producer 标识）
    :param stream: 目标 Stream 的名称
    :param key: 消息类型，取值 "start" 或 "end"
    :param id: 规则的唯一标识（id）
    :return: 返回消息发送成功后的偏移量 msg_id
    """
    message = {"key": key, "id": str(id)}

    for attempt in range(3):  # 最多尝试 3 次
        try:
            # 向 Redis Stream 发送消息
            msg_id = redis_client.xadd(stream, message)
            print(f"[{rule_name}] 发送消息成功 -> Stream: {stream}, Key: {key}, Rule-ID: {id}, 消息 ID: {msg_id}")
            return msg_id  # 发送成功，返回消息偏移量
        except Exception as e:
            print(f"[{rule_name}] 发送消息失败 (第 {attempt + 1} 次): {e}")
            time.sleep(0.5)  # 休眠后重试

    print(f"[{rule_name}] 发送消息失败，已达最大重试次数")
    return None  # 发送失败时返回 None

# 专门用于start类型消息的发送,确保一次性完整的插入规则相关设备队列上的start消息
def send_message_atomic(rule_name, stream_list, key, id):
    """
    以**原子性**方式向多个 Redis Streams 发送消息，支持失败重试。
    仅当 key="start" 时，才返回 {stream_name: msg_id}，否则返回 None。

    :param rule_name: 规则名称（用于日志）
    :param stream_list: 目标 Stream 列表
    :param key: 消息类型，可以是 "start" 或 "end"
    :param id: 规则的唯一 ID
    :return: 如果 key="start"，返回 {stream_name: msg_id}，否则返回 None
    """
    lua_script = """
    local stream_list = KEYS
    local key = ARGV[1]
    local id = ARGV[2]
    local max_retries = 3  -- 最大重试次数
    local offset_dict = {}

    for _, stream in ipairs(stream_list) do
        local attempt = 0
        local msg_id = nil

        while attempt < max_retries do
            msg_id = redis.call("XADD", stream, "*", "key", key, "id", id)
            if msg_id then
                break  -- 发送成功，跳出循环
            end
            attempt = attempt + 1
        end

        if not msg_id then
            return redis.error_reply("添加消息失败（已尝试 " .. max_retries .. " 次）: " .. stream)
        end

        if key == "start" then
            offset_dict[stream] = msg_id  -- 仅记录 start 消息的偏移量
        end
    end

    if key == "start" then
        return cjson.encode(offset_dict)  -- 仅在 key="start" 时返回 JSON
    else
        return "{}"  -- key="end" 时返回空 JSON
    end
    """

    try:
        send_to_streams = redis_client.register_script(lua_script)
        result_json = send_to_streams(keys=stream_list, args=[key, id])

        if key == "start":
            offset_dict = json.loads(result_json)  # 解析 Lua 返回的 JSON 数据
            print(f"[{rule_name}] Start 消息成功发送到多个 Streams: {offset_dict}, Rule-ID: {id}")
            return offset_dict
        else:
            print(f"[{rule_name}] End 消息成功发送到多个 Streams: {stream_list}, Rule-ID: {id}")
            return None  # end 消息不返回偏移量
    except Exception as e:
        print(f"[{rule_name}] 发送消息失败: {e}")
        return None



# 这个函数之所以不完善，还能检测出来，是因为缺乏标记，应该标记出target_id_set中应该来但是最终一直都没来的规则，返回到主线程中，来说明：当前规则不是不等待，而是那些规则已经超过了时间窗口。
def consume_messages_from_offset(rule_name, current_rule_id, stream, target_id_set, offset_dict_cur=None, missing_rules=None):
    """
    通过 Redis Stream 监听规则的 `start` 和 `end` 消息，并标记 `target_id_set` 中 **应该来但没来的规则**。

    :param rule_name: 当前规则线程名称
    :param current_rule_id: 当前规则 ID（整数）
    :param stream: 监听的 Redis Stream 名称
    :param target_id_set: 需要等待的规则 ID 集合（只监听这些规则的 start/end 消息）
    :param offset_dict_cur: {stream_name: offset}，决定不同 Stream 的消费起点，由外部传入，只会按照轮次使用
    :param missing_rules: 用于收集未出现的规则，格式 [(当前规则ID, 缺失规则ID)]
    :return: True (正常退出) / False (异常退出)
    """

    if not target_id_set:
        print(f"[{rule_name}] 无需等待任何规则，立即执行")
        return True

    group_name = f"CG_{rule_name}"
    consumer_name = rule_name  # 每个消费者组只有一个消费者
    missing_rules = missing_rules if missing_rules is not None else []

    # **如果 offset_dict 为空或没有该 stream，默认为 '0-0'**
    stream_offset = offset_dict_cur.get(stream, '0-0') if offset_dict_cur else '0-0'
    # stream_offset = '0-0'
    #  **尝试创建消费者组，最多重试 3 次**
    for attempt in range(3):
        try:
            redis_client.xgroup_create(stream, group_name, id=stream_offset, mkstream=True)
            print(f"[{rule_name}] 消费者组 {group_name} 创建成功，起始ID: {stream_offset}")
            break  # 成功创建后跳出循环
        except Exception as e:
            if "BUSYGROUP" in str(e):
                print(f"[{rule_name}] 消费者组 {group_name} 已存在，继续使用。")
                break
            print(f"[{rule_name}] 创建消费者组 {group_name} 失败 (第 {attempt + 1} 次): {e}")
            time.sleep(0.5)  # 休眠后重试
    else:
        print(f"[{rule_name}] 创建消费者组失败，已达最大重试次数")
        return False  # 超过 3 次则终止

    active_rules = set()  # 用于记录 `target_id_set` 里的规则
    own_start_received = False  # 标记是否已收到当前规则自己的 `start` 消息
    seen_start_rules = set()  # 记录已消费的 start 消息中的规则 ID

    print(f"[{rule_name}] 开始消费 stream '{stream}' 的消息，消费者组: {group_name}, 消费者: {consumer_name}")

    retry_count = 0  # 消费异常的重试次数

    while True:
        try:
            #  **使用 offset_dict 里的值作为消费起点**
            response = redis_client.xreadgroup(group_name, consumer_name, {stream: '>'}, count=1, block=0)

            for s_name, messages in response:
                for msg_id, msg_data in messages:
                    if 'status' in msg_data:
                        redis_client.xack(stream, group_name, msg_id)
                        continue

                    msg_type = msg_data.get('key')
                    try:
                        msg_rule_id = int(msg_data.get('id'))
                    except Exception as ex:
                        print(f"[{rule_name}] 消息 {msg_id} 中 id 数据异常: {msg_data.get('id')}, 错误: {ex}")
                        redis_client.xack(stream, group_name, msg_id)
                        continue

                    if msg_type == 'start':
                        if msg_rule_id == current_rule_id:
                            own_start_received = True
                            print(f"[{rule_name}] 收到自己的 start 消息 (rule-id: {msg_rule_id})")
                            redis_client.xack(stream, group_name, msg_id)

                            if not active_rules:
                                print(f"[{rule_name}] active_rules 为空，退出消费")
                                missing_rules_in_target = target_id_set - seen_start_rules
                                for missing_rule in missing_rules_in_target:
                                    missing_rules.append((current_rule_id, missing_rule))
                                return True
                        else:
                            if msg_rule_id in target_id_set and not own_start_received:
                                active_rules.add(msg_rule_id)
                                seen_start_rules.add(msg_rule_id)
                                print(f"[{rule_name}] 监听目标规则 {msg_rule_id} 的 start 消息，当前等待集合: {active_rules}")
                            redis_client.xack(stream, group_name, msg_id)

                    elif msg_type == 'end':
                        if msg_rule_id in active_rules:
                            active_rules.remove(msg_rule_id)
                            print(f"[{rule_name}] 规则 {msg_rule_id} 结束，移出等待集合，当前等待集合: {active_rules}")
                        redis_client.xack(stream, group_name, msg_id)

                        if own_start_received and not active_rules:
                            print(f"[{rule_name}] active_rules 为空且已收到自己的 start 消息，退出消费")

                            # **标记未出现的规则**
                            missing_rules_in_target = target_id_set - seen_start_rules
                            for missing_rule in missing_rules_in_target:
                                missing_rules.append((current_rule_id, missing_rule))
                            return True

        except Exception as e:
            retry_count += 1
            print(f"[{rule_name}] 消费消息异常 (第 {retry_count} 次): {e}")
            time.sleep(0.5)  # 休眠后重试
            if retry_count >= 3:
                print(f"[{rule_name}] 消费消息异常已达最大重试次数，停止监听")
                return False  # 超过 3 次则终止

