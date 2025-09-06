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
/* --- helpdesk enhancements --- */
.btn[disabled]{opacity:.65;cursor:not-allowed}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #fff;border-right-color:transparent;border-radius:50%;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
#ans{white-space:pre-wrap; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; line-height:1.45}
/* --- portal polish (card+form+spinner) --- */
:root{ --brand:#2563eb; --brandDark:#1e40af; --line:#e5e7eb; --bg:#eef3fb; --text:#111827; }
body{ background: radial-gradient(1200px 600px at 70% 20%, #e6eefc, #f2f4f9 60%, #f7f8fc); color:var(--text); }
.topbar{ display:flex; align-items:center; gap:12px; padding:12px 16px; background:linear-gradient(135deg,var(--brand),var(--brandDark)); color:#fff; }
.notice{ border:1px dashed var(--line); background:#fff; padding:10px 12px; border-radius:10px; box-shadow:0 2px 10px rgba(2,32,71,.05); display:inline-block; }
.center{ display:flex; justify-content:center; align-items:center; min-height:calc(100vh - 80px); padding:24px 16px; }
.card{ background:#fff; width:420px; max-width:92vw; padding:28px; border-radius:14px; box-shadow:0 14px 45px rgba(2,32,71,.10); }
.card h2{ margin:2px 0 14px; text-align:center; font-size:22px; color:var(--text); }
.card input{ width:100%; padding:12px 14px; margin:10px 0; border:1px solid var(--line); border-radius:8px; outline:none; background:#f9fafb; }
.card input:focus{ border-color:#93c5fd; box-shadow:0 0 0 3px rgba(59,130,246,.25); }
.card button,.card input[type=submit]{ width:100%; padding:12px 14px; border:none; border-radius:8px; background:var(--brand); color:#fff; font-weight:600; cursor:pointer; margin:12px 0 18px; }
.card button:hover,.card input[type=submit]:hover{ filter:brightness(1.05); }
.btn[disabled]{opacity:.65;cursor:not-allowed}
.spinner{display:inline-block;width:14px;height:14px;border:2px solid #fff;border-right-color:transparent;border-radius:50%;animation:spin .7s linear infinite;vertical-align:-2px;margin-right:6px}
@keyframes spin{to{transform:rotate(360deg)}}
#ans{white-space:pre-wrap; font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Arial; line-height:1.45; margin-top:6px;}
/* --- stage + two-column wrap + panel --- */
.notice{max-width:1100px;margin:14px auto 0;display:block}
.stage{min-height:calc(100vh - 80px);display:flex;align-items:center;justify-content:center;padding:28px 16px}
.wrap{display:grid;grid-template-columns:420px 1fr;gap:28px;max-width:1100px;width:100%;align-items:start}
.panel{background:#fff;padding:22px;border-radius:12px;box-shadow:0 10px 35px rgba(2,32,71,.08)}
.panel pre{margin:0;white-space:pre-wrap;line-height:1.5}
/* responsive: stack on small screens */
@media (max-width:980px){
  .wrap{grid-template-columns:1fr}
  .panel{display:none}
}
</style>
<div class="topbar">
  <div class="logo" aria-hidden="true"></div>
  <div class="title" style="font-size:22px; font-weight:700;">Employee Portal</div>
</div><div class="notice">Authorized use only. Activity may be monitored for security and training purposes.</div><div class="container">
  <div class="stage"><div class="wrap"><div class="card"><h2>Employee Portal</h2><form method="POST" action="/login">
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
<pre id="ans"></pre></div></div></div><script>
(function(){
  const help = document.getElementById('help');
  const ans  = document.getElementById('ans');
  if (!help || !ans) return;

  help.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = help.querySelector('button, input[type=submit]');
    const setBusy = (on) => {
      if (!btn) return;
      if (on) { btn._old = btn.innerHTML || btn.value || 'Ask'; btn.disabled = true; btn.classList.add('btn'); btn.innerHTML = '<span class="spinner"></span> Asking…'; }
      else    { btn.disabled = false; if ('innerHTML' in btn && btn._old) btn.innerHTML = btn._old; }
    };

    const q = (help.q && help.q.value || '').trim();
    if (!q) { ans.textContent = 'Please type a question for Helpdesk.'; return; }

    setBusy(true);
    ans.textContent = '…';
    try {
      const r = await fetch('/helpdesk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q })
      });
      const j = await r.json();
      ans.textContent = j.ans || j.answer || j.message || 'No answer';
    } catch (err) {
      ans.textContent = 'Temporary internal error contacting Helpdesk.';
    } finally {
      setBusy(false);
    }
  });
})();
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
def _throttle():\n    import time\n    ip = request.remote_addr or "?"\n    # Only throttle the helpdesk endpoint\n    if request.path != "/helpdesk":\n        return None\n    # Bypass throttle for localhost\n    if ip in ("127.0.0.1","::1"):\n        return None\n    now = time.time()\n    last = getattr(g, "_last_hit", 0.0)\n    if now - last < 0.5:\n        return jsonify({"error":"slow down"}), 429\n    g._last_hit = now\n    return jsonify({"error":"slow down"}), 429
    _rate[ip] = t




























@app.route("/health")
def health():
    return {"ok": True}, 200

