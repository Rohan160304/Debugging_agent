from executor import run_code
from analyzer import analyze_error
from ai_fixer import ai_fix, save_memory

def run_agent(code: str, max_attempts: int = 5):
    attempt = 1

    while attempt <= max_attempts:
        print(f"\n{'='*40}")
        print(f"Attempt {attempt}")
        print(f"{'='*40}")
        print("Running code:")
        print(code)

        result = run_code(code)

        if result["success"]:
            print("\n✅ Code fixed and working!")
            print("Output:", result["stdout"])
            # Only save to memory when fix actually worked
            save_memory("last_success", code)
            return

        # Show what went wrong
        analysis = analyze_error(result["stderr"])
        print("\n❌ Error     :", analysis["error_type"])
        print("💡 Suggestion:", analysis["suggestion"])
        print("📍 Line      :", analysis["line_number"])
        print("🔴 Stderr    :", result["stderr"])

        # Get AI fix
        fixed_code = ai_fix(code, analysis["error_type"], result["stderr"])

        # Check AI actually changed something
        if fixed_code.strip() == code.strip():
            print("⚠️ AI returned same code — forcing retry with fresh prompt")
        else:
            code = fixed_code

        attempt += 1

    print(f"\n🚫 Could not fix after {max_attempts} attempts.")

# --- Test ---
buggy_code = """
numbers = [1, 2, 3]
print(numbers[5])
"""

run_agent(buggy_code)