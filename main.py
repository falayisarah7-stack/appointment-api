from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_webhook():
    try:
        data = request.json
        print("✅ Webhook data received:", data)

        # Extract useful info (update this as needed)
        first_name = data.get('firstName') or data.get('first_name')
        email = data.get('email')
        phone = data.get('phone')

        print(f"Contact Info: {first_name}, {email}, {phone}")

        return jsonify({"status": "success", "message": "Data received"}), 200
    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/', methods=['GET'])
def check_status():
    return jsonify({"status": "ok", "message": "Webhook server active"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
