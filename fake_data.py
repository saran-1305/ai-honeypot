import random, datetime

NAMES = ["A. Sharma","V. Nair","K. Iyer","S. Reddy","P. Rao","D. Singh"]
DEPTS = ["Finance","Engineering","HR","Sales"]

def fake_employee_record():
    return {
        "employeeId": f"E{random.randint(10000,99999)}",
        "name": random.choice(NAMES),
        "dept": random.choice(DEPTS),
        "email": f"user{random.randint(100,999)}@corp.local",
        "lastLogin": (datetime.datetime.utcnow() - datetime.timedelta(hours=random.randint(1,48))).isoformat()+"Z"
    }

def fake_finance_rows(n=5):
    rows=[]
    for _ in range(n):
        rows.append({
            "txnId": f"T{random.randint(100000,999999)}",
            "amount": round(random.uniform(1000,50000),2),
            "approvedBy": random.choice(NAMES),
            "date": (datetime.datetime.utcnow() - datetime.timedelta(days=random.randint(1,30))).date().isoformat()
        })
    return rows

def fake_file_listing():
    return ["policies/leave_policy.pdf","finance/q2.xlsx","eng/sprint_notes.md"]

def fake_file_content(path:str) -> bytes:
    return f"Fake file content for {path}\\nGenerated at {datetime.datetime.utcnow().isoformat()}".encode()
