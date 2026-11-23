from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Root endpoint returning application status."""
    return jsonify({
        "status": "success",
        "message": "DevOps Capstone Project 1 - Flask App Running",
        "version": "1.0.0"
    }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for container orchestrators and load balancers."""
    return jsonify({
        "status": "healthy",
        "uptime": "normal"
    }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
