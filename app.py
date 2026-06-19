import streamlit as st
import streamlit.components.v1 as components
import google.generativeai as genai
from dotenv import load_dotenv
import os
import re
import html

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')

def ask_gemini(prompt):
    response = model.generate_content(prompt)
    return response.text

def truncate_text(text, max_chars=12000):
    """Safety cap so very large uploaded files don't blow past the model's context window."""
    if text and len(text) > max_chars:
        return text[:max_chars] + "\n\n[Content truncated due to length…]"
    return text

st.set_page_config(
    page_title="AI Study Buddy",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; }
html, body, .stApp { font-family: 'Inter', sans-serif; }

:root {
    --bg:          #06070f;
    --surface:     #0e1120;
    --surface2:    #151929;
    --border:      rgba(139,92,246,0.18);
    --border-hi:   rgba(139,92,246,0.55);
    --accent:      #7c3aed;
    --accent2:     #a78bfa;
    --accent3:     #ec4899;
    --text:        #e8e4f0;
    --muted:       #8b8fa8;
    --success-bg:  rgba(16,185,129,0.10);
    --success-bdr: rgba(16,185,129,0.35);
    --error-bg:    rgba(239,68,68,0.10);
    --error-bdr:   rgba(239,68,68,0.35);
    --radius:      10px;
}

.stApp {
    background: var(--bg);
    background-image:
        radial-gradient(ellipse 70% 45% at 15% 5%,  rgba(124,58,237,0.10) 0%, transparent 65%),
        radial-gradient(ellipse 55% 35% at 85% 90%, rgba(236,72,153,0.07) 0%, transparent 60%);
    color: var(--text);
}

#MainMenu, footer { visibility: hidden; }
header { visibility: visible !important; background: transparent !important; }
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* Hide streamlit's own toggle buttons - we replace them */
[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}
.block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; }

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    min-height: 100vh;
    overflow-y: auto;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 1.5rem 1rem 2rem 1rem !important;
}
.sb-brand {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.75rem 1.2rem 0.75rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.8rem;
}
.sb-brand-icon { font-size: 1.6rem; }
.sb-brand-name {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.1rem;
    background: linear-gradient(110deg, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stSidebar"] .stRadio > label {
    color: var(--muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
    gap: 0.15rem !important;
    display: flex !important;
    flex-direction: column !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #c4b5fd !important;
    font-size: 0.93rem !important;
    font-weight: 500 !important;
    padding: 0.5rem 0.75rem !important;
    border-radius: var(--radius) !important;
    transition: background 0.18s, color 0.18s !important;
    cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    background: rgba(124,58,237,0.12) !important;
    color: #fff !important;
}

/* ── TYPOGRAPHY ── */
h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 2.4rem !important;
    background: linear-gradient(110deg, #a78bfa 0%, #7c3aed 45%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px;
    line-height: 1.2 !important;
}
h2 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: #e2d9f3 !important;
    font-size: 1.35rem !important;
}
h3 { color: #a78bfa !important; font-family: 'Syne', sans-serif !important; font-size: 1rem !important; }
p  { color: #c4b5fd !important; line-height: 1.7; }
li { color: #a0aec0 !important; }
strong { color: #e2d9f3 !important; }
[data-testid="stCaptionContainer"] p { color: var(--muted) !important; font-size: 0.95rem; text-align: center; }

/* ── INPUTS ── */
.stTextInput > div > div,
.stTextArea  > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
.stTextInput > div > div:focus-within,
.stTextArea  > div > div:focus-within {
    border-color: var(--border-hi) !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12) !important;
}
.stSelectbox > div > div {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}
input, textarea { color: var(--text) !important; background: transparent !important; }
input::placeholder, textarea::placeholder { color: var(--muted) !important; }

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] section {
    background: var(--surface) !important;
    border: 1.5px dashed var(--border-hi) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stFileUploader"] section small { color: var(--muted) !important; }
[data-testid="stFileUploaderFile"] { color: var(--text) !important; }

/* ── BUTTONS ── */
.stButton > button {
    background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.8rem !important;
    font-size: 0.93rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.22s ease !important;
    box-shadow: 0 4px 18px rgba(124,58,237,0.32) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 26px rgba(124,58,237,0.48) !important;
    background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── ALERTS ── */
.stAlert {
    background: rgba(124,58,237,0.10) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: #c4b5fd !important;
}

/* ── SLIDER ── */
.stSlider > div > div > div { background: var(--accent) !important; }

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── PAGE HEADER ── */
.page-header { margin-bottom: 1.6rem; }
.page-tag {
    display: inline-block;
    background: rgba(124,58,237,0.15);
    border: 1px solid var(--border);
    color: var(--accent2);
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    margin-bottom: 0.5rem;
}
.page-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 1.7rem;
    color: #e2d9f3;
    margin-bottom: 0.3rem;
}
.page-desc { color: var(--muted); font-size: 0.92rem; }

/* ── QUIZ CARDS ── */
.quiz-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.3rem 1.5rem;
    margin-bottom: 1.2rem;
    transition: border-color 0.2s;
}
.quiz-card:hover { border-color: var(--border-hi); }
.quiz-num {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent2);
    margin-bottom: 0.5rem;
}
.quiz-q {
    color: #e2d9f3;
    font-weight: 600;
    font-size: 0.97rem;
    line-height: 1.55;
}
.quiz-result-correct {
    margin-top: 0.8rem;
    padding: 0.5rem 0.9rem;
    background: var(--success-bg);
    border: 1px solid var(--success-bdr);
    border-radius: 8px;
    color: #6ee7b7;
    font-weight: 600;
    font-size: 0.88rem;
}
.quiz-result-wrong {
    margin-top: 0.8rem;
    padding: 0.5rem 0.9rem;
    background: var(--error-bg);
    border: 1px solid var(--error-bdr);
    border-radius: 8px;
    color: #fca5a5;
    font-weight: 600;
    font-size: 0.88rem;
}
.quiz-correct-ans { margin-top: 0.4rem; color: #86efac; font-size: 0.86rem; }

/* ── SCORE BANNER ── */
.score-banner {
    background: linear-gradient(135deg, rgba(124,58,237,0.18), rgba(236,72,153,0.10));
    border: 1px solid var(--border-hi);
    border-radius: 12px;
    padding: 1rem 1.4rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    gap: 0.8rem;
}
.score-num {
    font-family: 'Syne', sans-serif;
    font-size: 2rem;
    font-weight: 800;
    color: var(--accent2);
}
.score-label { font-size: 0.88rem; color: var(--muted); }

/* ── FLIP FLASHCARDS ── */
.flash-hint {
    color: var(--muted);
    font-size: 0.85rem;
    margin-bottom: 0.9rem;
}
.flash-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.1rem;
    margin-bottom: 1rem;
}
.flip-card {
    background-color: transparent;
    height: 230px;
    perspective: 1200px;
}
.flip-card-inner {
    position: relative;
    width: 100%;
    height: 100%;
    transition: transform 0.55s cubic-bezier(0.4, 0.2, 0.2, 1);
    transform-style: preserve-3d;
}
.flip-card.flipped .flip-card-inner { transform: rotateY(180deg); }
.flip-face {
    position: absolute;
    width: 100%;
    height: 100%;
    -webkit-backface-visibility: hidden;
    backface-visibility: hidden;
    border-radius: 12px;
    padding: 1.25rem 1.35rem;
    display: flex;
    flex-direction: column;
    overflow-y: auto;
    border: 1px solid var(--border);
    transition: border-color 0.2s;
}
.flip-card:hover .flip-face { border-color: var(--border-hi); }
.flip-front {
    background: var(--surface);
    justify-content: space-between;
}
.flip-back {
    background: var(--surface2);
    transform: rotateY(180deg);
    justify-content: space-between;
}
.flip-num {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--muted);
    margin-bottom: 0.5rem;
}
.flip-label {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.5rem;
}
.flip-label.q-label { color: var(--accent2); }
.flip-label.a-label { color: #6ee7b7; }
.flip-q-text {
    color: #e2d9f3;
    font-weight: 600;
    font-size: 0.97rem;
    line-height: 1.5;
    flex-grow: 1;
}
.flip-a-text {
    color: #e2d9f3;
    font-size: 0.93rem;
    line-height: 1.55;
    flex-grow: 1;
}
</style>
""", unsafe_allow_html=True)

if "quiz_data"        not in st.session_state: st.session_state.quiz_data        = []
if "quiz_answers"     not in st.session_state: st.session_state.quiz_answers     = {}
if "quiz_submitted"   not in st.session_state: st.session_state.quiz_submitted   = False
if "quiz_topic"       not in st.session_state: st.session_state.quiz_topic       = ""
if "quiz_full_input"  not in st.session_state: st.session_state.quiz_full_input  = ""
if "quiz_batch"       not in st.session_state: st.session_state.quiz_batch       = 1
if "flash_data"       not in st.session_state: st.session_state.flash_data       = []
if "flash_topic"      not in st.session_state: st.session_state.flash_topic      = ""
if "flash_full_input" not in st.session_state: st.session_state.flash_full_input = ""
if "flash_flipped"    not in st.session_state: st.session_state.flash_flipped    = {}

def parse_quiz(text):
    blocks = re.split(r'\n(?=Q?\d+[\.\)])', text.strip())
    questions = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = [l.strip() for l in block.split('\n') if l.strip()]
        if not lines:
            continue
        q_text = lines[0]
        options, answer = [], ""
        for line in lines[1:]:
            if re.match(r'^[A-Da-d][\.\)]\s', line):
                options.append(line)
            elif re.match(r'^(Answer|Ans|Correct)[:\s]', line, re.IGNORECASE):
                answer = line.split(":", 1)[-1].strip() if ":" in line else line.split(None, 1)[-1].strip()
        if options:
            questions.append({"q": q_text, "options": options, "answer": answer})
    return questions


def generate_quiz_questions(topic, batch_num):
    prompt = f"""Generate 5 multiple-choice questions based on the following topic or content: '{topic}' (batch {batch_num}, use different questions each time).

Use EXACTLY this format — each part on its own line:

Q1. [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: B

Q2. [Question text]
...

Keep questions clear and progressively harder. Answer line must be just the letter."""
    return ask_gemini(prompt)


def render_quiz(questions):
    if not questions:
        return

    answered_all = len(st.session_state.quiz_answers) == len(questions)

    for i, item in enumerate(questions):
        q_key = f"quiz_q_{i}_b{st.session_state.quiz_batch}"
        st.markdown(f"""
        <div class="quiz-card">
            <div class="quiz-num">Question {i+1} &nbsp;·&nbsp; Batch {st.session_state.quiz_batch}</div>
            <div class="quiz-q">{item['q']}</div>
        </div>""", unsafe_allow_html=True)

        selected = st.radio(
            label=f"q{i}",
            options=item["options"],
            index=None,
            key=q_key,
            label_visibility="collapsed"
        )
        if selected and i not in st.session_state.quiz_answers:
            st.session_state.quiz_answers[i] = selected

        if st.session_state.quiz_submitted and i in st.session_state.quiz_answers:
            chosen = st.session_state.quiz_answers[i]
            chosen_match  = re.match(r'^([A-Da-d])', chosen.strip())
            correct_match = re.match(r'^([A-Da-d])', item["answer"].strip())
            chosen_letter  = chosen_match.group(1).upper()  if chosen_match  else ""
            correct_letter = correct_match.group(1).upper() if correct_match else ""

            if chosen_letter and chosen_letter == correct_letter:
                st.markdown('<div class="quiz-result-correct">✅ Correct!</div>', unsafe_allow_html=True)
            else:
                correct_option = next(
                    (opt for opt in item["options"]
                     if re.match(r'^([A-Da-d])', opt.strip()) and
                        re.match(r'^([A-Da-d])', opt.strip()).group(1).upper() == correct_letter),
                    item["answer"]
                )
                st.markdown(
                    f'<div class="quiz-result-wrong">❌ Incorrect'
                    f'<div class="quiz-correct-ans">✔ Correct answer: {correct_option}</div></div>',
                    unsafe_allow_html=True
                )
        st.markdown("<br>", unsafe_allow_html=True)

    if not st.session_state.quiz_submitted:
        if st.button("Submit Quiz ✔", disabled=not answered_all):
            st.session_state.quiz_submitted = True
            st.rerun()
    else:
        correct = sum(
            1 for i, item in enumerate(questions)
            if i in st.session_state.quiz_answers
            and re.match(r'^([A-Da-d])', st.session_state.quiz_answers[i].strip())
            and re.match(r'^([A-Da-d])', item["answer"].strip())
            and re.match(r'^([A-Da-d])', st.session_state.quiz_answers[i].strip()).group(1).upper()
            == re.match(r'^([A-Da-d])', item["answer"].strip()).group(1).upper()
        )
        total = len(questions)
        pct   = int(correct / total * 100)

        st.markdown(f"""
        <div class="score-banner">
            <div class="score-num">{correct}/{total}</div>
            <div>
                <div style="color:#e2d9f3;font-weight:600;">Batch {st.session_state.quiz_batch} Complete</div>
                <div class="score-label">You scored {pct}% &nbsp;·&nbsp; Topic: {st.session_state.quiz_topic}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ Next 5 Questions", use_container_width=True):
                with st.spinner("Generating next 5 questions…"):
                    result = generate_quiz_questions(
                        st.session_state.quiz_full_input,
                        st.session_state.quiz_batch + 1
                    )
                st.session_state.quiz_data      = parse_quiz(result)
                st.session_state.quiz_answers   = {}
                st.session_state.quiz_submitted = False
                st.session_state.quiz_batch    += 1
                st.rerun()
        with col2:
            if st.button("🔄 Start Over", use_container_width=True):
                st.session_state.quiz_data       = []
                st.session_state.quiz_answers    = {}
                st.session_state.quiz_submitted  = False
                st.session_state.quiz_topic      = ""
                st.session_state.quiz_full_input = ""
                st.session_state.quiz_batch      = 1
                st.rerun()

def parse_flashcards(text):
    cards_raw = re.split(r'\n(?=Card\s*\d+)', text.strip(), flags=re.IGNORECASE)
    cards = []
    for card in cards_raw:
        card = card.strip()
        if not card:
            continue
        lines = [l.strip() for l in card.split('\n') if l.strip()]
        if not lines:
            continue
        title, q_text, a_text = lines[0], "", ""
        for line in lines[1:]:
            if re.match(r'^Q\s*:', line, re.IGNORECASE):
                q_text = re.sub(r'^Q\s*:\s*', '', line, flags=re.IGNORECASE)
            elif re.match(r'^A\s*:', line, re.IGNORECASE):
                a_text = re.sub(r'^A\s*:\s*', '', line, flags=re.IGNORECASE)
        if q_text:
            cards.append({"title": title, "q": q_text, "a": a_text})
    return cards


def render_flashcards(cards):
    """Render flashcards as a grid of flip cards. Click 'Flip Card' under any card to reveal the answer.

    Note: flipping is driven by a Streamlit button + session_state (not raw onclick JS),
    because Streamlit's markdown renderer does not reliably execute inline HTML event
    handlers — that was the root cause of cards not flipping before.
    """
    if not cards:
        return

    st.markdown(
        '<div class="flash-hint">👆 Click <strong>Flip Card</strong> under any card to reveal the answer — click again to flip it back.</div>',
        unsafe_allow_html=True
    )

    n_cols = 3
    total  = len(cards)

    for row_start in range(0, total, n_cols):
        cols = st.columns(n_cols)
        for j in range(n_cols):
            idx = row_start + j
            if idx >= total:
                continue
            card = cards[idx]
            flipped = st.session_state.flash_flipped.get(idx, False)

            with cols[j]:
                title  = html.escape(card["title"])
                q_text = html.escape(card["q"])
                a_text = html.escape(card["a"]) if card["a"] else "<em>(no answer provided)</em>"
                flip_class = "flipped" if flipped else ""

                st.markdown(f"""
                <div class="flip-card {flip_class}">
                    <div class="flip-card-inner">
                        <div class="flip-face flip-front">
                            <div>
                                <div class="flip-num">{title}</div>
                                <div class="flip-label q-label">Question</div>
                                <div class="flip-q-text">{q_text}</div>
                            </div>
                        </div>
                        <div class="flip-face flip-back">
                            <div>
                                <div class="flip-num">{title}</div>
                                <div class="flip-label a-label">Answer</div>
                                <div class="flip-a-text">{a_text}</div>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                btn_label = "↩️ Show Question" if flipped else "🔄 Flip Card"
                if st.button(btn_label, key=f"flip_btn_{idx}", use_container_width=True):
                    st.session_state.flash_flipped[idx] = not flipped
                    st.rerun()


def extract_text_from_file(uploaded_file):
    """Extract plain text from an uploaded .txt, .pdf, or .docx file."""
    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception as e:
            st.error(f"Couldn't read the text file: {e}")
            return ""

    elif name.endswith(".pdf"):
        try:
            import PyPDF2
        except ImportError:
            st.error("Reading PDFs requires the **PyPDF2** package. Install it with:\n\n`pip install PyPDF2`")
            return ""
        try:
            reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += (page.extract_text() or "") + "\n"
            if not text.strip():
                st.warning("No extractable text was found in this PDF (it may be a scanned image).")
            return text
        except Exception as e:
            st.error(f"Couldn't read the PDF: {e}")
            return ""

    elif name.endswith(".docx"):
        try:
            import docx
        except ImportError:
            st.error("Reading Word documents requires the **python-docx** package. Install it with:\n\n`pip install python-docx`")
            return ""
        try:
            document = docx.Document(uploaded_file)
            return "\n".join(p.text for p in document.paragraphs)
        except Exception as e:
            st.error(f"Couldn't read the Word document: {e}")
            return ""

    else:
        st.error("Unsupported file type. Please upload a .txt, .pdf, or .docx file.")
        return ""


with st.sidebar:
    st.markdown("""
    <div class="sb-brand">
        <span class="sb-brand-icon">🎓</span>
        <span class="sb-brand-name">Study Buddy</span>
    </div>""", unsafe_allow_html=True)

    feature = st.radio(
        "TOOLS",
        options=[
            "💡 Concept Explainer",
            "📝 Note Summarizer",
            "🧠 Quiz Generator",
            "🃏 Flashcard Maker",
        ],
        label_visibility="visible"
    )

# ── Custom sidebar toggle button (uses components.html so JS actually runs) ──
components.html("""
<style>
#sb-toggle {
    position: fixed;
    top: 14px;
    left: 14px;
    z-index: 9999999;
    width: 38px;
    height: 38px;
    background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%);
    border: 2px solid #a78bfa;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 14px rgba(167,139,250,0.6), 0 4px 18px rgba(124,58,237,0.5);
    color: white;
    font-size: 13px;
    font-weight: bold;
    user-select: none;
    transition: all 0.2s;
}
#sb-toggle:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #6d28d9 100%);
    box-shadow: 0 0 26px rgba(167,139,250,0.9), 0 6px 28px rgba(124,58,237,0.8);
    transform: scale(1.08);
}
</style>
<div id="sb-toggle" title="Toggle sidebar">❮❮</div>
<script>
var open = true;

function getSidebar()  { return window.parent.document.querySelector('[data-testid="stSidebar"]'); }
function getToggle()   { return document.getElementById('sb-toggle'); }

function isSidebarVisible() {
    var sb = getSidebar();
    if (!sb) return false;
    var rect = sb.getBoundingClientRect();
    return rect.width > 10;
}

function showSidebar() {
    var sidebar = getSidebar();
    if (!sidebar) return;
    sidebar.style.removeProperty('display');
    sidebar.style.removeProperty('width');
    sidebar.style.removeProperty('min-width');
    sidebar.style.removeProperty('overflow');
    sidebar.style.removeProperty('visibility');
    var main = window.parent.document.querySelector('.main');
    if (main) main.style.removeProperty('margin-left');
    var block = window.parent.document.querySelector('.block-container');
    if (block) block.style.removeProperty('max-width');
    open = true;
    getToggle().innerHTML = '❮❮';
    getToggle().title = 'Hide sidebar';
}

function hideSidebar() {
    var sidebar = getSidebar();
    if (!sidebar) return;
    sidebar.style.setProperty('display', 'none', 'important');
    sidebar.style.setProperty('width', '0', 'important');
    sidebar.style.setProperty('min-width', '0', 'important');
    sidebar.style.setProperty('overflow', 'hidden', 'important');
    var main = window.parent.document.querySelector('.main');
    if (main) main.style.setProperty('margin-left', '0', 'important');
    var block = window.parent.document.querySelector('.block-container');
    if (block) block.style.setProperty('max-width', '100%', 'important');
    open = false;
    getToggle().innerHTML = '❯❯';
    getToggle().title = 'Show sidebar';
}

function toggle() {
    if (open) { hideSidebar(); } else { showSidebar(); }
}

// Wait for Streamlit to fully render, then sync state
function init() {
    var sidebar = getSidebar();
    if (!sidebar) { setTimeout(init, 150); return; }
    // Make sure sidebar is visible on load
    showSidebar();
}

document.getElementById('sb-toggle').addEventListener('click', toggle);
setTimeout(init, 300);
</script>
""", height=60)

if feature == "💡 Concept Explainer":
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">💡 Explain</div>
        <div class="page-title">Concept Explainer</div>
        <div class="page-desc">Type any topic and get a crystal-clear explanation tailored to your level.</div>
    </div>""", unsafe_allow_html=True)

    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis, Newton's Laws, Machine Learning")
    level = st.selectbox("Explain it like I'm a:", ["Beginner", "Intermediate", "Advanced", "Expert"])

    if st.button("Explain ✨"):
        if topic:
            with st.spinner("Generating explanation…"):
                prompt = (f"Explain '{topic}' clearly for a {level}. "
                          "Use relatable examples, keep it engaging, "
                          "and use bullet points where helpful.")
                result = ask_gemini(prompt)
            st.success("Here's your explanation:")
            st.markdown(result)
        else:
            st.warning("Please enter a topic first.")

elif feature == "📝 Note Summarizer":
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">📝 Summarize</div>
        <div class="page-title">Note Summarizer</div>
        <div class="page-desc">Paste long notes or upload a file, and get a concise, well-structured summary in seconds.</div>
    </div>""", unsafe_allow_html=True)

    input_method = st.radio(
        "How would you like to provide your notes?",
        options=[" Paste text", " Upload file"],
        horizontal=True
    )

    notes = ""

    if input_method == " Paste text":
        notes = st.text_area("Paste your notes:", height=280,
                              placeholder="Paste lecture notes, textbook content, or any text…")
    else:
        uploaded_file = st.file_uploader(
            "Upload a file (.txt, .pdf, or .docx):",
            type=["txt", "pdf", "docx"]
        )
        if uploaded_file is not None:
            with st.spinner("Reading file…"):
                notes = extract_text_from_file(uploaded_file)
            if notes.strip():
                st.success(f"Loaded **{uploaded_file.name}** ({len(notes)} characters).")
                with st.expander("📄 Preview extracted text"):
                    preview = notes[:2000] + ("…" if len(notes) > 2000 else "")
                    st.text(preview)

    summary_type = st.selectbox("Summary style:", ["Bullet points", "Short paragraph", "Key terms only"])

    if st.button("Summarize 📋"):
        if notes and notes.strip():
            with st.spinner("Summarizing…"):
                prompt = (f"Summarize the following notes using '{summary_type}' format. "
                          f"Be concise and capture every key idea:\n\n{truncate_text(notes)}")
                result = ask_gemini(prompt)
            st.success("Here's your summary:")
            st.markdown(result)
        else:
            st.warning("Please paste some notes or upload a file first.")

elif feature == "🧠 Quiz Generator":
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">🧠 Test yourself</div>
        <div class="page-title">Quiz Generator</div>
        <div class="page-desc">Answer 5 questions at a time — keep going for as long as you like!</div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.quiz_data:
        input_method = st.radio(
            "How would you like to provide your topic or notes?",
            options=[" Paste text", " Upload file"],
            horizontal=True,
            key="quiz_input_method"
        )

        quiz_input = ""

        if input_method == " Paste text":
            quiz_input = st.text_area("Topic or notes:", height=180,
                                      placeholder="e.g. 'The French Revolution' or paste your notes here")
        else:
            uploaded_file = st.file_uploader(
                "Upload a file (.txt, .pdf, or .docx):",
                type=["txt", "pdf", "docx"],
                key="quiz_file_uploader"
            )
            if uploaded_file is not None:
                with st.spinner("Reading file…"):
                    quiz_input = extract_text_from_file(uploaded_file)
                if quiz_input.strip():
                    st.success(f"Loaded **{uploaded_file.name}** ({len(quiz_input)} characters).")
                    with st.expander("📄 Preview extracted text"):
                        preview = quiz_input[:2000] + ("…" if len(quiz_input) > 2000 else "")
                        st.text(preview)

        if st.button("Start Quiz 🧠"):
            if quiz_input and quiz_input.strip():
                full_input = truncate_text(quiz_input)
                with st.spinner("Building your first 5 questions…"):
                    result = generate_quiz_questions(full_input, 1)
                st.session_state.quiz_data       = parse_quiz(result)
                st.session_state.quiz_answers    = {}
                st.session_state.quiz_submitted  = False
                st.session_state.quiz_topic      = quiz_input[:80] + ("…" if len(quiz_input) > 80 else "")
                st.session_state.quiz_full_input = full_input
                st.session_state.quiz_batch      = 1
                st.rerun()
            else:
                st.warning("Please enter a topic/notes or upload a file first.")
    else:
        render_quiz(st.session_state.quiz_data)


elif feature == "🃏 Flashcard Maker":
    st.markdown("""
    <div class="page-header">
        <div class="page-tag">🃏 Revise</div>
        <div class="page-title">Flashcard Maker</div>
        <div class="page-desc">Generate quick-revision flashcards — flip any card to reveal the answer.</div>
    </div>""", unsafe_allow_html=True)

    input_method = st.radio(
        "How would you like to provide your topic or notes?",
        options=[" Paste text", " Upload file"],
        horizontal=True,
        key="flash_input_method"
    )

    flash_input = ""

    if input_method == " Paste text":
        flash_input = st.text_area("Topic or notes:", height=180,
                                   placeholder="e.g. 'Photosynthesis' or paste your notes")
    else:
        uploaded_file = st.file_uploader(
            "Upload a file (.txt, .pdf, or .docx):",
            type=["txt", "pdf", "docx"],
            key="flash_file_uploader"
        )
        if uploaded_file is not None:
            with st.spinner("Reading file…"):
                flash_input = extract_text_from_file(uploaded_file)
            if flash_input.strip():
                st.success(f"Loaded **{uploaded_file.name}** ({len(flash_input)} characters).")
                with st.expander("📄 Preview extracted text"):
                    preview = flash_input[:2000] + ("…" if len(flash_input) > 2000 else "")
                    st.text(preview)

    if st.button("Generate Flashcards 🃏"):
        if flash_input and flash_input.strip():
            full_input = truncate_text(flash_input)
            with st.spinner("Creating flashcards…"):
                prompt = f"""Generate 8 flashcards based on the following content: '{full_input}'.

Use EXACTLY this format — each part on its own line:

Card 1:
Q: [Question]
A: [Clear, concise answer]

Card 2:
Q: [Question]
A: [Answer]

Keep answers clear and informative."""
                result = ask_gemini(prompt)
            st.session_state.flash_data       = parse_flashcards(result)
            st.session_state.flash_topic      = flash_input[:120] + ("…" if len(flash_input) > 120 else "")
            st.session_state.flash_full_input = full_input
            st.session_state.flash_flipped    = {}
            st.rerun()
        else:
            st.warning("Please enter a topic/notes or upload a file first.")

    if st.session_state.flash_data:
        st.success(f"Showing {len(st.session_state.flash_data)} flashcards:")
        render_flashcards(st.session_state.flash_data)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")

        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ Generate 5 More", use_container_width=True):
                with st.spinner("Generating 5 more flashcards…"):
                    existing = len(st.session_state.flash_data)
                    prompt = f"""Generate 5 more unique flashcards based on the following content: '{st.session_state.flash_full_input}'.
Do NOT repeat questions already covered. Focus on different aspects of the topic.

Use EXACTLY this format:

Card {existing + 1}:
Q: [Question]
A: [Answer]

Card {existing + 2}:
Q: [Question]
A: [Answer]

Card {existing + 3}:
Q: [Question]
A: [Answer]

Card {existing + 4}:
Q: [Question]
A: [Answer]

Card {existing + 5}:
Q: [Question]
A: [Answer]"""
                    result = ask_gemini(prompt)
                new_cards = parse_flashcards(result)
                st.session_state.flash_data += new_cards
                st.rerun()
        with col2:
            if st.button("🔄 Start Fresh", use_container_width=True):
                st.session_state.flash_data       = []
                st.session_state.flash_topic      = ""
                st.session_state.flash_full_input = ""
                st.session_state.flash_flipped    = {}
                st.rerun()