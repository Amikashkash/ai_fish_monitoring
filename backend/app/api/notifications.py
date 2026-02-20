"""WhatsApp notification endpoint for daily fish treatment reminders."""

from datetime import datetime
from fastapi import APIRouter, Depends, Header, HTTPException
from supabase import Client
import httpx

from app.config.settings import get_settings
from app.config.supabase_client import get_supabase

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


def _format_whatsapp_message(tasks_data: dict) -> str:
    if tasks_data["total_active_treatments"] == 0:
        return f"🐟 Fish Monitor\n📅 {tasks_data['date']}\nNo active treatments today. ✅"

    msg = f"🐟 *Fish Monitor — Daily Rounds*\n"
    msg += f"📅 {tasks_data['date']} | {tasks_data['total_active_treatments']} active treatment(s)\n"

    for i, t in enumerate(tasks_data["tasks"], 1):
        name = t.get("common_name") or t.get("fish_species") or "Unknown"
        qty = t.get("quantity", 0)
        msg += f"\n*{i}. {name}*"
        if qty:
            msg += f" ({qty} fish)"
        msg += "\n"
        drugs = t.get("drugs_required", [])
        if drugs:
            for d in drugs:
                msg += f"   💊 {d['name']} — {d['dosage']} {d['frequency']}\n"
        else:
            msg += "   No drugs — observation only\n"

    return msg.strip()


@router.post("/whatsapp-daily")
async def send_whatsapp_daily(
    x_cron_secret: str = Header(default=""),
    supabase: Client = Depends(get_supabase)
):
    """
    Send daily WhatsApp reminder with active treatment list.

    Called by cron-job.org every morning. Protected by X-Cron-Secret header.
    """
    settings = get_settings()

    # Verify cron secret
    if not settings.CRON_SECRET or x_cron_secret != settings.CRON_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Fetch active treatments
    response = (
        supabase.table("treatments")
        .select("*, shipments(*), treatment_drugs(*, drug_protocols(*))")
        .eq("status", "active")
        .execute()
    )

    tasks = []
    for treatment in (response.data or []):
        shipment = treatment.get("shipments") or {}
        drugs = treatment.get("treatment_drugs") or []
        tasks.append({
            "treatment_id": treatment["id"],
            "fish_species": shipment.get("scientific_name", ""),
            "common_name": shipment.get("common_name", ""),
            "quantity": shipment.get("quantity", 0),
            "drugs_required": [
                {
                    "name": (d.get("drug_protocols") or {}).get("drug_name", "Unknown"),
                    "dosage": str(d.get("actual_dosage", "")),
                    "frequency": d.get("actual_frequency", "")
                }
                for d in drugs
            ]
        })

    tasks_data = {
        "date": str(datetime.now().date()),
        "total_active_treatments": len(tasks),
        "tasks": tasks
    }

    # Skip sending if nothing configured
    if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID or not settings.WHATSAPP_TO_NUMBER:
        return {"status": "skipped", "reason": "WhatsApp credentials not configured"}

    message_text = _format_whatsapp_message(tasks_data)

    # Send via WhatsApp Cloud API
    url = f"https://graph.facebook.com/v19.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": settings.WHATSAPP_TO_NUMBER,
        "type": "text",
        "text": {"body": message_text}
    }
    headers = {
        "Authorization": f"Bearer {settings.WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        res = await client.post(url, json=payload, headers=headers, timeout=10)

    if res.status_code != 200:
        raise HTTPException(
            status_code=500,
            detail=f"WhatsApp API error: {res.status_code} {res.text}"
        )

    return {
        "status": "sent" if tasks_data["total_active_treatments"] > 0 else "no_treatments",
        "treatments": tasks_data["total_active_treatments"],
        "date": tasks_data["date"]
    }
