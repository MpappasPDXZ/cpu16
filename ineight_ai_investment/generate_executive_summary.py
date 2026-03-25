#!/usr/bin/env python3
"""
Generate one-page executive summary for InEight AI investment
Clean, modern Harvard Business Review style
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos

class ExecutiveSummaryPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_margins(12, 10, 12)
        self.set_auto_page_break(False)  # Disable auto page break to keep single page
    
    def header(self):
        # Clean header with rules
        self.set_line_width(0.4)
        self.set_draw_color(0, 0, 0)
        self.line(12, 10, 198, 10)
        
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(0, 0, 0)
        self.set_y(12)
        self.cell(0, 6, "InEight AI Investment", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        self.set_font("Helvetica", "", 9)
        self.set_text_color(80, 80, 80)
        self.cell(0, 4, "Executive Summary", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        
        self.set_line_width(0.4)
        self.line(12, 22, 198, 22)
        self.set_y(24)
    
    def section_header(self, number, title):
        """Clean section header with number and title"""
        self.ln(3)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        self.set_x(12)
        self.cell(0, 5, f"{number}. {title}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.2)
        self.line(12, self.get_y(), 198, self.get_y())
        self.ln(2)
    
    def paragraph(self, text, size=8):
        """Clean paragraph with proper line height"""
        self.set_font("Helvetica", "", size)
        self.set_text_color(40, 40, 40)
        self.set_x(12)
        self.multi_cell(174, 4, text)
        self.ln(1.5)
    
    def key_stat(self, label, value, description=""):
        """Inline key statistic"""
        self.set_font("Helvetica", "", 8)
        self.set_text_color(40, 40, 40)
        self.set_x(12)
        self.cell(0, 4, f"{label}: ", new_x=XPos.RIGHT)
        self.set_font("Helvetica", "B", 8)
        self.cell(0, 4, value, new_x=XPos.RIGHT)
        if description:
            self.set_font("Helvetica", "", 8)
            self.cell(0, 4, f" {description}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            self.ln()
    
    def draw_rounded_rect(self, x, y, w, h, r, style="D"):
        """Draw a rectangle with very subtle rounded corners"""
        # Use a much smaller radius for subtle effect
        r = min(r, 0.8)  # Cap at 0.8mm for very subtle corners
        
        if "F" in style:
            self.set_fill_color(248, 248, 248)
            # Fill main body
            self.rect(x + r, y, w - 2*r, h, style="F")
            self.rect(x, y + r, w, h - 2*r, style="F")
            # Fill corner areas
            self.rect(x + r, y + r, w - 2*r, h - 2*r, style="F")
        if "D" in style:
            self.set_draw_color(180, 180, 180)
            # Top
            self.line(x + r, y, x + w - r, y)
            # Bottom
            self.line(x + r, y + h, x + w - r, y + h)
            # Left
            self.line(x, y + r, x, y + h - r)
            # Right
            self.line(x + w, y + r, x + w, y + h - r)
            # Very subtle corner chamfers (barely visible)
            self.line(x, y + r, x + r, y)
            self.line(x + w - r, y, x + w, y + r)
            self.line(x, y + h - r, x + r, y + h)
            self.line(x + w - r, y + h, x + w, y + h - r)
    
    def draw_flow_boxes(self, boxes, y_start=None, tall=False):
        """Draw horizontal flow diagram"""
        if y_start:
            self.set_y(y_start)
        current_y = self.get_y()
        
        self.set_line_width(0.3)
        
        num_boxes = len(boxes)
        total_width = 174
        box_width = (total_width - (num_boxes - 1) * 6) / num_boxes
        x_start = 12
        box_height = 12 if tall else 9  # Reduced heights
        
        for i, (title, subtitle) in enumerate(boxes):
            x = x_start + i * (box_width + 6)
            
            # Draw box with very subtle rounded corners
            self.draw_rounded_rect(x, current_y, box_width, box_height, 0.8, style="FD")
            
            # Title (value/number)
            self.set_font("Helvetica", "B", 7)
            self.set_text_color(0, 0, 0)
            self.set_xy(x + 2, current_y + 1.5)
            self.cell(box_width - 4, 3.5, title, border=0, align="C")
            
            # Subtitle (label) - can be multi-line for tall boxes
            self.set_font("Helvetica", "", 5)
            self.set_text_color(100, 100, 100)
            if tall:
                self.set_xy(x + 2, current_y + 5)
                self.multi_cell(box_width - 4, 2.2, subtitle, border=0, align="C")
            else:
                self.set_xy(x + 2, current_y + 5)
                self.cell(box_width - 4, 2.5, subtitle, border=0, align="C")
            
            # Arrow
            if i < num_boxes - 1:
                arrow_x = x + box_width + 1
                arrow_y = current_y + box_height / 2
                self.set_draw_color(150, 150, 150)
                self.line(arrow_x, arrow_y, arrow_x + 4, arrow_y)
                self.line(arrow_x + 3, arrow_y - 1.5, arrow_x + 4, arrow_y)
                self.line(arrow_x + 3, arrow_y + 1.5, arrow_x + 4, arrow_y)
        
        self.set_y(current_y + box_height + 2)
    
    def draw_architecture_flow(self, y_start=None):
        """Draw Section 5 architecture with InEight vs Kiewit distinction"""
        if y_start:
            self.set_y(y_start)
        current_y = self.get_y()
        
        self.set_line_width(0.3)
        
        # Define boxes - 4 boxes with different styling
        boxes = [
            ("InEight", "Front End", "C# to React", "good"),      # InEight side
            ("InEight", "Backend", "SQL Server*", "warning"),      # InEight side, warning
            ("Kiewit", "KIP Lake", "Scalable AI", "good"),         # Kiewit side
            ("Kiewit", "AI Agents", "Built by Kiewit", "good"),    # Kiewit side
        ]
        
        num_boxes = len(boxes)
        total_width = 174
        box_width = (total_width - (num_boxes - 1) * 6) / num_boxes
        x_start = 12
        box_height = 14
        
        # Draw side labels first
        self.set_font("Helvetica", "I", 5)
        self.set_text_color(100, 100, 100)
        
        # InEight side label
        self.set_xy(x_start, current_y - 3)
        self.cell(box_width * 2 + 6, 3, "InEight Platform", align="C")
        
        # Kiewit side label
        self.set_xy(x_start + 2 * (box_width + 6), current_y - 3)
        self.cell(box_width * 2 + 6, 3, "Kiewit (KIP)", align="C")
        
        for i, (owner, title, subtitle, style) in enumerate(boxes):
            x = x_start + i * (box_width + 6)
            
            # Different fill colors based on style
            if style == "warning":
                self.set_fill_color(255, 245, 238)  # Light red tint
                self.set_draw_color(200, 150, 150)  # Reddish border
            else:
                self.set_fill_color(248, 248, 248)
                self.set_draw_color(180, 180, 180)
            
            # Draw box
            self.draw_rounded_rect(x, current_y, box_width, box_height, 0.8, style="FD")
            
            # Title
            self.set_font("Helvetica", "B", 7)
            self.set_text_color(0, 0, 0)
            self.set_xy(x + 2, current_y + 2)
            self.cell(box_width - 4, 3.5, title, border=0, align="C")
            
            # Subtitle - italic for warning
            if style == "warning":
                self.set_font("Helvetica", "I", 5)
                self.set_text_color(150, 80, 80)
            else:
                self.set_font("Helvetica", "", 5)
                self.set_text_color(100, 100, 100)
            self.set_xy(x + 2, current_y + 6)
            self.cell(box_width - 4, 2.5, subtitle, border=0, align="C")
            
            # Small note for SQL Server
            if style == "warning":
                self.set_font("Helvetica", "I", 4)
                self.set_text_color(150, 80, 80)
                self.set_xy(x + 2, current_y + 9)
                self.cell(box_width - 4, 2, "(compute=storage)", border=0, align="C")
            
            # Arrow
            if i < num_boxes - 1:
                arrow_x = x + box_width + 1
                arrow_y = current_y + box_height / 2
                self.set_draw_color(150, 150, 150)
                self.line(arrow_x, arrow_y, arrow_x + 4, arrow_y)
                self.line(arrow_x + 3, arrow_y - 1.5, arrow_x + 4, arrow_y)
                self.line(arrow_x + 3, arrow_y + 1.5, arrow_x + 4, arrow_y)
        
        self.set_y(current_y + box_height + 2)
    
    def draw_dual_path_architecture(self):
        """Draw InEight vs Kiewit architecture with Anthropic Agent Skills"""
        current_y = self.get_y()
        
        # Layout constants
        left_margin = 12
        ineight_width = 70
        kiewit_start = 90
        box_h = 7
        small_box = 22
        
        # === INEIGHT SIDE (Left) ===
        # Section label
        self.set_font("Helvetica", "B", 6)
        self.set_text_color(150, 80, 80)
        self.set_xy(left_margin, current_y)
        self.cell(ineight_width, 3, "INEIGHT (Source Of Data)", align="C")
        
        # C#/.NET box
        box_y = current_y + 4
        self.set_fill_color(255, 248, 245)
        self.set_draw_color(200, 160, 150)
        self.draw_rounded_rect(left_margin, box_y, 30, box_h, 0.8, style="FD")
        self.set_font("Helvetica", "B", 5)
        self.set_text_color(0, 0, 0)
        self.set_xy(left_margin, box_y + 1)
        self.cell(30, 2.5, "C#/.NET", align="C")
        self.set_font("Helvetica", "I", 4)
        self.set_text_color(150, 100, 80)
        self.set_xy(left_margin, box_y + 3.5)
        self.cell(30, 2.5, "(legacy UI)", align="C")
        
        # Arrow
        self.set_draw_color(180, 150, 130)
        self.line(left_margin + 31, box_y + box_h/2, left_margin + 35, box_y + box_h/2)
        
        # SQL Server box
        sql_x = left_margin + 36
        self.set_fill_color(255, 245, 238)
        self.set_draw_color(200, 150, 150)
        self.draw_rounded_rect(sql_x, box_y, 34, box_h, 0.8, style="FD")
        self.set_font("Helvetica", "B", 5)
        self.set_text_color(0, 0, 0)
        self.set_xy(sql_x, box_y + 1)
        self.cell(34, 2.5, "SQL Server", align="C")
        self.set_font("Helvetica", "I", 4)
        self.set_text_color(150, 80, 80)
        self.set_xy(sql_x, box_y + 3.5)
        self.cell(34, 2.5, "(compute=storage)", align="C")
        
        # InEight context labels
        self.set_font("Helvetica", "I", 4)
        self.set_text_color(100, 80, 80)
        self.set_xy(left_margin, box_y + box_h + 1)
        self.cell(ineight_width, 2.5, "$122.7M / 1.6M hrs digital work", align="C")
        self.set_xy(left_margin, box_y + box_h + 3.5)
        self.cell(ineight_width, 2.5, "AI most powerful here - but brittle", align="C")
        
        # === ARROW BETWEEN SIDES ===
        arrow_y = box_y + box_h/2
        self.set_draw_color(120, 120, 120)
        self.set_line_width(0.4)
        self.line(sql_x + 35, arrow_y, kiewit_start - 2, arrow_y)
        self.line(kiewit_start - 4, arrow_y - 1.5, kiewit_start - 2, arrow_y)
        self.line(kiewit_start - 4, arrow_y + 1.5, kiewit_start - 2, arrow_y)
        self.set_line_width(0.3)
        
        # === KIEWIT SIDE (Right) ===
        kiewit_width = 108
        
        # Section label
        self.set_font("Helvetica", "B", 6)
        self.set_text_color(80, 120, 80)
        self.set_xy(kiewit_start, current_y)
        self.cell(kiewit_width, 3, "KIEWIT (Scalable AI Tool Chain)", align="C")
        
        # Iceberg box
        self.set_fill_color(245, 250, 245)
        self.set_draw_color(150, 180, 150)
        self.draw_rounded_rect(kiewit_start, box_y, small_box, box_h, 0.8, style="FD")
        self.set_font("Helvetica", "B", 5)
        self.set_text_color(0, 0, 0)
        self.set_xy(kiewit_start, box_y + 1)
        self.cell(small_box, 2.5, "Iceberg", align="C")
        self.set_font("Helvetica", "", 4)
        self.set_text_color(80, 120, 80)
        self.set_xy(kiewit_start, box_y + 3.5)
        self.cell(small_box, 2.5, "(lake)", align="C")
        
        # Arrow
        self.set_draw_color(150, 180, 150)
        self.line(kiewit_start + small_box + 1, arrow_y, kiewit_start + small_box + 4, arrow_y)
        
        # Dagster + AKS box
        dag_x = kiewit_start + small_box + 5
        self.draw_rounded_rect(dag_x, box_y, small_box + 4, box_h, 0.8, style="FD")
        self.set_font("Helvetica", "B", 5)
        self.set_text_color(0, 0, 0)
        self.set_xy(dag_x, box_y + 1)
        self.cell(small_box + 4, 2.5, "Dagster+AKS", align="C")
        self.set_font("Helvetica", "", 4)
        self.set_text_color(80, 120, 80)
        self.set_xy(dag_x, box_y + 3.5)
        self.cell(small_box + 4, 2.5, "(elastic orch)", align="C")
        
        # Arrow to Anthropic box (will connect to its left side)
        agent_arrow_y = box_y + box_h/2 + 4  # Adjusted for moved box
        self.line(dag_x + small_box + 5, arrow_y, dag_x + small_box + 8, agent_arrow_y)
        
        # === ANTHROPIC AGENT SKILLS BOX ===
        agent_x = dag_x + small_box + 9
        agent_w = 50
        agent_h = 16
        agent_top = box_y + 2  # Moved down to align better
        
        self.set_fill_color(240, 248, 240)
        self.set_draw_color(130, 170, 130)
        self.draw_rounded_rect(agent_x, agent_top, agent_w, agent_h, 0.8, style="FD")
        
        # Title
        self.set_font("Helvetica", "B", 5)
        self.set_text_color(0, 0, 0)
        self.set_xy(agent_x, agent_top + 1)
        self.cell(agent_w, 2.5, "Anthropic Agent Skills", align="C")
        
        # Container copies (3 small boxes)
        copy_y = agent_top + 4  # Relative to agent box top
        copy_w = 12
        copy_h = 4
        copy_gap = 3
        copy_start = agent_x + 5
        
        self.set_fill_color(230, 245, 230)
        self.set_draw_color(150, 180, 150)
        for i in range(3):
            cx = copy_start + i * (copy_w + copy_gap)
            self.draw_rounded_rect(cx, copy_y, copy_w, copy_h, 0.5, style="FD")
            self.set_font("Helvetica", "", 3.5)
            self.set_text_color(80, 100, 80)
            self.set_xy(cx, copy_y + 1)
            self.cell(copy_w, 2, f"copy{i+1}", align="C")
        
        # Converging lines to analysis
        mid_x = agent_x + agent_w / 2
        analysis_y = copy_y + copy_h + 2
        self.set_draw_color(150, 180, 150)
        for i in range(3):
            cx = copy_start + i * (copy_w + copy_gap) + copy_w/2
            self.line(cx, copy_y + copy_h, mid_x, analysis_y)
        
        # Analysis box
        self.set_font("Helvetica", "B", 4)
        self.set_text_color(60, 100, 60)
        self.set_xy(agent_x, analysis_y)
        self.cell(agent_w, 2.5, "Analysis/Summary", align="C")
        self.set_font("Helvetica", "I", 3.5)
        self.set_xy(agent_x, analysis_y + 2.5)
        self.cell(agent_w, 2, "(DS Guided)", align="C")
        
        self.set_y(box_y + agent_h + 2)
    
    def data_table(self, headers, rows):
        """Clean data table with proper spacing and hours column"""
        self.ln(1)
        
        # Calculate column widths - expanded for hours
        col_widths = [22, 22, 22, 108]  # Module, Hours, Cost, Functions
        row_height = 4.5
        
        # Headers - centered
        self.set_font("Helvetica", "B", 6.5)
        self.set_text_color(60, 60, 60)
        self.set_x(12)
        for i, header in enumerate(headers):
            self.cell(col_widths[i], row_height, header, border=0, align="C")
        self.ln(row_height)
        
        # Separator
        self.set_draw_color(200, 200, 200)
        self.set_line_width(0.2)
        self.line(12, self.get_y(), 186, self.get_y())
        self.ln(1.5)
        
        # Rows with proper spacing
        self.set_text_color(40, 40, 40)
        for row in rows:
            self.set_x(12)
            self.set_font("Helvetica", "B", 6.5)
            self.cell(col_widths[0], row_height, row[0], border=0)
            self.set_font("Helvetica", "", 6.5)
            self.cell(col_widths[1], row_height, row[1], border=0, align="R")
            self.cell(col_widths[2], row_height, row[2], border=0, align="R")
            self.cell(col_widths[3], row_height, row[3], border=0)
            self.ln(row_height)
        self.ln(1)

def create_executive_summary():
    pdf = ExecutiveSummaryPDF()
    pdf.add_page()
    
    # Section 1: Digital Work Footprint
    pdf.section_header("1", "Kiewit's Digital Work Footprint")
    
    pdf.paragraph(
        "Kiewit employs 14,946 salaried staff according to the November 2025 COR. Focusing on construction districts "
        "(8,831 staff after removing 6,115 non-construction), and applying 80% for project execution, yields 7,065 "
        "execution staff. Using the Cumberland project as a proxy, 26% of execution staff hold InEight user roles "
        "(Field Engineer, Project Engineer, Superintendent) - or 1,837 users."
    )
    
    pdf.paragraph(
        "For InEight users, we estimate 30% of work time (624 hours/year) is spent in the platform - a cursory "
        "estimate that warrants validation. At all-in rates of $63-111/hour (base wage + temporary office + other "
        "non-direct costs), InEight digital work costs approximately $95M annually. This is the floor, not the ceiling. "
        "Expanding to all execution staff digital work could exceed $200M."
    )
    
    # Flow diagram with clearer labels
    pdf.draw_flow_boxes([
        ("8,831", "Construction\nDistrict Staff"),
        ("7,065", "Project Execution\nStaff (80%)"),
        ("1,837", "InEight Users\n(26% of Execution)"),
        ("~$95M", "Floor for\nDigital Work")
    ], tall=True)
    
    pdf.set_font("Helvetica", "BI", 7)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(12)
    pdf.multi_cell(174, 3.5, "Conclusion: The ~$95M floor - with potential to exceed $200M - justifies significant AI investment. The question is not whether to invest, but where, how, and most importantly what do we do now?")
    pdf.ln(1)
    
    # Section 2: Module Breakdown
    pdf.section_header("2", "Where the Digital Work Occurs")
    
    pdf.data_table(
        ["Module", "Hours/yr", "Cost", "Primary Functions"],
        [
            ("Plan", "504K", "$39.3M", "Work plans, crew scheduling, resource allocation (31%)"),
            ("Inspect", "422K", "$29.0M", "Quality inspections, safety docs, daily reports (26%)"),
            ("Control", "222K", "$18.6M", "Budget monitoring, cost tracking, forecasting (14%)"),
            ("Contract", "176K", "$13.3M", "Contract admin, change orders, RFIs (11%)"),
            ("Design", "101K", "$7.7M", "Engineering documentation, quantities (6%)"),
        ]
    )
    
    pdf.paragraph(
        "Plan and Inspect dominate (57% combined) - these high-volume modules represent primary AI targets. The path "
        "forward: identify precise agent use cases within each module, find common patterns across use cases, then "
        "build the underlying storage, processing, and retrieval architecture to support them."
    )
    
    pdf.set_font("Helvetica", "BI", 7)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(12)
    pdf.multi_cell(174, 3.5, "Conclusion: Plan and Inspect offer highest ROI. Scope specific agents first, then build architecture to support common patterns - not the reverse. Recommend 2-week AI sprints with 2-3 data scientists to prototype and establish cost baselines; may need to hire 2-5 more to sustain sprint velocity.")
    pdf.ln(1)
    
    # Section 3: Architecture & Build Strategy (Combined)
    pdf.section_header("3", "Architecture Challenge & Build Strategy")
    
    # Draw dual-path architecture showing InEight vs Kiewit
    pdf.draw_dual_path_architecture()
    
    pdf.paragraph(
        "Not all AI is created equal. Simple retrieval - search and return data - can run on InEight's existing SQL Server. "
        "But retrieval is not intelligence. True AI agents require skills - discrete capabilities that reason, decide, and "
        "act. This requires computing power that scales on demand - a different architecture designed for AI workloads."
    )
    
    pdf.paragraph(
        "The opportunity is clear: InEight excels at data collection and should modernize its storage layer - "
        "prioritize investments that also speed up Kiewit's data platform. Kiewit owns the data and how we use it: decision "
        "agents and generative solutions. InEight should prioritize modern storage architecture that separates compute from "
        "storage - benefiting both platforms."
    )
    
    pdf.set_font("Helvetica", "BI", 7)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(12)
    pdf.multi_cell(174, 3.5, "Conclusion: InEight modernizes storage (data in); Kiewit builds intelligence (decisions out). Prioritize InEight investments that also speed up KIP. Use 2-3 week POCs to validate ROI before large-scale commitments.")
    pdf.ln(1)
    
    # Section 4: ROI & Sequencing (Combined)
    pdf.section_header("4", "ROI Framework & Sequencing")
    
    pdf.paragraph(
        "The goal is knowledge products that replace human work - not augmented search or RAG chatbots. Each agent must "
        "have clear, measurable ROI. Do not approve high-level AI funding; approve in stages with early ROI checkpoints. "
        "Learn from vendors like Dell who have deployed agents at scale; augment with 3rd party services or expand data "
        "science capacity after successful 2-3 week sprints prove value."
    )
    
    # Simple flow diagram
    pdf.draw_flow_boxes([
        ("Module", "InEight\nSource"),
        ("Use Cases", "Many per\nModule"),
        ("Patterns", "Common\nAcross Cases"),
        ("Build", "Architecture\nto Support")
    ], tall=True)
    
    pdf.set_font("Helvetica", "BI", 7)
    pdf.set_text_color(60, 60, 60)
    pdf.set_x(12)
    pdf.multi_cell(174, 3.5, "Conclusion: Approve staged investments with early ROI gates. Prioritize proof-of-technology over proof-of-concept - validate the entire technology stack can deliver production agents, not just one tool in the chain. A disciplined $10M engagement outperforms a scattered $30M one.")
    
    # Footer
    pdf.set_y(-10)
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.2)
    pdf.line(12, pdf.get_y(), 198, pdf.get_y())
    pdf.set_font("Helvetica", "I", 6)
    pdf.set_text_color(120, 120, 120)
    pdf.set_y(-8)
    pdf.cell(0, 4, "Source: Cumberland proxy analysis | InEight documentation | Kiewit November 2025 COR | Anthropic Agent Skills", align="C")
    
    # Save
    output_path = "/Users/matthewpappas/code/Latex/ineight_ai_investment/executive_summary.pdf"
    pdf.output(output_path)
    print(f"Executive summary created: {output_path}")
    return output_path

if __name__ == "__main__":
    create_executive_summary()
