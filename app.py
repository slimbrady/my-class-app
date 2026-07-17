import streamlit as st
import json, os, time
from datetime import datetime
from collections import defaultdict, Counter

st.set_page_config(page_title="Sunday School", layout="wide", page_icon="📖")

# --- Try imports ---
try:
    import reveal_slides as rs
    HAS_SLIDES = True
except Exception:
    HAS_SLIDES = False

try:
    import qrcode
    from io import BytesIO
    HAS_QR = True
except Exception:
    HAS_QR = False

# --- Quiz data ---
QUIZZES = {
    "2 Kings 16-25": [
        {"q": "Who was king of Judah when Israel fell to Assyria?", "opts": ["Ahaz", "Hezekiah", "Josiah", "Manasseh"], "a": 1, "ref": "2 Kings 18:9-10"},
        {"q": "What did King Ahaz do that displeased the Lord?", "opts": ["He rebuilt the temple", "He copied a pagan altar from Damascus and placed it in the temple", "He gave all his gold to the poor", "He freed the captives"], "a": 1, "ref": "2 Kings 16:10-14"},
        {"q": "When the Assyrian army surrounded Jerusalem, what did Hezekiah do?", "opts": ["Surrendered immediately", "Fled to Egypt", "Prayed to the Lord and sought Isaiah's counsel", "Paid them double the tribute"], "a": 2, "ref": "2 Kings 19:1-14"},
        {"q": "How was Jerusalem delivered from Sennacherib's army?", "opts": ["Hezekiah's army defeated them", "An angel struck down 185,000 Assyrian soldiers overnight", "A plague of locusts", "Egypt came to rescue them"], "a": 1, "ref": "2 Kings 19:35"},
        {"q": "What sign did God give Hezekiah that he would recover?", "opts": ["A rainbow", "The shadow moved backward ten steps on the sundial", "A dove landed on his windowsill", "It rained for 40 days"], "a": 1, "ref": "2 Kings 20:9-11"},
        {"q": "Which king reigned 55 years and did much evil?", "opts": ["Josiah – 31 years", "Manasseh – 55 years", "Hezekiah – 29 years", "Zedekiah – 11 years"], "a": 1, "ref": "2 Kings 21:1-9"},
        {"q": "What did Josiah do when the Book of the Law was found?", "opts": ["Burned it", "Hid it again", "Tore his clothes in repentance and renewed the covenant", "Sold it for silver"], "a": 2, "ref": "2 Kings 22:11, 23:1-3"},
        {"q": "Josiah's Passover was described as:", "opts": ["Small and quiet", "The greatest Passover since the days of the judges", "Cancelled due to war", "Only for priests"], "a": 1, "ref": "2 Kings 23:21-23"},
        {"q": "Why did Judah finally fall to Babylon?", "opts": ["They ran out of food", "Continued idolatry and rejecting God's prophets", "They forgot how to fight", "An earthquake destroyed the walls"], "a": 1, "ref": "2 Kings 24:2-4"},
        {"q": "After Jerusalem fell, who was left to care for the land?", "opts": ["Nobody", "The poorest people, under Gedaliah as governor", "Only the priests", "The Babylonian army"], "a": 1, "ref": "2 Kings 25:12, 22"},
    ]
}

LESSONS = {
    "Genesis 24-41": "genesis.md",
    "2 Kings 16-25": "2kings.md",
}

# --- Response store (shared across sessions on same replica) ---
@st.cache_resource
def get_store():
    return {"responses": []}  # list of {name, answers dict, score, ts, source}

def save_response(name, answers, score, source="web"):
    store = get_store()
    store["responses"].append({
        "name": name or "Anonymous",
        "answers": answers,
        "score": score,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "source": source,
    })
    # also persist to /tmp for survival across reruns
    try:
        with open("/tmp/quiz_responses.json", "w") as f:
            json.dump(store["responses"], f)
    except Exception:
        pass

def load_responses():
    store = get_store()
    if not store["responses"]:
        try:
            with open("/tmp/quiz_responses.json", "r") as f:
                store["responses"] = json.load(f)
        except Exception:
            pass
    return store["responses"]

def reset_responses():
    get_store()["responses"] = []
    try:
        os.remove("/tmp/quiz_responses.json")
    except Exception:
        pass

# --- Sidebar ---
with st.sidebar:
    st.title("📖 Sunday School")
    lesson = st.selectbox("Lesson", list(LESSONS.keys()), index=1)
    mode = st.radio("Mode", ["Slides", "Interactive Quiz", "Live Results"], index=0)
    st.markdown("---")
    # QR / share URL
    default_url = os.environ.get("APP_URL", "https://my-class-app.streamlit.app")
    app_url = st.text_input("Quiz URL (for QR)", value=default_url, help="Set APP_URL env var on Streamlit Cloud to auto-fill your real URL")
    if HAS_QR and app_url:
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(app_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="Scan to open quiz")
    elif not HAS_QR:
        st.caption("Install `qrcode[pil]` for QR codes")
    st.markdown("---")
    st.caption("Ages 12-16")
    if not HAS_SLIDES:
        st.warning("reveal_slides not installed – slides show as markdown")

# --- Slides mode ---
if mode == "Slides":
    md_file = LESSONS[lesson]
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        if HAS_SLIDES:
            rs.slides(
                content,
                height=700,
                theme="black",
                config={"transition": "slide", "controls": True, "progress": True},
                initial_slide=0,
                key=lesson,
            )
        else:
            st.markdown(content, unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Missing {md_file}")

# --- Interactive Quiz mode ---
elif mode == "Interactive Quiz":
    st.title(f"📝 Quiz – {lesson}")
    col_q, col_side = st.columns([2, 1])
    with col_side:
        st.subheader("📱 Join on your phone")
        if HAS_QR and app_url:
            qr = qrcode.QRCode(box_size=6, border=2)
            qr.add_data(app_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            buf = BytesIO()
            img.save(buf, format="PNG")
            st.image(buf.getvalue())
            st.code(app_url, language=None)
        st.info("💬 **SMS text-in**: To enable students texting answers to a phone number, connect a Twilio number and point its SMS webhook to `/sms` on this app. DM me your Twilio SID/auth if you want me to wire it up – responses will feed into the same Live Results dashboard.")
        st.caption("Without Twilio: students just scan the QR and answer in their browser – responses are tracked live.")

    with col_q:
        if lesson not in QUIZZES:
            st.info("Interactive quiz is available for 2 Kings 16-25.")
            st.stop()
        questions = QUIZZES[lesson]
        if "answers" not in st.session_state or st.session_state.get("quiz_lesson") != lesson:
            st.session_state.answers = {}
            st.session_state.quiz_lesson = lesson
            st.session_state.submitted = False

        name = st.text_input("Your name (optional)", key="student_name", placeholder="e.g. Ethan")
        with st.form("quiz_form"):
            form_answers = {}
            for i, q in enumerate(questions):
                st.markdown(f"**Q{i+1}. {q['q']}**")
                form_answers[i] = st.radio(
                    f"q{i}", q["opts"], index=None, key=f"q_{i}", label_visibility="collapsed"
                )
                st.caption(f"📍 {q['ref']}")
            submitted = st.form_submit_button("Submit Quiz", type="primary")

        if submitted:
            # validate all answered
            if any(v is None for v in form_answers.values()):
                st.warning("Please answer all questions before submitting.")
            else:
                st.session_state.answers = form_answers
                st.session_state.submitted = True
                score = sum(1 for i, q in enumerate(questions) if form_answers[i] == q["opts"][q["a"]])
                # save to shared store
                save_response(
                    st.session_state.get("student_name", ""),
                    {str(k): v for k, v in form_answers.items()},
                    score,
                    source="web"
                )
                st.rerun()

        if st.session_state.get("submitted"):
            answers = st.session_state.answers
            score = sum(1 for i, q in enumerate(questions) if answers.get(i) == q["opts"][q["a"]])
            st.success(f"Score: {score} / {len(questions)}")
            if score == len(questions):
                st.balloons()
            with st.expander("Answer key", expanded=True):
                for i, q in enumerate(questions):
                    your = answers.get(i, "—")
                    correct = q["opts"][q["a"]]
                    ok = your == correct
                    icon = "✅" if ok else "❌"
                    st.markdown(f"{icon} **Q{i+1}.** {q['q']}<br>Your answer: {your}<br>**Correct: {correct}** — {q['ref']}", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Retake quiz"):
                    st.session_state.answers = {}
                    st.session_state.submitted = False
                    st.rerun()
            with c2:
                if st.button("View Live Results →"):
                    st.query_params["mode"] = "results"
                    st.rerun()

# --- Live Results mode ---
else:  # Live Results
    st.title("📊 Live Results – 2 Kings 16-25")
    responses = load_responses()
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Total submissions", len(responses))
    with c2:
        avg = sum(r["score"] for r in responses) / len(responses) if responses else 0
        st.metric("Average score", f"{avg:.1f} / 10")
    with c3:
        if st.button("🔄 Refresh"):
            st.rerun()
        if st.button("🗑️ Clear all", help="Clear all stored responses"):
            reset_responses()
            st.rerun()

    if not responses:
        st.info("No submissions yet. Have students scan the QR code in the Quiz tab to submit.")
        st.stop()

    questions = QUIZZES["2 Kings 16-25"]
    # per-question stats
    for i, q in enumerate(questions):
        st.markdown(f"**Q{i+1}. {q['q']}**")
        counts = Counter()
        for r in responses:
            ans = r["answers"].get(str(i), r["answers"].get(i))
            if ans:
                counts[ans] += 1
        total = sum(counts.values()) or 1
        for opt_idx, opt_text in enumerate(q["opts"]):
            n = counts.get(opt_text, 0)
            pct = n / total * 100
            is_correct = opt_idx == q["a"]
            label = f"{'✅ ' if is_correct else ''}{opt_text} — {n} ({pct:.0f}%)"
            st.progress(pct / 100.0, text=label)
        st.caption(f"📍 {q['ref']}")
        st.markdown("---")

    # response table
    with st.expander("All submissions"):
        import pandas as pd
        df = pd.DataFrame([{
            "Name": r["name"],
            "Score": f"{r['score']}/10",
            "Time": r["ts"],
            "Source": r["source"]
        } for r in responses])
        st.dataframe(df, use_container_width=True)
        st.download_button(
            "Download CSV",
            df.to_csv(index=False).encode(),
            "2kings_quiz_results.csv",
            "text/csv"
        )

    st.markdown("---")
    st.subheader("📱 SMS text-in setup")
    st.markdown("""
**Want students to text answers instead of using the web form?**

1. Create a free [Twilio](https://www.twilio.com/try-twilio) account – you get a phone number
2. Set the SMS webhook for that number to: `https://your-app-url/sms`
3. I can add a `/sms` endpoint to this Streamlit app (via a small Flask sidecar, or switch to FastAPI) that parses texts like:
   ```
   Q1 B
   Q2 B
   ...
   ```
   or: `BBBCCBCBBB` (one letter per question)

Responses via SMS feed into the **same Live Results dashboard** above, mixed with web submissions.

Currently the quiz accepts **web submissions only** (via the QR code). Ping me with your Twilio SID/auth token if you want me to wire up SMS – takes ~10 min.
""")
