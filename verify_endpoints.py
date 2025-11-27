import json
import sqlite3

import httpx

BASE = "http://127.0.0.1:8000"
API = "/api/v1"
PASSWORD = "Passw0rd!"

results = []


def log(name, response):
    try:
        body = response.json()
    except Exception:
        body = response.text
    results.append(
        {
            "name": name,
            "status": response.status_code,
            "body": body,
        }
    )
    print(f"{name}: {response.status_code}")


def promote(email, role):
    with sqlite3.connect("dev.db") as conn:
        conn.execute("UPDATE users SET role=? WHERE email=?", (role, email))
        conn.commit()


with httpx.Client(base_url=BASE, timeout=15.0) as client:
    log("docs", client.get("/docs"))
    log("openapi", client.get("/openapi.json"))

    def register(email, full_name):
        resp = client.post(
            f"{API}/auth/register",
            json={"email": email, "password": PASSWORD, "full_name": full_name},
        )
        log(f"register:{email}", resp)
        return resp.json()["id"]

    def login(email):
        resp = client.post(
            f"{API}/auth/login",
            json={"email": email, "password": PASSWORD},
        )
        log(f"login:{email}", resp)
        data = resp.json()
        return data["access_token"], data["refresh_token"]

    super_email = "super@example.com"
    super_id = register(super_email, "Super Admin")
    promote(super_email, "superadmin")
    super_access, super_refresh = login(super_email)
    log("me:super", client.get(f"{API}/auth/me", headers={"Authorization": f"Bearer {super_access}"}))
    log(
        "refresh:super",
        client.post(f"{API}/auth/refresh", json={"refresh_token": super_refresh}),
    )

    operator_email = "operator@example.com"
    register(operator_email, "Operator One")
    promote(operator_email, "operator")
    operator_access, _ = login(operator_email)

    owner_email = "owner@example.com"
    owner_id = register(owner_email, "Owner One")
    owner_access, _ = login(owner_email)

    owner2_email = "owner2@example.com"
    owner2_id = register(owner2_email, "Owner Two")
    owner2_access, _ = login(owner2_email)

    branch_admin_email = "branch@example.com"
    branch_admin_id = register(branch_admin_email, "Branch Admin")
    branch_admin_access, _ = login(branch_admin_email)

    cashier_email = "cashier@example.com"
    cashier_id = register(cashier_email, "Cashier User")
    cashier_access, _ = login(cashier_email)

    req_payload = {"name": "MediPharm", "address": "Main St", "phone": "123"}
    resp = client.post(
        f"{API}/pharmacies/requests",
        json=req_payload,
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("pharmacy_request:create", resp)
    request_id = resp.json()["id"]

    resp = client.post(
        f"{API}/pharmacies/requests/{request_id}/approve",
        headers={"Authorization": f"Bearer {operator_access}"},
    )
    log("pharmacy_request:approve", resp)
    pharmacy_id = resp.json()["id"]

    resp = client.post(
        f"{API}/pharmacies/requests",
        json={"name": "RejectPharm", "address": "Side St", "phone": "999"},
        headers={"Authorization": f"Bearer {owner2_access}"},
    )
    log("pharmacy_request:create2", resp)
    request2_id = resp.json()["id"]

    resp = client.post(
        f"{API}/pharmacies/requests/{request2_id}/reject",
        json={"reason": "Incomplete docs"},
        headers={"Authorization": f"Bearer {operator_access}"},
    )
    log("pharmacy_request:reject", resp)

    branch_payload = {"name": "Main Branch", "address": "1 Health Way", "phone": "111"}
    resp = client.post(
        f"{API}/branches",
        json={**branch_payload},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:create", resp)
    branch = resp.json()
    branch_id = branch["id"]

    branch2_payload = {"name": "Temp Branch", "address": "Temp", "phone": "222"}
    resp = client.post(
        f"{API}/branches",
        json={**branch2_payload},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:create2", resp)
    branch2_id = resp.json()["id"]

    resp = client.post(
        f"{API}/branches/{branch_id}/assign-admin",
        json={"user_id": branch_admin_id},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:assign_admin", resp)

    resp = client.get(
        f"{API}/branches",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:list", resp)

    resp = client.patch(
        f"{API}/branches/{branch_id}",
        json={"phone": "777"},
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:update", resp)

    resp = client.delete(
        f"{API}/branches/{branch2_id}",
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("branch:delete", resp)

    drug_payload = {"name": "PainAway", "code": "PA-001", "description": "Pain relief", "is_active": True}
    resp = client.post(
        f"{API}/drugs",
        json=drug_payload,
        headers={"Authorization": f"Bearer {operator_access}"},
    )
    log("drug:create", resp)
    drug_id = resp.json()["id"]

    resp = client.get(
        f"{API}/drugs",
        headers={"Authorization": f"Bearer {super_access}"},
    )
    log("drug:list", resp)

    resp = client.get(
        f"{API}/drugs/search",
        params={"query": "Pain"},
        headers={"Authorization": f"Bearer {super_access}"},
    )
    log("drug:search", resp)

    inventory_payload = {
        "branch_id": branch_id,
        "drug_id": drug_id,
        "quantity": 50,
        "reorder_level": 10,
    }
    resp = client.post(
        f"{API}/drugs/inventory",
        json=inventory_payload,
        headers={"Authorization": f"Bearer {owner_access}"},
    )
    log("inventory:add", resp)
    inventory_id = resp.json()["id"]

    resp = client.patch(
        f"{API}/drugs/inventory/{inventory_id}",
        json={"quantity": 75},
        headers={"Authorization": f"Bearer {branch_admin_access}"},
    )
    log("inventory:update:branch_admin", resp)

    resp = client.patch(
        f"{API}/drugs/inventory/{inventory_id}",
        json={"reorder_level": 5},
        headers={"Authorization": f"Bearer {cashier_access}"},
    )
    log("inventory:update:cashier", resp)

with open("verification_results.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
