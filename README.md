# 🛡️ AI Honeypot (Cowrie with Docker)

A **fake SSH honeypot** powered by [Cowrie](https://github.com/cowrie/cowrie), containerized with **Docker** to safely capture attacker behavior for research and educational purposes.

---

## ✨ Features
✅ Fake SSH server on port **2222**  
✅ Captures:
- Login attempts (usernames & passwords)  
- Executed commands  
- File download attempts (`wget` / `curl`)  
✅ JSON log output for easy analysis  
✅ Dockerized — quick setup & teardown  

---

## 📦 Project Structure
ai-honeypot/
├── docker-compose.cowrie.yml # Main Docker Compose file
├── docker-compose.override.yml # Optional overrides
├── web/ # Example web UI
├── docs/ # Documentation
├── logs/ # Honeypot events (ignored in Git)
├── cowrie-logs/ # JSON logs (ignored in Git)
├── cowrie-data/ # Runtime data (ignored in Git)
└── README.md

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/saran-1305/ai-honeypot.git
cd ai-honeypot
docker compose -f docker-compose.cowrie.yml up -d
ssh -o StrictHostKeyChecking=no -p 2222 root@127.0.0.1
# Enter any password (e.g., admin, toor, test123)
tail -f cowrie-logs/cowrie.json
{
  "eventid": "cowrie.session.connect",
  "src_ip": "192.168.1.10",
  "username": "root",
  "password": "admin",
  "command": "uname -a",
  "timestamp": "2025-09-20T12:00:00Z"
}
📊 Use Cases

🔍 Security research & attacker behavior study

🎓 Academic projects / cybersecurity demos

🛠️ Foundation for advanced deception systems
⚠️ Disclaimer

This is a research / demo project only.
Do NOT expose it directly to the public internet unless you know what you’re doing. Running honeypots can attract real attackers.

👤 Author: saran-1305
