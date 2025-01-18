import paho.mqtt.client as mqtt
import json

# Cấu hình MQTT
MQTT_BROKER = "192.168.0.103"  # Địa chỉ MQTT Broker
MQTT_PORT = 1883
MQTT_TOPIC = "nhom14"  # Tên topic
CLIENT_ID = "Subscriber_Client"  # ID client

# Hàm xử lý khi kết nối thành công
def on_connect(client, userdata, flags, rc):
    print(f"Kết nối thành công với mã: {rc}")
    client.subscribe(MQTT_TOPIC)  # Đăng ký nhận dữ liệu từ topic

# Hàm xử lý khi nhận được tin nhắn
def on_message(client, userdata, msg):
    try:
        # Giải mã dữ liệu nhận được
        data = json.loads(msg.payload.decode())
        print(f"Nhận được tin nhắn từ topic {msg.topic}: {data}")
    except json.JSONDecodeError:
        print(f"Dữ liệu không hợp lệ: {msg.payload}")

# Tạo client MQTT
client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message

# Kết nối tới broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Chạy chương trình
try:
    client.loop_forever()  # Duy trì vòng lặp xử lý nhận tin nhắn
except KeyboardInterrupt:
    print("Dừng chương trình.")
