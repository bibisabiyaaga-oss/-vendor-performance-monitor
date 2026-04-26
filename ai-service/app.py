from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
import time
import hashlib
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

START_TIME = time.time()
response_times = []

try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except:
    REDIS_AVAILABLE = False

def get_cache_key(endpoint, data):
    content = f"{endpoint}:{json.dumps(data, sort_keys=True)}"
    return hashlib.sha256(content.encode()).hexdigest()

def get_from_cache(key):
    if not REDIS_AVAILABLE:
        return None
    try:
        result = redis_client.get(key)
        return json.loads(result) if result else None
    except:
        return None

def save_to_cache(key, data, ttl=900):
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(data))
    except:
        pass

@app.route('/health', methods=['GET'])
def health():
    uptime_seconds = int(time.time() - START_TIME)
    avg = round(sum(response_times) / len(response_times), 3) if response_times else 0
    return jsonify({
        "status": "ok",
        "service": "ai-service",
        "model": "llama-3.3-70b-versatile",
        "uptime_seconds": uptime_seconds,
        "avg_response_time_ms": avg,
        "redis_connected": REDIS_AVAILABLE,
        "total_requests": len(response_times)
    })

@app.route('/describe', methods=['POST'])
def describe():
    start = time.time()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is empty"}), 400
    required_fields = ['vendor_name', 'category', 'performance_score',
                       'delivery_rate', 'quality_rating', 'contract_value']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    cache_key = get_cache_key("describe", data)
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify(cached)
    with open("prompts/describe_prompt.txt", "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(**data)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        result = response.choices[0].message.content
        output = {
            "vendor_name": data['vendor_name'],
            "analysis": result,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    start = time.time()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is empty"}), 400
    required_fields = ['vendor_name', 'category', 'performance_score',
                       'delivery_rate', 'quality_rating', 'contract_value']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    cache_key = get_cache_key("recommend", data)
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify(cached)
    with open("prompts/recommend_prompt.txt", "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(**data)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        result = response.choices[0].message.content
        recommendations = json.loads(result)
        output = {
            "vendor_name": data['vendor_name'],
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "recommendations": [],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
    start = time.time()
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is empty"}), 400
    required_fields = ['vendor_name', 'category', 'performance_score',
                       'delivery_rate', 'quality_rating', 'contract_value']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
    if 'report_period' not in data:
        data['report_period'] = 'Q1 2026'
    cache_key = get_cache_key("generate-report", data)
    cached = get_from_cache(cache_key)
    if cached:
        return jsonify(cached)
    with open("prompts/report_prompt.txt", "r") as f:
        prompt_template = f.read()
    prompt = prompt_template.format(**data)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=1000
        )
        result = response.choices[0].message.content
        report = json.loads(result)
        output = {
            "vendor_name": data['vendor_name'],
            "report_period": data['report_period'],
            "report": report,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)