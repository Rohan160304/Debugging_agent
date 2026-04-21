import streamlit as st
import json
from executor import run_code
from analyzer import analyze_error
from ai_fixer import ai_fix, save_memory, client

st.set_page_config(page_title="AI Debugging Agent", page_icon="🤖")
st.title("🤖 AI Self-Learning Debugging Agent")
st.caption("Supports Python, JavaScript, Java, HTML, CSS")

language = st.selectbox("🌐 Select Language",
    ["python", "javascript", "java", "html", "css"])

code = st.text_area("📝 Paste your buggy code here:", height=220)

def force_ai_fix(code, error_type, stderr, language, attempt_number):

    prompts = [
        f"""Fix this broken {language.upper()} code.
Error: {stderr}
Code:
{code}
Return ONLY the fixed code. No explanation. No markdown. No backticks.""",

        f"""This {language.upper()} code has an error: {error_type}
Error message: {stderr}
Rewrite the entire code from scratch so it works correctly.
Original code for reference:
{code}
Return ONLY raw working {language.upper()} code. Nothing else.""",

        f"""You are debugging {language.upper()} code.
Step 1: The error is: {stderr}
Step 2: The broken code is:
{code}
Step 3: Fix every single error in the code.
Step 4: Return the complete working code only.
No markdown. No backticks. No explanation. Just code.""",

        f"""ONLY OUTPUT CODE. NO TEXT. NO EXPLANATION.
Language: {language.upper()}
Error to fix: {stderr}
Broken code:
{code}
OUTPUT THE FIXED CODE BELOW:""",

        f"""Completely rewrite this {language.upper()} code so it works perfectly.
The current error is: {stderr}
Current broken code:
{code}
Write a clean working version. Output raw code only."""
    ]

    idx = min(attempt_number - 1, len(prompts) - 1)
    prompt = prompts[idx]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {language.upper()} developer. You ONLY output raw working code. You NEVER explain. You NEVER use markdown or backticks."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1 + (attempt_number * 0.05),
            max_tokens=2048
        )

        fixed = response.choices[0].message.content.strip()

        if "```" in fixed:
            lines = fixed.split("\n")
            cleaned = []
            inside = False
            for line in lines:
                if line.startswith("```"):
                    inside = not inside
                    continue
                cleaned.append(line)
            fixed = "\n".join(cleaned).strip()

        return fixed

    except Exception as e:
        st.error(f"Groq API error: {e}")
        return code


if st.button("🚀 Run Agent"):
    if not code.strip():
        st.warning("Please paste some code first!")
    else:
        st.divider()
        current_code = code
        attempt = 1
        max_attempts = 20
        same_code_count = 0

        # ── HTML / CSS ──
        if language in ["html", "css"]:
            st.info(f"🔍 Sending {language.upper()} to AI for review...")
            with st.spinner("🤖 AI is reviewing..."):
                fixed = force_ai_fix(current_code, "SyntaxError",
                                     "Review and fix all issues", language, 1)
            st.success("✅ AI reviewed and fixed your code!")
            st.code(fixed, language=language)

        else:
            # ── Python, JavaScript, Java ──
            while attempt <= max_attempts:
                st.markdown(f"### 🔁 Attempt {attempt}")

                result = run_code(current_code, language)

                if result["success"]:
                    st.success("✅ Code is working!")
                    st.code(current_code, language=language)
                    if result.get("stdout", "").strip():
                        st.markdown("**Output:**")
                        st.code(result["stdout"])
                    save_memory(f"{language}_last_success", current_code)
                    break

                analysis = analyze_error(result["stderr"], language)

                col1, col2 = st.columns(2)
                col1.error(f"❌ {analysis['error_type']}")
                col2.warning(f"💡 {analysis['suggestion']}")

                with st.expander(f"Raw error — attempt {attempt}"):
                    st.code(result["stderr"])

                with st.spinner(f"🤖 AI fixing — attempt {attempt}..."):
                    fixed = force_ai_fix(
                        current_code,
                        analysis["error_type"],
                        result["stderr"],
                        language,
                        attempt
                    )

                with st.expander(f"AI fix — attempt {attempt}"):
                    st.code(fixed, language=language)

                if fixed.strip() == current_code.strip():
                    same_code_count += 1
                    st.warning(f"⚠️ AI returned same code ({same_code_count} time/s) — trying harder...")
                    if same_code_count >= 3:
                        st.error("🚫 AI is stuck. Try checking if Java/Node is installed correctly.")
                        st.markdown("**Last code version:**")
                        st.code(current_code, language=language)
                        st.markdown("**Error that could not be fixed:**")
                        st.code(result["stderr"])
                        break
                else:
                    same_code_count = 0
                    current_code = fixed

                attempt += 1

            else:
                st.warning("⚠️ Reached 20 attempts.")
                st.code(current_code, language=language)

# ── Memory viewer ──
st.divider()
st.markdown("### 🧠 Agent Memory")
st.caption("All fixes the agent has learned")

try:
    with open("memory.json") as f:
        memory = json.load(f)
    if memory:
        for key, fix in memory.items():
            with st.expander(f"📌 {key}"):
                st.code(fix)
    else:
        st.info("No fixes learned yet — run the agent first!")
except:
    st.info("memory.json not found.")