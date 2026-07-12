"""
frontend/pages/page_drivers.py — Phase 2 + RBAC enforcement

Permissions enforced:
  Fleet Manager  → full CRUD + status change
  Safety Officer → add + edit + status (no delete)
  Dispatcher     → view only
  Financial Analyst → view only
"""
from __future__ import annotations
import datetime
import streamlit as st
import pandas as pd
from pydantic import ValidationError

from app.constants import DriverStatus, LicenseCategory
from app.schemas.driver_schema import DriverCreate, DriverUpdate
from app.services.driver_service import (
    get_all_drivers, get_driver_by_id, create_driver,
    update_driver, delete_driver, get_driver_summary,
)
from frontend.components.auth_guard import can

_KEY_EDIT = "driver_edit_id"
_KEY_DEL  = "driver_confirm_delete_id"

def _init():
    for k in [_KEY_EDIT, _KEY_DEL]:
        if k not in st.session_state:
            st.session_state[k] = None


def _show_kpis(summary: dict):
    cols = st.columns(6)
    items = [
        (summary["total"],           "Total Drivers",     "#3b82f6"),
        (summary["available"],       "Available",         "#10b981"),
        (summary["on_trip"],         "On Trip",           "#f59e0b"),
        (summary["suspended"],       "Suspended",         "#ef4444"),
        (summary["expired_license"], "Expired License",   "#ef4444"),
        (summary["expiring_soon"],   "Expiring ≤30 Days", "#f59e0b"),
    ]
    for col, (val, label, color) in zip(cols, items):
        with col:
            st.markdown(
                f'<div style="background:#21252e;border-radius:10px;padding:14px 16px;'
                f'border-left:4px solid {color};margin-bottom:8px;">'
                f'<p style="margin:0;color:#9ca3af;font-size:0.75rem;text-transform:uppercase;'
                f'letter-spacing:.05em;">{label}</p>'
                f'<p style="margin:0;color:{color};font-size:1.6rem;font-weight:700;">{val}</p></div>',
                unsafe_allow_html=True,
            )


def _license_alerts(drivers: list[dict]):
    expired  = [d for d in drivers if d["license_expired"]]
    expiring = [d for d in drivers if d["license_expiring_soon"]]
    if expired:
        names = ", ".join(d["name"] for d in expired[:5])
        st.error(f"🔴 **{len(expired)} driver(s) have EXPIRED licenses**: {names}")
    if expiring:
        names = ", ".join(f"{d['name']} ({d['days_to_expiry']}d)" for d in expiring[:5])
        st.warning(f"🟡 **{len(expiring)} driver(s) expiring within 30 days**: {names}")


def _add_driver_form():
    st.markdown("#### ➕ Add New Driver")
    with st.form("add_driver_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            name        = st.text_input("Full Name *",       placeholder="e.g. Raju Sharma")
            license_no  = st.text_input("License Number *",  placeholder="e.g. MH0120230012345")
            category    = st.selectbox("License Category *", [c.value for c in LicenseCategory])
            license_exp = st.date_input(
                "License Expiry *",
                value=datetime.date.today() + datetime.timedelta(days=365),
            )
        with c2:
            contact = st.text_input("Contact Number *", placeholder="+91 98765 43210")
            safety  = st.slider("Safety Score", 0, 100, 90,
                                help="Below 70 → auto-suspended.")
            if safety < 70:
                st.warning("⚠️ Score < 70 — driver will be auto-suspended.")
            elif safety < 80:
                st.info("ℹ️ Score < 80 — monitor closely.")
            days_left = (license_exp - datetime.date.today()).days
            if days_left < 0:
                st.error("🔴 License already expired!")
            elif days_left <= 30:
                st.warning(f"🟡 Expires in {days_left} day(s).")
        submitted = st.form_submit_button("👤 Add Driver", type="primary",
                                          use_container_width=True)
    if submitted:
        try:
            driver = create_driver(DriverCreate(
                name=name, license_no=license_no, license_category=category,
                license_expiry=license_exp, contact_no=contact, safety_score=float(safety),
            ))
            msg = f"✅ Driver **{driver['name']}** added!"
            if driver["status"] == DriverStatus.SUSPENDED:
                msg += " ⚠️ Auto-suspended (low safety score)."
            st.success(msg)
            st.rerun()
        except ValidationError as e:
            for err in e.errors(): st.error(f"⚠️ {err['msg']}")
        except ValueError as e:
            st.error(f"⚠️ {e}")


def _edit_driver_form(driver: dict):
    st.markdown(f"#### ✏️ Editing: **{driver['name']}** — {driver['license_no']}")
    with st.form("edit_driver_form"):
        c1, c2 = st.columns(2)
        with c1:
            name        = st.text_input("Full Name",       value=driver["name"])
            license_no  = st.text_input("License Number",  value=driver["license_no"])
            category    = st.selectbox("License Category",
                                       [c.value for c in LicenseCategory],
                                       index=[c.value for c in LicenseCategory].index(driver["license_category"]))
            license_exp = st.date_input("License Expiry",  value=driver["license_expiry"])
        with c2:
            contact = st.text_input("Contact Number",  value=driver["contact_no"])
            safety  = st.slider("Safety Score", 0, 100, int(driver["safety_score"]))
            if safety < 70:
                st.warning("⚠️ Score < 70 — will auto-suspend on save.")
            status  = st.selectbox("Status",
                                   [s.value for s in DriverStatus],
                                   index=[s.value for s in DriverStatus].index(driver["status"]),
                                   disabled=not can("drivers.status"))
        cs, cc = st.columns(2)
        with cs: save   = st.form_submit_button("💾 Save", type="primary",
                                                 use_container_width=True)
        with cc: cancel = st.form_submit_button("✖ Cancel", use_container_width=True)

    if save:
        try:
            result = update_driver(driver["id"], DriverUpdate(
                name=name, license_no=license_no, license_category=category,
                license_expiry=license_exp, contact_no=contact,
                safety_score=float(safety), status=status,
            ))
            msg = "✅ Driver updated!"
            if result["status"] == DriverStatus.SUSPENDED and driver["status"] != DriverStatus.SUSPENDED:
                msg += " ⚠️ Auto-suspended (low safety score)."
            st.success(msg)
            st.session_state[_KEY_EDIT] = None
            st.rerun()
        except (ValidationError, ValueError) as e:
            st.error(str(e))
    if cancel:
        st.session_state[_KEY_EDIT] = None
        st.rerun()


def _driver_table(drivers: list[dict]):
    if not drivers:
        st.info("No drivers match your filters.")
        return
    df = pd.DataFrame([{
        "Name":           d["name"],
        "License No":     d["license_no"],
        "Category":       d["license_category"],
        "Expiry":         d["license_expiry"].strftime("%d %b %Y"),
        "Safety Score":   f"{d['safety_score']:.0f}%",
        "Contact":        d["contact_no"],
        "Status":         d["status"],
        "License Status": ("EXPIRED" if d["license_expired"]
                           else f"Exp. {d['days_to_expiry']}d" if d["license_expiring_soon"]
                           else "Valid"),
    } for d in drivers])

    def cs(v):
        m = {"Available":"color:#10b981;font-weight:700;","On Trip":"color:#f59e0b;font-weight:700;",
             "Off Duty":"color:#9ca3af;font-weight:700;","Suspended":"color:#ef4444;font-weight:700;"}
        return m.get(v, "")

    def cl(v):
        if v == "EXPIRED":     return "color:#ef4444;font-weight:700;"
        if v.startswith("Exp."): return "color:#f59e0b;font-weight:700;"
        return "color:#10b981;"

    st.dataframe(df.style.map(cs, subset=["Status"]).map(cl, subset=["License Status"]),
                 use_container_width=True, hide_index=True)


def _driver_selection_card(d: dict) -> str:
    status_cls = {
        "Available":  "sc-badge-green",
        "On Trip":    "sc-badge-yellow",
        "Off Duty":   "sc-badge-gray",
        "Suspended":  "sc-badge-red",
    }.get(d["status"], "sc-badge-gray")
    score_color = (
        "#10b981" if d["safety_score"] >= 80
        else "#f59e0b" if d["safety_score"] >= 70
        else "#ef4444"
    )
    lic_cls = (
        "sc-badge-red"    if d["license_expired"]
        else "sc-badge-yellow" if d["license_expiring_soon"]
        else "sc-badge-green"
    )
    lic_label = (
        "EXPIRED"           if d["license_expired"]
        else f"Exp. {d['days_to_expiry']}d" if d["license_expiring_soon"]
        else "Valid"
    )
    return f"""
    <div class="selection-card">
        <div class="sc-title">👤 {d['name']}</div>
        <span class="sc-meta"><strong>License:</strong> {d['license_no']}</span>
        <span class="sc-meta"><strong>Category:</strong> {d['license_category']}</span>
        <span class="sc-meta"><strong>Contact:</strong> {d['contact_no']}</span>
        <span class="sc-meta"><strong>Safety Score:</strong>
            <span style="color:{score_color};font-weight:700;">{d['safety_score']:.0f}%</span>
        </span>
        <span class="sc-badge {lic_cls}">🔑 {lic_label}</span>
        <span class="sc-badge {status_cls}">{d['status']}</span>
    </div>
    """


def _actions_panel(drivers: list[dict]):
    can_edit_d   = can("drivers.edit")
    can_delete_d = can("drivers.delete")
    can_status_d = can("drivers.status")

    if not any([can_edit_d, can_delete_d, can_status_d]):
        return
    if not drivers:
        return

    st.markdown("---")
    st.markdown("#### 🔧 Driver Actions")
    options = {f"{d['name']} — {d['license_no']}": d for d in drivers}
    chosen  = options[st.selectbox("Select driver:", list(options.keys()),
                                   key="driver_select")]

    # Selection card
    st.markdown(_driver_selection_card(chosen), unsafe_allow_html=True)

    # Primary action buttons
    num_btns = sum([can_edit_d, can_delete_d])
    if num_btns:
        bcols = st.columns(max(num_btns, 1))
        idx   = 0
        if can_edit_d:
            with bcols[idx]:
                if st.button("✏️  Edit Driver", use_container_width=True,
                             type="primary", key="driver_edit_btn"):
                    st.session_state[_KEY_EDIT] = chosen["id"]
                    st.session_state[_KEY_DEL]  = None
                    st.rerun()
            idx += 1
        if can_delete_d:
            with bcols[idx]:
                if st.button("🗑️  Remove Driver", use_container_width=True,
                             key="driver_del_btn"):
                    st.session_state[_KEY_DEL]  = chosen["id"]
                    st.session_state[_KEY_EDIT] = None
                    st.rerun()

    # Status change
    if can_status_d:
        st.markdown("<hr class='actions-divider'>", unsafe_allow_html=True)
        st.markdown("**🔄 Change Driver Status**")
        sc1, sc2 = st.columns([3, 1])
        other = [s.value for s in DriverStatus if s.value != chosen["status"]]
        with sc1:
            new_s = st.selectbox("New status:", ["(keep current)"] + other,
                                 key="driver_status_sel", label_visibility="collapsed")
        with sc2:
            if st.button("Apply", use_container_width=True, key="driver_status_btn"):
                if new_s != "(keep current)":
                    try:
                        update_driver(chosen["id"], DriverUpdate(status=new_s))
                        st.success(f"✅ Status updated → **{new_s}**")
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
                else:
                    st.warning("Select a status to apply.")

    # Confirmation
    if st.session_state.get(_KEY_DEL) == chosen["id"]:
        st.warning(f"⚠️ Remove **{chosen['name']}**? "
                   "Drivers with trip history will be set to Off Duty instead of deleted.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, proceed", use_container_width=True,
                         key="driver_del_confirm"):
                try:
                    action = delete_driver(chosen["id"])
                    st.success("Status → **Off Duty**" if action == "retired"
                               else f"'{chosen['name']}' deleted.")
                    st.session_state[_KEY_DEL] = None
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
        with c2:
            if st.button("❌ Cancel", use_container_width=True, key="driver_del_cancel"):
                st.session_state[_KEY_DEL] = None
                st.rerun()

    # Edit form
    if st.session_state.get(_KEY_EDIT) and can_edit_d:
        st.markdown("---")
        driver = get_driver_by_id(st.session_state[_KEY_EDIT])
        if driver:
            _edit_driver_form(driver)
        else:
            st.session_state[_KEY_EDIT] = None



def render():
    _init()
    st.markdown('<div class="page-header"><h1 class="page-title">👤 Driver Management</h1></div>',
                unsafe_allow_html=True)

    _show_kpis(get_driver_summary())
    st.markdown("<br>", unsafe_allow_html=True)

    tabs = ["📋 All Drivers"]
    if can("drivers.add"):
        tabs.append("➕ Add Driver")

    rendered_tabs = st.tabs(tabs)
    tab_list = rendered_tabs[0]
    tab_add  = rendered_tabs[1] if len(rendered_tabs) > 1 else None

    if tab_add:
        with tab_add:
            _add_driver_form()

    with tab_list:
        if not can("drivers.add") and not can("drivers.edit"):
            st.info("🔒 You have **view-only** access to Driver Management.")

        fc1, fc2, fc3 = st.columns([2, 2, 2])
        with fc1:
            status_f = st.selectbox("Status", ["All"] + [s.value for s in DriverStatus],
                                    key="driver_status_filter")
        with fc2:
            cat_f    = st.selectbox("Category", ["All"] + [c.value for c in LicenseCategory],
                                    key="driver_cat_filter")
        with fc3:
            search   = st.text_input("Search name", placeholder="Type to filter...",
                                     key="driver_name_search")

        drivers = get_all_drivers(status_filter=status_f, category_filter=cat_f,
                                  name_search=search or None)
        _license_alerts(drivers)
        st.caption(f"{len(drivers)} driver(s)")
        _driver_table(drivers)
        _actions_panel(drivers)
