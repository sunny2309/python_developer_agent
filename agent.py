import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import requests
from dotenv import load_dotenv


# Configuration
BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills"
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)

OPEN_ROUTER_KEY = os.environ.get("OPEN_ROUTER_KEY")
CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-v4.1-flash"
DEFAULT_SYSTEM_PROMPT = "You are a helpful Python developer assistant."

if not OPEN_ROUTER_KEY:
    raise RuntimeError(
        f"OPEN_ROUTER_KEY was not found. Add it to {ENV_FILE}."
    )

HEADERS = {
    "Authorization": f"Bearer {OPEN_ROUTER_KEY}",
    "Content-Type": "application/json",
}


def call_model(messages, temperature=0.2):
    """Send messages to the configured OpenRouter chat model."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "temperature": temperature,
    }
    response = requests.post(
        CHAT_URL,
        headers=HEADERS,
        json=payload,
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def read_skill_metadata(skill_dir):
    """Read a Skill's name and description from SKILL.md frontmatter."""
    skill_file = skill_dir / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")

    if not content.startswith("---"):
        raise ValueError(f"Missing YAML frontmatter in {skill_file}")

    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid YAML frontmatter in {skill_file}")

    metadata = {}
    for line in parts[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip().strip("'\"")

    return {
        "name": metadata.get("name", skill_dir.name),
        "description": metadata.get("description", ""),
        "path": str(skill_file),
    }


def discover_skills():
    """Discover Skills under the local skills/ directory."""
    if not SKILLS_DIR.is_dir():
        return []

    skills = []
    for child in sorted(SKILLS_DIR.iterdir()):
        skill_file = child / "SKILL.md"
        if child.is_dir() and skill_file.is_file():
            try:
                skills.append(read_skill_metadata(child))
            except (OSError, ValueError) as exc:
                print(f"Warning: skipping {child.name}: {exc}", file=sys.stderr)

    return skills


def select_skill(user_request, skills):
    """Select at most one Skill for the request."""
    if not skills:
        return None, "No Skills available; using default LLM behavior."

    options = [
        {"name": skill["name"], "description": skill["description"]}
        for skill in skills
    ]
    router_prompt = (
        "Choose the single most relevant Skill for the user's request. "
        "If none is relevant, choose null. Return only JSON in this format: "
        '{"skill": "skill-name-or-null", "reason": "brief reason"}.'
    )

    result = call_model([
        {"role": "system", "content": router_prompt},
        {
            "role": "user",
            "content": json.dumps(
                {
                    "request": user_request,
                    "available_skills": options,
                },
                indent=2,
            ),
        },
    ])

    cleaned = result.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        decision = json.loads(cleaned)
    except json.JSONDecodeError:
        return None, "Could not parse Skill selection; using default LLM behavior."

    name = decision.get("skill")
    reason = decision.get("reason", "")
    valid_names = {skill["name"] for skill in skills}

    if name not in valid_names:
        return None, reason or "No relevant Skill selected; using default LLM behavior."

    selected = next(skill for skill in skills if skill["name"] == name)
    return selected, reason


def load_skill_resources(skill):
    """Load SKILL.md plus readable reference and asset files."""
    skill_file = Path(skill["path"])
    skill_dir = skill_file.parent
    sections = [
        "## SKILL.md\n\n" + skill_file.read_text(encoding="utf-8")
    ]
    supported_extensions = {
        ".md", ".txt", ".json", ".yaml", ".yml", ".toml", ".csv", ".sql"
    }
    max_file_chars = 15_000
    max_context_chars = 40_000
    total_chars = sum(len(section) for section in sections)

    # Scripts are executed separately by execute_skill_scripts().
    for directory_name in ("references", "assets"):
        resource_dir = skill_dir / directory_name
        if not resource_dir.is_dir():
            continue

        for file_path in sorted(resource_dir.rglob("*")):
            if not file_path.is_file():
                continue
            if file_path.suffix.lower() not in supported_extensions:
                continue
            if total_chars >= max_context_chars:
                break

            try:
                content = file_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            content = content[:max_file_chars]
            remaining = max_context_chars - total_chars
            content = content[:remaining]
            relative_path = file_path.relative_to(skill_dir)

            section = f"## Resource: {relative_path}\n\n{content}"
            sections.append(section)
            total_chars += len(section)

    return "\n\n".join(sections)


def extract_code_from_request(user_request):
    """Extract the first fenced Python code block from the request."""
    pattern = r"```(?:python|py)?\s*\n(.*?)```"
    matches = re.findall(
        pattern, user_request, flags=re.IGNORECASE | re.DOTALL
    )
    return matches[0].strip() if matches else None


def execute_skill_scripts(skill, code):
    """Run Python scripts in the selected Skill's scripts/ directory."""
    scripts_dir = Path(skill["path"]).parent / "scripts"
    if not scripts_dir.is_dir() or not code:
        return ""

    scripts = sorted(scripts_dir.glob("*.py"))
    if not scripts:
        return ""

    results = []

    # Only use trusted scripts from the local Skills directory.
    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = Path(temp_dir) / "user_code.py"
        code_path.write_text(code, encoding="utf-8")

        for script_path in scripts:
            try:
                result = subprocess.run(
                    [sys.executable, str(script_path), str(code_path)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    check=False,
                    cwd=script_path.parent.parent,
                )
                status = "SUCCESS" if result.returncode == 0 else "FAILED"
                results.append(
                    f"### Script: {script_path.name}\n"
                    f"Status: {status}\n"
                    f"Exit code: {result.returncode}\n"
                    f"Output:\n{result.stdout or '(No output)'}\n"
                    f"Errors:\n{result.stderr or '(No errors)'}"
                )
            except subprocess.TimeoutExpired:
                results.append(
                    f"### Script: {script_path.name}\n"
                    "Status: FAILED\nExecution timed out after 30 seconds."
                )
            except OSError as exc:
                results.append(
                    f"### Script: {script_path.name}\n"
                    f"Status: FAILED\nCould not launch script: {exc}"
                )

    return "\n\n".join(results)


def ask_agent(user_request):
    """Answer a request using one relevant Skill, if available."""
    skills = discover_skills()
    selected_skill, reason = select_skill(user_request, skills)

    messages = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT}
    ]

    if selected_skill is not None:
        skill_context = load_skill_resources(selected_skill)
        user_code = extract_code_from_request(user_request)
        script_results = execute_skill_scripts(selected_skill, user_code)

        if script_results:
            skill_context += (
                "\n\n## Results from Skill Scripts\n\n"
                "Use these results as supporting evidence. Distinguish "
                "successful checks from errors, and do not claim a check "
                "passed if it failed.\n\n"
                f"{script_results}"
            )

        messages.append({
            "role": "system",
            "content": (
                "Follow the instructions in the selected Skill and use its "
                "supporting resources and script results when relevant.\n\n"
                f"Selected Skill: {selected_skill['name']}\n"
                f"Selection reason: {reason}\n\n"
                f"{skill_context}"
            ),
        })

    messages.append({"role": "user", "content": user_request})
    return call_model(messages)



def read_multiline_input():
    """Read a multiline request until the user enters END."""
    print("Enter your request. Type END on a new line to submit.")
    lines = []

    while True:
        line = input()

        if line.strip()  == "END" :
            break
        if line.strip() in {"END", "exit", "quit"} :
            lines.append(line)
            break

        lines.append(line)

    return "\n".join(lines).strip()


def main():
    """Run an interactive multiline chat with the agent."""
    print("Python Developer Agent")
    print(f"Model: {MODEL}")
    print(f"Skills directory: {SKILLS_DIR}")
    print("Paste your request or code below.")    
    print(
        "Wrap your code in triple backticks (```), "
        "like this:\n\n"
        "```python\n"
        "def greet():\n"
        "    print('Hello, world!')\n"
        "```\n"
    )
    print("Enter END on a new line to submit, or type exit to quit.\n")

    while True:
        try:
            user_request = read_multiline_input()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        
        if user_request.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        if not user_request:
            continue

        try:
            print("Received query. Processing ....")
            answer = ask_agent(user_request)
            print(f"\nAgent:\n{answer}\n")

        except requests.RequestException as exc:
            print(f"\nOpenRouter request failed: {exc}\n")

        except (KeyError, ValueError, RuntimeError) as exc:
            print(f"\nAgent error: {exc}\n")
        print("-"*50)

if __name__ == "__main__":
    main()
