from parser import parse_pdf
from rag import build_retriever

from llm import (
    extract_findings,
    detect_conflicts,
    generate_root_cause,
    assess_severity,
    generate_ddr
)

from report import create_final_report


def enrich_findings(findings, model=None):
    """
    Add root cause and severity.
    """

    observations = findings.get(
        "observations",
        []
    )

    enriched = []

    for obs in observations:

        observation = obs.get(
            "observation",
            "Not Available"
        )

        thermal_finding = obs.get(
            "thermal_finding",
            "Not Available"
        )

        # Propagate dynamic model configuration
        kwargs = {}
        if model:
            kwargs["model"] = model

        root_cause_result = generate_root_cause(
            observation,
            thermal_finding,
            **kwargs
        )

        severity_result = assess_severity(
            observation,
            **kwargs
        )

        enriched.append(
            {
                "area": obs.get(
                    "area",
                    "Not Available"
                ),

                "observation": observation,

                "thermal_finding":
                thermal_finding,

                "root_cause":
                root_cause_result.get(
                    "root_cause",
                    "Not Available"
                ),

                "severity":
                severity_result.get(
                    "severity",
                    "Unknown"
                ),

                "recommendation":
                generate_recommendation(
                    severity_result.get(
                        "severity",
                        "Unknown"
                    )
                )
            }
        )

    return enriched


def generate_recommendation(
    severity
):
    """
    Basic recommendation logic.
    """

    severity = severity.lower()

    if severity == "critical":
        return (
            "CRITICAL: Immediate emergency safety mitigation "
            "and professional repairs required."
        )

    elif severity == "high":
        return (
            "Immediate professional "
            "inspection recommended."
        )

    elif severity == "medium":
        return (
            "Schedule corrective action "
            "within a reasonable timeframe."
        )

    elif severity == "low":
        return (
            "Monitor condition and "
            "perform preventive maintenance."
        )

    return "Further investigation required."


def process_documents(
    inspection_pdf,
    thermal_pdf,
    model=None,
    temperature=None
):
    """
    Main DDR pipeline.
    """

    print("Parsing inspection report...")

    inspection_data = parse_pdf(
        inspection_pdf
    )

    print("Parsing thermal report...")

    thermal_data = parse_pdf(
        thermal_pdf
    )

    inspection_text = (
        inspection_data["text"]
    )

    thermal_text = (
        thermal_data["text"]
    )

    inspection_images = (
        inspection_data["images"]
    )

    thermal_images = (
        thermal_data["images"]
    )

    all_images = (
        inspection_images +
        thermal_images
    )

    print("Building RAG index...")

    retriever = build_retriever(
        inspection_text,
        thermal_text
    )

    query = """
    Extract all defects,
    observations,
    thermal anomalies,
    temperature readings,
    structural concerns,
    moisture issues,
    recommendations.
    """

    retrieved_context = (
        retriever.retrieve_context(
            query=query,
            top_k=8
        )
    )

    print("Extracting findings...")

    llm_kwargs = {}
    if model:
        llm_kwargs["model"] = model

    findings = extract_findings(
        retrieved_context,
        **llm_kwargs
    )

    print("Checking conflicts...")

    conflicts = detect_conflicts(
        inspection_text,
        thermal_text,
        **llm_kwargs
    )

    print("Enriching findings...")

    enriched_observations = (
        enrich_findings(
            findings,
            model=model
        )
    )

    findings[
        "observations"
    ] = enriched_observations

    print("Generating DDR...")

    ddr_kwargs = {}
    if model:
        ddr_kwargs["model"] = model
    if temperature is not None:
        ddr_kwargs["temperature"] = temperature

    ddr = generate_ddr(
        retrieved_context,
        findings,
        conflicts,
        **ddr_kwargs
    )

    if not ddr.get(
        "area_observations"
    ):
        ddr[
            "area_observations"
        ] = enriched_observations

    print("Generating PDF...")

    pdf_path = create_final_report(
        ddr_data=ddr,
        image_paths=all_images
    )

    ddr["pdf_path"] = pdf_path

    return ddr


if __name__ == "__main__":

    result = process_documents(
        "inspection.pdf",
        "thermal.pdf"
    )

    print(
        result[
            "property_issue_summary"
        ]
    )