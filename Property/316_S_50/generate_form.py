#!/usr/bin/env python3
"""Generate a fillable PDF for the Self-Guided Showing Agreement."""

from fpdf import FPDF, XPos, YPos

class ShowingForm(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        self.logo_path = "/Users/matthewpappas/code/Latex/Property/sm_logo.png"
        self.accent_color = (25, 55, 95)
        self.field_bg = (240, 245, 250)
        self.field_border = (180, 190, 200)
        
    def header_section(self):
        self.image(self.logo_path, x=10, y=7, w=22)
        self.set_xy(35, 8)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*self.accent_color)
        self.cell(0, 6, "SELF-GUIDED SHOWING AGREEMENT", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_x(35)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(60, 60, 60)
        self.cell(0, 5, "Property: 316 S 50th Ave, Omaha, NE", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_y(22)
        self.divider()
        
    def divider(self):
        self.set_draw_color(*self.accent_color)
        self.set_line_width(0.3)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)
        
    def section_header(self, text):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*self.accent_color)
        self.cell(0, 5, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)
        
    def draw_field_box(self, x, y, w, h=5):
        self.set_fill_color(*self.field_bg)
        self.set_draw_color(*self.field_border)
        self.rect(x, y, w, h, style='DF')
        
    def form_row(self, label, field_width=None):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(40, 40, 40)
        label_w = self.get_string_width(label) + 2
        self.cell(label_w, 6, label)
        x = self.get_x()
        y = self.get_y() + 0.5
        fw = field_width if field_width else (195 - x)
        self.draw_field_box(x, y, fw)
        self.ln(7)
        
    def form_row_multi(self, fields):
        self.set_font("Helvetica", "", 8)
        self.set_text_color(40, 40, 40)
        start_x = 10
        y = self.get_y() + 0.5
        for label, field_width in fields:
            self.set_x(start_x)
            label_w = self.get_string_width(label) + 2
            self.cell(label_w, 6, label)
            x = self.get_x()
            self.draw_field_box(x, y, field_width)
            start_x = x + field_width + 6
        self.ln(7)
        
    def para(self, title, content):
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(40, 40, 40)
        self.cell(0, 4.5, title, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_font("Helvetica", "", 8)
        self.multi_cell(0, 3.8, content)
        self.ln(1)


def create_form():
    pdf = ShowingForm()
    pdf.add_page()
    
    # Header
    pdf.header_section()
    
    # Visitor Information
    pdf.section_header("VISITOR INFORMATION")
    pdf.form_row("Full Legal Name:")
    pdf.form_row("Address:")
    pdf.form_row_multi([("City:", 55), ("State:", 20), ("ZIP:", 30)])
    pdf.form_row_multi([("Phone:", 60), ("Email:", 85)])
    pdf.form_row_multi([("Driver's License #:", 55), ("State:", 20), ("DOB:", 35)])
    
    pdf.divider()
    
    # Access Details
    pdf.section_header("ACCESS AUTHORIZATION")
    pdf.form_row_multi([("Date of Showing:", 40), ("Time: From", 20), ("to", 20)])
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 3.8, "I am granted temporary access to view this Property for potential rental. I have provided a photo of my government-issued ID for verification. The access code is for my exclusive, one-time use only. Sharing, transferring, or disclosing this code to any third party constitutes unauthorized entry and criminal trespass under Nebraska law (Neb. Rev. Stat. § 28-520).")
    pdf.ln(1)
    
    pdf.divider()
    
    # Terms - Condensed
    pdf.section_header("TERMS AND CONDITIONS")
    
    pdf.para("1. CONDUCT & SURVEILLANCE",
        "I acknowledge the Property may be monitored by security cameras and smart devices. During access, I agree to: (a) enter/exit only through designated doors; (b) not smoke or bring pets; (c) not damage, remove, or tamper with any property, fixtures, locks, or keys; (d) lock all doors and windows upon departure; and (e) vacate promptly at the scheduled end time.")
    
    pdf.para("2. GUESTS",
        "I may bring up to two (2) adult guests who must enter with me, remain with me at all times, and exit with me. Guests may not enter separately or remain after I depart. I am fully responsible for their conduct and any damage they cause.")
    
    pdf.para("3. NO TENANCY OR POSSESSION RIGHTS",
        "This Agreement grants a revocable license for temporary viewing only. NO tenancy, leasehold, or possessory interest is created. I acquire no right to occupy, reside in, or remain on the Property beyond the scheduled showing time. Any attempt to remain, re-enter, or claim possession constitutes criminal trespass and unlawful detainer.")
    
    pdf.divider()
    
    # Liability - Consolidated
    pdf.section_header("LIABILITY AND RELEASE")
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 3.8, "I voluntarily assume all risks associated with entering this Property. To the fullest extent permitted by Nebraska law, I release and hold harmless the Property Owner, Landlord, and their agents from any claims arising from my access. I am personally liable for any theft, damage, or loss discovered after my access, including missing appliances, fixtures, or new damage not documented prior to my entry. I authorize use of my identification information to pursue civil or criminal remedies.")
    pdf.ln(1)
    
    pdf.divider()
    
    # Representations - Condensed
    pdf.section_header("REPRESENTATIONS")
    
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 3.8, "I represent that: I am at least 18 years of age; the information provided is true and accurate; I have not been convicted of any felony involving theft, burglary, or trespass; and I am genuinely interested in renting this Property.")
    pdf.ln(2)
    
    pdf.divider()
    
    # Application Note
    pdf.section_header("APPLICATION PROCESS")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 3.8, "Among similarly qualified applicants, priority is given to those who complete all screenings and submit deposit and first month's rent first. Landlord uses MySmartMove for tenant screening; a link will be provided upon request.")
    pdf.ln(1)
    
    pdf.divider()
    
    # Signature
    pdf.section_header("ACKNOWLEDGMENT AND SIGNATURE")
    pdf.set_font("Helvetica", "B", 7.5)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 3.5, "BY SIGNING BELOW, I ACKNOWLEDGE THAT I HAVE READ AND UNDERSTAND THIS AGREEMENT, INCLUDING THE RELEASE OF LIABILITY, AND AGREE TO BE BOUND BY ITS TERMS.")
    pdf.ln(4)
    
    pdf.form_row("Signature:", 100)
    pdf.form_row("Printed Name:", 100)
    pdf.form_row_multi([("Date:", 45), ("Time:", 45)])
    
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 7)
    pdf.set_text_color(120, 120, 120)
    pdf.multi_cell(0, 3.5, "This Agreement is governed by the laws of the State of Nebraska. Any disputes shall be resolved in the courts of Douglas County, Nebraska.")
    
    # Save
    output_path = "/Users/matthewpappas/code/Latex/Property/316_S_50/self_guided_showing_form.pdf"
    pdf.output(output_path)
    print(f"PDF created: {output_path}")
    return output_path


if __name__ == "__main__":
    create_form()
