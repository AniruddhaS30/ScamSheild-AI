from typing import List, Dict


Tip = Dict[str, str]


BASE_SAFE_TIPS: List[Tip] = [
    {
        "title": "Never share OTPs",
        "text": "Legitimate banks and services will never ask you to share an OTP over call, SMS, or chat.",
    },
    {
        "title": "Verify from official channels",
        "text": "If you receive a suspicious message, call the official customer care number printed on your card or website.",
    },
    {
        "title": "Do not click unknown links",
        "text": "Avoid opening links from unknown senders, especially if they ask for login, card, or OTP details.",
    },
]


SCAM_TYPE_TIPS = {
    "Bank Fraud": {
        "high": [
            {
                "title": "Do not share OTP or PIN",
                "text": "Immediately stop the conversation. Do NOT share any OTP, PIN, or card number with the caller or sender.",
            },
            {
                "title": "Contact your bank now",
                "text": "Call the official bank helpline, report the suspicious message, and ask them to check recent activity.",
            },
            {
                "title": "Change passwords and enable alerts",
                "text": "Change your net banking and UPI passwords and enable SMS/email alerts for all transactions.",
            },
        ],
        "medium": [
            {
                "title": "Double-check with the bank",
                "text": "If the message mentions blocking, suspension, or urgent action, confirm directly with your bank.",
            },
            {
                "title": "Ignore unknown numbers",
                "text": "Avoid calling or messaging back unknown phone numbers claiming to be from the bank.",
            },
            {
                "title": "Watch for pressure tactics",
                "text": "Scammers create urgency like 'last chance' or 'account will be closed'. Take time to verify first.",
            },
        ],
    },
    "KYC Scam": {
        "high": [
            {
                "title": "Do not submit KYC over links",
                "text": "Banks do not ask you to update KYC through random links on WhatsApp or SMS.",
            },
            {
                "title": "Report fake KYC requests",
                "text": "Forward the message to your bank’s fraud email or helpline and delete it from your phone.",
            },
            {
                "title": "Never share full ID documents",
                "text": "Do not share Aadhaar, PAN, or ID photos over chat unless you initiated the process with a verified channel.",
            },
        ],
        "medium": [
            {
                "title": "Confirm KYC status from bank",
                "text": "Use official mobile or net banking apps to check if your KYC is actually pending.",
            },
            {
                "title": "Beware of blocking threats",
                "text": "Messages threatening immediate account closure for KYC are a classic scam pattern.",
            },
            {
                "title": "Type URLs yourself",
                "text": "If you must update KYC, type your bank’s URL manually in the browser instead of clicking any message link.",
            },
        ],
    },
    "Lottery Scam": {
        "high": [
            {
                "title": "You do not win random lotteries",
                "text": "If you never entered a contest or lottery, you cannot win it. Treat such messages as scams.",
            },
            {
                "title": "Never pay to claim a prize",
                "text": "Legitimate contests do not ask for fees, taxes, or OTPs to release your prize.",
            },
            {
                "title": "Do not share bank details",
                "text": "Avoid sharing account numbers, cards, or OTPs to receive a so-called 'lottery' reward.",
            },
        ],
        "medium": [
            {
                "title": "Check official announcements",
                "text": "Real contests publish winners on official websites or news, not just via random SMS/WhatsApp.",
            },
            {
                "title": "Search for scam reports",
                "text": "Look up the message text or phone number on the internet from a safe device to see if others reported it.",
            },
            {
                "title": "Be skeptical of big rewards",
                "text": "Huge rewards with very little effort are almost always scams.",
            },
        ],
    },
    "Tech Support Scam": {
        "high": [
            {
                "title": "Do not grant remote access",
                "text": "Never install remote-access apps like AnyDesk or TeamViewer at the request of a stranger.",
            },
            {
                "title": "Do not share banking details",
                "text": "Tech support will never ask for your OTP, UPI PIN, or card details to 'fix' an issue.",
            },
            {
                "title": "Disconnect immediately",
                "text": "End the call or chat, uninstall any unknown remote tools, and run a security scan on your device.",
            },
        ],
        "medium": [
            {
                "title": "Use official support channels",
                "text": "Contact support via numbers or chat options listed on the official website or app only.",
            },
            {
                "title": "Avoid unsolicited popups",
                "text": "Ignore popups claiming your device is infected and offering a support phone number.",
            },
            {
                "title": "Verify company identity",
                "text": "Ask for official email confirmation and cross-check the sender domain and contact details.",
            },
        ],
    },
    "Legitimate": {
        "high": [],
        "medium": [],
    },
}


def get_tips_for_result(scam_type: str, risk_score: float) -> List[Tip]:
    """
    Return a list of tips based on scam type and risk score.
    High risk >= 70, medium 40-70, safe < 40.
    """
    if risk_score >= 70:
        level = "high"
    elif risk_score >= 40:
        level = "medium"
    else:
        # Safe – generic reminders
        return BASE_SAFE_TIPS

    scam_type_key = scam_type if scam_type in SCAM_TYPE_TIPS else "Legitimate"
    tips_for_type = SCAM_TYPE_TIPS.get(scam_type_key, {}).get(level, [])

    # Fallback to base safe tips if we somehow have no type-specific tips
    if not tips_for_type:
        return BASE_SAFE_TIPS
    return tips_for_type

