"""
Suíte Automatizada de Testes Ponta a Ponta — MapaLeads PRO
Valida Fases 1, 3 (P0), 4 (P1), 5 (Segurança, Isolamento Multi-Tenant, Pagamentos e Backups).
"""
import os
import sys
import tempfile
import shutil

# Usa banco temporário isolado para o teste automatizado não sujar o banco local
_TMP_DIR = tempfile.mkdtemp(prefix="mapaleads_test_suite_")
os.environ["DATABASE_PATH"] = os.path.join(_TMP_DIR, "test_mapaleads.db")
os.environ["BILLING_WEBHOOK_SECRET"] = "test_webhook_secret_2026"
os.environ["WA_INTERNAL_TOKEN"] = "test_internal_wa_token_2026"

import database
import backup_manager
import server


def run_tests():
    database.init_db()
    app = server.app
    app.config["TESTING"] = True

    # 1. Criação de 2 usuários distintos (Isolamento Multi-Tenant) + 1 Admin
    uid_admin, _ = database.create_user("Admin Master", "admin_test@mapaleads.pro", "senha123", role="admin", plan="enterprise")
    uid_a, err_a = database.create_user("Cliente A", "clientea@teste.com", "senha123", role="user", plan="pro", days=30)
    uid_b, err_b = database.create_user("Cliente B", "clienteb@teste.com", "senha123", role="user", plan="trial", days=1, max_leads=25)
    assert uid_a and uid_b, f"Falha ao criar usuários: {err_a}, {err_b}"

    # 2. Inserção de leads separados para Cliente A e Cliente B
    lead_a_id, _ = database.upsert_lead({
        "name": "Pizzaria Bella Napoli A",
        "category": "Pizzaria",
        "address": "Rua A, 100 - Centro",
        "neighborhood": "Centro",
        "city": "São Paulo, SP",
        "phone": "(11) 98888-1111",
        "clean_phone": "5511988881111",
        "is_whatsapp": True,
        "phone_type": "mobile",
        "whatsapp_verified": 1,
        "rating": 4.2,
        "reviews_count": 18,
        "website": "",
        "website_type": "none",
        "maps_url": "https://maps.google.com/?cid=11111",
    }, user_id=uid_a)

    lead_b_id, _ = database.upsert_lead({
        "name": "Clínica Sorriso B",
        "category": "Dentista",
        "address": "Av. B, 200 - Savassi",
        "neighborhood": "Savassi",
        "city": "Belo Horizonte, MG",
        "phone": "(31) 97777-2222",
        "clean_phone": "5531977772222",
        "is_whatsapp": True,
        "phone_type": "mobile",
        "whatsapp_verified": 0,
        "rating": 4.9,
        "reviews_count": 210,
        "website": "https://clinicasorrisob.com.br",
        "website_type": "own",
        "maps_url": "https://maps.google.com/?cid=22222",
    }, user_id=uid_b)
    assert lead_a_id > 0 and lead_b_id > 0

    # 3. Teste de Criptografia em Repouso (meta_access_token)
    database.save_wa_user_config(uid_a, {"meta_access_token": "EAABZ_super_secret_meta_token_12345"})
    conn = database.get_connection()
    raw_tok = conn.execute("SELECT meta_access_token FROM wa_user_configs WHERE user_id = ?", (uid_a,)).fetchone()[0]
    conn.close()
    assert raw_tok.startswith("ENCv1:") and "super_secret" not in raw_tok, "Token não foi criptografado no SQLite!"
    dec_cfg = database.get_wa_user_config(uid_a)
    assert dec_cfg["meta_access_token"] == "EAABZ_super_secret_meta_token_12345", "Falha ao descriptografar token!"

    # 4. Teste de Isolamento Multi-Tenant (Leads + Fila WhatsApp)
    client_b = app.test_client()
    with client_b.session_transaction() as sess:
        sess["user_id"] = uid_b

    res_leads_b = client_b.get("/api/leads").get_json()
    assert len(res_leads_b) == 1 and res_leads_b[0]["id"] == lead_b_id, "Vazamento de leads em /api/leads!"

    res_queue_b = client_b.get("/api/wa/queue").get_json()
    preview_ids_b = [x["id"] for x in res_queue_b.get("preview", [])]
    assert lead_a_id not in preview_ids_b, "CRÍTICO: /api/wa/queue vazou lead do Cliente A para o Cliente B!"

    # Cliente B não pode acessar painel Admin
    assert client_b.get("/api/admin/saas-overview").status_code == 403
    assert client_b.get("/api/admin/backups").status_code == 403

    # 5. Teste de Proteção CSRF e Webhook Interno /api/wa/incoming
    csrf_res = client_b.post(
        "/api/leads/cleanup",
        json={"mode": "sem_whatsapp"},
        headers={"Origin": "https://atacante-malicioso.com", "Host": "mapaleadspro.online"},
    )
    assert csrf_res.status_code == 403, "Falha na proteção CSRF por Origin!"

    unauth_inc = client_b.post(
        "/api/wa/incoming",
        json={"user_id": uid_a, "phone": "5511988881111", "text": "Mensagem falsa"},
        headers={"X-Forwarded-For": "198.51.100.55"},
    )
    assert unauth_inc.status_code == 403, "/api/wa/incoming aceitou requisição externa sem token!"

    auth_inc = client_b.post(
        "/api/wa/incoming",
        json={"user_id": uid_a, "phone": "5511988881111", "text": "Olá, quero saber mais"},
        headers={"X-Forwarded-For": "172.18.0.2", "X-Internal-Token": "test_internal_wa_token_2026"},
    )
    assert auth_inc.status_code == 200 and auth_inc.get_json().get("received") is True

    # 6. Teste de Idempotência e Segurança do Webhook de Pagamento
    bad_wh = client_b.post("/api/billing/webhook/kiwify?token=errado", json={"event": "order_approved", "email": "clienteb@teste.com"})
    assert bad_wh.status_code == 403

    wh_payload = {
        "order_id": "ORD-999888",
        "webhook_event_type": "order_approved",
        "plan": "pro",
        "amount": 79.0,
        "Customer": {"email": "clienteb@teste.com", "full_name": "Cliente B"},
    }
    ok_wh1 = client_b.post("/api/billing/webhook/kiwify?token=test_webhook_secret_2026", json=wh_payload).get_json()
    assert ok_wh1.get("success") is True and ok_wh1.get("action") == "renewed"
    exp_after_1 = ok_wh1.get("expires_at")

    ok_wh2 = client_b.post("/api/billing/webhook/kiwify?token=test_webhook_secret_2026", json=wh_payload).get_json()
    assert ok_wh2.get("idempotent_skip") is True, "Webhook duplicado não foi filtrado por idempotência!"
    assert database.get_user_by_id(uid_b)["plan_expires_at"] == exp_after_1

    # 7. Teste P0.1 & P0.3 — Onboarding Inteligente & Analytics
    client_a = app.test_client()
    with client_a.session_transaction() as sess:
        sess["user_id"] = uid_a

    ob1 = client_a.get("/api/onboarding").get_json()["onboarding"]
    assert ob1["step_first_search"] == 1  # já tem lead salvo
    client_a.post("/api/onboarding", json={"step_welcome": 1})
    client_a.post("/api/analytics/event", json={"event_name": "lead_viewed", "metadata": {"lead_id": lead_a_id}})
    ob2 = client_a.get("/api/onboarding").get_json()["onboarding"]
    assert ob2["step_welcome"] == 1 and ob2["step_view_lead"] == 1

    # 8. Teste P1.1 — Lead Score Auditável
    leads_a = client_a.get("/api/leads?opportunity_level=alta&sort_by=lead_score").get_json()
    assert len(leads_a) == 1
    la = leads_a[0]
    assert la["lead_score"] >= 70 and la["opportunity_level"] == "alta"
    assert len(la["verified_facts"]) >= 3 and len(la["score_reasons"]) >= 3

    # 9. Teste P1.2 — Copiloto de Vendas com IA (todas as 6 ações)
    for act in ("analyze", "suggest_product", "approach", "whatsapp", "call_script", "followup"):
        cop = client_a.post("/api/ai/copilot", json={"lead_id": lead_a_id, "action": act}).get_json()
        assert cop.get("success") is True and "pizzaria bella napoli a" in cop.get("content", "").lower(), f"Falha na ação {act} do Copiloto!"
    quota_a = client_a.get("/api/ai/quota").get_json()
    assert quota_a["used_today"] == 6

    # 10. Teste P1.3 — Follow-up e Histórico de Interações no CRM
    today_str = database.datetime.now().strftime("%Y-%m-%d")
    fu_res = client_a.post(f"/api/leads/{lead_a_id}/followup", json={"next_followup_at": today_str, "followup_note": "Ligar às 14h"}).get_json()
    assert fu_res.get("success") is True and fu_res["lead"]["next_followup_at"] == today_str

    agenda = client_a.get("/api/crm/followups").get_json()
    assert agenda["due_today_count"] >= 1

    int_res = client_a.post(f"/api/leads/{lead_a_id}/interactions", json={"kind": "call", "summary": "Cliente pediu proposta por WhatsApp"}).get_json()
    assert int_res.get("success") is True and len(int_res["interactions"]) >= 2

    # 11. Teste P1.4 — Dashboard Individual de Resultados do Assinante
    client_a.post(f"/api/leads/{lead_a_id}/record-sale", json={"sale_value": 497.0, "product_interest": "gmn"})
    my_res = client_a.get("/api/my-results?period=30d").get_json()
    assert my_res["leads_saved"] == 1 and my_res["closed_sales"] == 1 and my_res["closed_revenue_brl"] == 497.0

    # 12. Teste P0.2, P0.4 & Fase 1.1 — Painel Admin SaaS, Regras de Ativação & Backup Consistente
    client_adm = app.test_client()
    with client_adm.session_transaction() as sess:
        sess["user_id"] = uid_admin

    saas_ov = client_adm.get("/api/admin/saas-overview?period=30d").get_json()
    assert saas_ov.get("success") is True
    assert saas_ov["kpis"]["paying_subscribers"] >= 2
    assert saas_ov["kpis"]["mrr_brl"] > 0

    rules_res = client_adm.get("/api/admin/activation-rules").get_json()
    assert len(rules_res.get("rules", [])) == 7

    bk_res = client_adm.post("/api/admin/backups").get_json()
    assert bk_res.get("success") is True, f"Falha no backup consistente: {bk_res}"
    assert bk_res["encrypted"] is True
    assert bk_res["restore_verified"]["success"] is True
    assert bk_res["restore_verified"]["integrity"] == "ok"

    # Testa falha de autenticação HMAC se tentar restaurar com chave errada
    bad_restore = backup_manager.verify_backup_restore(bk_res["path"], secret="chave_errada_123")
    assert bad_restore["success"] is False and "HMAC" in bad_restore.get("error", "")

    print("ALL_MASTER_TESTS_PASSED_OK")


if __name__ == "__main__":
    try:
        run_tests()
    finally:
        shutil.rmtree(_TMP_DIR, ignore_errors=True)
