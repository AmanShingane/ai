import os

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Image,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import enums
from reportlab.lib.colors import HexColor

# Premium Palette Colors
PRIMARY_COLOR = HexColor("#1E3A8A")   # Deep Navy
SECONDARY_COLOR = HexColor("#475569") # Slate Gray
ACCENT_COLOR = HexColor("#3B82F6")    # Cool Blue
BG_LIGHT = HexColor("#F8FAFC")        # Soft Light Blue/Gray


OUTPUT_DIR = "output"


def ensure_output_dir():
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )


def safe_value(value):

    if value is None:
        return "Not Available"

    if isinstance(value, str):

        if value.strip() == "":
            return "Not Available"

    return str(value)


def add_images(story, image_paths):

    if not image_paths:
        story.append(
            Paragraph(
                "Image Not Available",
                getSampleStyleSheet()["BodyText"]
            )
        )
        return

    for image_path in image_paths[:3]:

        try:

            img = Image(
                image_path,
                width=350,
                height=250
            )

            story.append(img)
            story.append(Spacer(1, 10))

        except Exception:
            continue


def get_severity_color(severity):
    sev = str(severity).lower().strip()
    if sev == "critical":
        return HexColor("#EF4444")  # Red
    elif sev == "high":
        return HexColor("#F97316")  # Orange
    elif sev == "medium":
        return HexColor("#EAB308")  # Amber/Yellow
    elif sev == "low":
        return HexColor("#22C55E")  # Green
    return HexColor("#64748B")      # Slate/Gray


def draw_page_decorations(canvas, doc):
    canvas.saveState()
    # Draw Running Header
    canvas.setFont('Helvetica-Bold', 8)
    canvas.setFillColor(PRIMARY_COLOR)
    canvas.drawString(54, 755, "DETAILED DIAGNOSTIC REPORT (DDR)")
    
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(SECONDARY_COLOR)
    canvas.drawRightString(558, 755, "BUILDING DIAGNOSTICS AI")
    
    # Divider Line
    canvas.setStrokeColor(HexColor("#E2E8F0"))
    canvas.setLineWidth(0.5)
    canvas.line(54, 747, 558, 747)
    
    # Draw Running Footer
    canvas.drawString(54, 36, "CONFIDENTIAL")
    canvas.drawRightString(558, 36, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def generate_pdf(
    ddr_data,
    image_paths=None,
    filename="DDR_Report.pdf"
):
    ensure_output_dir()

    pdf_path = os.path.join(
        OUTPUT_DIR,
        filename
    )

    # Margins leaving 504 pt width (612 - 108)
    doc = SimpleDocTemplate(
        pdf_path,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Premium Typography Styles
    style_title = ParagraphStyle(
        'DDRTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=PRIMARY_COLOR,
        alignment=enums.TA_LEFT,
        spaceAfter=15
    )

    style_h1 = ParagraphStyle(
        'DDRHeading1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=PRIMARY_COLOR,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'DDRBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=SECONDARY_COLOR,
        spaceAfter=8
    )

    style_obs_title = ParagraphStyle(
        'DDRObsTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=PRIMARY_COLOR,
        spaceAfter=3
    )

    style_obs_body = ParagraphStyle(
        'DDRObsBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=SECONDARY_COLOR,
        spaceAfter=2
    )

    story = []

    story.append(Spacer(1, 10))
    
    title = Paragraph(
        "Detailed Diagnostic Report",
        style_title
    )
    story.append(title)
    
    # Decorative Accent line
    divider = Table([[""]], colWidths=[504], rowHeights=[3])
    divider.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), ACCENT_COLOR),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(divider)
    story.append(Spacer(1, 15))

    # Summary
    story.append(
        Paragraph(
            "Property Issue Summary",
            style_h1
        )
    )

    story.append(
        Paragraph(
            safe_value(
                ddr_data.get(
                    "property_issue_summary"
                )
            ),
            style_body
        )
    )

    story.append(
        Spacer(1, 10)
    )

    # Observations
    story.append(
        Paragraph(
            "Area-wise Observations",
            style_h1
        )
    )

    observations = ddr_data.get(
        "area_observations",
        []
    )

    if not observations:
        story.append(
            Paragraph(
                "No observations available.",
                style_body
            )
        )
    else:
        for obs in observations:
            area = safe_value(obs.get("area"))
            severity = safe_value(obs.get("severity"))
            sev_color = get_severity_color(severity)

            p_area = Paragraph(f"Area: {area}", style_obs_title)
            
            p_severity = Paragraph(
                f"<b>Severity:</b> <font color='{sev_color.hexval()}'><b>{severity.upper()}</b></font>",
                style_obs_body
            )
            
            p_obs = Paragraph(
                f"<b>Observation:</b> {safe_value(obs.get('observation'))}",
                style_obs_body
            )
            
            p_thermal = Paragraph(
                f"<b>Thermal Finding:</b> {safe_value(obs.get('thermal_finding'))}",
                style_obs_body
            )
            
            p_cause = Paragraph(
                f"<b>Root Cause:</b> {safe_value(obs.get('root_cause'))}",
                style_obs_body
            )
            
            p_rec = Paragraph(
                f"<b>Recommendation:</b> {safe_value(obs.get('recommendation'))}",
                style_obs_body
            )

            card_data = [
                [p_area],
                [p_severity],
                [p_obs],
                [p_thermal],
                [p_cause],
                [p_rec]
            ]

            card_table = Table(card_data, colWidths=[504])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), BG_LIGHT),
                ('BOX', (0, 0), (-1, -1), 0.5, HexColor("#E2E8F0")),
                ('LINEBEFORE', (0, 0), (0, -1), 3.5, sev_color),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))

            story.append(card_table)
            story.append(Spacer(1, 12))

    story.append(
        PageBreak()
    )

    story.append(
        Paragraph(
            "Supporting Images",
            style_h1
        )
    )

    add_images(
        story,
        image_paths
    )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            "Additional Notes",
            style_h1
        )
    )

    story.append(
        Paragraph(
            safe_value(
                ddr_data.get(
                    "additional_notes"
                )
            ),
            style_body
        )
    )

    story.append(
        Spacer(1, 10)
    )

    story.append(
        Paragraph(
            "Missing Information",
            style_h1
        )
    )

    missing = ddr_data.get(
        "missing_information",
        []
    )

    if not missing:
        story.append(
            Paragraph(
                "None identified.",
                style_body
            )
        )
    else:
        for item in missing:
            story.append(
                Paragraph(
                    f"• {item}",
                    style_body
                )
            )

    doc.build(
        story,
        onFirstPage=draw_page_decorations,
        onLaterPages=draw_page_decorations
    )

    return pdf_path


def create_final_report(
    ddr_data,
    image_paths
):

    pdf_path = generate_pdf(
        ddr_data=ddr_data,
        image_paths=image_paths
    )

    return pdf_path


if __name__ == "__main__":

    sample = {
        "property_issue_summary":
        "Multiple thermal anomalies detected.",

        "area_observations": [
            {
                "area": "Kitchen",
                "observation":
                "Leakage found",

                "thermal_finding":
                "Hotspot present",

                "root_cause":
                "Plumbing issue",

                "severity":
                "High",

                "recommendation":
                "Immediate repair"
            }
        ],

        "additional_notes":
        "Inspection completed.",

        "missing_information":
        [
            "Moisture reading unavailable"
        ]
    }

    pdf = create_final_report(
        sample,
        []
    )

    print(pdf)