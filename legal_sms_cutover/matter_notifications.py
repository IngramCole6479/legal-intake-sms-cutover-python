from datetime import date
from typing import Dict, List

from pydantic import BaseModel, Field


class MatterAlertRequest(BaseModel):
    matter_id: str = Field(min_length=1)
    matter_title: str = Field(min_length=1)
    client_phone: str = Field(min_length=1)
    attorney_phone: str = Field(min_length=1)
    paralegal_phone: str = Field(min_length=1)
    signed_packet: bool
    deadline: date
    today: date


class MatterNotificationPolicy:
    def plan_messages(self, request: MatterAlertRequest) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = []

        messages.append(
            {
                "to": request.client_phone,
                "message": (
                    f"Matter intake received for {request.matter_title} "
                    f"({request.matter_id}). We will review the submission and contact you if anything is missing."
                ),
            }
        )

        if request.signed_packet:
            messages.append(
                {
                    "to": request.attorney_phone,
                    "message": (
                        f"Signed document delivery ready for matter {request.matter_id}. "
                        f"Review the packet for {request.matter_title}."
                    ),
                }
            )

        days_until_deadline = (request.deadline - request.today).days
        if days_until_deadline <= 3:
            messages.append(
                {
                    "to": request.paralegal_phone,
                    "message": (
                        f"Deadline follow-up: matter {request.matter_id} for {request.matter_title} "
                        f"is due on {request.deadline.isoformat()}."
                    ),
                }
            )

        return messages
