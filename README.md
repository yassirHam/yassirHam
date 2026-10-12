<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0f2027,50:203a43,100:2c9a8f&height=220&section=header&text=Yassir%20Hamri&fontSize=62&fontColor=ffffff&animation=fadeIn&fontAlignY=36&desc=Teaching%20machines%20to%20read%2C%20retrieve%20and%20(mostly)%20behave&descSize=18&descAlignY=58" alt="Yassir Hamri banner" />

<a href="https://git.io/typing-svg">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=22&duration=3200&pause=900&color=2C9A8F&center=true&vCenter=true&width=640&lines=Engineering+student+%40+ENSA+Al+Hoceima+%F0%9F%87%B2%F0%9F%87%A6;I+fine-tune+LLMs+on+a+GPU+that+begs+for+mercy;I+build+RAG+that+says+%22I+don't+know%22+when+it+should;I+also+make+ESP32+boards+blink+at+the+cloud" alt="Typing SVG" />
</a>

<br/>

[![Portfolio](https://img.shields.io/badge/Portfolio-yassir--hamri--portfolio-2C9A8F?style=for-the-badge&logo=vercel&logoColor=white)](https://yassir-hamri-portfolio.vercel.app)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-yassir--hamri-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://linkedin.com/in/yassir-hamri)
[![Location](https://img.shields.io/badge/Morocco-Al_Hoceima-C1272D?style=for-the-badge&logo=googlemaps&logoColor=white)](https://github.com/yassirHam)
[![Open to](https://img.shields.io/badge/Open_to-Internships-22c55e?style=for-the-badge&logo=handshake&logoColor=white)](https://linkedin.com/in/yassir-hamri)

</div>

---

## 👋 Hey, I'm Yassir

I'm a 22-year-old engineering student at **ENSA Al Hoceima**, in the *Digital Transformation & AI* track (class of 2027). I spend my days somewhere between **LLMs, data pipelines and tiny microcontrollers**, and I like it when all three end up in the same project.

- 🧠 I like AI that can **show its sources**, and that **refuses to answer** when it has none
- 🔧 I like backends that are boring in the best way: queued, containerised, tested
- 📡 I like hardware, because nothing humbles you like a sensor that lies
- 🗣️ Arabic (native) · French · English · a little 中文 and Deutsch on the side

---

## 🛠️ Toolbox

**Languages**

<img src="https://skillicons.dev/icons?i=py,java,c,cpp,js,ts,sql&perline=7" alt="Languages" />

**AI / ML / Data**

<img src="https://skillicons.dev/icons?i=pytorch,sklearn,pandas,numpy,postgres,mysql,powerbi&perline=7" alt="AI and data" />

![Hugging Face](https://img.shields.io/badge/🤗_Transformers-FFD21E?style=flat-square&logoColor=black)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langgraph&logoColor=white)
![FAISS](https://img.shields.io/badge/FAISS-0467DF?style=flat-square&logo=meta&logoColor=white)
![pgvector](https://img.shields.io/badge/pgvector-336791?style=flat-square&logo=postgresql&logoColor=white)
![QLoRA](https://img.shields.io/badge/QLoRA-4--bit-8A2BE2?style=flat-square)
![MLflow](https://img.shields.io/badge/MLflow-0194E2?style=flat-square&logo=mlflow&logoColor=white)

**Backend & DevOps**

<img src="https://skillicons.dev/icons?i=fastapi,spring,docker,kubernetes,terraform,githubactions,aws,azure,linux,git&perline=10" alt="Backend and DevOps" />

![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=flat-square&logo=rabbitmq&logoColor=white)
![Argo CD](https://img.shields.io/badge/Argo_CD-EF7B4D?style=flat-square&logo=argo&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-660066?style=flat-square&logo=mqtt&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-E7352C?style=flat-square&logo=espressif&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white)

---

## 🚀 Stuff I've built

### 🏛️ Dhakira · knowledge platform at UM6P
*Internship at Mohammed VI Polytechnic University, summer 2026*

An AI knowledge platform for a company's messy pile of documents. Ask a question, get an answer **with citations**, and if the docs don't back it up, it politely declines instead of making things up.

Hybrid retrieval (Postgres full-text + pgvector + cross-encoder reranking), an async ingestion pipeline on RabbitMQ that eats PDFs, DOCX, Markdown and HTML, OCR routing, and benchmarks that yell at me when retrieval quality drops.

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![Spring Boot](https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat-square&logo=springboot&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=flat-square&logo=rabbitmq&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

👉 [UM6P_DHAKIRA](https://github.com/yassirHam/UM6P_DHAKIRA)

### 🩺 Medical chatbot · Qwen2.5-7B, squeezed onto a small GPU
I cleaned **125k+ medical dialogues**, fine-tuned Qwen2.5-7B with 4-bit QLoRA, bolted FAISS retrieval on top so answers lean on real references, and wrapped it all in a Dockerised FastAPI service. Under 500 ms per answer in my benchmarks.

![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)
![QLoRA](https://img.shields.io/badge/QLoRA-8A2BE2?style=flat-square)
![FAISS](https://img.shields.io/badge/FAISS-0467DF?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)

👉 [MedicalChatbot_DeepLearning](https://github.com/yassirHam/MedicalChatbot_DeepLearning)

### 💼 Job Intelligent · a job market that finally makes sense
Selenium scrapers hit several job portals, a cleaning pipeline dedupes and normalises everything into Postgres, then embeddings match candidates to offers. Power BI dashboards show which skills are actually in demand.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-43B02A?style=flat-square&logo=selenium&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white)
![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black)

👉 [job-intelligent](https://github.com/yassirHam/job-intelligent)

### 📡 IoT motion sensor · from an ESP32 to an Azure dashboard
An ESP32 detects motion, sends it over MQTT to Azure IoT Hub, and a web frontend shows live events and alerts. [Live demo here](https://iot-motion-sensor.vercel.app/).

![C++](https://img.shields.io/badge/C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![MQTT](https://img.shields.io/badge/MQTT-660066?style=flat-square&logo=mqtt&logoColor=white)
![Azure](https://img.shields.io/badge/Azure_IoT_Hub-0078D4?style=flat-square&logo=microsoftazure&logoColor=white)

👉 [IOT-MOTION-SENSOR](https://github.com/yassirHam/IOT-MOTION-SENSOR)

### 🎓 gestion-PFE · a scheduler that ends the group-chat chaos
A Java EE system that assigns final-year projects, pairs supervisors, builds jury panels and schedules defenses while respecting everyone's availability. It cut admin coordination work by roughly 70%.

![Java](https://img.shields.io/badge/Java_EE-ED8B00?style=flat-square&logo=openjdk&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white)
![LangChain4j](https://img.shields.io/badge/LangChain4j-1C3C3C?style=flat-square)

👉 [gestion-PFE](https://github.com/yassirHam/gestion-PFE)

### 🛡️ Spam & phishing detector
Random Forest and SVM classifiers on NLP features, **97%+ accuracy** on held-out data, served as a tiny FastAPI + Docker service.

👉 [cyber_security_email_spam](https://github.com/yassirHam/cyber_security_email_spam)

---

## 🔬 Currently cooking

| | Project | What's going on |
|---|---|---|
| 🛰️ | **ORION** | Multimodal research platform. Vision Transformers, time-series and knowledge graphs, so a model can reason about industrial sensors *and* images with Graph RAG and LangGraph agents |
| ⚓ | **Sentinel** | A policy-driven MLOps setup on AWS/EKS. Terraform, Argo CD and MLflow handle deployments, drift detection and rollbacks without drama |

---

## 🏅 Receipts

- 🎖️ **Global UGRAD semi-finalist** (US State Dept exchange program, 2023–24)
- ☁️ **Oracle Cloud Infrastructure AI Foundations Associate** (2026)
- ☸️ **IBM** · Istio & IBM Cloud Kubernetes Service (two courses, 2026)
- 🤖 Automated a content pipeline (Python + n8n + Canva API) that cut manual work by 90% and now pumps out 1,200+ visuals a month

---

<div align="center">

### 💬 Got an idea, an internship, or a cursed bug?
Come say hi on [LinkedIn](https://linkedin.com/in/yassir-hamri) or poke around my [portfolio](https://yassir-hamri-portfolio.vercel.app).

<br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:2c9a8f,50:203a43,100:0f2027&height=110&section=footer" alt="footer" />

</div>
