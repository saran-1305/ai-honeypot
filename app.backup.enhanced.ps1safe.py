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
  :root{
    --bg1:#eef3fb; --bg2:#dce7f7;
    --brand:#2563eb; --brandDark:#1e40af;
    --line:#e5e7eb; --text:#111827;
  }
  *{box-sizing:border-box}
  body{
    margin:0;
    font-family:"Segoe UI",Arial,Helvetica,sans-serif;
    color:var(--text);
    background:linear-gradient(135deg,var(--bg1),var(--bg2));
  }

  /* Top bar */
  .topbar{
    display:flex;align-items:center;gap:12px;
    padding:14px 20px;
    background:linear-gradient(90deg,var(--brand),var(--brandDark));
    color:#fff;font-weight:600;box-shadow:0 2px 6px rgba(0,0,0,.18);
  }
  .logo{width:24px;height:24px;background:url("/static/brand.svg") center/contain no-repeat}

  /* Center the content */
  .main{
    min-height:calc(100vh - 60px);
    display:grid;place-items:center;
    padding:22px;
  }
  .stack{
    width:100%;
    max-width:980px;
    display:grid;
    grid-template-columns:1fr;
    gap:18px;
    justify-items:center;
  }

  .notice{
    width:min(720px,100%);
    background:#fff;border:1px dashed var(--line);
    padding:10px 14px;border-radius:8px;
    box-shadow:0 2px 8px rgba(0,0,0,.05);
    font-size:14px;
  }

  .card{
    width:min(480px,100%);
    background:#fff;border-radius:14px;
    padding:26px 24px 28px;
    box-shadow:0 8px 22px rgba(0,0,0,.12);
  }
  .card h2{
    margin:0 0 14px 0;text-align:center;
    color:var(--brandDark);
  }

  label{display:block;font-size:12px;margin:8px 2px 6px;color:#374151}
  input,button{
    font-size:14px;border-radius:8px;
  }
  input[type="text"],input[type="password"]{
    width:100%;padding:11px 12px;
    border:1px solid var(--line);background:#fff;
  }
  input[type="text"]:focus,input[type="password"]:focus{
    outline:none;border-color:var(--brand);
    box-shadow:0 0 0 3px rgba(37,99,235,.15);
  }

  .btn{
    display:inline-block;width:100%;
    padding:11px 12px;margin-top:8px;border:0;
    border-radius:8px;color:#fff;background:var(--brand);
    font-weight:600;cursor:pointer;transition:.15s background;
  }
  .btn:hover{background:var(--brandDark)}

  /* Ask helpdesk row (input + button) */
  .row{
    display:grid;grid-template-columns:1fr 120px;gap:10px;
    margin-top:10px;
  }
/* center card */
.center {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 80px);
  padding: 24px 16px;
}
.card {
  background: #ffffff;
  padding: 28px;
  border-radius: 14px;
  width: 420px;
  box-shadow: 0 10px 35px rgba(2, 32, 71, 0.08);
}
.card h2 {
  margin: 0 0 14px 0;
  text-align: center;
  font-size: 22px;
  color: #111827;
}
.card input {
  width: 100%;
  padding: 12px 14px;
  margin: 10px 0;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  outline: none;
  background: #f9fafb;
}
.card button {
  width: 100%;
  padding: 12px 14px;
  border: none;
  border-radius: 8px;
  background: #2563eb;
  color: #fff;
  font-weight: 600;
  cursor: pointer;
  margin: 10px 0 18px 0;
}
.card button:hover { filter: brightness(1.05); }
</style>
<div class="topbar">
  <div class="logo" aria-hidden="true"></div>
  <div class="title" style="font-size:22px; font-weight:700;">Employee Portal</div>
</div><div class="notice">Authorized use only. Activity may be monitored for security and training purposes.</div><div class="container">
  <form method="POST" action="/login">
    <input type="text" name="user" placeholder="Employee ID" required>
    <input type="password" name="password" placeholder="Password" required>
    <input type="submit" value="Login">
  </form>
  
  <div class="helpdesk">
    <form id="help" method="post">
      <input type="text" name="q" placeholder="Ask Helpdesk">
      <button type="submit">Ask</button>
    </form>
  </div>
</div>
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

    system = SYSTEM_HELPDESK + "" + STYLE_HINTS
    user = f"Question: {q}Constraints:- No real credentials/PII.- Provide only small, plausible samples.- If asked for admin/secrets, respond with policy + ticket."
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

























