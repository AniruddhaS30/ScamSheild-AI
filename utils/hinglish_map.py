HINGLISH_TO_ENGLISH = {
    "otp mat dena": "do not share otp",
    "otp nahi dena": "do not share otp",
    "otp share mat": "do not share otp",
    "otp de do": "give otp",
    "otp bhej do": "send otp",
    "otp urgently bhejo": "send otp urgently",
    "account band ho jayega": "account will be blocked",
    "account block ho jayega": "account will be blocked",
    "account band ho jaega": "account will be blocked",
    "account block ho jaega": "account will be blocked",
    "turant otp": "urgent otp",
    "turant bhejo": "send urgently",
    "abhi bhejo": "send now",
    "abhi otp do": "give otp now",
    "turant karo": "do urgently",
    "turant verify": "verify urgently",
    "kyc update karo": "update kyc",
    "kyc nahi kiya": "kyc not done",
    "kyc expire ho gaya": "kyc expired",
    "kyc nahi hoga to account band": "if kyc not done account will be blocked",
    "lottery jeet li": "won lottery",
    "aap jeet gaye": "you have won",
    "inam": "prize",
    "inaam": "prize",
    "reward mila": "got reward",
    "free gift": "free gift",
    "price jeet": "won prize",
    "cash jeet": "won cash",
    "paise jeet": "won money",
    "link par click": "click on link",
    "ye link khol": "open this link",
    "link open karo": "open link",
    "verify karo": "verify",
    "verify karna hai": "need to verify",
    "bank se bol raha": "calling from bank",
    "bank se call": "call from bank",
    "customer care se": "from customer care",
    "technical support se": "from technical support",
    "tech support se": "from tech support",
    "remote access": "remote access",
    "anydesk install": "install anydesk",
    "teamviewer install": "install teamviewer",
    "screen share karo": "share screen",
    "screenshot bhejo": "send screenshot",
}

def normalize_hinglish(text: str) -> str:
    """
    Replace common Hinglish scam phrases with their English equivalents.
    Uses simple substring replacement on lowercased text.
    """
    if not text:
        return text
    normalized = text.lower()
    for hinglish, english in HINGLISH_TO_ENGLISH.items():
        if hinglish in normalized:
            normalized = normalized.replace(hinglish, english)
    return normalized

