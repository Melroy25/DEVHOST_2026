"""scripts/generate_demo_files.py — Create sample medical files for UI upload testing.

Creates:
1. demo_files/1_Lab_Report_Metabolic_Panel.pdf  (Multi-page PDF)
2. demo_files/2_Prescription_Outpatient.docx    (DOCX document)
3. demo_files/3_Clinical_Scan_Note.png         (High-res medical note for OCR)
4. demo_files/4_Discharge_Summary.txt          (Multi-page TXT with smart pagination)
"""

from pathlib import Path
from fpdf import FPDF
from docx import Document
from PIL import Image, ImageDraw, ImageFont

ROOT_DIR = Path(__file__).resolve().parent.parent
DEMO_DIR = ROOT_DIR / "demo_files"
DEMO_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Generate PDF: Lab Report (2 pages)
# ---------------------------------------------------------------------------
def create_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Page 1: Comprehensive Metabolic Panel
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(14, 94, 86)  # Dark teal
    pdf.cell(0, 10, "METROPOLITAN CLINICAL LABORATORIES", ln=True, align="C")

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 61, 58)
    pdf.cell(0, 8, "COMPREHENSIVE METABOLIC & LIPID PANEL", ln=True, align="C")
    pdf.ln(4)

    pdf.set_draw_color(213, 233, 230)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(94, 127, 123)
    pdf.cell(100, 6, "Patient Name: Jhon Doe", ln=False)
    pdf.cell(90, 6, "DOB: 1980-05-12 (Age: 46)", ln=True)
    pdf.cell(100, 6, "Patient ID: 44444444-4444-4444", ln=False)
    pdf.cell(90, 6, "Collection Date: 2026-10-15", ln=True)
    pdf.cell(100, 6, "Ordering Physician: Dr. Robert Chen, MD", ln=False)
    pdf.cell(90, 6, "Status: FINAL REPORT", ln=True)
    pdf.ln(6)

    # Table Header
    pdf.set_fill_color(230, 244, 242)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(15, 61, 58)
    pdf.cell(60, 8, "Test Description", 1, 0, "L", fill=True)
    pdf.cell(35, 8, "Result", 1, 0, "C", fill=True)
    pdf.cell(30, 8, "Reference", 1, 0, "C", fill=True)
    pdf.cell(30, 8, "Units", 1, 0, "C", fill=True)
    pdf.cell(35, 8, "Flag", 1, 1, "C", fill=True)

    # Table Rows
    tests = [
        ("Fasting Blood Glucose", "118", "70 - 99", "mg/dL", "HIGH"),
        ("Hemoglobin A1c", "6.8", "4.0 - 5.6", "%", "HIGH"),
        ("Serum Creatinine", "1.05", "0.70 - 1.30", "mg/dL", "NORMAL"),
        ("Blood Urea Nitrogen (BUN)", "18", "7 - 20", "mg/dL", "NORMAL"),
        ("eGFR", "> 60", "> 60", "mL/min/1.73m2", "NORMAL"),
        ("Sodium", "140", "136 - 145", "mmol/L", "NORMAL"),
        ("Potassium", "4.4", "3.5 - 5.1", "mmol/L", "NORMAL"),
        ("Total Cholesterol", "215", "< 200", "mg/dL", "BORDERLINE"),
        ("HDL Cholesterol", "42", "> 40", "mg/dL", "NORMAL"),
        ("LDL Cholesterol", "138", "< 100", "mg/dL", "ELEVATED"),
        ("Triglycerides", "175", "< 150", "mg/dL", "HIGH"),
    ]

    pdf.set_font("Helvetica", "", 9)
    for name, res, ref, units, flag in tests:
        if flag in ("HIGH", "ELEVATED"):
            pdf.set_text_color(183, 121, 31)  # Amber warning
        else:
            pdf.set_text_color(15, 61, 58)
        pdf.cell(60, 7, name, 1, 0, "L")
        pdf.cell(35, 7, res, 1, 0, "C")
        pdf.cell(30, 7, ref, 1, 0, "C")
        pdf.cell(30, 7, units, 1, 0, "C")
        pdf.cell(35, 7, flag, 1, 1, "C")

    # Page 2: Clinical Interpretation
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(14, 94, 86)
    pdf.cell(0, 10, "ENDOCRINOLOGY CLINICAL INTERPRETATION", ln=True)
    pdf.ln(3)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(15, 61, 58)
    summary_text = (
        "CLINICAL IMPRESSION & RECOMMENDATIONS:\n\n"
        "1. Glycemic Control:\n"
        "   Fasting blood glucose of 118 mg/dL and HbA1c of 6.8% indicate Type 2 Diabetes Mellitus with sub-optimal glycemic control.\n\n"
        "2. Lipid Profile:\n"
        "   Total cholesterol (215 mg/dL), LDL (138 mg/dL) and triglycerides (175 mg/dL) demonstrate mixed dyslipidemia.\n\n"
        "3. Renal Function:\n"
        "   Serum creatinine (1.05 mg/dL) and estimated GFR > 60 mL/min remain within normal baseline parameters.\n\n"
        "MANAGEMENT PLAN:\n"
        "- Initiate Metformin 500mg BID orally with meals.\n"
        "- Continue Atorvastatin 20mg once daily at bedtime.\n"
        "- Dietary lifestyle modifications: low glycemic index diet and 150 min/week moderate aerobic activity.\n"
        "- Repeat complete metabolic profile and HbA1c in 12 weeks.\n\n"
        "Attending Physician: Dr. Robert Chen, MD, FACP\n"
        "Department of Endocrinology, Metropolitan Health System"
    )
    pdf.multi_cell(0, 6, summary_text)

    out_path = DEMO_DIR / "1_Lab_Report_Metabolic_Panel.pdf"
    pdf.output(str(out_path))
    print(f"Created: {out_path}")

# ---------------------------------------------------------------------------
# 2. Generate DOCX: Prescription Order
# ---------------------------------------------------------------------------
def create_docx():
    doc = Document()

    doc.add_heading("ST. JUDE AMBULATORY HEALTH CLINIC", level=1)
    doc.add_paragraph("OUTPATIENT PHARMACY PRESCRIPTION ORDER\nDate: October 20, 2026")

    p = doc.add_paragraph()
    p.add_run("PATIENT DETAILS:\n").bold = True
    p.add_run("Patient Name: Jhon Doe\n")
    p.add_run("DOB: 1980-05-12 | Sex: Male\n")
    p.add_run("Known Drug Allergies: Penicillin (severe urticaria/hives)\n")

    doc.add_heading("PRESCRIBED MEDICATIONS:", level=2)

    meds = [
        ("1. Metformin Hydrochloride 500mg Oral Tablet",
         "Sig: Take 1 tablet by mouth twice daily with morning and evening meals.",
         "Dispense: 60 tablets | Refills: 3 | Indication: Type 2 Diabetes Mellitus"),
        ("2. Atorvastatin Calcium 20mg Oral Tablet",
         "Sig: Take 1 tablet by mouth once daily at bedtime.",
         "Dispense: 30 tablets | Refills: 2 | Indication: Hypercholesterolemia"),
        ("3. Lisinopril 10mg Oral Tablet",
         "Sig: Take 1 tablet by mouth once daily in the morning.",
         "Dispense: 30 tablets | Refills: 2 | Indication: Essential Hypertension")
    ]

    for title, sig, meta in meds:
        doc.add_heading(title, level=3)
        doc.add_paragraph(sig)
        doc.add_paragraph(meta)

    doc.add_heading("PRESCRIBER VERIFICATION", level=2)
    doc.add_paragraph(
        "Prescribed by: Dr. Sarah Vance, MD\n"
        "State License #: MD-8849201 | DEA: BV9284711\n"
        "Electronically Signed on 2026-10-20 at 14:30 EST"
    )

    out_path = DEMO_DIR / "2_Prescription_Outpatient.docx"
    doc.save(str(out_path))
    print(f"Created: {out_path}")

# ---------------------------------------------------------------------------
# 3. Generate PNG: Clinical Scan Note (For Vision OCR)
# ---------------------------------------------------------------------------
def create_image():
    # 1000 x 700 crisp image
    img = Image.new("RGB", (1000, 720), color="#F4FBFA")
    draw = ImageDraw.Draw(img)

    # Frame border
    draw.rectangle([20, 20, 980, 700], outline="#D5E9E6", width=2)
    # Header box
    draw.rectangle([22, 22, 978, 90], fill="#0E5E56")

    # Draw header text
    draw.text((40, 35), "CENTRAL REGIONAL HOSPITAL - CLINICAL CONSULTATION NOTE", fill="#FFFFFF")
    draw.text((40, 60), "DEPARTMENT OF CARDIOLOGY & INTERNAL MEDICINE", fill="#CFEDE7")

    # Metadata
    y = 110
    draw.text((40, y), "PATIENT: Jhon Doe", fill="#0F3D3A")
    draw.text((360, y), "DOB: 12-May-1980", fill="#0F3D3A")
    draw.text((640, y), "VISIT DATE: 2026-11-05", fill="#0F3D3A")

    draw.line([40, y + 25, 960, y + 25], fill="#D5E9E6", width=1)

    y = 150
    draw.text((40, y), "VITAL SIGNS & OBSERVATIONS:", fill="#0E5E56")
    y += 25
    draw.text((60, y), "Blood Pressure: 132/84 mmHg  |  Pulse: 72 bpm  |  Temp: 98.6 F  |  SpO2: 99% on room air", fill="#0F3D3A")
    y += 20
    draw.text((60, y), "BMI: 27.4 kg/m2  |  Cardiovascular: Regular rate and rhythm, no S3/S4 gallop, no murmurs", fill="#5E7F7B")

    y += 35
    draw.text((40, y), "ACTIVE CLINICAL ASSESSMENT & ORDERS:", fill="#0E5E56")
    y += 25
    notes = [
        "1. Chronic Essential Hypertension: Moderately well controlled on Lisinopril 10mg daily.",
        "2. Type 2 Diabetes Mellitus: Continue Metformin 500mg BID. Patient reports good gastrointestinal tolerance.",
        "3. Hyperlipidemia: Continue Atorvastatin 20mg at bedtime. Lipid profile improving.",
        "4. Acute Upper Respiratory Symptoms: Mild non-productive cough, lungs clear to auscultation bilaterally.",
        "   - Rx: Benzonatate 100mg PO TID PRN for cough (Quantity: 20 capsules, Refills: 0)",
        "   - Rx: Guaifenesin 600mg extended-release 1 tablet every 12 hours with plenty of water",
        "5. ALLERGY WARNING: Confirmed allergy to Penicillin (anaphylactoid hives) - Beta-lactams prohibited."
    ]
    for line in notes:
        draw.text((60, y), line, fill="#0F3D3A")
        y += 28

    y += 20
    draw.line([40, y, 960, y], fill="#D5E9E6", width=1)
    y += 15
    draw.text((40, y), "Attending Physician: Dr. Marcus Henderson, MD (Cardiology & Internal Medicine)", fill="#0E5E56")
    draw.text((40, y + 22), "Verified Electronic Signature: M. Henderson, MD [NPI: 104928502]", fill="#5E7F7B")

    out_path = DEMO_DIR / "3_Clinical_Scan_Note.png"
    img.save(str(out_path), "PNG")
    print(f"Created: {out_path}")

# ---------------------------------------------------------------------------
# 4. Generate TXT: Discharge Summary with Smart Pagination
# ---------------------------------------------------------------------------
def create_txt():
    content = """RECORD #1 - HOSPITAL ADMISSION & COURSE

PATIENT NAME: Jhon Doe
RECORD TYPE: Hospital Discharge Summary
ADMISSION DATE: September 01, 2026
DISCHARGE DATE: September 04, 2026
ADMITTING DIAGNOSIS: Acute Bronchitis with Mild Exertional Dyspnea
SECONDARY DIAGNOSES: Essential Hypertension, Type 2 Diabetes Mellitus

HOSPITAL COURSE:
The patient is a 46-year-old male who presented to the Emergency Department with a 3-day history of productive cough, wheezing, and low-grade pyrexia (99.8 F). Chest radiography demonstrated peribronchial thickening without focal alveolar consolidation or pleural effusion.

During hospitalization, the patient received nebulized Albuterol/Ipratropium treatments, systemic corticosteroid taper (Prednisone 40mg daily x 3 days), and supplemental oxygen via nasal cannula. Respiratory symptoms improved significantly over 72 hours. By hospital day 3, oxygen saturation remained stable at 98% on room air.

RECORD #2 - DISCHARGE MEDICATIONS & POST-ACUTE CARE PLAN

DISCHARGE MEDICATIONS:
1. Albuterol HFA 90mcg Inhalation Aerosol:
   Inhale 2 puffs every 4 to 6 hours as needed for shortness of breath or wheezing.
2. Lisinopril 10mg Oral Tablet:
   Take 1 tablet daily in the morning for hypertension.
3. Metformin 500mg Oral Tablet:
   Take 1 tablet twice daily with morning and evening meals.
4. Atorvastatin 20mg Oral Tablet:
   Take 1 tablet once daily at bedtime.

ALLERGIES & CONTRAINDICATIONS:
- Penicillin: Severe allergic reaction (generalized hives). Avoid all penicillins and cephalosporins.

FOLLOW-UP APPOINTMENTS:
- Primary Care Clinic: Schedule follow-up appointment within 7-10 days of discharge.
- Pulmonary Function Testing: Planned in 6 weeks if exertional symptoms persist.

DISCHARGING PHYSICIAN:
Dr. Elena Rostova, MD — Department of Hospital Medicine
Valley Memorial Hospital
"""
    out_path = DEMO_DIR / "4_Discharge_Summary.txt"
    out_path.write_text(content, encoding="utf-8")
    print(f"Created: {out_path}")

if __name__ == "__main__":
    create_pdf()
    create_docx()
    create_image()
    create_txt()
    print("All demo files created successfully in demo_files/!")
