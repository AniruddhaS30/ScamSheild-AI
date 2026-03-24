import streamlit as st
import tensorflow as tf
import pickle
import re
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import time

st.set_page_config(page_title="ScamShield AI", page_icon="🛡️", layout="wide")

@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('model/scam_model.h5')
    with open('model/vectorizer.pkl', 'rb') as f:
        vectorizer_config = pickle.load(f)
    vectorizer_layer = tf.keras.layers.TextVectorization.from_config(vectorizer_config)
    return model, vectorizer_layer

try:
    model, vectorizer_layer = load_model()
except Exception as e:
    st.error(f"Error loading model: {e}")
    st.stop()

def predict_scam(text):
    clean = re.sub(r'[^a-zA-Z0-9!$]', ' ', text).lower()
    vec = vectorizer_layer(tf.expand_dims(tf.constant(clean), 0))
    prob = model.predict(vec, verbose=0)[0][0]
    return float(prob) * 100

def detect_scam_type(text):
    text_lower = text.lower()
    if 'kyc' in text_lower:
        return "KYC Scam 🪪"
    elif any(word in text_lower for word in ['lottery', 'won', 'prize', 'inam']):
        return "Lottery Scam 🎰"
    elif any(word in text_lower for word in ['bank', 'sbi', 'hdfc', 'icici', 'account']):
        return "Bank Fraud 🏦"
    elif any(word in text_lower for word in ['login', 'suspicious', 'verify', 'security']):
        return "Account Takeover 🔐"
    elif 'otp' in text_lower and any(word in text_lower for word in ['immediately', 'urgent', 'now', 'share', 'send']):
        return "OTP Fraud 📲"
    else:
        return "Unknown Scam Type"

with st.sidebar:
    st.title("🛡️ ScamShield AI")
    with st.spinner("Loading model..."):
        st.success("✅ Model Ready")
    st.markdown("### How it works:")
    st.markdown("1. **Input**: Enter SMS or chat message")
    st.markdown("2. **Analyze**: AI predicts scam probability")
    st.markdown("3. **Detect**: Identifies scam type & keywords")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔍 Analyzer", "💬 Simulator", "📊 Dashboard", "📞 AI Call Screen", "ℹ️ About"])

with tab1:
    st.header("🔍 Message Analyzer")
    text_input = st.text_area("Enter SMS message or conversation", height=100)
    sample_options = [
        "Your SBI account will be blocked. Share OTP immediately to verify.",
        "Congratulations! You won Rs.50000 in KBC lottery. Share OTP to claim.",
        "Your KYC expired. Share OTP with our agent or account gets blocked.",
        "Suspicious login detected. Verify by sharing OTP sent to your number.",
        "Hi I am calling from your bank. Share OTP urgently to secure account."
    ]
    sample = st.selectbox("Try a Sample Message", [""] + sample_options)
    if sample:
        text_input = sample
    if st.button("Analyze"):
        if text_input.strip():
            prob = predict_scam(text_input)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Scam Risk Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "green"},
                        {'range': [40, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
            fig.update_layout(template="plotly_dark")
            st.plotly_chart(fig)
            if prob < 40:
                st.success("🟢 LOW RISK - Likely Legitimate")
                scam_type = "Legitimate ✅"
            elif prob < 70:
                st.warning("🟡 MEDIUM RISK - Exercise Caution")
                scam_type = detect_scam_type(text_input)
            else:
                st.error("🔴 HIGH RISK - Potential Scam")
                scam_type = detect_scam_type(text_input)
            st.markdown(f"**Scam Type:** {scam_type}")
            suspicious_words = {
                'high': ['otp', 'share', 'immediately', 'urgent', 'verify', 'blocked', 'suspicious'],
                'medium': ['bank', 'account', 'kyc', 'login', 'prize', 'won', 'lottery']
            }
            def highlight_text(text):
                for word in suspicious_words['high']:
                    text = re.sub(r'\b' + re.escape(word) + r'\b', f'<span style="color:red;font-weight:bold;">{word}</span>', text, flags=re.IGNORECASE)
                for word in suspicious_words['medium']:
                    text = re.sub(r'\b' + re.escape(word) + r'\b', f'<span style="color:orange;font-weight:bold;">{word}</span>', text, flags=re.IGNORECASE)
                return text
            highlighted = highlight_text(text_input)
            st.markdown("**Message with highlights:**")
            st.markdown(highlighted, unsafe_allow_html=True)
            tips = {
                "KYC Scam 🪪": ["Never share KYC documents with unsolicited calls", "Verify caller identity through official channels", "Report suspicious KYC requests to your bank"],
                "Lottery Scam 🎰": ["No legitimate lottery requires upfront payment", "Verify winnings through official lottery websites", "Be wary of calls claiming you've won prizes"],
                "Bank Fraud 🏦": ["Banks never ask for OTP or PIN over phone", "Hang up and call back using official number", "Enable transaction alerts for monitoring"],
                "Account Takeover 🔐": ["Don't click suspicious login links", "Use two-factor authentication", "Monitor account activity regularly"],
                "OTP Fraud 📲": ["Never share OTP with anyone", "Verify the request source", "Use app-based authentication when possible"],
                "Legitimate ✅": ["Continue normal banking practices", "Stay vigilant for future scams", "Use official apps and websites"],
                "Unknown Scam Type": ["Be cautious with unsolicited requests", "Verify information independently", "Report suspicious activity"]
            }
            st.markdown("**Awareness Tips:**")
            for tip in tips.get(scam_type, tips["Unknown Scam Type"]):
                st.markdown(f"- {tip}")
            if 'scans' not in st.session_state:
                st.session_state.scans = []
            st.session_state.scans.append({
                'text': text_input,
                'score': prob,
                'type': scam_type
            })
        else:
            st.error("Please enter a message to analyze.")

with tab2:
    st.header("💬 Scam Conversation Simulator")
    conversations = {
        "Bank OTP Scam": [
            {"sender": "scammer", "msg": "Hello, this is SBI customer care. Your account shows suspicious activity."},
            {"sender": "victim", "msg": "Oh no, what should I do?"},
            {"sender": "scammer", "msg": "We need to verify your identity. Please share the OTP sent to your registered number."},
            {"sender": "victim", "msg": "Okay, the OTP is 123456"},
            {"sender": "scammer", "msg": "Thank you. Your account is now secure."}
        ],
        "Lottery Win": [
            {"sender": "scammer", "msg": "CONGRATULATIONS! You won Rs.1,00,000 in our lucky draw!"},
            {"sender": "victim", "msg": "Really? How do I claim it?"},
            {"sender": "scammer", "msg": "Just share your bank details and OTP for verification."},
            {"sender": "victim", "msg": "Here is my account number: 1234567890"},
            {"sender": "scammer", "msg": "Great! Now send the OTP to confirm."}
        ],
        "KYC Update": [
            {"sender": "scammer", "msg": "Your KYC is expired. Account will be blocked in 24 hours."},
            {"sender": "victim", "msg": "What do I need to do?"},
            {"sender": "scammer", "msg": "Our agent will call you. Share OTP when asked."},
            {"sender": "victim", "msg": "Okay, I will wait."},
            {"sender": "scammer", "msg": "This is the agent. Please share your OTP now."}
        ]
    }
    selected_conv = st.selectbox("Choose a Conversation Scenario", list(conversations.keys()))
    if 'conv_index' not in st.session_state:
        st.session_state.conv_index = 0
    if 'current_conv' not in st.session_state or st.session_state.current_conv != selected_conv:
        st.session_state.current_conv = selected_conv
        st.session_state.conv_index = 0
        st.session_state.messages = []
        st.session_state.scores = []
    if st.button("▶ Next Message") and st.session_state.conv_index < len(conversations[selected_conv]):
        msg = conversations[selected_conv][st.session_state.conv_index]
        st.session_state.messages.append(msg)
        st.session_state.conv_index += 1
        full_text = ' '.join([m['msg'] for m in st.session_state.messages])
        score = predict_scam(full_text)
        st.session_state.scores.append(score)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        if msg['sender'] == 'scammer':
            st.markdown(f'<div class="chat-bubble scammer">{msg["msg"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble victim">{msg["msg"]}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    if st.session_state.scores:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(1, len(st.session_state.scores)+1)), y=st.session_state.scores, mode='lines+markers', name='Risk Score'))
        fig.update_layout(title="Risk Score Over Conversation", xaxis_title="Message Number", yaxis_title="Risk Score %", template="plotly_dark")
        st.plotly_chart(fig)
    st.markdown("""
    <style>
    .chat-container {
        max-height: 400px;
        overflow-y: auto;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 10px;
    }
    .chat-bubble {
        padding: 10px;
        margin: 5px 0;
        border-radius: 10px;
        max-width: 70%;
    }
    .scammer {
        background-color: #333;
        color: white;
        text-align: left;
        margin-right: auto;
    }
    .victim {
        background-color: #007bff;
        color: white;
        text-align: right;
        margin-left: auto;
    }
    </style>
    """, unsafe_allow_html=True)

with tab3:
    st.header("📊 Analysis Dashboard")
    if 'scans' in st.session_state and st.session_state.scans:
        scans = st.session_state.scans
        total_scanned = len(scans)
        flagged = len([s for s in scans if s['score'] >= 40])
        avg_score = np.mean([s['score'] for s in scans])
        type_counts = pd.Series([s['type'] for s in scans]).value_counts()
        most_common = type_counts.idxmax() if not type_counts.empty else "None"
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Scanned", total_scanned)
        with col2:
            st.metric("Flagged as Scam", flagged)
        with col3:
            st.metric("Avg Risk Score", f"{avg_score:.1f}%")
        with col4:
            st.metric("Most Common Type", most_common)
        fig_bar = px.bar(x=[f"Scan {i+1}" for i in range(len(scans))], y=[s['score'] for s in scans], color=[s['score'] for s in scans], color_continuous_scale=['green', 'yellow', 'red'], title="Risk Scores of All Scans")
        fig_bar.update_layout(template="plotly_dark")
        st.plotly_chart(fig_bar)
        if not type_counts.empty:
            fig_pie = px.pie(values=type_counts.values, names=type_counts.index, title="Scam Type Distribution")
            fig_pie.update_layout(template="plotly_dark")
            st.plotly_chart(fig_pie)
    else:
        st.info("No scans yet. Use the Analyzer tab to get started.")

with tab4:
    st.header("📞 AI Call Screen")
    st.markdown("### Simulating an incoming call with AI-powered scam detection")
    
    call_scripts = {
        "Bank Fraud": [
            "Hello, am I speaking with the account holder?",
            "This is Rahul from SBI Bank fraud department.",
            "We have detected suspicious activity on your account.",
            "Your account will be blocked in 10 minutes.",
            "To prevent this, I need to verify your identity.",
            "Please share the OTP sent to your registered number.",
            "This is urgent, your account security is at risk."
        ],
        "KYC Scam": [
            "Hello, I am calling from your bank's KYC department.",
            "Your KYC documents have expired as of today.",
            "Your account will be frozen within 24 hours.",
            "I can help you update your KYC right now over the phone.",
            "I just need your Aadhaar number and the OTP for verification.",
            "This is a mandatory RBI regulation, you must comply.",
            "Please share the OTP you just received."
        ],
        "Lottery Scam": [
            "Congratulations! You have won 50 lakh rupees!",
            "This is from KBC Lottery department.",
            "Your number was selected from 10 million participants.",
            "To claim your prize you need to verify your identity.",
            "Please share your bank account OTP for the transfer.",
            "The prize money will be credited within 2 hours.",
            "This offer expires today, please hurry."
        ]
    }
    
    selected_script = st.selectbox("Select a Call Scenario", list(call_scripts.keys()))
    
    if 'call_screening' not in st.session_state:
        st.session_state.call_screening = False
        st.session_state.call_transcript = []
        st.session_state.call_scores = []
        st.session_state.current_script = None
    
    if selected_script != st.session_state.current_script:
        st.session_state.call_transcript = []
        st.session_state.call_scores = []
        st.session_state.call_screening = False
        st.session_state.current_script = selected_script
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("▶ Start AI Screening", use_container_width=True):
            st.session_state.call_screening = True
            st.session_state.call_transcript = []
            st.session_state.call_scores = []
    
    if st.session_state.call_screening:
        script = call_scripts[selected_script]
        placeholder = st.empty()
        
        for msg in script:
            with placeholder.container():
                st.markdown("""
                <style>
                .phone-mockup {
                    max-width: 400px;
                    margin: 20px auto;
                    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
                    border-radius: 40px;
                    padding: 20px;
                    border: 8px solid #0f3460;
                    box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
                    font-family: Arial, sans-serif;
                }
                .call-header {
                    text-align: center;
                    color: #00F5D4;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 15px;
                }
                .phone-number {
                    text-align: center;
                    color: #FFFFFF;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    font-family: monospace;
                }
                .status-indicator {
                    text-align: center;
                    margin-bottom: 15px;
                }
                .pulsing-dot {
                    display: inline-block;
                    width: 10px;
                    height: 10px;
                    background-color: #00FF00;
                    border-radius: 50%;
                    animation: pulse 1.5s infinite;
                }
                @keyframes pulse {
                    0% { opacity: 1; }
                    50% { opacity: 0.5; }
                    100% { opacity: 1; }
                }
                .status-text {
                    color: #FFFFFF;
                    font-size: 12px;
                    margin-top: 5px;
                }
                .transcript-box {
                    background-color: #0D1B2A;
                    border: 1px solid #00F5D4;
                    border-radius: 10px;
                    padding: 15px;
                    max-height: 200px;
                    overflow-y: auto;
                    margin: 15px 0;
                    color: #FFFFFF;
                    font-size: 13px;
                    line-height: 1.5;
                }
                .gauge-container {
                    margin: 15px 0;
                }
                .action-buttons {
                    display: flex;
                    gap: 10px;
                    margin-top: 15px;
                }
                </style>
                <div class="phone-mockup">
                    <div class="call-header">📞 Incoming Call</div>
                    <div class="phone-number">+91 98765 43210</div>
                    <div class="status-indicator">
                        <div class="pulsing-dot"></div>
                        <div class="status-text">AI is screening this call...</div>
                    </div>
                    <div class="transcript-box">
                """, unsafe_allow_html=True)
                
                st.session_state.call_transcript.append(msg)
                for line in st.session_state.call_transcript:
                    st.markdown(f"**Caller:** {line}")
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            full_transcript = " ".join(st.session_state.call_transcript)
            score = predict_scam(full_transcript)
            st.session_state.call_scores.append(score)
            
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=score,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Call Risk Score"},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "green"},
                        {'range': [40, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "red"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}
                }
            ))
            fig.update_layout(template="plotly_dark", height=300, margin=dict(l=50, r=50, t=50, b=50))
            st.plotly_chart(fig, use_container_width=True)
            
            time.sleep(1.5)
        
        st.markdown("---")
        st.subheader("📊 Final Analysis")
        
        final_score = st.session_state.call_scores[-1] if st.session_state.call_scores else 0
        
        if final_score > 70:
            st.error(f"🚨 HIGH SCAM RISK ({final_score:.1f}%) - Recommend Declining")
        elif final_score > 40:
            st.warning(f"⚠️ SUSPICIOUS ({final_score:.1f}%) - Proceed with caution")
        else:
            st.success(f"✅ Likely Safe ({final_score:.1f}%) - You may answer")
        
        st.markdown("### Why AI thinks this is a scam:")
        
        full_text = " ".join(st.session_state.call_transcript).lower()
        
        scam_reasons = []
        urgency_words = ["urgent", "immediately", "now", "quickly", "hurry", "10 minutes", "24 hours", "today"]
        authority_words = ["sbi", "bank", "fraud", "rbi", "department", "regulation", "kyc"]
        otp_words = ["otp", "share", "verify", "code", "confirm"]
        fear_words = ["blocked", "frozen", "closed", "disabled", "suspended", "expires", "will be"]
        
        if any(word in full_text for word in urgency_words):
            scam_reasons.append(("⏰ Urgency Language", "Detected: 'urgent', 'blocked', '10 minutes'"))
        if any(word in full_text for word in authority_words):
            scam_reasons.append(("🏛️ Authority Impersonation", "Detected: Bank/RBI/Department names"))
        if any(word in full_text for word in otp_words):
            scam_reasons.append(("📱 OTP Solicitation", "Direct request for verification codes"))
        if any(word in full_text for word in fear_words):
            scam_reasons.append(("😨 Fear Tactics", "Detected: 'account blocked', 'frozen', 'expires'"))
        
        if scam_reasons:
            cols = st.columns(2)
            for idx, (reason, detail) in enumerate(scam_reasons):
                with cols[idx % 2]:
                    st.markdown(f"**{reason}**  \n{detail}")
        else:
            st.info("No major scam indicators detected in this call.")
        
        st.markdown("### Top Scam Trigger Words:")
        
        high_risk_words = ['otp', 'share', 'immediately', 'urgent', 'verify', 'blocked', 'suspicious', 'kyc', 'bank', 'account', 'frozen', 'expires']
        found_words = {}
        
        for word in high_risk_words:
            count = full_text.count(word)
            if count > 0:
                found_words[word] = count
        
        if found_words:
            sorted_words = sorted(found_words.items(), key=lambda x: x[1], reverse=True)[:8]
            for word, count in sorted_words:
                risk_weight = min((count / max(found_words.values())) * 100 if found_words.values() else 0, 100)
                st.markdown(f"**{word}** - Risk: {'█' * int(risk_weight/10)}{'░' * (10-int(risk_weight/10))} {risk_weight:.0f}%")
        else:
            st.info("No scam trigger words detected.")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.call_screening = False
                st.session_state.call_transcript = []
                st.session_state.call_scores = []
                st.rerun()

with tab5:
    st.header("ℹ️ About ScamShield AI")
    st.markdown("""
    **ScamShield AI** is an advanced AI-powered tool designed to detect and prevent OTP-based scams in real-time. Using state-of-the-art Bidirectional LSTM neural networks, it analyzes text messages and conversations to identify potential fraudulent activities.

    ### Team: CIPHER NOVA

    ### Domain: AI in Cybersecurity

    ### Event: National Level AI Hackathon - AiFi, REVA University

    ### Tech Stack:
    - **Python** - Core programming language
    - **TensorFlow/Keras** - Deep learning framework for LSTM model
    - **Streamlit** - Web application framework
    - **Plotly** - Interactive data visualizations
    - **Pandas/Numpy** - Data processing

    """)
