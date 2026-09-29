from pprint import pprint

from .infrai_client import LegalSmsGateway
from .matter_notifications import MatterAlertRequest, MatterNotificationPolicy


def main() -> None:
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

    policy = MatterNotificationPolicy()
    messages = policy.plan_messages(request)

    print("planned messages:")
    pprint(messages)

    gateway = LegalSmsGateway()
    result = gateway.send_messages(
        matter_id=request.matter_id,
        workflow_step="matter-intake-signed-deadline",
        messages=messages,
    )

    print("delivery result:")
    pprint(result)


if __name__ == "__main__":
    main()
