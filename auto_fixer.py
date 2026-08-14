#!/usr/bin/env python3
import os
import re
import subprocess
import sys
from openai import OpenAI

# 1. Fetch API key from environment first
api_key = os.environ.get("OPENAI_API_KEY")

if not api_key:
    print("❌ Error: OPENAI_API_KEY environment variable is not set!")
    sys.exit(1)

# 2. Initialize OpenAI client targeting OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

# 3. Model Configuration (Update to your chosen OpenRouter model)
MAX_ATTEMPTS = 5
MODEL_NAME = "ai21/jamba-1-5-large" 


def run_pytest(test_path: str) -> tuple[bool, str]:
    """Runs pytest on the target path and captures output."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    passed = result.returncode == 0
    return passed, result.stdout


def extract_code_block(llm_response: str) -> str:
    """Extracts Python code from Markdown fences."""
    pattern = r"```(?:python)?\s*\n(.* nomination)?(.*?)```"
    match = re.search(pattern, llm_response, re.DOTALL)
    if match:
        return match.group(2).strip()
    return llm_response.strip()


def request_fix(target_code: str, test_output: str) -> str:
    """Sends the target code and failing pytest output to OpenRouter."""
    prompt = (
        "You are an expert Python developer tasked with fixing buggy code.\n"
        "The following code is causing unit tests to fail:\n\n"
        "=== SOURCE CODE ===\n"
        f"{target_code}\n"
        "===================\n\n"
        "Here is the pytest failure output and tracebacks:\n"
        "=== PYTEST OUTPUT ===\n"
        f"{test_output}\n"
        "=====================\n\n"
        "Please provide a corrected version of the source file that fixes all failing tests.\n"
        "Output ONLY the executable Python source code inside standard markdown fences (```python and ```).\n"
        "Do not include explanations outside the code block."
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a precise code-fixing agent."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )

    raw_text = response.choices[0].message.content or ""
    return extract_code_block(raw_text)


def auto_heal(source_file_path: str, test_file_path: str):
    """Iteratively runs pytest and updates source_file_path until tests pass."""
    if not os.path.exists(source_file_path) or not os.path.exists(test_file_path):
        print(f"Error: Specified files do not exist: '{source_file_path}' or '{test_file_path}'")
        sys.exit(1)

    print(f"🤖 Starting Self-Healing Loop for {source_file_path} using tests from {test_file_path}\n")

    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f"--- [Attempt {attempt}/{MAX_ATTEMPTS}] Running pytest ---")
        passed, pytest_output = run_pytest(test_file_path)

        if passed:
            print(f"\n✅ SUCCESS! All tests passed on attempt {attempt}.")
            return True

        print("❌ Tests failed. Capturing error output...\n")
        print("---------- PYTEST ERROR SUMMARY ----------")
        print("\n".join(pytest_output.splitlines()[-15:]))
        print("------------------------------------------\n")

        with open(source_file_path, "r", encoding="utf-8") as f:
            current_code = f.read()

        print("🧠 Querying OpenRouter for a code patch...")
        fixed_code = request_fix(current_code, pytest_output)

        with open(source_file_path, "w", encoding="utf-8") as f:
            f.write(fixed_code)

        print(f"✏️  Overwrote {source_file_path} with proposed fix. Re-testing...\n")

    print(f"\n🛑 FAILED: Reached maximum attempts ({MAX_ATTEMPTS}) without resolving test failures.")
    return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python auto_fixer.py <path_to_source.py> <path_to_test.py>")
        sys.exit(1)

    source_path = sys.argv[1]
    test_path = sys.argv[2]

    auto_heal(source_path, test_path)