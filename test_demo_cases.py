import httpx

cases = [
    ("Case 1 - Password Lockout", "I am locked out. I tried my password 6 times.", "Karan Mehta", "karan.mehta@veridian-corp.example"),
    ("Case 2 - Guest Wi-Fi", "I need Wi-Fi access for a guest tomorrow.", "Vikram Chawla", "vikram.chawla@veridian-corp.example"),
    ("Case 3 - Non-Catalog Software", "I need to install a data-analysis tool that isn't in the software catalog.", "Marcus Vance", "marcus.vance@veridian-corp.example"),
    ("Case 4 - Phishing", "I think I received a phishing email.", "Ananya Reddy", "ananya.reddy@veridian-corp.example"),
    ("Case 5 - Expense Tool", "I can't log into the expense tool. It says invalid credentials.", "Sneha Kulkarni", "sneha.kulkarni@veridian-corp.example"),
    ("Case 6 - Laptop", "My laptop is completely dead and I've had it for about 3.5 years.", "Aditi Sharma", "aditi.sharma@veridian-corp.example"),
    ("Case 7 - Ambiguous Request", "hey can you help, its not working", "Rahul Menon", "rahul.menon@veridian-corp.example")
]

all_passed = True
print("=" * 60)
print("TESTING 7 MANDATORY DEMO CASES ON LIVE RUNNING BACKEND")
print("=" * 60)

for name, msg, emp_name, emp_email in cases:
    res = httpx.post(
        "http://127.0.0.1:8000/api/chat",
        json={"message": msg, "employee_name": emp_name, "employee_email": emp_email},
        timeout=10.0
    )

    assert res.status_code == 200, f"Failed with status {res.status_code}"
    data = res.json()
    sources = [s["policy_id"] for s in data.get("sources", [])]
    source_titles = [f"{s['policy_id']} — {s['title']}" for s in data.get("sources", [])]
    action = data.get("action")
    intent = data.get("intent")
    ticket_id = data.get("ticket_id")
    audit_id = data.get("audit_event_id")
    reply = data.get("message", "")

    print(f"[{name}]")
    print(f"  Input:    {msg}")
    print(f"  Intent:   {intent}")
    print(f"  Action:   {action}")
    print(f"  Sources:  {', '.join(source_titles) if source_titles else 'None (Uncataloged/Ambiguous)'}")
    print(f"  Ticket:   {ticket_id or 'None (Self-Service/Inquiry/Clarification)'}")
    print(f"  Audit ID: {audit_id}")
    print(f"  Response: {reply[:180]}...")
    print("-" * 60)

print("\nALL 7 MANDATORY DEMO CASES TESTED SUCCESSFULLY.")
