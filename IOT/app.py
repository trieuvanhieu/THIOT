from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
import json
import eventlet

# Patching để cải thiện hiệu suất
eventlet.monkey_patch()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# Cấu hình MQTT
MQTT_BROKER = "192.168.0.100"  # Địa chỉ MQTT Broker
MQTT_PORT = 1883
MQTT_TOPIC = "MQTT_DongCo_DCs2"  # Tên topic
CLIENT_ID = "Python_Client"  # ID client

# Trạng thái động cơ (để đồng bộ giữa MQTT và giao diện web)
motor_status = 0  # 0: Tắt, 1: Bật

# Hàm xử lý khi kết nối MQTT thành công
def on_connect(client, userdata, flags, rc):
    print(f"Kết nối MQTT thành công với mã: {rc}")
    client.subscribe(MQTT_TOPIC)

# Hàm xử lý khi nhận được tin nhắn MQTT
def on_message(client, userdata, msg):
    global motor_status
    try:
        payload = json.loads(msg.payload.decode())
        print(f"Nhận dữ liệu từ MQTT: {payload}")

        # Kiểm tra và cập nhật trạng thái
        if "status" in payload:
            motor_status = int(payload["status"])
            # Gửi trạng thái qua WebSocket tới giao diện web
            socketio.emit("motor_status_update", {
                "date": payload.get("date", "N/A"),
                "time": payload.get("time", "N/A"),
                "Tốc độ động cơ": payload.get("Tốc độ động cơ", "N/A"),
                "status": motor_status
            })
        else:
            print("Payload không chứa khóa 'status'")

    except json.JSONDecodeError:
        print("Lỗi khi giải mã tin nhắn MQTT")
    except Exception as e:
        print(f"Lỗi khác: {e}")

# Khởi tạo MQTT Client
mqtt_client = mqtt.Client(client_id=CLIENT_ID, protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Chạy vòng lặp MQTT
mqtt_client.loop_start()

# Route hiển thị giao diện web
@app.route("/")
def index():
    return render_template("index.html")

# WebSocket xử lý bật/tắt động cơ
@socketio.on("motor_control")
def handle_motor_control(data):
    global motor_status
    try:
        status = data.get("status")  # Trạng thái động cơ
        if status not in [0, 1]:
            print("Trạng thái không hợp lệ:", status)
            return

        motor_status = status  # Cập nhật trạng thái động cơ
        message = {
            "status": motor_status
        }
        mqtt_client.publish(MQTT_TOPIC, json.dumps(message))  # Gửi dữ liệu qua MQTT
        print(f"Đã gửi MQTT: {message}")
        # Phát trạng thái cập nhật tới tất cả các client
        socketio.emit("motor_status_update", {"status": motor_status})
        print(f"Phát WebSocket: {motor_status}")
    except Exception as e:
        print(f"Lỗi xử lý WebSocket: {e}")

# Chạy ứng dụng Flask
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)