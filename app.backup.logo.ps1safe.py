import os, time
from dotenv import load_dotenv
load_dotenv()   # must be before importing LLM

from flask import Flask, request, jsonify, render_template_string, make_response
from llm_adapter import LLM
from deception_prompts import SYSTEM_HELPDESK, STYLE_HINTS
from fake_data import fake_employee_record, fake_finance_rows, fake_file_listing, fake_file_content
from logger import log_event, new_correlation_id

app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET","changeme")
llm = LLM()

PAGE = """
<style>
  header {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 24px;
    font-weight: bold;
    padding: 8px;
  }
  header::before {
    content: "";
    display: inline-block;
    width: 40px;
    height: 40px;
    background: url("/static/sk-logo.png") no-repeat center center;
    background-size: cover;
  }
</style>
<header>Employee Portal</header>`r`n<div style="padding:6px;border:1px dashed #999;margin:8px 0;font-size:12px;">Authorized use only. Activity may be monitored for security and training purposes.</div>`r`n<form method="POST" action="/login">
  <input name="eid" placeholder="Employee ID"><br>
  <input name="pw" type="password" placeholder="Password"><br>
  <button type="submit">Login</button>
</form>
<hr>
<form id="help">
  <input name="q" placeholder="Ask Helpdesk">
  <button type="submit">Ask</button>
</form>
<pre id="ans"></pre>
<script>
document.getElementById('help').addEventListener('submit',async e=>{
 e.preventDefault();
 let q=e.target.q.value;
 let r=await fetch('/helpdesk',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({q})});
 let j=await r.json();
 document.getElementById('ans').textContent=j.answer || j.ans || 'No answer';
});
</script>
"""

@app.before_request
def before():
    request.corr = new_correlation_id()

@app.after_request
def after(resp):
    resp.headers["Cache-Control"] = "no-store"
    return resp

@app.route("/")
def index():
    log_event("page_view", ip=request.remote_addr, cid=request.corr)
    return render_template_string(PAGE)

@app.route("/login", methods=["POST"])
def login():
    eid = request.form.get("eid"); pw = request.form.get("pw")
    log_event("login_attempt", eid=eid, ip=request.remote_addr, cid=request.corr)
    time.sleep(1)
    return make_response("Your account requires a reset. Ticket created.", 401)

@app.route("/helpdesk", methods=["POST"])
def helpdesk():
    data = request.get_json(silent=True) or {}
    q = (data.get("q") or "").strip()
    log_event("helpdesk_q", q=q, cid=request.corr, ip=request.remote_addr)
    if not q:
        return jsonify({"answer": "Please type a question for Helpdesk."}), 400

    system = SYSTEM_HELPDESK + "\n\n" + STYLE_HINTS
    user = f"Question: {q}\n\nConstraints:\n- No real credentials/PII.\n- Provide only small, plausible samples.\n- If asked for admin/secrets, respond with policy + ticket.\n"
    ans = llm.chat(system, user, max_tokens=250)
    ans = (ans or "").strip()[:800]
    log_event("helpdesk_a", a=ans, cid=request.corr)
    return jsonify({"answer": ans}), 200

@app.route("/diag2")
def diag2():
    return {
        "backend": os.getenv("LLM_BACKEND"),
        "ollama_host": os.getenv("OLLAMA_HOST"),
        "ollama_model": os.getenv("OLLAMA_MODEL"),
        "openai_model": os.getenv("OPENAI_MODEL"),
        "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8088)
# Warm-up once so the first user request is snappy
try:
    _ = llm.chat("You are a concise assistant.","Say ok", max_tokens=8)
except Exception:
    pass
@app.route("/vpnreset", methods=["POST"])
def vpnreset():
    data = request.get_json(silent=True) or {}
    uid = (data.get("uid") or "employee").strip()[:40]
    prompt = f"Employee {uid} requests VPN reset. Give a short, procedural response with fake ticket number and vague timing. No real credentials or secrets."
    ans = llm.chat("You are an IT helpdesk. Never reveal real data. Use small fake samples.", prompt, max_tokens=120)
    log_event("vpnreset", uid=uid, a=ans, cid=request.corr, ip=request.remote_addr)
    return jsonify({"status": "queued", "note": ans[:400]}), 200

@app.route("/server-status", methods=["GET"])
def server_status():
    # deliberately vague, enticing details
    fake = {
        "cluster": "intranet-eu",
        "health": "degraded",
        "incidents": 1,
        "next_maintenance": "Sun 02:00 UTC",
        "notes": "Intermittent auth failures; temp policy applied"
    }
    log_event("server_status", **fake, cid=request.corr, ip=request.remote_addr)
    return jsonify(fake), 200

@app.route("/admin/request-access", methods=["POST"])
def admin_request_access():
    data = request.get_json(silent=True) or {}
    appname = (data.get("app") or "FileShare").strip()[:40]
    reason  = (data.get("reason") or "migration").strip()[:120]
    prompt  = f"User requests admin access to {appname} for {reason}. Decline, cite policy, open fake ticket and next-steps."
    ans = llm.chat("You are a security admin. Never provide secrets. Respond with policy language and fake ticket.", prompt, max_tokens=140)
    log_event("admin_req", app=appname, reason=reason, a=ans, cid=request.corr, ip=request.remote_addr)
    return jsonify({"ticket": "SR-"+str(int(time.time()))[-6:], "message": ans[:500]}), 200
_rate = {}
@app.before_request
def _throttle():
    import time
    ip = request.remote_addr or "?"
    t = time.time()
    last = _rate.get(ip, 0)
    if t - last < 2.0:  # 2s cooldown per IP
        return jsonify({"error":"slow down"}), 429
    _rate[ip] = t





