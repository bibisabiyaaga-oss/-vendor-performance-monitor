\# AI Service Demo Script - Day 18



\## My Role: AI Developer 1

\## Time: 1.5 minutes



\---



\## 1. Opening Statement (15 seconds)

"Our AI service solves the problem of manual vendor performance analysis

by using Groq AI to automatically generate insights, recommendations,

and reports for any vendor."



\---



\## 2. Show Architecture (20 seconds)

"Our AI microservice is built with:

\- Flask Python framework on port 5000

\- Groq API with LLaMA-3.3-70b model

\- Redis caching with 15 minute TTL

\- 4 endpoints: /health, /describe, /recommend, /generate-report"



\---



\## 3. Live Demo - /describe endpoint (20 seconds)

Run this command:

curl -X POST http://127.0.0.1:5000/describe \\

\-H "Content-Type: application/json" \\

\-d '{"vendor\_name":"TechSupply Co","category":"Electronics",

"performance\_score":92,"delivery\_rate":98,

"quality\_rating":4.5,"contract\_value":50000}'



Say: "Watch the AI analyze this vendor in real time..."



\---



\## 4. Live Demo - /recommend endpoint (20 seconds)

Run this command:

curl -X POST http://127.0.0.1:5000/recommend \\

\-H "Content-Type: application/json" \\

\-d '{"vendor\_name":"TechSupply Co","category":"Electronics",

"performance\_score":92,"delivery\_rate":98,

"quality\_rating":4.5,"contract\_value":50000}'



Say: "Now watch AI generate 3 actionable recommendations..."



\---



\## 5. Show /health endpoint (15 seconds)

Run this command:

curl http://127.0.0.1:5000/health



Say: "Our health endpoint shows model name, uptime,

average response time, and Redis connection status."



\---



\## 6. Key Points to Mention

\- Average response time: under 2 seconds

\- Fallback templates if AI is unavailable

\- Security headers on all responses

\- Redis caching to avoid duplicate AI calls

\- ChromaDB with 10 domain knowledge documents

