import os
import subprocess

from rocketmq.client import Producer, Message, PushConsumer

from Synchronizer.ConditionVariable import RuleSet

NAMESRV_ADDR = "114.55.74.144:9876"
BROKER_ADDR = "114.55.74.144:10911"


MQADMIN_PATH = r"E:\研究生信息收集\论文材料\IoT-Event-Detector\Synchronizer\ConditionVariable\Message\mqadmin.cmd"
# 确保 RocketMQ_HOME 变量正确
os.environ["ROCKETMQ_HOME"] = r"E:\PycharmWorkSpace\rocketmq-all-5.3.1-bin-release"


def create_topics():
    for device in RuleSet.DeviceName:
        topic_name = f"Topic_{device}"
        cmd = [
            "cmd", "/c", MQADMIN_PATH, "updateTopic",
            "-n", NAMESRV_ADDR,
            "-b", BROKER_ADDR,
            "-t", topic_name,
            "-w", "1",
            "-r", "1"
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Topic '{topic_name}' 创建成功")
        except subprocess.CalledProcessError as e:
            print(f"创建 Topic '{topic_name}' 失败: {e}")



# 1. 发送消息
def send_message(rule_name, topic, key, body):
    """
    向指定 Topic 发送带 Key 的消息，ProducerGroup 设为 rule_name
    :param rule_name: 规则线程的名称（作为 ProducerGroup）
    :param topic: 目标 Topic
    :param key: "start" 或 "end"
    :param body: 消息内容
    """
    producer = Producer(rule_name)  # 每个 Rule 作为 ProducerGroup
    producer.set_namesrv_addr(NAMESRV_ADDR)
    producer.start()

    msg = Message(topic)
    msg.set_keys(key)
    msg.set_body(body)

    try:
        ret = producer.send_sync(msg)
        print(f"[{rule_name}] 发送消息成功 -> Topic: {topic}, Key: {key}, 结果: {ret.status}")
    except Exception as e:
        print(f"[{rule_name}] 发送消息失败: {e}")

    producer.shutdown()


# 2. 从指定的 Offset 读取带特定 Key 的消息
def consume_messages_from_offset(rule_name, topic, key, offset=0):
    """
    独立 ConsumerGroup 从指定 Offset 开始，消费带 Key 的消息。
    :param rule_name: 规则线程的名称（作为 ConsumerGroup）
    :param topic: 目标 Topic
    :param key: "start" 或 "end"
    :param offset: 开始消费的 Offset
    """
    consumer_group = f"ConsumerGroup_{rule_name}"  # 每个规则线程一个 ConsumerGroup
    consumer = PushConsumer(consumer_group)
    consumer.set_namesrv_addr(NAMESRV_ADDR)
    consumer.subscribe(topic, "*")

    active_rules = set()  # 维护活动的 RuleId 集合

    def callback(msg):
        try:
            message_body = msg.body.decode("utf-8")
            rule_id = int(message_body)  # 假设 body 里存储的是 RuleId

            if key == "start":
                active_rules.add(rule_id)
                print(f"[{rule_name}] 规则 {rule_id} 开始执行，当前规则集合: {active_rules}")

            elif key == "end":
                if rule_id in active_rules:
                    active_rules.remove(rule_id)
                    print(f"[{rule_name}] 规则 {rule_id} 结束执行，当前规则集合: {active_rules}")

                # 如果集合为空，则终止消费者
                if not active_rules:
                    print(f"[{rule_name}] 所有规则执行完毕，关闭消费者...")
                    consumer.shutdown()

        except Exception as e:
            print(f"[{rule_name}] 消费消息异常: {e}")

    consumer.register_message_listener(callback)
    consumer.start()

    print(f"[{rule_name}] 正在消费 Topic '{topic}' 的 Key '{key}' 的消息...")