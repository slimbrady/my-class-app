import json
import os
from datetime import datetime
from collections import Counter
import streamlit as st


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

# 1. Page Configuration (Must always be the first Streamlit command)
st.set_page_config(page_title="Sunday School", layout="wide", page_icon="📖")

# 2. Universal styling application wrapper
st.html(
    """
    <style>
    /* Safely target and destroy all host container dotted borders/lines */
    hr, .stMarkdownContainer hr, [data-testid="stHeader"]::after {
        border: none !important;
        height: 0 !important;
        display: none !important;
    }
    
    /* Bigger quiz fonts */
    .stRadio > label, div[data-testid="stRadio"] label { 
        font-size: 1.25rem !important; 
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label { 
        font-size: 1.35rem !important; 
        padding: 0.5rem 0 !important; 
        line-height: 1.5 !important; 
    }

    /* Question text style specifications */
    h3, .stMarkdown h3 { 
        font-size: 1.9rem !important; 
    }

    /* Quiz block design structure setup */
    section.main > div, .block-container { 
        padding-left: 1.5rem !important; 
    }
    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stRadio"]) { 
        background: #ffffff; 
        border-radius: 14px; 
        padding: 1.5rem 1.8rem !important; 
        margin-left: 12px; 
        box-shadow: 0 4px 18px rgba(0,0,0,0.07), -4px 0 0 #0ea5b9; 
        border-left: 5px solid #0ea5b9; 
    }

    div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stRadio"])::before, .slide-header::after { 
        display: none !important; 
        content: none !important; 
    }

    div[role="radiogroup"] p { 
        font-size: 1.3rem !important; 
    }
    </style>
    """
)
# --- Quiz data – with explanations for every answer choice ---
QUIZZES = {
    "2 Kings 16-25": [
        {
            "q": "Who was king of Judah when the northern kingdom of Israel fell to Assyria?",
            "opts": ["Ahaz", "Hezekiah", "Josiah", "Manasseh"],
            "a": 1,
            "ref": "2 Kings 18:9-10",
            "explain_correct": "Hezekiah was king of Judah in the 6th year of his reign when Samaria fell (722 BC). He trusted in the Lord unlike the kings of Israel – 2 Kings 18:5 says 'there was no one like him among all the kings of Judah.'",
            "explain_wrong": {
                0: "Ahaz was Hezekiah's father – he died before Israel fell. Ahaz was the one who copied the pagan altar from Damascus (2 Kings 16).",
                2: "Josiah came about 90 years later – he was the boy king who found the Book of the Law in the temple (2 Kings 22).",
                3: "Manasseh was Hezekiah's son – he reigned AFTER Hezekiah, for 55 evil years (2 Kings 21)."
            }
        },
        {
            "q": "What did King Ahaz do that displeased the Lord?",
            "opts": ["He rebuilt the temple", "He copied a pagan altar from Damascus and placed it in the temple", "He gave all his gold to the poor", "He freed the captives"],
            "a": 1,
            "ref": "2 Kings 16:10-14",
            "explain_correct": "Ahaz saw a pagan altar in Damascus, liked the design, sent the plans to Jerusalem, and had Uriah the priest build a copy – then moved God's bronze altar aside and put the pagan copy in its place in the temple courtyard.",
            "explain_wrong": {
                0: "Rebuilding/fixing the temple would have pleased God – that's what Josiah and Hezekiah did. Ahaz did the opposite – he corrupted it.",
                2: "Giving gold to the poor would have been righteous. Ahaz actually stripped gold from the temple to bribe the king of Assyria (2 Kings 16:8).",
                3: "Freeing captives would have been merciful and Christlike. Ahaz took Judah deeper into idolatry, even sacrificing his own son (2 Kings 16:3-4)."
            }
        },
        {
            "q": "When the Assyrian army surrounded Jerusalem, what did King Hezekiah do?",
            "opts": ["Surrendered immediately", "Fled to Egypt", "Prayed to the Lord and sought Isaiah's counsel", "Paid them double the tribute"],
            "a": 2,
            "ref": "2 Kings 19:1-14",
            "explain_correct": "Hezekiah tore his clothes (sign of humility), went into the temple to pray, and sent messengers to the prophet Isaiah asking him to pray too. He then spread Sennacherib's threatening letter before the Lord in the temple (2 Kings 19:14).",
            "explain_wrong": {
                0: "Hezekiah did NOT surrender – that's what most kings would have done against 185,000 soldiers. He trusted God instead.",
                1: "Egypt was offering help, but Hezekiah didn't flee there – Isaiah had warned that Egypt was a 'broken reed' that would pierce your hand (2 Kings 18:21).",
                3: "Hezekiah had already paid tribute to Assyria earlier (2 Kings 18:14-16, even stripping gold from the temple doors). This time, when Sennacherib came back demanding surrender, Hezekiah prayed instead of paying."
            }
        },
        {
            "q": "How was Jerusalem delivered from Sennacherib's army?",
            "opts": ["Hezekiah's army defeated them", "An angel of the Lord struck down 185,000 Assyrian soldiers overnight", "A plague of locusts", "Egypt came to rescue them"],
            "a": 1,
            "ref": "2 Kings 19:35",
            "explain_correct": "\"That night the angel of the Lord went out and put to death a hundred and eighty-five thousand in the Assyrian camp. When the people got up the next morning—there were all the dead bodies!\" – 2 Kings 19:35 NIV. Sennacherib went home humiliated and was later assassinated by his own sons.",
            "explain_wrong": {
                0: "Judah's army was vastly outnumbered – they didn't fight. God fought for them. This is the point – deliverance came from God, not military strength.",
                2: "No locusts – it was an angel of the Lord, in one night. The text is very specific.",
                3: "Egypt never showed up. Isaiah had prophesied that trusting Egypt was useless – God alone delivered Jerusalem."
            }
        },
        {
            "q": "When Hezekiah was sick and told he would die, what sign did God give that he would recover?",
            "opts": ["A rainbow", "The shadow moved backward ten steps on the sundial", "A dove landed on his windowsill", "It rained for 40 days"],
            "a": 1,
            "ref": "2 Kings 20:9-11",
            "explain_correct": "Isaiah offered Hezekiah a choice: should the shadow go forward 10 steps (normal) or backward 10 steps (impossible)? Hezekiah chose backward – harder to believe, so a stronger sign. God made the shadow go BACKWARD ten steps on Ahaz's sundial. Hezekiah was healed and lived 15 more years.",
            "explain_wrong": {
                0: "Rainbows are God's sign of covenant with Noah (Genesis 9) – not used here. This sign was specifically about reversing time.",
                2: "No dove – that's a nice image but not in the text. The sign was unmistakably supernatural: the sun's shadow moving backwards.",
                3: "40 days of rain = Noah's flood. Not relevant here. Hezekiah's sign was the sundial shadow reversing – a miracle over time itself."
            }
        },
        {
            "q": "Which king of Judah reigned the longest and did much evil in the sight of the Lord?",
            "opts": ["Josiah", "Manasseh", "Hezekiah", "Zedekiah"],
            "a": 1,
            "ref": "2 Kings 21:1-9",
            "explain_correct": "Manasseh reigned 55 years in Jerusalem – the longest reign of any king of Judah – and 'did evil in the eyes of the Lord, following the detestable practices of the nations' (2 Kings 21:2). He rebuilt the high places his father Hezekiah had destroyed, erected altars to Baal, and even sacrificed his own son.",
            "explain_wrong": {
                0: "Josiah reigned 31 years and he was one of Judah's BEST kings – he found the Book of the Law and led a national revival. Not evil at all.",
                2: "Hezekiah reigned 29 years and he was one of Judah's BEST kings – 'he held fast to the Lord and did not stop following him' (2 Kings 18:6).",
                3: "Zedekiah reigned 11 years and he WAS evil – but only 11 years, not the longest. He was the last king before Jerusalem fell."
            }
        },
        {
            "q": "What did young King Josiah do when the Book of the Law was found in the temple?",
            "opts": ["Burned it", "Hid it again", "Tore his clothes in repentance and renewed the covenant", "Sold it for silver"],
            "a": 2,
            "ref": "2 Kings 22:11, 23:1-3",
            "explain_correct": "When Shaphan the scribe read the Book of the Law to Josiah, 'he tore his robes' – a sign of deep grief and repentance. He realized how far Judah had strayed from God's word. He then gathered all the people, read the entire Book of the Covenant aloud, and renewed the covenant before the Lord.",
            "explain_wrong": {
                0: "Burning God's word is what the WICKED king Jehoiakim later did to Jeremiah's scroll (Jeremiah 36). Josiah did the opposite – he TREMBLED at God's word.",
                1: "Hiding it again would have been like the priests before him who lost/forgot it in the first place. Josiah brought it into the light.",
                3: "Selling scripture for silver? No – Josiah valued God's word above silver. He was 26 years old and chose to follow God with his whole heart."
            }
        },
        {
            "q": "Josiah celebrated a Passover that was described as:",
            "opts": ["Small and quiet", "The greatest Passover since the days of the judges", "Cancelled due to war", "Only for priests"],
            "a": 1,
            "ref": "2 Kings 23:21-23",
            "explain_correct": "\"Neither before nor after Josiah was there a king like him who turned to the Lord as he did – with all his heart and with all his soul and with all his strength\" (2 Kings 23:25). His Passover was the greatest since the days of the judges – roughly 600+ years, going back to Samuel's time.",
            "explain_wrong": {
                0: "The opposite – it was MASSIVE. All of Judah and Israel were invited. It was a national event.",
                2: "It was NOT cancelled – Josiah specifically RESTORED the Passover which hadn't been properly kept in generations.",
                3: "It was for EVERYONE – 'all the people from the least to the greatest' (2 Kings 23:2). Josiah wanted the whole nation to return to God, not just the priests."
            }
        },
        {
            "q": "Why did Judah finally fall to Babylon?",
            "opts": ["They ran out of food", "Continued idolatry and rejecting God's prophets", "They forgot how to fight", "An earthquake destroyed the walls"],
            "a": 1,
            "ref": "2 Kings 24:2-4, 25",
            "explain_correct": "\"Surely these things happened to Judah according to the Lord's command, in order to remove them from his presence because of the sins of Manasseh and all he had done, including the shedding of innocent blood\" (2 Kings 24:3-4). God sent prophet after prophet – Isaiah, Jeremiah, and more – for generations. Judah refused to listen. After repeated warnings, judgment came through Babylon under Nebuchadnezzar.",
            "explain_wrong": {
                0: "Food DID run out during the 18-month siege of Jerusalem (2 Kings 25:3) – but that was a symptom, not the cause. The CAUSE was spiritual – generations of idolatry.",
                2: "They hadn't forgotten how to fight – they fought Babylon for years across multiple invasions. They lost because God allowed Babylon to be His instrument of judgment.",
                3: "No earthquake destroyed Jerusalem's walls – Nebuchadnezzar's army breached them after a long siege, then burned the temple and the city (2 Kings 25:9-10)."
            }
        },
        {
            "q": "After Jerusalem was destroyed, who was left behind to care for the land?",
            "opts": ["Nobody – it was completely empty", "The poorest people, under Gedaliah as governor", "Only the priests", "The Babylonian army"],
            "a": 1,
            "ref": "2 Kings 25:12, 22",
            "explain_correct": "Nebuchadnezzar 'left behind some of the poorest people of the land to work the vineyards and fields' (2 Kings 25:12) and appointed Gedaliah son of Ahikam as governor over them at Mizpah (2 Kings 25:22). Even in judgment, God preserved a remnant.",
            "explain_wrong": {
                0: "The land wasn't empty – Babylon needed farmers to work it and produce food/taxes. They took the skilled, wealthy, and leaders into exile, leaving the poor.",
                2: "The priests were taken captive too – in fact, the chief priest Seraiah was executed at Riblah (2 Kings 25:18-21). The temple was burned.",
                3: "Babylon stationed some soldiers, but they didn't farm the land – that's why they left the poorest Judeans behind, to work the vineyards and fields."
            }
        },
    ]
}

LESSONS = {
    "Genesis 24-41": "genesis.md",
    "2 Kings 16-25": "2kings.md",
}

# --- Response store ---
@st.cache_resource
def get_store():
    return {"responses": []}

def save_response(name, answers, score, source="web"):
    store = get_store()
    store["responses"].append({
        "name": name or "Anonymous",
        "answers": answers,
        "score": score,
        "ts": datetime.now().isoformat(timespec="seconds"),
        "source": source,
    })
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
        import os
        os.remove("/tmp/quiz_responses.json")
    except Exception:
        pass

# --- Sidebar ---
with st.sidebar:
    st.title("📖 Sunday School")
    lesson = st.selectbox("Lesson", list(LESSONS.keys()), index=1)
    mode = st.radio("Mode", ["Slides", "Interactive Quiz", "Live Results"], index=1)
    st.markdown("---")
    default_url = os.environ.get("APP_URL", "https://ssbrady.streamlit.app")
    app_url = st.text_input("Quiz URL (for QR)", value=default_url)
    if HAS_QR and app_url:
        qr = qrcode.QRCode(box_size=4, border=2)
        qr.add_data(app_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        st.image(buf.getvalue(), caption="Scan to open quiz")
    st.markdown("---")
    st.caption("Ages 12-16")

# --- Slides mode ---
if mode == "Slides":
    # 1. We still look up which lesson file to load based on the user's choice
    md_file = LESSONS[lesson]
    
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            markdown_content = f.read()
            
        # 2. RENDER THE SEPARATE TABS HERE INSTEAD OF FLOATING LATER IN THE FILE
        tab1, tab2 = st.tabs(["📊 Presentation Slides", "📝 Lesson Quiz"])
        
                with tab1:
            if HAS_SLIDES:
                slide_custom_css = """
                .reveal .slides section { 
                    padding: 15px 30px !important; 
                    box-sizing: border-box !important; 
                }
                .reveal h3 { font-size: 1.6em !important; line-height: 1.3 !important; }
                .reveal p, .reveal li { font-size: 0.85em !important; }
                .reveal .slides { height: 100% !important; }
                """
                # ADDED THE UNSAFE HTML FLAG TO ENABLE THE VERTICAL HTML TAGS
                rs.slides(
                    markdown_content, 
                    height=850, 
                    theme="black", 
                    css=slide_custom_css,
                    allow_unsafe_html=True  # <--- THIS ENABLES THE DOWN ARROW STACKING
                )
            else:
                st.info("Slide viewer: install `streamlit-reveal-slides` for full slide mode. Showing markdown fallback.")
                st.markdown(markdown_content, unsafe_allow_html=True)

                
        with tab2:
            st.subheader("Sunday School Quiz")
            # ========================================================
            # YOUR QUIZ / RADIO CODE (QUIZZES = { ... }) SITS NATIVELY HERE
            # ========================================================

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

    with col_q:
        if lesson not in QUIZZES:
            st.info("Interactive quiz is available for 2 Kings 16-25.")
            st.stop()

        questions = QUIZZES[lesson]
        total_q = len(questions)

        # session state init
        if "quiz_idx" not in st.session_state or st.session_state.get("quiz_lesson") != lesson:
            st.session_state.quiz_idx = 0
            st.session_state.quiz_lesson = lesson
            st.session_state.quiz_answers = {}
            st.session_state.quiz_revealed = {}
            st.session_state.quiz_name = ""
            st.session_state.quiz_submitted = False

        idx = st.session_state.quiz_idx
        q = questions[idx]

        # progress
        st.progress((idx) / total_q, text=f"Question {idx+1} of {total_q}")
        
        # name field on first question only
        if idx == 0 and not st.session_state.quiz_submitted:
            st.session_state.quiz_name = st.text_input(
                "Your name (optional)",
                value=st.session_state.get("quiz_name", ""),
                placeholder="e.g. Ethan",
                key="student_name_input"
            )

        st.markdown(f"### Q{idx+1}. {q['q']}")
        st.caption(f"📍 {q['ref']}")

        # answer selection
        revealed = st.session_state.quiz_revealed.get(idx, False)
        selected_key = f"selected_{lesson}_{idx}"
        
        # show radio buttons – disabled after reveal
        selected = st.radio(
            "Choose one:",
            options=list(range(len(q["opts"]))),
            format_func=lambda i: f"{chr(65+i)}. {q['opts'][i]}",
            index=None,
            key=selected_key,
            disabled=revealed,
        )

        # Check Answer button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            check_disabled = selected is None or revealed
            if st.button("✅ Check Answer", disabled=check_disabled, type="primary", use_container_width=True):
                st.session_state.quiz_revealed[idx] = True
                st.session_state.quiz_answers[idx] = selected
                st.rerun()
        
        with col2:
            # nav buttons
            if idx > 0:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.quiz_idx = idx - 1
                    st.rerun()
            if revealed and idx < total_q - 1:
                if st.button("Next →", use_container_width=True):
                    st.session_state.quiz_idx = idx + 1
                    st.rerun()

        # --- Answer reveal section ---
        if revealed:
            chosen = st.session_state.quiz_answers.get(idx)
            correct_idx = q["a"]
            is_correct = chosen == correct_idx

            if is_correct:
                st.success(f"✅ Correct! **{chr(65+correct_idx)}. {q['opts'][correct_idx]}**")
            else:
                st.error(f"❌ Not quite. You chose **{chr(65+chosen)}. {q['opts'][chosen]}**")
                st.success(f"✅ Correct answer: **{chr(65+correct_idx)}. {q['opts'][correct_idx]}**")

            # Explanation – why correct is correct
            st.markdown("**Why this is correct:**")
            st.info(q["explain_correct"])

            # Why the wrong answers are wrong
            st.markdown("**Why the other options are wrong:**")
            for opt_idx, opt_text in enumerate(q["opts"]):
                if opt_idx == correct_idx:
                    continue
                wrong_expl = q.get("explain_wrong", {}).get(opt_idx, "")
                was_chosen = " ← **you chose this**" if opt_idx == chosen else ""
                st.markdown(f"**{chr(65+opt_idx)}. {opt_text}**{was_chosen}  \n{wrong_expl if wrong_expl else '_No explanation provided._'}")

            st.caption(f"📖 Reference: {q['ref']}")
            st.markdown("---")

            # navigation after reveal
            nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])
            with nav_col1:
                if idx > 0 and st.button("← Previous Question", key=f"prev2_{idx}"):
                    st.session_state.quiz_idx = idx - 1
                    st.rerun()
            with nav_col2:
                if idx < total_q - 1:
                    if st.button("Next Question →", key=f"next2_{idx}", type="primary"):
                        st.session_state.quiz_idx = idx + 1
                        st.rerun()
                else:
                    # last question – finish quiz
                    if st.button("Finish Quiz →", key="finish_quiz", type="primary"):
                        # calculate score and save
                        answers = st.session_state.quiz_answers
                        score = sum(1 for i, qq in enumerate(questions) if answers.get(i) == qq["a"])
                        # convert answers to text for storage
                        answers_text = {}
                        for i, ans_idx in answers.items():
                            if ans_idx is not None and 0 <= ans_idx < len(questions[i]["opts"]):
                                answers_text[str(i)] = questions[i]["opts"][ans_idx]
                        save_response(
                            st.session_state.get("quiz_name", ""),
                            answers_text,
                            score,
                            source="web"
                        )
                        st.session_state.quiz_submitted = True
                        st.session_state.quiz_final_score = score
                        st.rerun()
            with nav_col3:
                if st.button("🔄 Restart Quiz", key=f"restart_{idx}"):
                    for k in list(st.session_state.keys()):
                        if k.startswith("selected_") or k.startswith("quiz_"):
                            del st.session_state[k]
                    st.rerun()

        # --- Quiz complete screen ---
        if st.session_state.get("quiz_submitted") and idx == total_q - 1 and st.session_state.quiz_revealed.get(idx, False):
            score = st.session_state.get("quiz_final_score", 0)
            st.markdown("---")
            st.success(f"🎉 Quiz Complete! Score: **{score} / {total_q}**")
            if score == total_q:
                st.balloons()
                st.markdown("### 🌟 Perfect score! Well done!")
            elif score >= 8:
                st.markdown("### 👏 Great job!")
            elif score >= 6:
                st.markdown("### 👍 Good work – review the ones you missed!")
            else:
                st.markdown("### 📖 Keep studying 2 Kings 16-25 – you'll get it next time!")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                if st.button("🔄 Retake Quiz", use_container_width=True):
                    for k in list(st.session_state.keys()):
                        if k.startswith("selected_") or k.startswith("quiz_"):
                            del st.session_state[k]
                    st.rerun()
            with col_b:
                if st.button("📊 View Live Results", use_container_width=True):
                    st.switch_page  # can't switch mode programmatically easily, user uses sidebar
                    st.rerun()
            with col_c:
                if st.button("🖼️ View Slides", use_container_width=True):
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
        if st.button("🗑️ Clear all"):
            reset_responses()
            st.rerun()

    if not responses:
        st.info("No submissions yet. Have students scan the QR code in the Quiz tab.")
        st.stop()

    questions = QUIZZES["2 Kings 16-25"]
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
            pct = n / total * 100 if total else 0
            is_correct = opt_idx == q["a"]
            label = f"{'✅ ' if is_correct else ''}{chr(65+opt_idx)}. {opt_text} — {n} ({pct:.0f}%)"
            st.progress(min(pct / 100.0, 1.0), text=label)
        st.caption(f"📖 {q['ref']}")
        st.markdown("---")

    with st.expander("All submissions"):
        try:
            import pandas as pd
            df = pd.DataFrame([{
                "Name": r["name"],
                "Score": f"{r['score']}/10",
                "Time": r["ts"],
                "Source": r["source"]
            } for r in responses])
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button("Download CSV", df.to_csv(index=False).encode(), "2kings_quiz_results.csv", "text/csv")
        except Exception:
            st.write(responses)
