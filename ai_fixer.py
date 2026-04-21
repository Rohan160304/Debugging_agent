import json
import os
from groq import Groq

def get_api_key():
    # Try Streamlit secrets first
    try:
        import streamlit as st
        return st.secrets["GROQ_API_KEY"]
    except:
        pass
    # Try environment variable
    try:
        key = os.environ.get("GROQ_API_KEY")
        if key:
            return key
    except:
        pass
    return None

api_key = get_api_key()
client = Groq(api_key=api_key)

MEMORY_FILE = "memory.json"

def load_memory():
    try:
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_memory(key: str, fixed_code: str):
    memory = load_memory()
    memory[key] = fixed_code
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def ai_fix(code: str, error_type: str, stderr: str, language: str = "python") -> str:
    memory_key = f"{language}_{error_type}"

    # Check memory first
    memory = load_memory()
    if memory_key in memory:
        stored = memory[memory_key]
        if stored.strip() != code.strip():
            print("🧠 Found in memory — reusing past fix!")
            return stored

    print(f"🤖 Asking AI to fix {language.upper()} code...")

    # Strong language-specific prompts
    lang_hints = {
        "python":     "Fix Python syntax, indentation, variable names, types, imports.",
        "javascript": "Fix JavaScript syntax, missing semicolons, undefined variables, wrong types. Use vanilla JS only.",
        "java":       "Fix Java syntax. Class must be named Main. Add missing semicolons, brackets, correct types.",
        "c":          "Fix C syntax. Include correct headers like stdio.h. Fix semicolons, types, pointers.",
        "cpp":        "Fix C++ syntax. Include correct headers like iostream. Fix semicolons, types, pointers.",
        "html":       "Fix HTML structure. Close all tags properly. Fix attributes and nesting.",
        "css":        "Fix CSS syntax. Close all braces. Fix property names and values.",
    }

    hint = lang_hints.get(language, "Fix the code.")

    prompt = f"""You are a senior {language.upper()} developer and debugging expert.

TASK: Fix the broken {language.upper()} code below so it runs without any errors.

ERROR TYPE: {error_type}
ERROR MESSAGE:
{stderr}

BROKEN CODE:
{code}

INSTRUCTIONS:
1. Carefully read the error message
2. Find exactly what is wrong in the code
3. Fix ONLY the broken parts — do not rewrite the whole code unnecessarily
4. {hint}
5. Return the complete fixed code

OUTPUT FORMAT:
- Return ONLY the raw fixed code
- No explanations
- No comments about what you changed
- No markdown formatting
- No triple backticks
- Just the working code itself"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert {language.upper()} debugger. You only return raw fixed code. Never explain. Never use markdown. Never use backticks."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=2048
        )

        fixed_code = response.choices[0].message.content.strip()

        # Aggressively strip markdown if model added it
        if "```" in fixed_code:
            lines = fixed_code.split("\n")
            cleaned = []
            inside = False
            for line in lines:
                if line.startswith("```"):
                    inside = not inside
                    continue
                if inside or not line.startswith("```"):
                    cleaned.append(line)
            fixed_code = "\n".join(cleaned).strip()

        # Save to memory only if it's different from broken code
        if fixed_code.strip() != code.strip():
            save_memory(memory_key, fixed_code)
            print("💾 Fix saved to memory!")
        else:
            print("⚠️ AI returned same code")

        return fixed_code

    except Exception as e:
        print(f"❌ Groq API error: {e}")
        return code