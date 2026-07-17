import streamlit as st
from groq import Groq
import os

# Get free key from console.groq.com
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", os.environ.get("GROQ_API_KEY")))

SYSTEM_PROMPT = """You are the ancient spirit inside a cursed monkey's paw. You are old, cruel, and impossibly literal.

YOUR JOB:
Grant the wish by exploiting the EXACT WORDING. Find the worst technically-true interpretation. The horror must come FROM THE WORDS THEMSELVES.

RULES:
- 3-5 sentences only
- Second person, ominous, matter-of-fact
- Never give them what they meant, only what they SAID
- Build on previous wishes - make it escalate
- Never explain the joke, never break character

EXAMPLES:
Wish: "I wish to be rich" -> You are rich. Your bank account now holds $47 million from the life insurance payout after your entire family died in an accident this morning. The money is already cleared.

Wish: "I wish my crush would love me" -> She loves you. Incessantly. She is now outside your window, has been for 8 hours, whispering your name and won't leave even when police are called. She says you wished for this.

Wish number: {wish_count}. CURSE LEVEL: 5/5 - maximum darkness. Make the consequences truly catastrophic and irreversible."""

# Initialize session state
if 'history' not in st.session_state:
    st.session_state.history = []
if 'wish_count' not in st.session_state:
    st.session_state.wish_count = 0

# Page config
st.set_page_config(
    page_title="The Monkey's Paw", 
    page_icon="🐾",
    layout="centered"
)

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0e0e0e;
    }
    .main-title {
        text-align: center;
        color: #ff4444;
        font-size: 3em;
        text-shadow: 2px 2px 4px #000000;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-style: italic;
    }
    .wish-counter {
        font-family: monospace;
        font-size: 1.2em;
        text-align: center;
        padding: 10px;
        background-color: #1a1a1a;
        border-radius: 5px;
        margin: 10px 0;
        color: #ff4444;
    }
    .wish-display {
        background-color: #1a1a1a;
        padding: 15px;
        border-left: 4px solid #ff4444;
        margin: 10px 0;
        border-radius: 5px;
    }
    .paw-response {
        background-color: #2a0a0a;
        padding: 15px;
        border: 2px solid #ff4444;
        margin: 10px 0;
        border-radius: 5px;
        color: #ffcccc;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-title">🐾 THE MONKEY\'S PAW 🐾</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">A withered paw sits before you. It is listening.</p>', unsafe_allow_html=True)

# Display wish counter only (no level shown)
st.markdown(f'<div class="wish-counter">Wishes made: {st.session_state.wish_count}</div>', unsafe_allow_html=True)

st.markdown("---")

# Display conversation history
if st.session_state.history:
    for i, msg in enumerate(st.session_state.history):
        if msg['role'] == 'user':
            wish_text = msg['content'].split(':', 1)[1].strip(' "')
            st.markdown(f'<div class="wish-display"><strong>YOUR WISH:</strong> {wish_text}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="paw-response">The paw curls...<br><br>{msg["content"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

# Input form
with st.form(key='wish_form', clear_on_submit=True):
    wish = st.text_input("Type your wish:", placeholder="I wish for...")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        submit = st.form_submit_button("🐾 MAKE WISH", use_container_width=True, type="primary")
    
    with col2:
        reset = st.form_submit_button("🔄 RESET", use_container_width=True)

# Handle reset
if reset:
    st.session_state.history = []
    st.session_state.wish_count = 0
    st.rerun()

# Handle wish submission
if submit and wish:
    st.session_state.wish_count += 1
    
    # Add to history
    st.session_state.history.append({
        "role": "user", 
        "content": f'Wish #{st.session_state.wish_count}: "{wish}"'
    })
    
    # Get response
    with st.spinner("The paw curls..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                temperature=1.5,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT.format(
                        wish_count=st.session_state.wish_count,
                        curse_level=5  # Always max level
                    )},
                    *st.session_state.history
                ]
            )
            
            answer = response.choices[0].message.content
            st.session_state.history.append({
                "role": "assistant",
                "content": answer
            })
            
        except Exception as e:
            st.error(f"The paw rejects your wish. Error: {str(e)}")
    
    st.rerun()

# Footer
st.markdown("---")
st.caption("⚠️ Press RESET to flee while you still can...")
