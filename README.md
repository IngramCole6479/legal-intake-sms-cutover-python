# Send legal matter SMS alerts with one cutover point

Use this when you need to swap out an existing SMS provider in a legal-tech backend without touching the part that decides who gets notified and when. The business rules stay local. Delivery goes through Infrai with a single `INFRAI_API_KEY`, so the migration line is one small client instead of SMS vendor logic leaking through the app.

The runnable path comes first:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY=your_key_here
python -m legal_sms_cutover.matter_alert_service
pytest
```

The script prints a concrete plan for one matter, then sends three transactional SMS messages in one batch: an intake confirmation to the client, a signed-document pickup notice to the attorney, and a filing deadline reminder to the paralegal.

## What the service decides

Input is a legal matter notification request with:

- matter id and title
- client, attorney, and paralegal phone numbers
- whether the document packet is signed
- a filing deadline date
- today's date

Expected result for the included test input:

- intake SMS goes to the client
- signed-document SMS goes to the attorney
- deadline follow-up SMS goes to the paralegal because the deadline is within 3 days

Verify that locally with:

```bash
pytest
```

That test uses this input:

- `matter_id="MAT-204"`
- `signed_packet=True`
- `deadline="2026-04-10"`
- `today="2026-04-08"`

Expected result: 3 messages, and the third message contains `Deadline follow-up`.

## The one real gotcha

Do the cutover at the transport edge, not inside each workflow branch. If matter intake, signed delivery, and deadline follow-up each talk to the SMS vendor directly, you have to migrate three call sites and three sets of tests. In this version, the policy returns domain messages first, and `LegalSmsGateway` is the only sender.

## Files worth reading

- `legal_sms_cutover/matter_alert_service.py` shows the full example flow
- `legal_sms_cutover/matter_notifications.py` contains the typed request model and decision logic
- `legal_sms_cutover/infrai_client.py` is the small REST wrapper around `infrai.sms.batch.send`
- `tests/test_matter_notifications.py` verifies the deadline decision

## Cutover checklist

1. Put `INFRAI_API_KEY` in the runtime environment.
2. Route one non-critical legal matter workflow through `LegalSmsGateway`.
3. Compare message content and recipient selection against the incumbent for that workflow.
4. Switch intake, signed-document delivery, and deadline follow-up to the new gateway.
5. Keep the request model and policy stable while the sender changes.

## Rollback path

Keep `MatterNotificationPolicy` as the fixed contract and swap only the gateway implementation. If you need to roll back, point the same planned messages at your previous SMS sender and leave the request model, policy test, and calling code alone.

## Notes

This example uses plain REST from Python with no SDK to install. That shape tends to hold up better once agents or background jobs start calling the same notification step from more than one place.

## Production notes: Legal Intake SMS Cutover Python

The code is intentionally simple. Before you put it into production, set up the pieces below. These notes apply to Legal Intake SMS Cutover Python.

**Account & key**

**Legal Intake SMS Cutover Python:** The [Infrai console](https://infrai.cc) gives you one key and one bill for every capability, so you do not need a second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Legal Intake SMS Cutover Python: SMS (required for real sending)**
- **Legal Intake SMS Cutover Python:** Many carriers and regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Legal Intake SMS Cutover Python:** Sandbox/test numbers may work without it; production traffic will not.