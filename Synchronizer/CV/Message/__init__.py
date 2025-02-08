import time
import redis
from Synchronizer.CV import RuleSet

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
    向指定的 Redis Stream 发送消息

    :param rule_name: 规则线程的名称（作为 Producer 标识）
    :param stream: 目标 Stream 的名称
    :param key: 消息类型，取值 "start" 或 "end"，用于区分当前规则线程在开始执行时发送开始消息或结束执行时发送结束消息
    :param id: 规则的唯一标识（id）
    """
    # 构造消息数据，将 id 转换为字符串存储
    message = {
        "key": key,
        "id": str(id)
    }
    try:
        msg_id = redis_client.xadd(stream, message)
        print(f"[{rule_name}] 发送消息成功 -> Stream: {stream}, Key: {key}, Rule-ID: {id}, 消息 ID: {msg_id}")
    except Exception as e:
        print(f"[{rule_name}] 发送消息失败: {e}")


def consume_messages_from_offset(rule_name, current_rule_id, stream, target_id_set, offset='0-0'):
    """
    通过 Redis Stream 监听规则的 `start` 和 `end` 消息，仅等待 `target_id_set` 里的规则。

    :param rule_name: 当前规则线程名称
    :param current_rule_id: 当前规则 ID（整数）
    :param stream: 监听的 Redis Stream 名称
    :param target_id_set: 需要等待的规则 ID 集合（只监听这些规则的 start/end 消息）
    :param offset: 消费起始消息 ID，默认 '0-0' 表示从头开始
    :return: 当退出消费时返回 True；出现异常则返回 False
    """
    # 如果没有需要等待的规则，直接返回 True
    if not target_id_set:
        print(f"[{rule_name}] 无需等待任何规则，立即执行")
        return True

    group_name = f"CG_{rule_name}"
    consumer_name = rule_name  # 每个消费者组只有一个消费者

    # 尝试创建消费者组，若已存在则捕获 BUSYGROUP 异常
    try:
        redis_client.xgroup_create(stream, group_name, id=offset, mkstream=True)
        print(f"[{rule_name}] 消费者组 {group_name} 创建成功，起始ID: {offset}")
    except Exception as e:
        if "BUSYGROUP" in str(e):
            print(f"[{rule_name}] 消费者组 {group_name} 已存在，继续使用。")
        else:
            print(f"[{rule_name}] 创建消费者组 {group_name} 失败: {e}")
            return False

    active_rules = set()  # 用于记录 `target_id_set` 里的规则
    own_start_received = False  # 标记是否已收到当前规则自己的 `start` 消息

    print(f"[{rule_name}] 开始消费 stream '{stream}' 的消息，消费者组: {group_name}, 消费者: {consumer_name}")

    while True:
        try:
            # 使用 XREADGROUP 阻塞等待消息，block=0 表示无限等待
            response = redis_client.xreadgroup(group_name, consumer_name, {stream: '>'}, count=1, block=0)
            # response 格式：[ (stream_name, [ (msg_id, {field: value, ...}), ... ]), ... ]
            for s_name, messages in response:
                for msg_id, msg_data in messages:
                    # 如果消息为初始化消息（含 status 字段），直接 ACK 后跳过
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
                        # **当前规则自己的 start 消息**
                        if msg_rule_id == current_rule_id:
                            own_start_received = True
                            print(f"[{rule_name}] 收到自己的 start 消息 (rule-id: {msg_rule_id})")
                            redis_client.xack(stream, group_name, msg_id)

                            # **如果没有正在等待的规则，直接返回**
                            if not active_rules:
                                print(f"[{rule_name}] active_rules 为空，退出消费")
                                return True
                        else:
                            # **仅监听 target_id_set 里的规则**
                            if msg_rule_id in target_id_set and not own_start_received:
                                active_rules.add(msg_rule_id)
                                print(
                                    f"[{rule_name}] 监听目标规则 {msg_rule_id} 的 start 消息，当前等待集合: {active_rules}")
                            redis_client.xack(stream, group_name, msg_id)

                    elif msg_type == 'end':
                        # **仅移除 target_id_set 里的规则**
                        if msg_rule_id in active_rules:
                            active_rules.remove(msg_rule_id)
                            print(f"[{rule_name}] 规则 {msg_rule_id} 结束，移出等待集合，当前等待集合: {active_rules}")
                        redis_client.xack(stream, group_name, msg_id)

                        # **若已收到自己 start 消息且 active_rules 为空，则退出**
                        if own_start_received and not active_rules:
                            print(f"[{rule_name}] active_rules 为空且已收到自己的 start 消息，退出消费")
                            return True

        except Exception as e:
            print(f"[{rule_name}] 消费消息异常: {e}")
            return False
