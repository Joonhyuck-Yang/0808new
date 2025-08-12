from flask import Flask, jsonify
import os

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        "message": "Hello from Railway!",
        "status": "success",
        "port": os.getenv("PORT", "unknown")
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/v1/health')
def api_health():
    return jsonify({
        "status": "healthy",
        "message": "API Gateway is running",
        "railway_status": "success"
    })

@app.route('/api/v1/signup', methods=['POST'])
def signup():
    return jsonify({
        "status": "success",
        "message": "회원가입 성공!",
        "railway_logged": True
    })

if __name__ == '__main__':
    port = int(os.getenv("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
