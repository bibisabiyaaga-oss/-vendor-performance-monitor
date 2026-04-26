from flask import Flask, request, jsonify
from datetime import datetime
import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "ai-service"})

@app.route('/describe', methods=['POST'])
def describe():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is empty"}), 400
    required_fields = ['vendor_name', 'category', 'performance_score',
                       'delivery_rate', 'quality_rating', 'contract_value']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
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
        return jsonify({
            "vendor_name": data['vendor_name'],
            "analysis": result,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is empty"}), 400
    required_fields = ['vendor_name', 'category', 'performance_score',
                       'delivery_rate', 'quality_rating', 'contract_value']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing field: {field}"}), 400
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
        return jsonify({
            "vendor_name": data['vendor_name'],
            "recommendations": recommendations,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "recommendations": [],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

@app.route('/generate-report', methods=['POST'])
def generate_report():
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
        return jsonify({
            "vendor_name": data['vendor_name'],
            "report_period": data['report_period'],
            "report": report,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        })
    except Exception as e:
        return jsonify({
            "error": "AI service unavailable",
            "is_fallback": True,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)