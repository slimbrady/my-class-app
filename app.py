import streamlit as st
from streamlit_reveal_slides import reveal_slides

st.set_page_config(page_title="Sunday School", layout="wide", page_icon="📖")

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

# --- Sidebar ---
with st.sidebar:
    st.title("📖 Sunday School")
    lesson = st.selectbox("Lesson", list(LESSONS.keys()), index=1)
    mode = st.radio("Mode", ["Slides", "Interactive Quiz"], index=0)
    st.markdown("---")
    st.caption("Ages 12-16 • streamlit-reveal-slides")

# --- Slides mode ---
if mode == "Slides":
    md_file = LESSONS[lesson]
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            content = f.read()
        reveal_slides(
            content,
            height=700,
            theme="black",
            config={
                "transition": "slide",
                "controls": True,
                "progress": True,
            },
            initial_slide=0,
            key=lesson,
        )
    except FileNotFoundError:
        st.error(f"Missing {md_file}")
        st.info("Make sure genesis.md / 2kings.md are in the repo root.")

# --- Interactive Quiz mode ---
else:
    st.title(f"📝 Quiz – {lesson}")
    if lesson not in QUIZZES:
        st.info("Interactive quiz is available for 2 Kings 16-25. Switch lessons in the sidebar.")
        st.stop()

    questions = QUIZZES[lesson]
    if "answers" not in st.session_state or st.session_state.get("quiz_lesson") != lesson:
        st.session_state.answers = {}
        st.session_state.quiz_lesson = lesson
        st.session_state.submitted = False

    with st.form("quiz_form"):
        for i, q in enumerate(questions):
            st.markdown(f"**Q{i+1}. {q['q']}**")
            st.session_state.answers[i] = st.radio(
                f"q{i}", q["opts"], index=None, key=f"q_{i}", label_visibility="collapsed"
            )
            st.caption(f"📍 {q['ref']}")
            st.markdown("")
        submitted = st.form_submit_button("Submit Quiz", type="primary")

    if submitted:
        st.session_state.submitted = True

    if st.session_state.get("submitted"):
        score = sum(1 for i, q in enumerate(questions) if st.session_state.answers.get(i) == q["opts"][q["a"]])
        st.success(f"Score: {score} / {len(questions)}")
        if score == len(questions):
            st.balloons()
        with st.expander("Answer key", expanded=True):
            for i, q in enumerate(questions):
                your = st.session_state.answers.get(i, "— no answer —")
                correct = q["opts"][q["a"]]
                ok = your == correct
                icon = "✅" if ok else "❌"
                st.markdown(f"{icon} **Q{i+1}.** {q['q']}<br>Your answer: {your}<br>**Correct: {correct}** — {q['ref']}", unsafe_allow_html=True)
        if st.button("Retake"):
            st.session_state.answers = {}
            st.session_state.submitted = False
            st.rerun()
