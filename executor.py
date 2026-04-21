import subprocess
import tempfile
import os

def run_code(code: str, language: str = "python") -> dict:
    try:

        # ── Python ──
        if language == "python":
            result = subprocess.run(
                ["python3", "-c", code],
                capture_output=True, text=True, timeout=60
            )
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0
            }

        # ── JavaScript ──
        elif language == "javascript":
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "main.js")
                with open(filepath, "w") as f:
                    f.write(code)
                result = subprocess.run(
                    ["node", filepath],
                    capture_output=True, text=True, timeout=60
                )
                return {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "success": result.returncode == 0
                }

        # ── Java ──
        elif language == "java":
            with tempfile.TemporaryDirectory() as tmpdir:
                filepath = os.path.join(tmpdir, "Main.java")
                with open(filepath, "w") as f:
                    f.write(code)
                compile_result = subprocess.run(
                    ["javac", filepath],
                    capture_output=True, text=True, timeout=30
                )
                if compile_result.returncode != 0:
                    return {"stdout": "", "stderr": compile_result.stderr, "success": False}
                run_result = subprocess.run(
                    ["java", "-cp", tmpdir, "Main"],
                    capture_output=True, text=True, timeout=30
                )
                return {
                    "stdout": run_result.stdout,
                    "stderr": run_result.stderr,
                    "success": run_result.returncode == 0
                }

        # ── HTML / CSS ── (no execution, AI reviews directly)
        elif language in ["html", "css"]:
            return {
                "stdout": "",
                "stderr": "",
                "success": True,
                "raw_code": code
            }

    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": "TimeoutError: Code took too long to run", "success": False}
    except FileNotFoundError as e:
        return {"stdout": "", "stderr": f"Compiler not found: {str(e)}", "success": False}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "success": False}