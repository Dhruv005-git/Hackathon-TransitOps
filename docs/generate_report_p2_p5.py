"""
docs/generate_report_p2_p5.py
Generates TransitOps_Phases2to5_Report.pdf using ReportLab.
Run: python docs/generate_report_p2_p5.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ── Colour palette ──────────────────────────────────────────
C_BG      = colors.HexColor("#0e1117")
C_CARD    = colors.HexColor("#21252e")
C_ORANGE  = colors.HexColor("#f59e0b")
C_GREEN   = colors.HexColor("#10b981")
C_RED     = colors.HexColor("#ef4444")
C_BLUE    = colors.HexColor("#3b82f6")
C_PURPLE  = colors.HexColor("#8b5cf6")
C_GRAY    = colors.HexColor("#9ca3af")
C_WHITE   = colors.HexColor("#e6e6e6")
C_DARK    = colors.HexColor("#1a1d24")
C_BORDER  = colors.HexColor("#2d3341")

# ── Styles ─────────────────────────────────────────────────
SS = getSampleStyleSheet()

def style(name, **kw):
    return ParagraphStyle(name, **kw)

H1 = style("H1", fontSize=22, textColor=C_WHITE,
           fontName="Helvetica-Bold", spaceAfter=6, spaceBefore=18)
H2 = style("H2", fontSize=15, textColor=C_ORANGE,
           fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=14,
           borderPad=4)
H3 = style("H3", fontSize=11, textColor=C_WHITE,
           fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=10)
BODY = style("BODY", fontSize=9, textColor=C_WHITE,
             fontName="Helvetica", leading=14, spaceAfter=4)
BODY_GRAY = style("BODY_GRAY", fontSize=9, textColor=C_GRAY,
                  fontName="Helvetica", leading=14, spaceAfter=4)
CAPTION = style("CAPTION", fontSize=8, textColor=C_GRAY,
                fontName="Helvetica-Oblique", leading=12, spaceAfter=6)
CODE = style("CODE", fontSize=8, textColor=C_GREEN,
             fontName="Courier", leading=12, spaceAfter=4,
             backColor=C_CARD, leftIndent=12, borderPad=6)
BULLET = style("BULLET", fontSize=9, textColor=C_WHITE,
               fontName="Helvetica", leading=14, leftIndent=14,
               bulletFontName="Helvetica", bulletFontSize=9,
               spaceAfter=3)
TAG_GREEN  = style("TG", fontSize=8, textColor=C_GREEN,  fontName="Helvetica-Bold")
TAG_RED    = style("TR", fontSize=8, textColor=C_RED,    fontName="Helvetica-Bold")
TAG_BLUE   = style("TB", fontSize=8, textColor=C_BLUE,   fontName="Helvetica-Bold")
TAG_ORANGE = style("TO", fontSize=8, textColor=C_ORANGE, fontName="Helvetica-Bold")

def HR():
    return HRFlowable(width="100%", thickness=0.5, color=C_BORDER, spaceAfter=6, spaceBefore=4)

def SP(h=6):
    return Spacer(1, h)

def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BODY)
def pg(t): return Paragraph(t, BODY_GRAY)
def cap(t):return Paragraph(t, CAPTION)
def bl(t): return Paragraph(f"• &nbsp; {t}", BULLET)
def code(t):return Paragraph(t, CODE)

def badge_table(items):
    """Render coloured badge row."""
    data = [[Paragraph(label, style(f"b{i}", fontSize=8,
                        textColor=c, fontName="Helvetica-Bold",
                        backColor=bc))
             for i, (label, c, bc) in enumerate(items)]]
    t = Table(data, hAlign="LEFT")
    t.setStyle(TableStyle([("TOPPADDING",(0,0),(-1,-1),4),
                            ("BOTTOMPADDING",(0,0),(-1,-1),4),
                            ("LEFTPADDING",(0,0),(-1,-1),6),
                            ("RIGHTPADDING",(0,0),(-1,-1),6)]))
    return t


def feature_table(rows, col_widths=None):
    """Dark-styled two-column table."""
    if col_widths is None:
        col_widths = [5*cm, 11.5*cm]
    tbl = Table(rows, colWidths=col_widths, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  C_CARD),
        ("TEXTCOLOR",      (0, 0), (-1, 0),  C_ORANGE),
        ("FONTNAME",       (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0, 0), (-1, 0),  9),
        ("BACKGROUND",     (0, 1), (-1, -1), C_DARK),
        ("TEXTCOLOR",      (0, 1), (-1, -1), C_WHITE),
        ("FONTNAME",       (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",       (0, 1), (-1, -1), 8.5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_DARK, C_CARD]),
        ("GRID",           (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 8),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def rbac_table():
    headers = ["Module", "Fleet Manager", "Dispatcher", "Safety Officer", "Financial Analyst"]
    rows = [
        ["Dashboard",       "👁 View",      "👁 View",            "👁 View",                   "👁 View"],
        ["Fleet",           "✏️ Full CRUD",  "👁 View only",       "👁 View only",               "👁 View only"],
        ["Drivers",         "✏️ Full CRUD",  "👁 View only",       "✏️ Add/Edit/Status (no del)","👁 View only"],
        ["Trips",           "✏️ Full workflow","✏️ Full workflow",  "👁 View only",               "👁 View only"],
        ["Maintenance",     "✏️ Full CRUD",  "👁 View only",       "👁 View only",               "👁 View only"],
        ["Fuel & Expenses", "✏️ Full CRUD",  "👁 View only",       "👁 View only",               "✏️ Add/View"],
        ["Analytics",       "👁 + CSV Export","👁 Charts only",   "👁 Charts only",             "👁 + CSV Export"],
        ["Settings",        "✏️ Full",        "❌ Hidden",          "❌ Hidden",                   "❌ Hidden"],
    ]
    col_w = [3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 3.5*cm]
    all_rows = [[Paragraph(h, style(f"rh{i}", fontSize=8, textColor=C_ORANGE,
                                    fontName="Helvetica-Bold"))
                 for i, h in enumerate(headers)]]
    for row in rows:
        all_rows.append([Paragraph(cell, style(f"rc{j}", fontSize=7.5,
                         textColor=C_WHITE if j == 0 else C_GRAY,
                         fontName="Helvetica-Bold" if j == 0 else "Helvetica"))
                         for j, cell in enumerate(row)])
    tbl = Table(all_rows, colWidths=col_w, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND",     (0, 0), (-1, 0),  C_CARD),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_DARK, C_CARD]),
        ("GRID",           (0, 0), (-1, -1), 0.4, C_BORDER),
        ("TOPPADDING",     (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",  (0, 0), (-1, -1), 5),
        ("LEFTPADDING",    (0, 0), (-1, -1), 6),
        ("VALIGN",         (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def build():
    out = os.path.join(os.path.dirname(__file__), "TransitOps_Phases2to5_Report.pdf")
    doc = SimpleDocTemplate(out, pagesize=A4, topMargin=1.8*cm, bottomMargin=1.8*cm,
                            leftMargin=2*cm, rightMargin=2*cm)
    story = []

    # ── Cover ──────────────────────────────────────────────
    story += [SP(40)]
    story.append(Paragraph("🚛 <b>TransitOps</b>", style("cover_brand", fontSize=32,
                 textColor=C_ORANGE, fontName="Helvetica-Bold", alignment=TA_CENTER)))
    story.append(Paragraph("Smart Transport Operations Platform",
                 style("cover_sub", fontSize=13, textColor=C_GRAY,
                       fontName="Helvetica", alignment=TA_CENTER, spaceAfter=8)))
    story.append(HR())
    story.append(Paragraph("Post-Phase-1 Development Report",
                 style("cover_title", fontSize=18, textColor=C_WHITE,
                       fontName="Helvetica-Bold", alignment=TA_CENTER, spaceBefore=10, spaceAfter=6)))
    story.append(Paragraph("Phases 2 – 5  |  RBAC Enforcement  |  UI/UX Upgrades",
                 style("cover_phases", fontSize=11, textColor=C_BLUE,
                       fontName="Helvetica", alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph("July 2026  ·  Odoo Virtual Hackathon Round",
                 style("cover_date", fontSize=9, textColor=C_GRAY,
                       fontName="Helvetica", alignment=TA_CENTER)))
    story += [SP(20), PageBreak()]

    # ── Table of Contents ────────────────────────────────────
    story.append(h1("Table of Contents"))
    story.append(HR())
    toc_items = [
        ("1", "Phase 2 — Vehicle & Driver Management",      "Fleet CRUD, schemas, services, RBAC"),
        ("2", "Phase 3 — Trip Dispatch Engine",             "Trip lifecycle, business rule validation"),
        ("3", "Phase 4 — Maintenance & Fuel/Expenses",      "Workflow, vehicle status transitions"),
        ("4", "Phase 5 — Analytics & Settings",             "5 charts, CSV export, user management"),
        ("5", "RBAC Enforcement",                           "Two-layer permission system"),
        ("6", "UI/UX Upgrades",                             "Selection cards, CSS polish, dashboard fix"),
        ("7", "Errors Encountered & Resolutions",           "All bugs fixed during development"),
        ("8", "Architecture Overview",                      "File structure and design decisions"),
    ]
    for num, title, desc in toc_items:
        story.append(Paragraph(f"<b>{num}.</b>  {title}  <font color='#9ca3af'>— {desc}</font>",
                     style(f"toc{num}", fontSize=10, textColor=C_WHITE,
                           fontName="Helvetica", leading=18, leftIndent=10)))
    story += [SP(8), PageBreak()]

    # ══════════════════════════════════════════════════════
    # PHASE 2
    # ══════════════════════════════════════════════════════
    story.append(h1("Phase 2 — Vehicle & Driver Management"))
    story.append(HR())
    story.append(p("Phase 2 delivers complete CRUD operations for the two core fleet entities: "
                   "<b>Vehicles</b> and <b>Drivers</b>. Each entity follows the same three-layer "
                   "architecture: Pydantic schema → service → Streamlit page."))
    story += [SP(6)]

    story.append(h2("2.1  New Files Created"))
    rows = [
        ["File", "Purpose"],
        ["app/schemas/vehicle_schema.py", "VehicleCreate, VehicleUpdate — field validation, type coercion"],
        ["app/schemas/driver_schema.py",  "DriverCreate, DriverUpdate — license, score, expiry validation"],
        ["app/services/vehicle_service.py","get_all, get_by_id, create, update, delete, fleet_summary"],
        ["app/services/driver_service.py", "get_all, get_by_id, create, update, delete, driver_summary"],
        ["frontend/pages/page_fleet.py",   "KPI bar, filter table, add/edit forms, status change, delete"],
        ["frontend/pages/page_drivers.py", "KPI bar, license alerts, filter, add/edit, status, delete"],
    ]
    story.append(feature_table(rows))
    story += [SP(6)]

    story.append(h2("2.2  Business Rules"))
    rules = [
        "Registration number must be unique — service raises ValueError on duplicate.",
        "Safety score < 70 → Driver auto-suspended on create/update.",
        "Vehicles with trip history are Retired (not hard-deleted); drivers set to Off Duty.",
        "Driver license expiry < today → flagged as EXPIRED in table + red alert banner.",
        "Driver license expiry ≤ 30 days → flagged as EXPIRING SOON + yellow warning banner.",
        "Cannot change vehicle status from 'On Trip' manually while a trip is Dispatched.",
    ]
    for r in rules: story.append(bl(r))
    story += [SP(6)]

    story.append(h2("2.3  Key UI Features"))
    rows2 = [
        ["Feature", "Details"],
        ["6-KPI header (Drivers)", "Total, Available, On Trip, Suspended, Expired License, Expiring Soon"],
        ["5-KPI header (Fleet)",   "Total, Available, On Trip, In Maintenance, Retired"],
        ["Filter bar",             "Type + Status (Fleet); Status + Category + Name search (Drivers)"],
        ["Color-coded table",      "Status column styled green/amber/red/gray via Pandas Styler"],
        ["Add tab / Actions tab",  "Tabs shown/hidden dynamically based on RBAC can() check"],
        ["Selection card",         "Clicking a vehicle/driver shows a styled detail card, then action buttons"],
    ]
    story.append(feature_table(rows2))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # PHASE 3
    # ══════════════════════════════════════════════════════
    story.append(h1("Phase 3 — Trip Dispatch Engine"))
    story.append(HR())
    story.append(p("Phase 3 implements the core operational workflow: create a trip, "
                   "validate all business rules, dispatch it (locking vehicle + driver), "
                   "complete it (releasing resources), or cancel it."))
    story += [SP(6)]

    story.append(h2("3.1  Trip Lifecycle"))
    lifecycle = [
        ["Status",      "Trigger",           "Vehicle",    "Driver"],
        ["Draft",       "Trip created",      "Available",  "Available"],
        ["Dispatched",  "Dispatch action",   "On Trip",    "On Trip"],
        ["Completed",   "Complete action",   "Available",  "Available"],
        ["Cancelled",   "Cancel action",     "Available*", "Available*"],
    ]
    tbl = Table(lifecycle, colWidths=[3.5*cm, 5*cm, 4*cm, 4*cm], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0),  C_CARD),
        ("TEXTCOLOR",   (0,0), (-1,0),  C_ORANGE),
        ("FONTNAME",    (0,0), (-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 8.5),
        ("ROWBACKGROUNDS",(0,1),(-1,-1),[C_DARK, C_CARD]),
        ("TEXTCOLOR",   (0,1), (-1,-1), C_WHITE),
        ("GRID",        (0,0), (-1,-1), 0.4, C_BORDER),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(tbl)
    story.append(cap("* Vehicle and Driver only released if trip was Dispatched at time of cancellation."))
    story += [SP(6)]

    story.append(h2("3.2  Dispatch Validation Rules"))
    drules = [
        "Vehicle status must be <b>Available</b> at dispatch time.",
        "Driver status must be <b>Available</b> at dispatch time.",
        "Driver license must NOT be expired (hard block, not a warning).",
        "cargo_weight_kg must be ≤ vehicle.max_capacity_kg.",
        "planned_distance_km must be > 0; revenue and cargo_weight must be ≥ 0.",
        "Soft capacity check also runs at trip creation to catch obvious errors early.",
        "Trip code auto-generated: <b>TRP-DDMMYY-XXXXXX</b> (date + 6-char UUID fragment).",
    ]
    for r in drules: story.append(bl(r))
    story += [SP(6)]

    story.append(h2("3.3  New Files"))
    rows3 = [
        ["File", "Purpose"],
        ["app/schemas/trip_schema.py",    "TripCreate, TripUpdate, TripComplete with validators"],
        ["app/services/trip_service.py",  "Full lifecycle + get_available_vehicles/drivers helpers"],
        ["frontend/pages/page_trips.py",  "6-KPI header, All Trips tab, Create Trip tab, Actions panel"],
    ]
    story.append(feature_table(rows3))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # PHASE 4
    # ══════════════════════════════════════════════════════
    story.append(h1("Phase 4 — Maintenance & Fuel/Expense Logging"))
    story.append(HR())
    story += [SP(4)]

    story.append(h2("4.1  Maintenance Workflow"))
    maint_rules = [
        "Vehicle must NOT be On Trip before logging maintenance (cannot repair a moving truck).",
        "Vehicle must NOT already be In Shop (must close existing record first).",
        "Logging maintenance → Vehicle status: <b>Available → In Shop</b>.",
        "Closing maintenance → Vehicle status: <b>In Shop → Available</b>.",
        "Only one Active maintenance record allowed per vehicle at a time.",
        "Closing allows optional actual_cost override (recorded against the log).",
    ]
    for r in maint_rules: story.append(bl(r))
    story += [SP(4)]

    story.append(h2("4.2  Fuel & Expense Logging"))
    rows4 = [
        ["Entity",   "Key Fields",               "Validation"],
        ["FuelLog",  "vehicle, liters, cost, date, optional trip_id",
                     "liters > 0; cost > 0; trip must belong to same vehicle if linked"],
        ["Expense",  "vehicle, category, amount, date",
                     "category ∈ [Toll, Insurance, Fine, Parking, Loading/Unloading, Driver Allowance, Misc]"],
    ]
    story.append(feature_table(rows4, col_widths=[2.5*cm, 7*cm, 7*cm]))
    story += [SP(4)]

    story.append(h2("4.3  New Files"))
    rows4b = [
        ["File", "Purpose"],
        ["app/schemas/maintenance_schema.py", "MaintenanceCreate, MaintenanceClose"],
        ["app/schemas/fuel_schema.py",         "FuelCreate, ExpenseCreate + EXPENSE_CATEGORIES list"],
        ["app/services/maintenance_service.py","log, close, summary, vehicle selector helpers"],
        ["app/services/fuel_service.py",       "add_fuel_log, add_expense, cost_summary, get_all"],
        ["frontend/pages/page_maintenance.py", "4-KPI header, Log tab, All Records tab, Close panel"],
        ["frontend/pages/page_fuel_expenses.py","4-tab layout: Log Fuel, Log Expense, Fuel Records, Expense Records"],
    ]
    story.append(feature_table(rows4b))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # PHASE 5
    # ══════════════════════════════════════════════════════
    story.append(h1("Phase 5 — Analytics & Settings"))
    story.append(HR())
    story += [SP(4)]

    story.append(h2("5.1  Analytics Page"))
    charts = [
        ["Chart", "Type", "Data Source"],
        ["Revenue by Vehicle",           "Bar (green)", "Trip.revenue grouped by vehicle (Completed only)"],
        ["Completed Trips by Month",     "Bar (blue)",  "Trip.created_at grouped by month"],
        ["Fuel Efficiency per Vehicle",  "Bar (color-coded)", "trip.fuel_consumed_l / planned_distance_km"],
        ["Cost Breakdown",               "Donut pie",   "FuelLog.cost + Expense.amount + Maintenance.cost"],
        ["Total Trips per Vehicle",      "Bar (purple)", "All trips (any status) by vehicle"],
    ]
    story.append(feature_table(charts, col_widths=[5*cm, 3*cm, 8.5*cm]))
    story += [SP(4)]
    story.append(p("All charts are rendered with <b>Plotly</b> using the app's dark theme palette. "
                   "CSV export (3 buttons: Trips, Fuel, Expenses) is gated to Fleet Manager "
                   "and Financial Analyst roles."))
    story += [SP(4)]

    story.append(h2("5.2  Settings Page"))
    settings_features = [
        "System Info tab — App name, DB type, framework, ORM, debug mode.",
        "User Management tab — Role-colour-coded user table + role change form (Fleet Manager only).",
        "RBAC Matrix tab — Read-only colour-coded view of all role permissions.",
        "Danger Zone — 'Reset Database' button that calls reset_database() (dev tool, FM only).",
        "Access gated: renders an error and stops for any non-Fleet-Manager role.",
    ]
    for f in settings_features: story.append(bl(f))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # RBAC
    # ══════════════════════════════════════════════════════
    story.append(h1("RBAC Enforcement — Two-Layer System"))
    story.append(HR())
    story += [SP(4)]

    story.append(h2("6.1  Architecture"))
    story.append(p("Two independent layers prevent unauthorised access:"))
    layers = [
        ("<b>Layer 1 — Coarse (Sidebar)</b>",
         "PERMISSIONS dict in rbac.py. Maps role → module → 'none'/'view'/'edit'. "
         "Sidebar only renders items where access ≠ 'none'. Settings hidden for all non-FM roles."),
        ("<b>Layer 2 — Granular (In-page)</b>",
         "ROLE_ACTIONS dict in rbac.py. Maps role → action → bool. "
         "e.g. 'fleet.add', 'trips.dispatch', 'fuel.add'. "
         "Pages call can(action) from auth_guard.py to show/hide individual buttons and forms."),
    ]
    for title, desc in layers:
        story.append(Paragraph(f"<b>{title}</b><br/>{desc}",
                     style("layer", fontSize=9, textColor=C_WHITE, fontName="Helvetica",
                           leading=14, leftIndent=10, spaceAfter=6,
                           backColor=C_CARD, borderPad=6)))

    story += [SP(6)]
    story.append(h2("6.2  RBAC Matrix"))
    story.append(rbac_table())
    story += [SP(4)]

    story.append(h2("6.3  How It Works in Code"))
    story.append(code("# auth_guard.py — used in every page"))
    story.append(code("from frontend.components.auth_guard import can"))
    story.append(code(""))
    story.append(code("if can('fleet.add'):"))
    story.append(code("    show_add_vehicle_tab()"))
    story.append(code(""))
    story.append(code("if can('trips.dispatch') and trip['status'] == 'Draft':"))
    story.append(code("    show_dispatch_button()"))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # UI/UX
    # ══════════════════════════════════════════════════════
    story.append(h1("UI/UX Upgrades"))
    story.append(HR())
    story += [SP(4)]

    story.append(h2("7.1  Dashboard Fixes"))
    dashboard_fixes = [
        "<b>Removed dead filter row</b> — Type / Status / Region dropdowns had no effect and confused users.",
        "<b>Recent Trips now live</b> — Added Vehicle and Driver columns; queries live DB on every render.",
        "<b>Flat bar → Donut chart</b> — Fleet status donut with center label (total count) + mini stat row.",
        "<b>8 KPIs instead of 7</b> — Added Total Revenue tile (Rs. from completed trips).",
    ]
    for f in dashboard_fixes: story.append(bl(f))
    story += [SP(6)]

    story.append(h2("7.2  Selection Card (Actions Panel)"))
    story.append(p("All three management pages (Fleet, Drivers, Trips) previously showed a cramped "
                   "3-column layout where the status dropdown was squeezed between Edit and Delete buttons. "
                   "This was replaced with a <b>styled selection card</b> that shows all key details of "
                   "the chosen item, followed by clearly labelled action buttons and a separate "
                   "'Change Status' row."))
    card_features = [
        "Orange left-border card with flex-wrap meta tags (Model, Type, Capacity, etc.).",
        "Colour-coded status badge inside card (green/amber/red/gray).",
        "Driver card shows safety score in colour (green ≥ 80, amber ≥ 70, red < 70) + license badge.",
        "Trip card shows route, vehicle, driver, cargo weight, revenue, status badge.",
        "Action buttons only appear for the actions actually available for the selected item's status.",
        "Status change moved to its own labelled section with a [3:1] wide selector + Apply button.",
    ]
    for f in card_features: story.append(bl(f))
    story += [SP(6)]

    story.append(h2("7.3  CSS Enhancements (style.css)"))
    css_items = [
        "Primary button — gradient fill, glow box-shadow, translateY hover lift.",
        "Secondary button — border turns orange on hover.",
        "Form inputs — border highlights orange on focus with soft glow ring.",
        "Dataframe — border-radius 10px on all tables.",
        "Custom scrollbar — thin 6px dark scrollbar matching theme.",
        "Tab transitions — subtle radius on tab list items.",
        ".selection-card, .sc-badge-* — new classes powering the actions panel.",
    ]
    for f in css_items: story.append(bl(f))
    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # ERRORS
    # ══════════════════════════════════════════════════════
    story.append(h1("Errors Encountered & Resolutions"))
    story.append(HR())
    story += [SP(4)]

    errors = [
        (
            "StreamlitAPIException: st.switch_page() page not found",
            "Phase 1 initially used st.switch_page() with SDD file paths. "
            "Streamlit only supports pages/ folder convention. ",
            "Abandoned st.switch_page(); built custom PAGE_MAP router in frontend/router.py. "
            "Single app.py entry point with session_state['page'] driving all navigation."
        ),
        (
            "UnicodeEncodeError: 'cp1252' codec can't encode character",
            "Windows terminal (cp1252) can't print Unicode emoji from Python logging on stdout.",
            "Added sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace') "
            "at top of all CLI scripts (smoke tests, seed, PDF generator)."
        ),
        (
            "SQLite OperationalError: database is locked",
            "Smoke tests tried to reset_database() (delete .db file) while Streamlit had an open connection.",
            "Always stop Streamlit before running smoke tests. "
            "reset_database() now has a clear error message. Documented in dev workflow."
        ),
        (
            "SyntaxError: invalid syntax (walrus := operator in assert)",
            "Smoke test p345 used 'assert f.cost_per_l_calc := round(...)' — walrus in assert is invalid Python.",
            "Removed the malformed assert; the cost_per_l field is computed in the service, not the schema."
        ),
        (
            "Pydantic ValidationError: 'model_post_init' not called for default date",
            "MaintenanceCreate used 'date: datetime.date = None' but Pydantic v2 doesn't call model_post_init "
            "on None defaults the same way.",
            "Changed to use model_post_init with object.__setattr__ for the default date assignment, "
            "matching the pattern used in FuelCreate and ExpenseCreate."
        ),
        (
            "Protobuf 'Descriptors cannot be created directly' on page imports",
            "Importing Streamlit pages (which import streamlit) outside the Streamlit runtime raises a "
            "protobuf version conflict error.",
            "This is a known Streamlit limitation. Backend-only smoke tests skip page imports. "
            "Pages are verified by running the app manually. Not a code error."
        ),
        (
            "Dashboard Recent Trips showing stale/no data",
            "The recent trips query existed but the DataFrame lacked Vehicle and Driver columns. "
            "Also, the page had a non-functional filter row (Type / Status / Region) that misled users.",
            "Removed filter row. Added v_map and d_map lookup in _get_dashboard_data(). "
            "Recent trips now shows Trip Code, Route, Vehicle, Driver, Revenue, Status."
        ),
        (
            "Actions panel UX — cramped 3-column layout",
            "Vehicle/Driver/Trip action panels had Edit | [Status dropdown + Apply] | Delete "
            "in three equal columns, making the status dropdown tiny and confusing.",
            "Replaced with a styled .selection-card HTML component showing item details, "
            "followed by clean action buttons (dynamic count) and a dedicated status-change row."
        ),
    ]

    for i, (title, cause, fix) in enumerate(errors, 1):
        story.append(KeepTogether([
            h3(f"Error {i}: {title}"),
            Paragraph(f"<b><font color='#ef4444'>Cause:</font></b>  {cause}",
                      style(f"ec{i}", fontSize=8.5, textColor=C_WHITE, fontName="Helvetica",
                            leading=13, spaceAfter=3, leftIndent=8)),
            Paragraph(f"<b><font color='#10b981'>Fix:</font></b>  {fix}",
                      style(f"ef{i}", fontSize=8.5, textColor=C_WHITE, fontName="Helvetica",
                            leading=13, spaceAfter=8, leftIndent=8)),
            HR(),
        ]))

    story += [SP(4), PageBreak()]

    # ══════════════════════════════════════════════════════
    # ARCHITECTURE
    # ══════════════════════════════════════════════════════
    story.append(h1("Architecture Overview"))
    story.append(HR())
    story += [SP(4)]

    story.append(h2("8.1  Directory Structure"))
    struct = [
        "TransitOps/",
        "├── app.py                      ← Single entry point; session router",
        "├── .env                        ← DATABASE_URL, SECRET_KEY, APP_NAME, DEBUG",
        "├── app/",
        "│   ├── config.py               ← Loads .env via python-dotenv",
        "│   ├── constants.py            ← Enums (VehicleStatus, TripStatus, …)",
        "│   ├── logger.py               ← get_logger() factory (rotating file handler)",
        "│   ├── auth/",
        "│   │   ├── rbac.py             ← PERMISSIONS + ROLE_ACTIONS + helpers",
        "│   │   └── security.py         ← bcrypt hash/verify",
        "│   ├── database/",
        "│   │   ├── engine.py           ← get_session(), init_db(), reset_database()",
        "│   │   └── seed.py             ← 4 roles, 4 users, 6 vehicles, 5 drivers, 5 trips",
        "│   ├── models/                 ← 8 SQLAlchemy ORM models",
        "│   │   └── (base, user, role, vehicle, driver, trip, maintenance, fuel_log, expense)",
        "│   ├── schemas/                ← Pydantic v2 input/update schemas",
        "│   │   └── (vehicle, driver, trip, maintenance, fuel)",
        "│   └── services/               ← Business logic, zero Streamlit imports",
        "│       └── (auth, vehicle, driver, trip, maintenance, fuel)",
        "├── frontend/",
        "│   ├── router.py               ← PAGE_MAP dict; maps page names to render()",
        "│   ├── assets/style.css        ← Global dark theme CSS",
        "│   ├── components/",
        "│   │   ├── auth_guard.py       ← require_auth(), require_role(), can(action)",
        "│   │   ├── kpi_card.py         ← render_kpi_card() HTML component",
        "│   │   └── sidebar.py          ← Role-filtered navigation sidebar",
        "│   └── pages/                  ← 8 page modules each with render()",
        "│       └── (dashboard, fleet, drivers, trips, maintenance,",
        "│              fuel_expenses, analytics, settings)",
        "├── data/transitops.db          ← SQLite database",
        "└── docs/                       ← Generated PDF reports",
    ]
    for line in struct:
        story.append(Paragraph(line, style("struct", fontSize=7.5, textColor=C_GREEN,
                               fontName="Courier", leading=11)))
    story += [SP(8)]

    story.append(h2("8.2  Key Design Decisions"))
    decisions = [
        ("<b>Zero-Streamlit backend</b>",
         "app/ contains no streamlit imports. All business logic is pure Python. "
         "Pages in frontend/ are the only place st.* is called."),
        ("<b>Custom router over st.switch_page</b>",
         "Streamlit's native multi-page routing requires files in pages/ and breaks "
         "with SDD folder structure. PAGE_MAP in router.py gives full control."),
        ("<b>SQLite + SQLAlchemy ORM</b>",
         "SQLite requires no server for hackathon. SQLAlchemy ORM with mapped_column "
         "and typed Mapped[] fields. reset_database() available for development iterations."),
        ("<b>Pydantic v2 schemas</b>",
         "All user input validated before reaching services. ValidationError messages "
         "shown directly in UI via st.error(). Services only receive clean data."),
        ("<b>bcrypt authentication</b>",
         "Passwords hashed with bcrypt at seed time. Login validates via "
         "bcrypt.checkpw(). JWT/sessions simulated via Streamlit session_state."),
    ]
    for title, desc in decisions:
        story.append(Paragraph(f"{title}  — {desc}",
                     style(f"dec{title}", fontSize=8.5, textColor=C_WHITE,
                           fontName="Helvetica", leading=13, leftIndent=10,
                           spaceAfter=6)))

    story += [SP(10)]
    story.append(HR())
    story.append(Paragraph("TransitOps — Odoo Virtual Hackathon 2026  |  Phases 2–5 Development Report",
                 style("footer", fontSize=8, textColor=C_GRAY,
                       fontName="Helvetica", alignment=TA_CENTER)))

    doc.build(story)
    print(f"[OK] Report saved: {out}")
    return out


if __name__ == "__main__":
    build()
