"""
Extract certificate data from multiple PDFs into a single table.
Extracts: course_name, topic, agency, skills_id
Uses text extraction (no tables).
"""
import os
import re
import pdfplumber
import pandas as pd


# def extract_certificate_data(pdf_path):
#     with pdfplumber.open(pdf_path) as pdf:
#         full_text = ""
#         for page in pdf.pages:
#             text = page.extract_text()
#             if text:
#                 full_text += text + "\n"

#     lines = [l.strip() for l in full_text.splitlines() if l.strip()]

#     # Course name: lines after "Learning" and before "Course completed by"
#     course_name = ""
#     topic = ""
#     skills_id = ""
#     agency = "LinkedIn Learning"
#     top_skills = []

#     for i, line in enumerate(lines):
#         # Course name sits between "Learning" header and "Course completed by"
#         if line.lower() == "learning" and i + 1 < len(lines):
#             # Collect lines until "Course completed by"
#             name_parts = []
#             j = i + 1
#             while j < len(lines) and not lines[j].lower().startswith("course completed by"):
#                 name_parts.append(lines[j])
#                 j += 1
#             course_name = " ".join(name_parts)

#         # Top skills: lines after "Top skills covered" until instructor line
#         if line.lower() == "top skills covered":
#             j = i + 1
#             while j < len(lines) and "head of learning" not in lines[j].lower():
#                 top_skills.append(lines[j])
#                 j += 1
#             topic = ", ".join(top_skills)

#         # Certificate ID
#         if line.lower().startswith("certificate id:"):
#             skills_id = line.split(":", 1)[-1].strip()

#     return {
#         "course_name": course_name,
#         "topic": topic,
#         "agency": agency,
#         "skills_id": skills_id,
#         "source_pdf": os.path.basename(pdf_path),
#     }

# def extract_field(text, pattern):
#     """Try to extract a field using a regex pattern."""
#     match = re.search(pattern, text, re.IGNORECASE)
#     if match:
#         return match.group(1).strip()
#     return ""


def extract_from_all_pdfs(pdf_folder, output_file="certificates_combined.csv"):
    """Process all PDFs in folder and combine into single DataFrame."""
    all_data = []

    pdf_files = [f for f in os.listdir(pdf_folder) if f.lower().endswith(".pdf")]
    if not pdf_files:
        print(f"No PDF files found in {pdf_folder}")
        return None

    print(f"Found {len(pdf_files)} PDF files")

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        print(f"Processing: {pdf_file}")
        try:
            data = extract_certificate_data(pdf_path)
            all_data.append(data)
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

    if not all_data:
        print("No data extracted")
        return None

    df = pd.DataFrame(all_data)

    df.to_csv(output_file, index=False)
    print(f"\n✓ Saved {len(df)} rows to {output_file}")

    excel_file = output_file.replace(".csv", ".xlsx")
    df.to_excel(excel_file, index=False)
    print(f"✓ Saved {len(df)} rows to {excel_file}")

#     return df

#---------------------
def extract_certificate_data(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"

    lines = [l.strip() for l in full_text.splitlines() if l.strip()]

    course_name = ""
    topic = ""
    skills_id = ""
    agency = "LinkedIn Learning"
    top_skills = []

    for i, line in enumerate(lines):
        # Course name: lines between "Learning" and "Course completed by"
        if line.lower() == "learning" and i + 1 < len(lines):
            name_parts = []
            j = i + 1
            while j < len(lines) and not lines[j].lower().startswith("course completed by"):
                name_parts.append(lines[j])
                j += 1
            course_name = " ".join(name_parts)

        # Top skills
        if line.lower() == "top skills covered":
            j = i + 1
            while j < len(lines) and "head of learning" not in lines[j].lower():
                top_skills.append(lines[j])
                j += 1
            topic = ", ".join(top_skills)

        # Detect co-issuing agency
        if "nasba" in line.lower():
            agency = "LinkedIn Learning / NASBA"
        if "pmi" in line.lower() or "meeting professionals international" in line.lower():
            agency = "LinkedIn Learning / PMI"
            
            
# Version 2.0
        # # Certificate ID — handles both formats:
        # # 1. "Certificate ID: xxxx" on its own line
        # # 2. "Certificate ID: xxxx" buried inside a longer line
        # if "certificate id:" in line.lower():
        #     match = re.search(r"certificate id[:\s]+([a-f0-9\-]{20,})", line, re.IGNORECASE)
        #     if match:
        #         skills_id = match.group(1).strip()

        # # Also catch Registry ID used in some NASBA certs
        # if not skills_id and "registry id" in line.lower():
        #     match = re.search(r"registry id[#:\s]+(\S+)", line, re.IGNORECASE)
        #     if match:
        #         skills_id = match.group(1).strip()

        
# version 3.0        # Certificate ID — handles 3 formats:
# 1. "Certificate ID: xxxx" on same line
# 2. "Certificate ID:" label with value on the NEXT line (PMI style)
# 3. Buried inside a longer line (NASBA style)
        

        
        
    # for i, line in enumerate(lines):
    #     if "certificate id:" in line.lower():
    # # Try to get ID from same line first
    #         match = re.search(r"certificate id[:\s]+([a-f0-9\-]{20,})", line, re.IGNORECASE)
    #         if match:
    #             skills_id = match.group(1).strip()
    # # If nothing found on same line, check the next line
    #         elif i + 1 < len(lines):
    #             next_line = lines[i + 1].strip()
    #         if re.match(r"^[a-f0-9\-]{20,}$", next_line, re.IGNORECASE):
    #             skills_id = next_line
                
                
                
    # for i, line in enumerate(lines):
    #     if "certificate id:" in line.lower():
    #         # Try same line first
    #         match = re.search(r"certificate id[:\s]+([a-f0-9\-]{20,})", line, re.IGNORECASE)
    #         if match:
    #             skills_id = match.group(1).strip()
    #     # Check next 2 lines (in case of blank line between)
    #         else:
    #             for offset in [1, 2]:
    #                 if i + offset < len(lines):                        
    #                     next_line = lines[i + offset].strip()
    #                     print(f"DEBUG next line +{offset}: '{next_line}'")  # <-- remove after fix
    #                     if re.match(r"^[a-f0-9]{20,}$", next_line, re.IGNORECASE):
    #                         skills_id = next_line
    #                         break
                        
    for i, line in enumerate(lines):
        if "certificate id:" in line.lower():
            # Try same line first
            match = re.search(r"[a-f0-9]{32,}", line, re.IGNORECASE)
            if match:
                skills_id = match.group(0).strip()
            else:
            # Check next 2 lines — ID may be on next line, or embedded in longer text
                for offset in [1, 2]:
                    if i + offset < len(lines):
                        next_line = lines[i + offset].strip()
                        match = re.search(r"[a-f0-9]{32,}", next_line, re.IGNORECASE)
                        if match:
                            skills_id = match.group(0).strip()
                            break
                        
    return {
        "course_name": course_name,
        "topic": topic,
        "agency": agency,
        "skills_id": skills_id,
        "source_pdf": os.path.basename(pdf_path),
    }
    
    
    
# Usage
if __name__ == "__main__":
    pdf_folder = "/Users/r/Documents/LinkedInLearning/CertificatesDocs/Professional_Certificates"
    df = extract_from_all_pdfs(pdf_folder)

    if df is not None:
        print("\n=== Sample Data ===")
        print(df[["course_name", "topic", "agency", "skills_id", "source_pdf"]].head())
        print(f"\nTotal certificates: {len(df)}")