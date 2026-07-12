"""
docs/generate_report_p2_p5.py
Generates TransitOps_Phases2to5_Report.pdf  (professional light-theme layout)
Run from project root: python docs/generate_report_p2_p5.py
"""
import sys, os, datetime
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether, ListFlowable, ListItem,
)
from reportlab.platypus.tableofcontents import TableOfContents

# ── Brand colours ──────────────────────────────────────────────────────────────
ORANGE   = colors.HexColor("#f59e0b")
ORANGE_D = colors.HexColor("#d97706")
BLUE     = colors.HexColor("#1e40af")
BLUE_L   = colors.HexColor("#3b82f6")
GREEN    = colors.HexColor("#065f46")
GREEN_L  = colors.HexColor("#10b981")
RED      = colors.HexColor("#991b1b")
RED_L    = colors.HexColor("#ef4444")
PURPLE   = colors.HexColor("#5b21b6")
PURPLE_L = colors.HexColor("#8b5cf6")
GRAY_D   = colors.HexColor("#1f2937")
GRAY_M   = colors.HexColor("#4b5563")
GRAY_L   = colors.HexColor("#9ca3af")
GRAY_BG  = colors.HexColor("#f3f4f6")
GRAY_BG2 = colors.HexColor("#e5e7eb")
WHITE    = colors.white
COVER_BG = colors.HexColor("#0f172a")
STRIPE   = colors.HexColor("#f9fafb")

# ── Paragraph styles ───────────────────────────────────────────────────────────
def ps(name, **kw):
    return ParagraphStyle(name, **kw)

COVER_TITLE = ps("CoverTitle",  fontSize=34, textColor=WHITE,        fontName="Helvetica-Bold", leading=40, alignment=TA_LEFT, spaceAfter=6)
COVER_SUB   = ps("CoverSub",   fontSize=14, textColor=ORANGE,        fontName="Helvetica-Bold", leading=18, alignment=TA_LEFT, spaceAfter=4)
COVER_META  = ps("CoverMeta",  fontSize=10, textColor=colors.HexColor("#94a3b8"), fontName="Helvetica", alignment=TA_LEFT)

H1 = ps("H1", fontSize=22, textColor=GRAY_D, fontName="Helvetica-Bold", spaceBefore=22, spaceAfter=4, leading=28)
H2 = ps("H2", fontSize=14, textColor=BLUE,   fontName="Helvetica-Bold", spaceBefore=16, spaceAfter=4, leading=18)
H3 = ps("H3", fontSize=11, textColor=GRAY_D, fontName="Helvetica-Bold", spaceBefore=10, spaceAfter=3, leading=14)

BODY  = ps("Body",  fontSize=9.5, textColor=GRAY_M, fontName="Helvetica", leading=15, spaceAfter=5, alignment=TA_JUSTIFY)
BODY2 = ps("Body2", fontSize=9.5, textColor=GRAY_D, fontName="Helvetica", leading=15, spaceAfter=4)
SMALL = ps("Small", fontSize=8,   textColor=GRAY_L, fontName="Helvetica-Oblique", leading=12, spaceAfter=6)
CODE  = ps("Code",  fontSize=8.5, textColor=colors.HexColor("#1e3a5f"), fontName="Courier",
           leading=12, spaceAfter=4, leftIndent=12, backColor=colors.HexColor("#eff6ff"),
           borderPad=6)

BULLET_S = ps("BulletS", fontSize=9.5, textColor=GRAY_M, fontName="Helvetica",
              leading=15, leftIndent=16, spaceAfter=3)
TOC_H1   = ps("TocH1", fontSize=11, textColor=GRAY_D, fontName="Helvetica-Bold", leading=18, spaceAfter=2)
TOC_H2   = ps("TocH2", fontSize=10, textColor=GRAY_M, fontName="Helvetica",      leading=16, leftIndent=12, spaceAfter=2)
FOOTER_S = ps("Footer", fontSize=8, textColor=GRAY_L, fontName="Helvetica", alignment=TA_CENTER)


# ── Helpers ────────────────────────────────────────────────────────────────────
def sp(n=8): return Spacer(1, n)

def hr(color=GRAY_BG2, thickness=1):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=6, spaceBefore=4)

def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BODY)
def p2(t): return Paragraph(t, BODY2)
def sm(t): return Paragraph(t, SMALL)
def code(t): return Paragraph(t, CODE)

def bullet_list(*items):
    return ListFlowable(
        [ListItem(Paragraph(i, BULLET_S), bulletColor=ORANGE, leftIndent=14) for i in items],
        bulletType="bullet", bulletFontSize=10, bulletColor=ORANGE,
        leftIndent=12, spaceAfter=6,
    )

def section_label(text, color=BLUE):
    """Coloured section number pill."""
    return Paragraph(
        f'<font color="#{color.hexval()[2:]}"><b>{text}</b></font>',
        ps(f"sl_{text}", fontSize=10, textColor=color, fontName="Helvetica-Bold",
           leading=14, spaceAfter=2)
    )


def callout(text, bg=colors.HexColor("#fffbeb"), border=ORANGE, icon="💡"):
    """Info callout box."""
    inner = Paragraph(f"{icon}&nbsp; {text}",
                      ps("callout_inner", fontSize=9, textColor=GRAY_D,
                         fontName="Helvetica", leading=14))
    t = Table([[inner]], colWidths=[16.2*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0,0), (-1,-1), bg),
        ("LEFTPADDING",  (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
        ("TOPPADDING",   (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0), (-1,-1), 8),
        ("LINEAFTER",    (0,0), (0,-1),  0, WHITE),
        ("LINEBEFORE",   (0,0), (0,-1),  4, border),
        ("BOX",          (0,0), (-1,-1), 0.5, colors.HexColor("#e5e7eb")),
    ]))
    return t


def data_table(rows, col_widths, header_bg=BLUE, zebra=True):
    """Professional striped table with blue header."""
    tbl = Table(rows, colWidths=col_widths, hAlign="LEFT", repeatRows=1)
    style = [
        # Header
        ("BACKGROUND",    (0,0), (-1,0),  header_bg),
        ("TEXTCOLOR",     (0,0), (-1,0),  WHITE),
        ("FONTNAME",      (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,0),  9),
        ("TOPPADDING",    (0,0), (-1,0),  8),
        ("BOTTOMPADDING", (0,0), (-1,0),  8),
        # Body
        ("FONTNAME",      (0,1), (-1,-1), "Helvetica"),
        ("FONTSIZE",      (0,1), (-1,-1), 8.5),
        ("TEXTCOLOR",     (0,1), (-1,-1), GRAY_D),
        ("TOPPADDING",    (0,1), (-1,-1), 6),
        ("BOTTOMPADDING", (0,1), (-1,-1), 6),
        # Grid
        ("LINEBELOW",     (0,0), (-1,-2), 0.4, GRAY_BG2),
        ("LINEBELOW",     (0,-1),(-1,-1), 0.8, GRAY_BG2),
        ("BOX",           (0,0), (-1,-1), 0.8, GRAY_BG2),
        ("LEFTPADDING",   (0,0), (-1,-1), 10),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
    ]
    if zebra:
        for i in range(1, len(rows)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0,i), (-1,i), STRIPE))
    tbl.setStyle(TableStyle(style))
    return tbl


def badge(text, fg, bg):
    return Paragraph(
        f'<font color="#{fg.hexval()[2:]}" size="8"><b> {text} </b></font>',
        ps(f"badge_{text}", fontSize=8, backColor=bg,
           fontName="Helvetica-Bold", textColor=fg, borderPad=3, leading=12)
    )


def phase_header(num, title, subtitle, color=BLUE):
    """Full-width coloured phase header strip."""
    inner = Table([[
        Paragraph(f"<b>Phase {num}</b>",
                  ps(f"ph_num_{num}", fontSize=11, textColor=WHITE,
                     fontName="Helvetica-Bold", leading=13)),
        Paragraph(f"<b>{title}</b><br/>"
                  f'<font size="9" color="#cbd5e1">{subtitle}</font>',
                  ps(f"ph_title_{num}", fontSize=14, textColor=WHITE,
                     fontName="Helvetica-Bold", leading=18)),
    ]], colWidths=[2.5*cm, 13.5*cm])
    inner.setStyle(TableStyle([
        ("VALIGN",        (0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",   (0,0),(-1,-1),0),
        ("RIGHTPADDING",  (0,0),(-1,-1),0),
        ("TOPPADDING",    (0,0),(-1,-1),0),
        ("BOTTOMPADDING", (0,0),(-1,-1),0),
    ]))
    outer = Table([[inner]], colWidths=[16.2*cm])
    outer.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("LEFTPADDING",   (0,0),(-1,-1), 16),
        ("RIGHTPADDING",  (0,0),(-1,-1), 16),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("BOX",           (0,0),(-1,-1), 0, WHITE),
    ]))
    return outer


def status_row(status, color, desc):
    clr = {"✅": GREEN_L, "⏳": ORANGE, "❌": RED_L}.get(status[:2], GRAY_L)
    return [
        Paragraph(f"<b>{status}</b>",
                  ps(f"sr_{status}", fontSize=9, textColor=clr, fontName="Helvetica-Bold")),
        Paragraph(desc, ps(f"srd_{status}", fontSize=9, textColor=GRAY_D, fontName="Helvetica")),
    ]


# ── Page template with header/footer ──────────────────────────────────────────
class ReportTemplate(SimpleDocTemplate):
    def __init__(self, path):
        super().__init__(
            path, pagesize=A4,
            topMargin=2.2*cm, bottomMargin=2*cm,
            leftMargin=2*cm,  rightMargin=2*cm,
        )
        self.page_number = 0

    def handle_pageBegin(self):
        super().handle_pageBegin()
        self.page_number += 1

    def afterPage(self):
        canvas = self.canv
        w, h   = A4
        # skip cover page header/footer
        if self.page_number == 1:
            return
        # Header bar
        canvas.setFillColor(COVER_BG)
        canvas.rect(0, h - 1.1*cm, w, 1.1*cm, fill=1, stroke=0)
        canvas.setFillColor(ORANGE)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(2*cm, h - 0.72*cm, "TransitOps")
        canvas.setFillColor(colors.HexColor("#64748b"))
        canvas.setFont("Helvetica", 8)
        canvas.drawRightString(w - 2*cm, h - 0.72*cm, "Post-Phase-1 Development Report  ·  2026")
        # Footer
        canvas.setFillColor(GRAY_BG)
        canvas.rect(0, 0, w, 1.2*cm, fill=1, stroke=0)
        canvas.setStrokeColor(GRAY_BG2)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.2*cm, w - 2*cm, 1.2*cm)
        canvas.setFillColor(GRAY_L)
        canvas.setFont("Helvetica", 8)
        canvas.drawCentredString(w/2, 0.45*cm, f"Page {self.page_number - 1}")
        canvas.drawString(2*cm, 0.45*cm, "TransitOps · Smart Transport Operations")
        canvas.drawRightString(w - 2*cm, 0.45*cm, "Confidential — Hackathon Documentation")


# ── Cover page ─────────────────────────────────────────────────────────────────
def cover_page():
    w, h = A4
    elems = []

    # Dark background panel (simulate via a tall table)
    cover_data = [[
        Paragraph(
            '<b>🚛 TransitOps</b>',
            ps("cover_brand", fontSize=38, textColor=ORANGE,
               fontName="Helvetica-Bold", leading=44)
        )
    ]]
    cover_tbl = Table(cover_data, colWidths=[16.2*cm])
    cover_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), COVER_BG),
        ("LEFTPADDING",   (0,0),(-1,-1), 24),
        ("RIGHTPADDING",  (0,0),(-1,-1), 24),
        ("TOPPADDING",    (0,0),(-1,-1), 48),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    elems.append(cover_tbl)

    content_rows = [
        [Paragraph("Smart Transport Operations Platform",
                   ps("cs1", fontSize=14, textColor=colors.HexColor("#94a3b8"),
                      fontName="Helvetica", leading=18))],
        [Spacer(1, 16)],
        [Paragraph('<b>Post-Phase-1 Development Report</b>',
                   ps("cs2", fontSize=22, textColor=WHITE,
                      fontName="Helvetica-Bold", leading=26))],
        [Spacer(1, 8)],
        [Paragraph("Phases 2 – 5  ·  RBAC Enforcement  ·  UI/UX Upgrades",
                   ps("cs3", fontSize=12, textColor=ORANGE,
                      fontName="Helvetica-Bold", leading=16))],
        [Spacer(1, 28)],
        [HRFlowable(width="60%", thickness=1, color=colors.HexColor("#334155"),
                    spaceAfter=20, spaceBefore=0)],
        [Table([
            [Paragraph("Prepared for", ps("cl1", fontSize=8, textColor=colors.HexColor("#64748b"),
                        fontName="Helvetica", leading=12)),
             Paragraph("Date", ps("cl2", fontSize=8, textColor=colors.HexColor("#64748b"),
                        fontName="Helvetica", leading=12)),
             Paragraph("Version", ps("cl3", fontSize=8, textColor=colors.HexColor("#64748b"),
                        fontName="Helvetica", leading=12))],
            [Paragraph("Odoo Virtual Hackathon",
                        ps("cv1", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold", leading=13)),
             Paragraph("July 2026",
                        ps("cv2", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold", leading=13)),
             Paragraph("1.0",
                        ps("cv3", fontSize=9, textColor=WHITE, fontName="Helvetica-Bold", leading=13))],
        ], colWidths=[6*cm, 5*cm, 5*cm],
           style=TableStyle([
               ("TEXTCOLOR",     (0,0),(-1,-1), WHITE),
               ("TOPPADDING",    (0,0),(-1,-1), 4),
               ("BOTTOMPADDING", (0,0),(-1,-1), 4),
               ("LEFTPADDING",   (0,0),(-1,-1), 0),
               ("LINEBELOW",     (0,0),(-1,0),  0.5, colors.HexColor("#334155")),
           ]))],
        [Spacer(1, 32)],
    ]

    content_tbl = Table(content_rows, colWidths=[16.2*cm])
    content_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), COVER_BG),
        ("LEFTPADDING",   (0,0),(-1,-1), 24),
        ("RIGHTPADDING",  (0,0),(-1,-1), 24),
        ("TOPPADDING",    (0,0),(-1,-1), 0),
        ("BOTTOMPADDING", (0,0),(-1,-1), 0),
    ]))
    elems.append(content_tbl)

    # Orange accent strip
    strip = Table([[Paragraph(
        "Phases 2 · 3 · 4 · 5  completed  ·  Full RBAC  ·  Plotly Analytics  ·  PDF Report",
        ps("strip_txt", fontSize=9, textColor=COVER_BG, fontName="Helvetica-Bold", leading=12))
    ]], colWidths=[16.2*cm])
    strip.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), ORANGE),
        ("LEFTPADDING",   (0,0),(-1,-1), 24),
        ("RIGHTPADDING",  (0,0),(-1,-1), 24),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
    ]))
    elems.append(strip)
    elems.append(PageBreak())
    return elems


# ── Executive Summary ──────────────────────────────────────────────────────────
def executive_summary():
    elems = [h1("Executive Summary"), hr(ORANGE, 2), sp(4)]
    elems.append(p(
        "TransitOps is a <b>Smart Transport Operations Platform</b> built for the Odoo Virtual "
        "Hackathon. It provides a complete fleet management solution covering vehicle tracking, "
        "driver management, trip dispatch, maintenance workflows, fuel/expense logging, and "
        "analytics — all secured behind a two-layer Role-Based Access Control (RBAC) system."
    ))
    elems.append(sp(6))

    # Status summary table
    status_rows = [
        ["Phase", "Scope", "Status"],
        ["Phase 1", "Auth · DB Models · Seed · Dashboard · Dark Theme · Router", "✅ Complete"],
        ["Phase 2", "Vehicle Registry CRUD · Driver Management CRUD · Business Rules", "✅ Complete"],
        ["Phase 3", "Trip Dispatch Engine · Lifecycle · Validation", "✅ Complete"],
        ["Phase 4", "Maintenance Workflow · Fuel & Expense Logging", "✅ Complete"],
        ["Phase 5", "Analytics (5 charts) · CSV Export · Settings · User Mgmt", "✅ Complete"],
        ["RBAC",    "Two-layer permission system: Sidebar + Per-button enforcement", "✅ Complete"],
        ["UI/UX",   "Selection cards · CSS polish · Dashboard overhaul", "✅ Complete"],
    ]
    rows_fmt = [[Paragraph(c, ps(f"es_{r}_{ci}", fontSize=9,
                                  textColor=WHITE if r==0 else (GREEN_L if "✅" in c else GRAY_D),
                                  fontName="Helvetica-Bold" if (r==0 or "✅" in c) else "Helvetica",
                                  leading=14))
                  for ci, c in enumerate(row)]
                 for r, row in enumerate(status_rows)]
    elems.append(data_table(rows_fmt, [2.8*cm, 10.4*cm, 3*cm]))
    elems.append(sp(10))

    # Key numbers
    elems.append(h2("Key Numbers at a Glance"))
    num_data = [
        ["8", "Streamlit Pages"],
        ["8", "SQLAlchemy Models"],
        ["5", "Service Modules"],
        ["5", "Pydantic Schema Files"],
        ["4", "User Roles"],
        ["44", "Granular RBAC Actions"],
        ["5", "Plotly Charts"],
        ["8", "Bugs Fixed"],
    ]
    cells = []
    row = []
    for i, (num, label) in enumerate(num_data):
        cell = Table([[
            Paragraph(f"<b>{num}</b>", ps(f"kn_{i}", fontSize=28, textColor=BLUE,
                                           fontName="Helvetica-Bold", leading=32, alignment=TA_CENTER)),
            Paragraph(label, ps(f"kl_{i}", fontSize=9, textColor=GRAY_M,
                                fontName="Helvetica", leading=13, alignment=TA_CENTER)),
        ]], colWidths=[4*cm])
        cell.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), GRAY_BG),
            ("TOPPADDING",    (0,0),(-1,-1), 10),
            ("BOTTOMPADDING", (0,0),(-1,-1), 10),
            ("BOX",           (0,0),(-1,-1), 0.5, GRAY_BG2),
        ]))
        row.append(cell)
        if len(row) == 4:
            cells.append(row)
            row = []
    if row:
        cells.append(row + [Spacer(4*cm, 1)] * (4 - len(row)))

    grid = Table(cells, colWidths=[4*cm, 4*cm, 4*cm, 4*cm], hAlign="LEFT",
                 spaceBefore=8, spaceAfter=8)
    grid.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),2),
                               ("RIGHTPADDING",(0,0),(-1,-1),2),
                               ("TOPPADDING",(0,0),(-1,-1),2),
                               ("BOTTOMPADDING",(0,0),(-1,-1),2)]))
    elems.append(grid)
    elems.append(PageBreak())
    return elems


# ── Phase sections ─────────────────────────────────────────────────────────────
def phase2():
    elems = [phase_header(2, "Vehicle & Driver Management",
                           "Full CRUD · schemas · services · RBAC · business rules"), sp(12)]

    elems.append(p(
        "Phase 2 delivers complete Create-Read-Update-Delete operations for the two core "
        "fleet entities — <b>Vehicles</b> and <b>Drivers</b> — following a strict three-layer "
        "architecture: <i>Pydantic schema → Service → Streamlit page</i>."
    ))
    elems.append(sp(8))

    elems.append(h2("2.1  New Files"))
    rows = [
        ["File", "Layer", "Purpose"],
        ["app/schemas/vehicle_schema.py", "Schema",   "VehicleCreate, VehicleUpdate — field validation, type coercion"],
        ["app/schemas/driver_schema.py",  "Schema",   "DriverCreate, DriverUpdate — license, score, expiry validation"],
        ["app/services/vehicle_service.py","Service", "get_all, get_by_id, create, update, delete, fleet_summary"],
        ["app/services/driver_service.py", "Service", "get_all, get_by_id, create, update, delete, driver_summary"],
        ["frontend/pages/page_fleet.py",   "UI",      "5-KPI bar, type/status filters, add form, edit form, status change, soft delete"],
        ["frontend/pages/page_drivers.py", "UI",      "6-KPI bar, license expiry alerts, add/edit forms, status change, soft delete"],
    ]
    fmt = [[Paragraph(c, ps(f"p2f_{r}_{ci}",
                             fontSize=9 if r>0 else 9,
                             textColor=WHITE if r==0 else (BLUE if ci==0 else GRAY_D),
                             fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica",
                             leading=13))
             for ci, c in enumerate(row)] for r, row in enumerate(rows)]
    elems.append(data_table(fmt, [5.8*cm, 2.4*cm, 8*cm]))
    elems.append(sp(8))

    elems.append(h2("2.2  Business Rules"))
    elems.append(bullet_list(
        "Registration number must be unique — service raises <b>ValueError</b> on duplicate.",
        "Safety score < 70 → driver is <b>auto-suspended</b> on create or update.",
        "Vehicles with trip history are <b>Retired</b> (not hard-deleted); drivers set to <b>Off Duty</b>.",
        "Driver license expiry < today → flagged <b>EXPIRED</b> with a red banner across the page.",
        "License expiry ≤ 30 days → <b>EXPIRING SOON</b> amber warning banner.",
        "Cannot manually set a vehicle to Available while a Dispatched trip uses it.",
    ))
    elems.append(sp(4))

    elems.append(h2("2.3  UI Features"))
    rows2 = [
        ["Feature", "Details"],
        ["5-KPI header (Fleet)",    "Total · Available · On Trip · In Maintenance · Retired"],
        ["6-KPI header (Drivers)",  "Total · Available · On Trip · Suspended · Expired Licence · Expiring ≤30d"],
        ["Filter bar — Fleet",      "Type dropdown + Status dropdown"],
        ["Filter bar — Drivers",    "Status + Licence Category + Name search (text input)"],
        ["Colour-coded table",      "Status column styled green / amber / red / gray via Pandas Styler"],
        ["Dynamic tabs",            "Add tab appears only when role has can(\"fleet.add\") permission"],
        ["Selection card",          "Orange left-border card with model, type, capacity, odometer, cost, status badge"],
        ["Actions row",             "Edit + Delete buttons; Status change in its own 3:1 row below card"],
    ]
    fmt2 = [[Paragraph(c, ps(f"p2f2_{r}_{ci}",
                              fontSize=9, textColor=WHITE if r==0 else GRAY_D,
                              fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica",
                              leading=13))
              for ci, c in enumerate(row)] for r, row in enumerate(rows2)]
    elems.append(data_table(fmt2, [5*cm, 11.2*cm]))
    elems.append(PageBreak())
    return elems


def phase3():
    elems = [phase_header(3, "Trip Dispatch Engine",
                           "Full lifecycle · business rule validation · status automation",
                           color=colors.HexColor("#1d4ed8")), sp(12)]

    elems.append(p(
        "Phase 3 implements the core operational workflow: create a trip, validate all "
        "business constraints, <b>dispatch</b> it (locking vehicle + driver), "
        "<b>complete</b> it (releasing resources + recording fuel/odometer), "
        "or <b>cancel</b> it at any actionable stage."
    ))
    elems.append(sp(8))

    elems.append(h2("3.1  Trip Lifecycle"))
    lifecycle = [
        ["Status", "Trigger", "Vehicle Status", "Driver Status"],
        ["Draft",      "Trip created",   "Available (unchanged)", "Available (unchanged)"],
        ["Dispatched", "Dispatch action","On Trip",               "On Trip"],
        ["Completed",  "Complete action","Available",             "Available"],
        ["Cancelled",  "Cancel action",  "Available *",           "Available *"],
    ]
    status_colors = [GRAY_D, BLUE_L, GREEN_L, RED_L]
    fmt = []
    for r, row in enumerate(lifecycle):
        frow = []
        for ci, c in enumerate(row):
            sc = status_colors[r-1] if (r > 0 and ci == 0) else (WHITE if r==0 else GRAY_D)
            fw = "Helvetica-Bold" if (r==0 or ci==0) else "Helvetica"
            frow.append(Paragraph(c, ps(f"p3lc_{r}_{ci}", fontSize=9,
                                         textColor=WHITE if r==0 else sc if ci==0 else GRAY_D,
                                         fontName=fw, leading=13)))
        fmt.append(frow)
    elems.append(data_table(fmt, [3.2*cm, 3.5*cm, 4.5*cm, 5*cm]))
    elems.append(sm("* Released only if the trip was Dispatched at time of cancellation."))
    elems.append(sp(8))

    elems.append(h2("3.2  Dispatch Validation Rules"))
    elems.append(bullet_list(
        "Vehicle status must be <b>Available</b> at dispatch time.",
        "Driver status must be <b>Available</b> at dispatch time.",
        "Driver licence must <b>not</b> be expired — hard block (shown as red error, not a warning).",
        "<b>cargo_weight_kg</b> must be ≤ <b>vehicle.max_capacity_kg</b>.",
        "<b>planned_distance_km</b> must be > 0; revenue and cargo weight must be ≥ 0.",
        "Trip code is auto-generated: <b>TRP-DDMMYY-XXXXXX</b> (date + 6-char UUID fragment).",
        "Soft capacity check also runs at <i>trip creation</i> (Draft) to catch obvious errors early.",
    ))
    elems.append(sp(6))

    elems.append(h2("3.3  New Files"))
    rows3 = [
        ["File", "Purpose"],
        ["app/schemas/trip_schema.py",   "TripCreate · TripUpdate · TripComplete with Pydantic v2 validators"],
        ["app/services/trip_service.py", "create · dispatch · complete · cancel · get_available_vehicles/drivers"],
        ["frontend/pages/page_trips.py", "6-KPI header · All Trips tab · Create Trip tab · Actions panel"],
    ]
    fmt3 = [[Paragraph(c, ps(f"p3f_{r}_{ci}", fontSize=9,
                               textColor=WHITE if r==0 else (BLUE if ci==0 else GRAY_D),
                               fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica", leading=13))
              for ci, c in enumerate(row)] for r, row in enumerate(rows3)]
    elems.append(data_table(fmt3, [6.5*cm, 9.7*cm]))
    elems.append(sp(8))

    elems.append(callout(
        "The Dispatcher role has full trip workflow access (create, dispatch, complete, cancel). "
        "Fleet Manager also has full access. Safety Officer and Financial Analyst are view-only.",
        icon="ℹ️"
    ))
    elems.append(PageBreak())
    return elems


def phase4():
    elems = [phase_header(4, "Maintenance & Fuel / Expense Logging",
                           "Auto vehicle status transitions · cost tracking",
                           color=colors.HexColor("#7c3aed")), sp(12)]

    elems.append(h2("4.1  Maintenance Workflow"))
    elems.append(p(
        "Maintenance records act as <b>automatic state machines</b> for vehicle availability. "
        "Logging puts a vehicle In Shop; closing releases it back to Available — no manual status "
        "change needed by the user."
    ))
    elems.append(sp(4))
    elems.append(bullet_list(
        "Vehicle must <b>not</b> be On Trip before logging (cannot repair a moving vehicle).",
        "Vehicle must <b>not</b> already be In Shop — must close existing record first.",
        "Logging maintenance → vehicle status: <b>Available → In Shop</b> (automatic).",
        "Closing maintenance → vehicle status: <b>In Shop → Available</b> (automatic).",
        "Only one <b>Active</b> maintenance record allowed per vehicle at a time.",
        "Closing allows an optional <b>actual_cost</b> override (defaults to estimated cost).",
    ))
    elems.append(sp(8))

    elems.append(h2("4.2  Fuel & Expense Entities"))
    rows4 = [
        ["Entity",    "Key Fields",                                       "Validation"],
        ["FuelLog",   "vehicle · liters · cost · date · trip (optional)", "liters > 0; cost > 0; trip must belong to same vehicle"],
        ["Expense",   "vehicle · category · amount · date",               "category must be in defined list (7 categories)"],
    ]
    fmt4 = [[Paragraph(c, ps(f"p4f_{r}_{ci}", fontSize=9,
                               textColor=WHITE if r==0 else GRAY_D,
                               fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica", leading=13))
              for ci, c in enumerate(row)] for r, row in enumerate(rows4)]
    elems.append(data_table(fmt4, [2.8*cm, 6.2*cm, 7.2*cm]))
    elems.append(sp(4))
    elems.append(p2("<b>Expense Categories:</b> Toll · Insurance · Fine · Parking · "
                    "Loading/Unloading · Driver Allowance · Misc"))
    elems.append(sp(8))

    elems.append(h2("4.3  New Files"))
    rows4b = [
        ["File", "Purpose"],
        ["app/schemas/maintenance_schema.py", "MaintenanceCreate · MaintenanceClose"],
        ["app/schemas/fuel_schema.py",         "FuelCreate · ExpenseCreate · EXPENSE_CATEGORIES list"],
        ["app/services/maintenance_service.py","log · close · summary · vehicle selector helpers"],
        ["app/services/fuel_service.py",       "add_fuel_log · add_expense · cost_summary · get_all"],
        ["frontend/pages/page_maintenance.py", "4-KPI header · Log tab · All Records · Close panel (FM only)"],
        ["frontend/pages/page_fuel_expenses.py","Dynamic 4-tab: Log Fuel · Log Expense · Fuel Records · Expense Records"],
    ]
    fmt4b = [[Paragraph(c, ps(f"p4bf_{r}_{ci}", fontSize=9,
                                textColor=WHITE if r==0 else (BLUE if ci==0 else GRAY_D),
                                fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica", leading=13))
               for ci, c in enumerate(row)] for r, row in enumerate(rows4b)]
    elems.append(data_table(fmt4b, [6.5*cm, 9.7*cm]))
    elems.append(PageBreak())
    return elems


def phase5():
    elems = [phase_header(5, "Analytics & Settings",
                           "5 Plotly charts · CSV export · user management · danger zone",
                           color=colors.HexColor("#065f46")), sp(12)]

    elems.append(h2("5.1  Analytics Charts"))
    charts = [
        ["Chart", "Type", "Metric", "Colour Logic"],
        ["Revenue by Vehicle",          "Bar",   "Trip.revenue (Completed only)",             "Green bars"],
        ["Completed Trips by Month",    "Bar",   "Trip.created_at grouped monthly",            "Blue bars"],
        ["Fuel Efficiency per Vehicle", "Bar",   "planned_distance_km / fuel_consumed_l",     "Green ≥10 · Amber ≥7 · Red <7 km/L"],
        ["Cost Breakdown",              "Donut", "Fuel cost + Expense amount + Maint. cost",   "3-segment donut"],
        ["Total Trips per Vehicle",     "Bar",   "All trips (any status) by vehicle",          "Purple bars"],
    ]
    fmt5 = [[Paragraph(c, ps(f"p5f_{r}_{ci}", fontSize=9,
                               textColor=WHITE if r==0 else GRAY_D,
                               fontName="Helvetica-Bold" if r==0 else "Helvetica", leading=13))
              for ci, c in enumerate(row)] for r, row in enumerate(charts)]
    elems.append(data_table(fmt5, [4.5*cm, 2*cm, 5*cm, 4.7*cm]))
    elems.append(sp(4))
    elems.append(callout(
        "All charts use the app's dark theme palette via Plotly's paper_bgcolor='rgba(0,0,0,0)'. "
        "CSV export (Trips · Fuel Logs · Expenses) is visible only to Fleet Manager and Financial Analyst roles.",
        icon="📊"
    ))
    elems.append(sp(8))

    elems.append(h2("5.2  Settings Page Tabs"))
    rows5b = [
        ["Tab", "Access", "Content"],
        ["System Info",     "All roles",       "App name · DB type · framework version · ORM · debug mode"],
        ["User Management", "Fleet Manager",   "Role-coloured user table + role-change form"],
        ["RBAC Matrix",     "Fleet Manager",   "Read-only colour-coded view of all 4 roles × 8 modules"],
        ["Danger Zone",     "Fleet Manager",   "Reset Database button — deletes + reseeds data (dev tool)"],
    ]
    fmt5b = [[Paragraph(c, ps(f"p5bf_{r}_{ci}", fontSize=9,
                                textColor=WHITE if r==0 else GRAY_D,
                                fontName="Helvetica-Bold" if r==0 else "Helvetica", leading=13))
               for ci, c in enumerate(row)] for r, row in enumerate(rows5b)]
    elems.append(data_table(fmt5b, [3.5*cm, 3.5*cm, 9.2*cm]))
    elems.append(PageBreak())
    return elems


def rbac_section():
    elems = [h1("RBAC — Two-Layer Permission System"), hr(ORANGE, 2), sp(8)]

    elems.append(p(
        "Access control is enforced at <b>two independent layers</b>, ensuring that no action "
        "can be performed by an unauthorised role — even if they navigate directly to a URL."
    ))
    elems.append(sp(8))

    # Layer diagram
    layers = [
        ["Layer 1 — Coarse (Sidebar)",
         "PERMISSIONS dict in rbac.py\n"
         "Maps: role → module → 'none' / 'view' / 'edit'\n"
         "Effect: Sidebar only shows modules where access ≠ 'none'.\n"
         "Settings is completely hidden from Dispatcher, Safety Officer, Financial Analyst."],
        ["Layer 2 — Granular (In-page)",
         "ROLE_ACTIONS dict in rbac.py\n"
         "Maps: role → action → True / False\n"
         "44 named actions: fleet.add, trips.dispatch, fuel.add, analytics.export …\n"
         "Pages call can(action) from auth_guard.py to show/hide individual buttons and form tabs."],
    ]
    lrows = []
    for title, body in layers:
        lines = body.split("\n")
        content = [Paragraph(f"<b>{title}</b>",
                              ps(f"lt_{title}", fontSize=10, textColor=BLUE,
                                 fontName="Helvetica-Bold", leading=14, spaceAfter=4))]
        for line in lines:
            content.append(Paragraph(f"• {line}",
                                      ps(f"lb_{title}_{line[:10]}", fontSize=9, textColor=GRAY_M,
                                         fontName="Helvetica", leading=14, leftIndent=8)))
        lrows.append([content])

    for lrow in lrows:
        tbl = Table(lrow, colWidths=[16.2*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),(-1,-1), GRAY_BG),
            ("LEFTPADDING",   (0,0),(-1,-1), 16),
            ("RIGHTPADDING",  (0,0),(-1,-1), 16),
            ("TOPPADDING",    (0,0),(-1,-1), 14),
            ("BOTTOMPADDING", (0,0),(-1,-1), 14),
            ("LINEBEFORE",    (0,0),(0,-1),  4, BLUE),
            ("BOX",           (0,0),(-1,-1), 0.5, GRAY_BG2),
        ]))
        elems.append(tbl)
        elems.append(sp(6))

    elems.append(sp(4))
    elems.append(h2("Permission Matrix"))

    headers = ["Module", "Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"]
    matrix  = [
        ["Dashboard",       "👁  View",        "👁  View",        "👁  View",                    "👁  View"],
        ["Fleet",           "✏️  Full CRUD",    "👁  View only",   "👁  View only",                "👁  View only"],
        ["Drivers",         "✏️  Full CRUD",    "👁  View only",   "✏️  Add / Edit / Status",     "👁  View only"],
        ["Trips",           "✏️  Full workflow","✏️  Full workflow","👁  View only",               "👁  View only"],
        ["Maintenance",     "✏️  Full CRUD",    "👁  View only",   "👁  View only",                "👁  View only"],
        ["Fuel & Expenses", "✏️  Full CRUD",    "👁  View only",   "👁  View only",                "✏️  Add / View"],
        ["Analytics",       "👁  + CSV Export", "👁  Charts only", "👁  Charts only",             "👁  + CSV Export"],
        ["Settings",        "✏️  Full access",  "❌  Hidden",       "❌  Hidden",                   "❌  Hidden"],
    ]
    fmt = []
    for r, row in enumerate([headers] + matrix):
        frow = []
        for ci, c in enumerate(row):
            if r == 0:
                s = ps(f"rm_h_{ci}", fontSize=9, textColor=WHITE,
                        fontName="Helvetica-Bold", leading=13)
            elif "✏️" in c:
                s = ps(f"rm_{r}_{ci}", fontSize=9, textColor=BLUE,
                        fontName="Helvetica-Bold", leading=13)
            elif "❌" in c:
                s = ps(f"rm_{r}_{ci}", fontSize=9, textColor=RED_L,
                        fontName="Helvetica-Bold", leading=13)
            elif ci == 0:
                s = ps(f"rm_{r}_{ci}", fontSize=9, textColor=GRAY_D,
                        fontName="Helvetica-Bold", leading=13)
            else:
                s = ps(f"rm_{r}_{ci}", fontSize=9, textColor=GRAY_M,
                        fontName="Helvetica", leading=13)
            frow.append(Paragraph(c, s))
        fmt.append(frow)
    elems.append(data_table(fmt, [3.2*cm, 3.2*cm, 3.2*cm, 3.3*cm, 3.3*cm]))
    elems.append(sp(8))

    elems.append(h2("Code Pattern — Using can()"))
    for line in [
        "from frontend.components.auth_guard import can",
        "",
        "# Show 'Add Vehicle' tab only if role permits",
        "if can('fleet.add'):",
        "    tabs.append('➕ Add Vehicle')",
        "",
        "# Show Dispatch button only for valid status + permission",
        "if can('trips.dispatch') and trip['status'] == 'Draft':",
        "    show_dispatch_button()",
    ]:
        elems.append(code(line if line else "&nbsp;"))
    elems.append(PageBreak())
    return elems


def uiux_section():
    elems = [h1("UI / UX Upgrades"), hr(ORANGE, 2), sp(8)]

    elems.append(h2("Dashboard Overhaul"))
    elems.append(bullet_list(
        "<b>Removed dead filter row</b> — Type / Status / Region dropdowns had no effect and "
        "were confusing. Removed entirely.",
        "<b>Recent Trips — now live</b> — Added Vehicle and Driver columns; queries the live DB "
        "on every render. Previously showed only Trip Code, Route, Distance, Status.",
        "<b>Flat bar → Donut chart</b> — Fleet Status is now a donut with the total vehicle count "
        "as the centre label, plus a mini 3-stat row (Available · On Trip · In Shop) below.",
        "<b>8th KPI tile</b> — Total Revenue (Rs.) from completed trips added to the KPI bar.",
    ))
    elems.append(sp(8))

    elems.append(h2("Selection Card — Actions Panel Redesign"))
    elems.append(p(
        "All three management pages (Fleet, Drivers, Trips) previously had a cramped three-column "
        "layout where the status dropdown was squeezed between the Edit and Delete buttons. "
        "This has been replaced with a <b>styled Selection Card</b> system."
    ))
    elems.append(sp(4))

    before_after = [
        ["Before", "After"],
        ["Dropdown → [Edit] [Status dropdown + Apply] [Delete]\n"
         "Status change forced into the middle column\n"
         "No item details visible\n"
         "4 fixed columns regardless of role",
         "Dropdown → Orange left-border card (shows all key fields)\n"
         "Then: [Edit] [Delete] buttons (dynamic count)\n"
         "Then: — Change Status — wide 3:1 row\n"
         "Only buttons valid for current status + role appear"],
    ]
    fmt_ba = []
    for r, row in enumerate(before_after):
        frow = []
        for ci, c in enumerate(row):
            lines = c.split("\n")
            paras = [Paragraph(lines[0],
                               ps(f"ba_h_{r}_{ci}", fontSize=9,
                                   textColor=WHITE if r==0 else (RED_L if ci==0 else GREEN_L),
                                   fontName="Helvetica-Bold", leading=13))]
            for ln in lines[1:]:
                paras.append(Paragraph(f"• {ln}",
                                        ps(f"ba_b_{r}_{ci}_{ln[:8]}", fontSize=8.5,
                                            textColor=GRAY_M, fontName="Helvetica", leading=13,
                                            leftIndent=8)))
            frow.append(paras)
        fmt_ba.append(frow)

    ba_tbl = Table(fmt_ba, colWidths=[8*cm, 8.2*cm], hAlign="LEFT")
    ba_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  BLUE),
        ("BACKGROUND",    (0,1),(0,1),   colors.HexColor("#fef2f2")),
        ("BACKGROUND",    (1,1),(1,1),   colors.HexColor("#f0fdf4")),
        ("LINEBEFORE",    (0,1),(0,1),   3, RED_L),
        ("LINEBEFORE",    (1,1),(1,1),   3, GREEN_L),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("BOX",           (0,0),(-1,-1), 0.5, GRAY_BG2),
        ("LINEAFTER",     (0,0),(0,-1),  0.5, GRAY_BG2),
    ]))
    elems.append(ba_tbl)
    elems.append(sp(8))

    elems.append(h2("CSS Enhancements (style.css)"))
    css_rows = [
        ["Element", "Enhancement"],
        ["Primary Button",    "Gradient fill (orange→dark orange) · glow box-shadow · translateY(-1px) hover lift"],
        ["Secondary Button",  "Border colour transitions to orange on hover"],
        ["Form Inputs",       "Border highlights orange on focus with soft 2px glow ring"],
        ["Dataframe Tables",  "border-radius: 10px on all st.dataframe() outputs"],
        ["Scrollbar",         "Custom 6px dark scrollbar matching dark theme palette"],
        [".selection-card",   "New CSS class — orange left-border · flex-wrap meta tags · hover effect"],
        [".sc-badge-*",       "6 colour variants (green / yellow / red / gray / blue / purple)"],
    ]
    fmt_css = [[Paragraph(c, ps(f"css_{r}_{ci}", fontSize=9,
                                  textColor=WHITE if r==0 else (BLUE if ci==0 else GRAY_D),
                                  fontName="Helvetica-Bold" if (r==0 or ci==0) else "Helvetica", leading=13))
                 for ci, c in enumerate(row)] for r, row in enumerate(css_rows)]
    elems.append(data_table(fmt_css, [4.5*cm, 11.7*cm]))
    elems.append(PageBreak())
    return elems


def errors_section():
    elems = [h1("Errors Encountered & Resolutions"), hr(ORANGE, 2), sp(8)]
    elems.append(p(
        "This section documents every notable error or bug encountered during development, "
        "along with its root cause and the resolution applied."
    ))
    elems.append(sp(8))

    errors = [
        (
            "StreamlitAPIException — st.switch_page() page not found",
            "st.switch_page() requires files inside a root-level pages/ folder. "
            "Our architecture places pages in frontend/pages/ (per SDD) which Streamlit's "
            "native router doesn't support.",
            "Replaced st.switch_page() with a custom PAGE_MAP router in frontend/router.py. "
            "Single app.py entry point; navigation is driven by session_state['current_page'].",
            "High"
        ),
        (
            "UnicodeEncodeError — cp1252 codec can't encode emoji",
            "Windows PowerShell terminal uses cp1252 encoding. Python's print() crashes on "
            "Unicode emoji used in log messages and test output.",
            "Added sys.stdout.reconfigure(encoding='utf-8', errors='replace') at the top of "
            "all CLI scripts (smoke tests, seed, PDF generator).",
            "Low"
        ),
        (
            "SQLite OperationalError — database is locked",
            "Smoke tests attempted reset_database() (deletes .db file) while Streamlit held "
            "an open SQLAlchemy connection to the same file.",
            "Always stop Streamlit before running tests. reset_database() now prints a clear "
            "error message. Documented in developer workflow guide.",
            "Medium"
        ),
        (
            "SyntaxError — walrus operator := in assert statement",
            "Smoke test used assert f.cost_per_l_calc := round(...) which is invalid Python syntax. "
            "The walrus operator cannot be used inside assert.",
            "Removed the malformed assertion. cost_per_l is computed inside the service layer "
            "and returned in the response dict — no assertion needed.",
            "Low"
        ),
        (
            "Pydantic ValidationError — model_post_init not called for None date",
            "MaintenanceCreate used date: datetime.date = None as a field default. "
            "Pydantic v2 does not call model_post_init for None defaults the same way v1 did.",
            "Changed to use model_post_init with object.__setattr__ for the default date "
            "assignment — consistent with the pattern in FuelCreate and ExpenseCreate.",
            "Medium"
        ),
        (
            "Protobuf — Descriptors cannot be created directly",
            "Importing any Streamlit page module outside the Streamlit runtime raises a protobuf "
            "version conflict. Happens when smoke tests try to import frontend.pages.*",
            "Backend-only smoke tests skip all frontend page imports. Pages are verified by "
            "running the full Streamlit app and manually exercising each role. Known limitation.",
            "Low"
        ),
        (
            "Dashboard — Recent Trips showing no Vehicle or Driver",
            "The DB query existed but the resulting dict only had Trip Code, Route, Distance, "
            "Status — no joins for vehicle or driver names. Filter dropdowns (Type / Status / "
            "Region) had no underlying logic and confused users.",
            "Added v_map and d_map lookups inside _get_dashboard_data(). Recent Trips now "
            "shows 6 columns. Removed the dead filter row entirely.",
            "Medium"
        ),
        (
            "KeyError: 'can_edit_v' — list comprehension scope bug",
            "The fleet actions panel used locals()[c] inside a list comprehension to check "
            "boolean flags. In Python 3, list comprehensions have their own scope, so "
            "locals() returns only the comprehension's variables, not the enclosing function's.",
            "Removed the broken list comprehension. The button count was already tracked by "
            "num_btns = sum([can_edit_v, can_delete_v]) — used that directly.",
            "High"
        ),
    ]

    severity_color = {"High": RED_L, "Medium": ORANGE, "Low": GREEN_L}

    for i, (title, cause, fix, severity) in enumerate(errors, 1):
        sc = severity_color.get(severity, GRAY_L)
        block = [
            Table([[
                Paragraph(f"#{i}",
                           ps(f"en_{i}", fontSize=11, textColor=WHITE,
                              fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
                Paragraph(f"<b>{title}</b>",
                           ps(f"et_{i}", fontSize=10, textColor=WHITE,
                              fontName="Helvetica-Bold", leading=14)),
                Paragraph(f"<b>{severity}</b>",
                           ps(f"es_{i}", fontSize=8, textColor=WHITE,
                              fontName="Helvetica-Bold", leading=12, alignment=TA_RIGHT)),
            ]], colWidths=[1*cm, 13.2*cm, 2*cm],
               style=TableStyle([
                   ("BACKGROUND",    (0,0),(-1,-1), sc),
                   ("LEFTPADDING",   (0,0),(-1,-1), 10),
                   ("RIGHTPADDING",  (0,0),(-1,-1), 10),
                   ("TOPPADDING",    (0,0),(-1,-1), 8),
                   ("BOTTOMPADDING", (0,0),(-1,-1), 8),
                   ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
               ])),
            Table([
                [Paragraph("<b>Root Cause</b>",
                            ps(f"ec_{i}", fontSize=8.5, textColor=RED_L,
                               fontName="Helvetica-Bold", leading=13)),
                 Paragraph(cause,
                            ps(f"ecb_{i}", fontSize=9, textColor=GRAY_D,
                               fontName="Helvetica", leading=14))],
                [Paragraph("<b>Resolution</b>",
                            ps(f"ef_{i}", fontSize=8.5, textColor=GREEN,
                               fontName="Helvetica-Bold", leading=13)),
                 Paragraph(fix,
                            ps(f"efb_{i}", fontSize=9, textColor=GRAY_D,
                               fontName="Helvetica", leading=14))],
            ], colWidths=[2.5*cm, 13.7*cm],
               style=TableStyle([
                   ("BACKGROUND",    (0,0),(-1,-1), GRAY_BG),
                   ("LEFTPADDING",   (0,0),(-1,-1), 10),
                   ("RIGHTPADDING",  (0,0),(-1,-1), 10),
                   ("TOPPADDING",    (0,0),(-1,-1), 8),
                   ("BOTTOMPADDING", (0,0),(-1,-1), 8),
                   ("LINEBELOW",     (0,0),(-1,0),  0.4, GRAY_BG2),
                   ("BOX",          (0,0),(-1,-1),  0.5, GRAY_BG2),
                   ("VALIGN",       (0,0),(-1,-1),  "TOP"),
               ])),
            sp(10),
        ]
        elems.extend([KeepTogether(block[:2]), block[2]])

    elems.append(PageBreak())
    return elems


def architecture_section():
    elems = [h1("Architecture Overview"), hr(ORANGE, 2), sp(8)]

    elems.append(h2("Design Principles"))
    elems.append(bullet_list(
        "<b>Zero-Streamlit backend</b> — app/ contains no streamlit imports. All business logic is "
        "pure Python. Only frontend/pages/ calls st.*",
        "<b>Custom router</b> — PAGE_MAP in router.py replaces Streamlit's native multipage system, "
        "enabling full RBAC control and our folder structure.",
        "<b>SQLite + SQLAlchemy ORM</b> — No server needed for hackathon. Typed Mapped[] fields, "
        "reset_database() for development iterations.",
        "<b>Pydantic v2 schemas</b> — All user input validated before reaching services. "
        "ValidationError messages shown via st.error(). Services only receive clean data.",
        "<b>bcrypt authentication</b> — Passwords hashed at seed time. Sessions via "
        "st.session_state with get_current_user() helper.",
    ))
    elems.append(sp(8))

    elems.append(h2("Request Flow"))
    flow_steps = [
        ("1", "User logs in", "app.py validates credentials via auth_service.login()"),
        ("2", "Sidebar renders", "sidebar.py filters SIDEBAR_ITEMS by has_access(role, module)"),
        ("3", "Page selected",  "session_state['current_page'] updated; router.py calls page.render()"),
        ("4", "Page loads",     "require_auth() verifies session; can(action) gates UI components"),
        ("5", "Form submitted", "Pydantic schema validates → service processes → DB updated"),
        ("6", "Page re-renders","Streamlit re-runs; all data fetched fresh from DB"),
    ]
    flow_rows = [[Paragraph(c, ps(f"flh_{ci}", fontSize=9, textColor=WHITE,
                                    fontName="Helvetica-Bold", leading=13))
                   for ci, c in enumerate(["Step", "Action", "Code Location"])]]
    for s, a, d in flow_steps:
        flow_rows.append([
            Paragraph(s, ps(f"fl_{s}", fontSize=9, textColor=BLUE,
                             fontName="Helvetica-Bold", leading=13, alignment=TA_CENTER)),
            Paragraph(a, ps(f"fa_{s}", fontSize=9, textColor=GRAY_D,
                             fontName="Helvetica-Bold", leading=13)),
            Paragraph(d, ps(f"fd_{s}", fontSize=9, textColor=GRAY_M,
                             fontName="Helvetica", leading=13)),
        ])
    elems.append(data_table(flow_rows, [1.2*cm, 5.5*cm, 9.5*cm]))

    elems.append(sp(8))

    elems.append(h2("Directory Structure"))
    struct_lines = [
        ("TransitOps/", ORANGE),
        ("├── app.py                         Entry point · login · sidebar · router", GRAY_D),
        ("├── .env                           DATABASE_URL · SECRET_KEY · APP_NAME · DEBUG", GRAY_M),
        ("├── .streamlit/config.toml         Dark theme · orange accent", GRAY_M),
        ("├── requirements.txt", GRAY_M),
        ("│", GRAY_L),
        ("├── app/                           Backend (zero Streamlit imports)", BLUE),
        ("│   ├── config.py                  Reads .env · typed settings constants", GRAY_D),
        ("│   ├── constants.py               Status enums: VehicleStatus, DriverStatus …", GRAY_D),
        ("│   ├── logger.py                  get_logger(__name__) rotating file handler", GRAY_D),
        ("│   ├── auth/", GRAY_D),
        ("│   │   ├── hashing.py             bcrypt hash_password / verify_password", GRAY_M),
        ("│   │   └── rbac.py                PERMISSIONS + ROLE_ACTIONS + role_can() + can_edit()", GRAY_M),
        ("│   ├── database/", GRAY_D),
        ("│   │   ├── engine.py              get_session · init_db · reset_database", GRAY_M),
        ("│   │   └── seed.py                4 roles · 4 users · 6 vehicles · 5 drivers · 5 trips", GRAY_M),
        ("│   ├── models/                    8 SQLAlchemy ORM models", GRAY_D),
        ("│   │   └── role · user · vehicle · driver · trip · maintenance · fuel_log · expense", GRAY_M),
        ("│   ├── schemas/                   Pydantic v2 validation schemas", GRAY_D),
        ("│   │   └── vehicle · driver · trip · maintenance · fuel", GRAY_M),
        ("│   └── services/                  Business logic — pure Python", GRAY_D),
        ("│       └── auth · vehicle · driver · trip · maintenance · fuel", GRAY_M),
        ("│", GRAY_L),
        ("├── frontend/", BLUE),
        ("│   ├── router.py                  PAGE_MAP + route_to_page() dispatcher", GRAY_D),
        ("│   ├── assets/style.css           Global dark theme CSS", GRAY_D),
        ("│   ├── components/", GRAY_D),
        ("│   │   ├── auth_guard.py          require_auth() · require_role() · can(action)", GRAY_M),
        ("│   │   ├── kpi_card.py            render_kpi_card(value, label, color)", GRAY_M),
        ("│   │   └── sidebar.py             Role-filtered navigation sidebar", GRAY_M),
        ("│   └── pages/                     Each file: render() only", GRAY_D),
        ("│       └── dashboard · fleet · drivers · trips · maintenance", GRAY_M),
        ("│              fuel_expenses · analytics · settings", GRAY_M),
        ("│", GRAY_L),
        ("├── docs/", GRAY_D),
        ("│   ├── TransitOps_Phase1_Report.pdf", GRAY_M),
        ("│   ├── TransitOps_Phases2to5_Report.pdf", GRAY_M),
        ("│   └── generate_report_p2_p5.py", GRAY_M),
        ("└── data/transitops.db             Auto-created SQLite database", GRAY_D),
    ]

    struct_tbl_data = []
    for line, color in struct_lines:
        struct_tbl_data.append([
            Paragraph(line, ps(f"st_{line[:10]}", fontSize=7.5, textColor=color,
                                fontName="Courier", leading=11))
        ])
    struct_tbl = Table(struct_tbl_data, colWidths=[16.2*cm], hAlign="LEFT")
    struct_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#f8fafc")),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 1),
        ("BOTTOMPADDING", (0,0),(-1,-1), 1),
        ("BOX",           (0,0),(-1,-1), 0.5, GRAY_BG2),
    ]))
    elems.append(struct_tbl)
    return elems


# ── Main builder ───────────────────────────────────────────────────────────────
def build():
    out = os.path.join(os.path.dirname(__file__), "TransitOps_Phases2to5_Report.pdf")
    doc = ReportTemplate(out)

    story = []
    story += cover_page()
    story += executive_summary()
    story += phase2()
    story += phase3()
    story += phase4()
    story += phase5()
    story += rbac_section()
    story += uiux_section()
    story += errors_section()
    story += architecture_section()

    # Final page footer
    story += [sp(16), hr(ORANGE, 1), sp(6),
              Paragraph("TransitOps — Odoo Virtual Hackathon 2026  ·  Post-Phase-1 Development Report  ·  All rights reserved",
                        FOOTER_S)]

    doc.build(story)
    print(f"[OK] Report saved: {out}")
    return out


if __name__ == "__main__":
    build()
