import re

def analyze_error(stderr: str, language: str = "python") -> dict:
    error_type = "Unknown"
    suggestion = "Unrecognized error — AI will attempt to fix"
    line_number = None

    line_match = re.search(r"line (\d+)|:(\d+):", stderr)
    if line_match:
        line_number = int(line_match.group(1) or line_match.group(2))

    if language == "python":
        if "SyntaxError"           in stderr: error_type, suggestion = "SyntaxError",       "Missing colon, bracket, or quote"
        elif "NameError"           in stderr: error_type, suggestion = "NameError",          "Variable used before being defined"
        elif "IndexError"          in stderr: error_type, suggestion = "IndexError",         "List index out of range"
        elif "TypeError"           in stderr: error_type, suggestion = "TypeError",          "Wrong data type used"
        elif "ImportError"         in stderr or \
             "ModuleNotFoundError" in stderr: error_type, suggestion = "ImportError",        "Module not installed"
        elif "ZeroDivisionError"   in stderr: error_type, suggestion = "ZeroDivisionError",  "Cannot divide by zero"
        elif "AttributeError"      in stderr: error_type, suggestion = "AttributeError",     "Object does not have this attribute"
        elif "KeyError"            in stderr: error_type, suggestion = "KeyError",           "Dictionary key does not exist"
        elif "ValueError"          in stderr: error_type, suggestion = "ValueError",         "Wrong value passed to function"

    elif language == "javascript":
        if "SyntaxError"           in stderr: error_type, suggestion = "SyntaxError",        "Check for missing brackets or semicolons"
        elif "ReferenceError"      in stderr: error_type, suggestion = "ReferenceError",     "Variable used before being defined"
        elif "TypeError"           in stderr: error_type, suggestion = "TypeError",          "Wrong data type or undefined property"
        elif "RangeError"          in stderr: error_type, suggestion = "RangeError",         "Value out of allowed range"

    elif language == "java":
        if "error:"                in stderr: error_type, suggestion = "CompileError",       "Check syntax — missing semicolons or brackets"
        elif "NullPointerException"       in stderr: error_type, suggestion = "NullPointer", "Object is null before use"
        elif "ArrayIndexOutOfBounds"      in stderr: error_type, suggestion = "IndexError",  "Array index out of range"
        elif "ClassNotFoundException"     in stderr: error_type, suggestion = "ClassError",  "Class not found — check class name matches filename"
        elif "NumberFormatException"      in stderr: error_type, suggestion = "FormatError", "Invalid number format"

    elif language in ["c", "cpp"]:
        if "error:"                in stderr: error_type, suggestion = "CompileError",       "Check syntax — missing semicolons or brackets"
        elif "undefined reference" in stderr: error_type, suggestion = "LinkerError",        "Function or variable not defined"
        elif "segmentation fault"  in stderr.lower(): error_type, suggestion = "SegFault",   "Memory access error — check pointers"
        elif "warning:"            in stderr: error_type, suggestion = "Warning",            "Non-critical issue but should be fixed"

    elif language in ["html", "css"]:
        error_type = "SyntaxError"
        suggestion  = "Check for unclosed tags or missing properties"

    return {
        "error_type":  error_type,
        "suggestion":  suggestion,
        "line_number": line_number
    }