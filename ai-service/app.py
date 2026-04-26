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

@app.after_request
def add_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

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

def describe_fallback(vendor_name):
    return {
        "vendor_name": vendor_name,
        "analysis": "AI service temporarily unavailable. Please try again later.",
        "is_fallback": True,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

def recommend_fallback(vendor_name):
    return {
        "vendor_name": vendor_name,
        "recommendations": [
            {"action_type": "monitor", "description": "Monitor vendor performance closely.", "priority": "high"},
            {"action_type": "improve", "description": "Request performance improvement plan.", "priority": "medium"},
            {"action_type": "monitor", "description": "Schedule quarterly review meeting.", "priority": "low"}
        ],
        "is_fallback": True,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

def report_fallback(vendor_name, report_period):
    return {
        "vendor_name": vendor_name,
        "report_period": report_period,
        "report": {
            "title": f"Performance Report for {vendor_name}",
            "summary": "AI service temporarily unavailable. Report generated with default template.",
            "overview": "Please try again later for a detailed AI-generated report.",
            "key_items": ["Data collection in progress", "Analysis pending", "Report will be available soon"],
            "recommendations": ["Monitor performance", "Schedule review", "Update contract terms"]
        },
        "is_fallback": True,
        "generated_at": datetime.utcnow().isoformat() + "Z"
    }

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
            "is_fallback": False,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        fallback = describe_fallback(data['vendor_name'])
        return jsonify(fallback), 200

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
            "is_fallback": False,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        fallback = recommend_fallback(data['vendor_name'])
        return jsonify(fallback), 200

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
            "is_fallback": False,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }
        save_to_cache(cache_key, output)
        response_times.append((time.time() - start) * 1000)
        return jsonify(output)
    except Exception as e:
        fallback = report_fallback(data['vendor_name'], data['report_period'])
        return jsonify(fallback), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)