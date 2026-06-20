import os
import json
import re

from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

EXTRACTION_MODEL = "llama-3.1-8b-instant"
REASONING_MODEL = "llama-3.3-70b-versatile"



def clean_json_response(text):
    """
    Extract JSON from LLM response.
    """

    text = text.strip()

    text = re.sub(
        r"^```json",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```$",
        "",
        text
    )

    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1:
        raise ValueError(
            "No JSON found in response"
        )

    return text[start:end + 1]


def ask_groq(
    prompt,
    model=REASONING_MODEL,
    temperature=0
):
    api_key = os.environ.get("GROQ_API_KEY")
    chat = ChatGroq(
        model=model,
        temperature=temperature,
        groq_api_key=api_key
    )

    response = chat.invoke(prompt)

    return response.content


def parse_json_response(response):

    try:
        cleaned = clean_json_response(
            response
        )

        return json.loads(cleaned)

    except Exception as e:

        print(
            f"JSON Parsing Error: {e}"
        )

        return None


def extract_findings(context, model=EXTRACTION_MODEL):

    prompt = f"""
You are an expert building inspection analyst.

Extract all observations from the context.

Return ONLY JSON.

Structure:

{{
    "observations":[
        {{
            "area":"",
            "observation":"",
            "thermal_finding":"",
            "temperature":"",
            "evidence":""
        }}
    ]
}}

CONTEXT:

{context}
"""

    response = ask_groq(
        prompt,
        model=model
    )

    data = parse_json_response(
        response
    )

    if data:
        return data

    return {
        "observations": []
    }


def detect_conflicts(
    inspection_text,
    thermal_text,
    model=REASONING_MODEL
):

    prompt = f"""
Compare the inspection report
with the thermal report.

Identify:

1. Contradictions
2. Missing information
3. Inconsistencies

Return ONLY JSON.

{{
    "conflicts":[
        {{
            "issue":"",
            "inspection_statement":"",
            "thermal_statement":""
        }}
    ]
}}

INSPECTION REPORT:

{inspection_text}

THERMAL REPORT:

{thermal_text}
"""

    response = ask_groq(
        prompt,
        model=model
    )

    data = parse_json_response(
        response
    )

    if data:
        return data

    return {
        "conflicts": []
    }


def generate_root_cause(
    observation,
    thermal_finding,
    model=REASONING_MODEL
):

    prompt = f"""
Determine the probable root cause.

Observation:
{observation}

Thermal Finding:
{thermal_finding}

Return ONLY JSON.

{{
    "root_cause":""
}}
"""

    response = ask_groq(
        prompt,
        model=model
    )

    data = parse_json_response(
        response
    )

    if data:
        return data

    return {
        "root_cause":
        "Not Available"
    }


def assess_severity(
    observation,
    thermal_finding="",
    model=REASONING_MODEL
):

    prompt = f"""
Assess severity.

Observation:
{observation}

Thermal Finding:
{thermal_finding}

Classify:

Low
Medium
High
Critical

Return ONLY JSON.

{{
    "severity":"",
    "reason":""
}}
"""

    response = ask_groq(
        prompt,
        model=model
    )

    data = parse_json_response(
        response
    )

    if data:
        return data

    return {
        "severity": "Unknown",
        "reason": ""
    }


def generate_ddr(
    context,
    findings,
    conflicts,
    model=REASONING_MODEL,
    temperature=0.2
):

    prompt = f"""
You are a senior building diagnostics engineer.

Create a professional
Detailed Diagnostic Report.

Rules:

- Use only supplied data.
- Do not invent facts.
- Mention conflicts.
- Mention missing data.
- Use client-friendly language.

Return ONLY JSON.

Structure:

{{
  "property_issue_summary":"",

  "area_observations":[
    {{
      "area":"",
      "observation":"",
      "thermal_finding":"",
      "root_cause":"",
      "severity":"",
      "recommendation":""
    }}
  ],

  "additional_notes":"",

  "missing_information":[]
}}

FINDINGS:

{json.dumps(findings, indent=2)}

CONFLICTS:

{json.dumps(conflicts, indent=2)}

CONTEXT:

{context}
"""

    response = ask_groq(
        prompt,
        model=model,
        temperature=temperature
    )

    data = parse_json_response(
        response
    )

    if data:
        return data

    return {
        "property_issue_summary":
        "DDR generation failed.",

        "area_observations": [],

        "additional_notes":
        response,

        "missing_information": []
    }


if __name__ == "__main__":

    sample_context = """
    Kitchen leakage observed.

    Thermal hotspot detected
    near kitchen wall.
    """

    findings = extract_findings(
        sample_context
    )

    print(
        json.dumps(
            findings,
            indent=2
        )
    )