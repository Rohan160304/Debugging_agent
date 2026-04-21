def apply_fix(code: str, error_type: str) -> str:

    if error_type == "IndexError":
        # Wrap risky index access with a length check
        fix = code + "\n# FIX: check list length before indexing"
        return fix

    elif error_type == "NameError":
        fix = "# FIX: make sure all variables are defined before use\n" + code
        return fix

    elif error_type == "ImportError":
        fix = code + "\n# FIX: run  →  pip install <missing_module>"
        return fix

    elif error_type == "TypeError":
        fix = "# FIX: check data types — try wrapping with str() or int()\n" + code
        return fix

    else:
        # Can't auto-fix — return code unchanged, Phase 4 AI will handle this
        return code