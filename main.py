
import streamlit as st
import PyPDF2
import io
import ollama
import html
import json
import re

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

# ---------- CUSTOM CSS ----------

# ---------- PROFESSIONAL CUSTOM CSS ----------
st.markdown("""
<style>

/* Main application background */
.stApp {
    background:
        radial-gradient(ellipse at 5% 5%, rgba(109,40,217,0.20), transparent 38%),
        radial-gradient(ellipse at 95% 90%, rgba(14,165,233,0.13), transparent 38%),
        linear-gradient(135deg, #080c1b 0%, #11152c 50%, #0b1020 100%);
    color: #e8edff;
}

/* Main content spacing */
.block-container {
    max-width: 1150px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* Typography */
h1, h2, h3 {
    color: #f8faff !important;
    letter-spacing: -0.5px;
}

p, label {
    color: #cbd5e1;
}

/* Header gradient */
h1 {
    text-shadow: 0 0 25px rgba(139,92,246,0.18);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        100deg,
        #7c3aed 0%,
        #6366f1 50%,
        #2563eb 100%
    );
    color: #ffffff !important;
    border: 1px solid rgba(196,181,253,0.55);
    border-radius: 12px;
    padding: 0.72rem 1.5rem;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 0.3px;
    box-shadow:
        0 5px 18px rgba(99,102,241,0.25),
        0 0 12px rgba(139,92,246,0.15);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    background: linear-gradient(
        100deg,
        #8b5cf6,
        #6366f1,
        #3b82f6
    );
    border-color: #c4b5fd;
    transform: translateY(-2px);
    box-shadow:
        0 8px 25px rgba(99,102,241,0.4),
        0 0 20px rgba(139,92,246,0.3);
}

/* Input field */
[data-testid="stTextInput"] input {
    background: rgba(20,25,52,0.85);
    color: #ffffff;
    border: 1px solid rgba(129,140,248,0.4);
    border-radius: 11px;
    padding: 12px;
    transition: all 0.25s ease;
}

[data-testid="stTextInput"] input:focus {
    border-color: #a78bfa;
    box-shadow: 0 0 0 2px rgba(139,92,246,0.18);
}

/* Upload area */
[data-testid="stFileUploader"] {
    background: rgba(99,102,241,0.055);
    border: 1px dashed rgba(167,139,250,0.65);
    border-radius: 15px;
    padding: 18px;
    transition: all 0.3s ease;
}

[data-testid="stFileUploader"]:hover {
    background: rgba(99,102,241,0.11);
    border-color: #a78bfa;
}

/* Native Streamlit bordered container */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(
        135deg,
        rgba(30,35,70,0.75),
        rgba(17,24,50,0.75)
    );
    border: 1px solid rgba(129,140,248,0.3);
    border-radius: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.2);
}

/* Equal-sized Skills and Weaknesses cards */
.skills-card {
    background:
        linear-gradient(
            145deg,
            rgba(45,42,91,0.88),
            rgba(20,29,58,0.92)
        );
    border: 1px solid rgba(139,92,246,0.38);
    border-radius: 20px;
    padding: 25px;
    height: 210px;
    min-height: 210px;
    box-sizing: border-box;
    overflow-y: auto;
    box-shadow:
        0 10px 30px rgba(0,0,0,0.2),
        inset 0 1px 0 rgba(255,255,255,0.05);
    backdrop-filter: blur(14px);
    transition: all 0.3s ease;
}

.skills-card:hover {
    border-color: rgba(167,139,250,0.8);
    box-shadow: 0 12px 32px rgba(99,102,241,0.16);
    transform: translateY(-3px);
}

/* Recommendations card */
.recommendations-card {
    background:
        linear-gradient(
            120deg,
            rgba(49,38,91,0.85),
            rgba(20,38,72,0.92),
            rgba(18,30,56,0.92)
        );
    border: 1px solid rgba(129,140,248,0.42);
    border-radius: 20px;
    padding: 28px;
    width: 100%;
    box-sizing: border-box;
    margin-top: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.22);
    backdrop-filter: blur(14px);
    overflow-wrap: anywhere;
    transition: all 0.3s ease;
}

.recommendations-card:hover {
    border-color: rgba(167,139,250,0.8);
}

.recommendations-card h3,
.skills-card h3 {
    color: #f8faff !important;
    margin-bottom: 20px;
    font-weight: 700;
}

.recommendations-card p {
    color: #dbe4ff;
    font-size: 16px;
    line-height: 1.8;
    padding: 5px 0;
}

/* Skill badges */
.skill-badge {
    display: inline-block;
    background: linear-gradient(
        120deg,
        rgba(16,185,129,0.16),
        rgba(20,184,166,0.10)
    );
    color: #86efac;
    border: 1px solid rgba(52,211,153,0.42);
    padding: 8px 13px;
    margin: 5px 5px 5px 0;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

/* Weakness badges */
.weakness-badge {
    display: inline-block;
    background: linear-gradient(
        120deg,
        rgba(244,63,94,0.15),
        rgba(249,115,22,0.08)
    );
    color: #fda4af;
    border: 1px solid rgba(251,113,133,0.38);
    padding: 8px 13px;
    margin: 5px 5px 5px 0;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
}

/* Score card */
.ui-card {
    background: linear-gradient(
        135deg,
        rgba(49,46,129,0.55),
        rgba(30,41,80,0.8)
    );
    border: 1px solid rgba(167,139,250,0.35);
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
}

.score-number {
    font-size: 46px;
    font-weight: 800;
    background: linear-gradient(90deg,#c4b5fd,#60a5fa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0 0 20px rgba(139,92,246,0.2);
}

/* Progress bar */
.stProgress > div > div > div > div {
    background: linear-gradient(
        90deg,
        #8b5cf6,
        #6366f1,
        #38bdf8
    );
    border-radius: 20px;
}

/* Loading animation */
@keyframes pulse {
    0%, 100% {
        opacity: 1;
        text-shadow: 0 0 8px rgba(167,139,250,0.2);
    }
    50% {
        opacity: 0.55;
        text-shadow: 0 0 18px rgba(167,139,250,0.6);
    }
}

.loading-text {
    color: #c4b5fd;
    animation: pulse 1.2s infinite;
    font-weight: 700;
}

/* Scrollbar styling */
.skills-card::-webkit-scrollbar {
    width: 6px;
}

.skills-card::-webkit-scrollbar-thumb {
    background: #6d5ab5;
    border-radius: 10px;
}

/* Responsive layout */
@media (max-width: 768px) {
    .block-container {
        padding: 1rem;
    }

    .score-number {
        font-size: 34px;
    }

    .skills-card {
        height: auto;
        min-height: 180px;
    }

    .recommendations-card {
        padding: 20px;
    }
}

</style>
""", unsafe_allow_html=True)



# ---------- HEADER ----------
st.markdown("""
<div style="text-align:center; padding:25px 10px 15px;">
    <div style="font-size:48px;"></div>
    <h1 style="
        font-size:38px;
        font-weight:800;
        background:linear-gradient(90deg,#c4b5fd,#60a5fa);
        -webkit-background-clip:text;
        -webkit-text-fill-color:transparent;
    ">
        AI Resume Analyzer
    </h1>
    <p style="color:#a5b4fc; font-size:16px;">
        Analyze your resume. Discover your strengths. Improve your career.
    </p>
</div>
""", unsafe_allow_html=True)


# ---------- PDF UPLOAD ----------
# Group the header, description, and uploader into one native card
with st.container(border=True):  
    st.markdown("### 📤 Upload Your Resume")  
    st.markdown(
        "<p style='color:#a5b4fc; margin-bottom: 15px;'>Upload your resume in PDF format to begin your AI analysis.</p>", 
        unsafe_allow_html=True
    )  
    
    uploaded_file = st.file_uploader(
        "Choose your resume",
        type=["pdf"],
        label_visibility="collapsed"
    )

job_role = st.text_input(
    "Enter the job role you are applying for:",
    placeholder="Example: Python Developer"
)


# ---------- PDF TEXT EXTRACTION ----------
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(
        io.BytesIO(uploaded_file.getvalue())
    )

    text = ""

    for page in pdf_reader.pages:
        text += (page.extract_text() or "") + "\n"

    return text


# ---------- JSON RESPONSE PARSER ----------
def parse_ai_response(content):
    content = content.strip()

    # Remove Markdown code fences if present
    content = re.sub(r"^```(?:json)?\s*", "", content)
    content = re.sub(r"\s*```$", "", content)

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Try to locate a JSON object inside the response
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if match:
            return json.loads(match.group())

        raise ValueError("The AI did not return valid JSON.")


# ---------- ANALYSIS BUTTON ----------
if st.button(" Analyze My Resume", use_container_width=True):

    if not uploaded_file:
        st.warning("Please upload your resume first.")

    else:
        try:
            progress = st.progress(10)
            status = st.empty()

            status.markdown(
                '<p class="loading-text"> Reading your resume...</p>',
                unsafe_allow_html=True
            )

            resume_text = extract_text_from_pdf(uploaded_file)

            if not resume_text.strip():
                st.error(
                    "No readable text found. Your PDF may be scanned. "
                    "Please upload a text-based PDF."
                )
                st.stop()

            progress.progress(25)

            status.markdown(
                '<p class="loading-text"> AI is analyzing your resume...</p>',
                unsafe_allow_html=True
            )

            prompt = f"""
You are an expert resume analyzer.

Analyze this resume text and provide a detailed assessment. Focus on the following aspects:
- Overall quality and clarity of the resume 
- Relevance of skills and experience to the target job role
Target job role: {job_role.strip() if job_role.strip() else "Not specified"}

If a targeted job role is provided, evaluate how well the resume aligns with that role.
If no job role is specified, provide a general assessment.

Return ONLY a valid JSON object. Do not use Markdown fences.

Use exactly this structure:

{{
    "score": 75,
    "summary": "Short overall resume assessment",
    "skills": ["Python", "SQL"],
    "weaknesses": ["Missing measurable achievements"],
    "suggestions": [
        "Add measurable results to project descriptions"
    ]
}}

Rules:
- Score must be an integer between 0 and 100.
- Skills must be supported by the resume.
- Weaknesses should identify genuine gaps or areas to improve.
- Suggestions should be specific and practical.
- Do not invent qualifications or experience.

RESUME:
{resume_text}
"""

            progress.progress(40)

            with st.spinner("✨ Reviewing your resume with AI..."):
                response = ollama.chat(
                    model="qwen2.5:0.5b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a professional resume analyzer. "
                                "Return accurate analysis in valid JSON only."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

            progress.progress(85)

            ai_content = response["message"]["content"]
            result = parse_ai_response(ai_content)

            score = int(result.get("score", 0))
            score = max(0, min(100, score))

            skills = result.get("skills", [])
            weaknesses = result.get("weaknesses", [])
            suggestions = result.get("suggestions", [])
            summary = result.get("summary", "Analysis completed.")

            progress.progress(100)
            status.success("✅ Resume analysis completed!")

            # ---------- SCORE CARD ----------
            st.markdown("## 📊 Your Resume Dashboard")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.markdown(f"""
                <div class="ui-card">
                    <p style="color:#a5b4fc;">RESUME SCORE</p>
                    <div class="score-number">{score}/100</div>
                    <p style="color:#86efac;">AI-generated assessment</p>
                </div>
                """, unsafe_allow_html=True)

                st.progress(score / 100)

            with col2:
                st.markdown(f"""
                <div class="ui-card">
                    <h3>📝 Overall Assessment</h3>
                    <p>{html.escape(str(summary))}</p>
                    <p style="color:#a5b4fc;">
                        Target role: {html.escape(job_role)}
                    </p>
                </div>
                """, unsafe_allow_html=True)

            # ---------- SKILLS AND WEAKNESSES ----------
            st.markdown("## 🔍 Skills & Improvement Areas")

            col1, col2 = st.columns(2, gap="large")

            # KEY SKILLS BOX
            with col1:
                skill_html = "".join(
                    f'<span class="skill-badge">{html.escape(str(skill))}</span>'
                    for skill in skills
                )

                st.markdown(f"""
                <div class="skills-card">
                    <h3>✅ Key Skills</h3>
                    {skill_html if skill_html else "No skills identified."}
                </div>
                """, unsafe_allow_html=True)

            # WEAKNESSES BOX
            with col2:
                weakness_html = "".join(
                    f'<span class="weakness-badge">{html.escape(str(item))}</span>'
                    for item in weaknesses
                )

                st.markdown(f"""
                <div class="skills-card">
                    <h3>⚠️ Weaknesses</h3>
                    {weakness_html if weakness_html else "No weaknesses identified."}
                </div>
                """, unsafe_allow_html=True)

            # ---------- RECOMMENDATIONS BOX ----------
            st.markdown("## 🚀 Recommendations")

            if suggestions:
                recommendations_html = "".join(
                    f'<p><strong>{i}.</strong> {html.escape(str(suggestion))}</p>'
                    for i, suggestion in enumerate(suggestions, 1)
                )
            else:
                recommendations_html = "<p>No suggestions returned.</p>"

            st.markdown(f"""
            <div class="recommendations-card">
                <h3>💡 Recommendations 🔗</h3>
                {recommendations_html}
            </div>
            """, unsafe_allow_html=True)

        except json.JSONDecodeError:
            st.error(
                "The AI response could not be converted into structured "
                "analysis. Please try again."
            )

        except Exception as e:
            st.error(f"An error occurred: {e}")
