from legal_sms_cutover.matter_notifications import MatterAlertRequest, MatterNotificationPolicy


def test_plan_messages_includes_deadline_follow_up_when_due_within_three_days() -> None:
    request = MatterAlertRequest(
        matter_id="MAT-204",
        matter_title="Lopez Estate Intake",
        client_phone="+15550000001",
        attorney_phone="+15550000002",
        paralegal_phone="+15550000003",
        signed_packet=True,
        deadline="2026-04-10",
        today="2026-04-08",
    )

    messages = MatterNotificationPolicy().plan_messages(request)

    assert len(messages) == 3
    assert messages[0]["to"] == "+15550000001"
    assert "Matter intake received" in messages[0]["message"]
    assert messages[1]["to"] == "+15550000002"
    assert "Signed document delivery ready" in messages[1]["message"]
    assert messages[2]["to"] == "+15550000003"
    assert "Deadline follow-up" in messages[2]["message"]
