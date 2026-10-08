class WhatsAppAdapter:
    async def send_message(self, destination: str, message: str, media=None, link=None) -> dict:
        return {
            "status": "not_configured",
            "destination": destination,
            "reason": (
                "Official WhatsApp destination/API capability must be verified "
                "before implementation. No unofficial WhatsApp Web automation is used."
            ),
        }
