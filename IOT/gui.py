import paho.mqtt.client as mqtt
from datetime import datetime
import json
import time

# Cấu hình MQTT
MQTT_BROKER = "192.168.0.100"  # Địa chỉ MQTT Broker
MQTT_PORT = 1883
MQTT_TOPIC = "MQTT_DongCo_DCs2"  # Tên topic
CLIENT_ID = "Publisher_Client"  # ID client

# Tạo client MQTT
client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)

# Kết nối tới broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Hàm gửi dữ liệu điều khiển động cơ
def publish_motor_control(speed, status):
    data = {
        "date": datetime.now().strftime("%d/%m/%Y"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "Tốc độ động cơ": f"{speed}%",
        "status": status  # 0: Tắt, 1: Bật
    }
    client.publish(MQTT_TOPIC, json.dumps(data))
    print(f"Đã gửi: {data}")

# Hàm điều khiển động cơ
def motor_control_loop():
    try:
        while True:
            speed = int(input("Nhập tốc độ động cơ (0-100): "))
            if speed < 0 or speed > 100:
                print("Tốc độ không hợp lệ, vui lòng nhập từ 0 đến 100.")
                continue

            status = input("Nhập trạng thái động cơ (1: Bật, 0: Tắt): ")
            if status not in ["0", "1"]:
                print("Trạng thái không hợp lệ, vui lòng nhập 0 hoặc 1.")
                continue

            publish_motor_control(speed, int(status))
            time.sleep(2)  # Gửi mỗi 2 giây

    except KeyboardInterrupt:
        print("Dừng chương trình.")

# Chạy chương trình
motor_control_loop()
