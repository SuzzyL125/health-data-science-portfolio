#!/usr/bin/env python3
"""Generate editable Tableau workbook templates connected to project CSV files."""

from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TABLEAU_NS = "http://www.tableausoftware.com/xml/user"
ET.register_namespace("user", TABLEAU_NS)


def add_text(parent: ET.Element, tag: str, text: str) -> ET.Element:
    node = ET.SubElement(parent, tag)
    node.text = text
    return node


def column_type(name: str, numeric: set[str]) -> tuple[str, str, str]:
    if name in numeric:
        return "real", "measure", "quantitative"
    return "string", "dimension", "nominal"


def build_workbook(
    output: Path,
    csv_name: str,
    datasource_caption: str,
    columns: list[str],
    numeric: set[str],
    sheets: list[dict],
    dashboard_name: str,
    dashboard_subtitle: str,
) -> None:
    workbook = ET.Element("workbook", {
        "locale": "en_US", "source-platform": "mac", "version": "18.1",
        "source-build": "2026.2.0 (20262.26.0710.0000)",
    })
    ET.SubElement(workbook, "preferences")
    ET.SubElement(workbook, "style-theme", {"name": "smooth"})
    datasources = ET.SubElement(workbook, "datasources")
    ds_name = "federated.portfolio"
    datasource = ET.SubElement(datasources, "datasource", {
        "caption": datasource_caption, "inline": "true", "name": ds_name, "version": "18.1"
    })
    connection = ET.SubElement(datasource, "connection", {"class": "federated"})
    named = ET.SubElement(connection, "named-connections")
    named_connection = ET.SubElement(named, "named-connection", {"caption": datasource_caption, "name": "csv.connection"})
    ET.SubElement(named_connection, "connection", {
        "class": "textscan", "directory": "../data/processed", "filename": csv_name,
        "header": "yes", "separator": ",", "text-qualifier": "&quot;", "character-set": "UTF-8",
    })
    relation_name = f"{csv_name.removesuffix('.csv')}#csv"
    relation = ET.SubElement(connection, "relation", {
        "connection": "csv.connection", "name": relation_name,
        "table": f"[{relation_name}]", "type": "table",
    })
    relation_columns = ET.SubElement(relation, "columns", {
        "character-set": "UTF-8", "header": "yes", "locale": "en_US", "separator": ",", "text-qualifier": "&quot;"
    })
    for ordinal, name in enumerate(columns):
        datatype, _, _ = column_type(name, numeric)
        ET.SubElement(relation_columns, "column", {"datatype": datatype, "name": name, "ordinal": str(ordinal)})

    for name in columns:
        datatype, role, type_name = column_type(name, numeric)
        ET.SubElement(datasource, "column", {
            "caption": name.replace("_", " ").title(), "datatype": datatype,
            "name": f"[{name}]", "role": role, "type": type_name,
        })

    worksheets = ET.SubElement(workbook, "worksheets")
    for sheet in sheets:
        worksheet = ET.SubElement(worksheets, "worksheet", {"name": sheet["name"]})
        layout = ET.SubElement(worksheet, "layout-options")
        title = ET.SubElement(layout, "title")
        formatted = ET.SubElement(title, "formatted-text")
        run = ET.SubElement(formatted, "run", {"bold": "true", "fontcolor": "#203864", "fontsize": "13"})
        run.text = sheet["title"]
        table = ET.SubElement(worksheet, "table")
        view = ET.SubElement(table, "view")
        view_ds = ET.SubElement(view, "datasources")
        ET.SubElement(view_ds, "datasource", {"caption": datasource_caption, "name": ds_name})
        deps = ET.SubElement(view, "datasource-dependencies", {"datasource": ds_name})
        used = set(sheet.get("rows", []) + sheet.get("cols", []) + sheet.get("color", []) + sheet.get("text", []) + sheet.get("detail", []))
        instances = {}
        for name in used:
            datatype, role, type_name = column_type(name, numeric)
            aggregation = sheet.get("aggregations", {}).get(name, "Sum" if name in numeric else "None")
            # Tableau's workbook schema uses Avg, not the UI label Average.
            aggregation = {"Average": "Avg"}.get(aggregation, aggregation)
            attrs = {"caption": name.replace("_", " ").title(), "datatype": datatype, "name": f"[{name}]", "role": role, "type": type_name}
            if name in numeric:
                attrs["aggregation"] = aggregation
            ET.SubElement(deps, "column", attrs)
            derivation = aggregation if aggregation != "None" else "None"
            token = "qk" if name in numeric else "nk"
            instance = f"[{derivation.lower()}:{name}:{token}]"
            ET.SubElement(deps, "column-instance", {
                "column": f"[{name}]", "derivation": derivation, "name": instance,
                "pivot": "key", "type": type_name,
            })
            instances[name] = instance
        ET.SubElement(view, "aggregation", {"value": "true"})
        # Tableau's table content model expects style before panes, even when no
        # worksheet-level formatting overrides are needed.
        ET.SubElement(table, "style")
        panes = ET.SubElement(table, "panes")
        pane = ET.SubElement(panes, "pane")
        pane_view = ET.SubElement(pane, "view")
        ET.SubElement(pane_view, "breakdown", {"value": "auto"})
        ET.SubElement(pane, "mark", {"class": sheet.get("mark", "Automatic")})
        encodings = ET.SubElement(pane, "encodings")
        for channel in ("color", "text", "detail"):
            for name in sheet.get(channel, []):
                # Tableau serializes Detail shelf fields as level-of-detail
                # encodings named `lod` in TWB XML.
                xml_channel = "lod" if channel == "detail" else channel
                ET.SubElement(encodings, xml_channel, {"column": f"[{ds_name}].{instances[name]}"})
        rows = " / ".join(f"[{ds_name}].{instances[name]}" for name in sheet.get("rows", []))
        cols = " / ".join(f"[{ds_name}].{instances[name]}" for name in sheet.get("cols", []))
        add_text(table, "rows", rows)
        add_text(table, "cols", cols)

    dashboards = ET.SubElement(workbook, "dashboards")
    dashboard = ET.SubElement(dashboards, "dashboard", {"name": dashboard_name})
    ET.SubElement(dashboard, "size", {"maxheight": "800", "maxwidth": "1200", "minheight": "800", "minwidth": "1200"})
    zones = ET.SubElement(dashboard, "zones")
    container = ET.SubElement(zones, "zone", {"h": "100000", "id": "1", "type": "layout-basic", "w": "100000", "x": "0", "y": "0"})
    ET.SubElement(container, "zone", {"h": "7000", "id": "2", "type": "title", "w": "100000", "x": "0", "y": "0"})
    subtitle = ET.SubElement(container, "zone", {"h": "6000", "id": "3", "type": "text", "w": "100000", "x": "0", "y": "7000"})
    formatted = ET.SubElement(subtitle, "formatted-text")
    run = ET.SubElement(formatted, "run", {"fontcolor": "#52606D", "fontsize": "10"})
    run.text = dashboard_subtitle
    positions = [(0, 13000, 50000, 39000), (50000, 13000, 50000, 39000), (0, 52000, 50000, 48000), (50000, 52000, 50000, 48000)]
    for idx, (sheet, pos) in enumerate(zip(sheets, positions), start=10):
        x, y, w, h = pos
        ET.SubElement(container, "zone", {"h": str(h), "id": str(idx), "name": sheet["name"], "show-title": "true", "w": str(w), "x": str(x), "y": str(y)})

    windows = ET.SubElement(workbook, "windows", {"source-height": "40"})
    window = ET.SubElement(windows, "window", {"class": "dashboard", "maximized": "true", "name": dashboard_name})
    viewpoints = ET.SubElement(window, "viewpoints")
    for sheet in sheets:
        viewpoint = ET.SubElement(viewpoints, "viewpoint", {"name": sheet["name"]})
        ET.SubElement(viewpoint, "zoom", {"type": "entire-view"})
    ET.SubElement(window, "active", {"id": "-1"})
    ET.SubElement(workbook, "thumbnails")

    ET.indent(workbook, space="  ")
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(workbook).write(output, encoding="utf-8", xml_declaration=True)


def main() -> None:
    hospital_columns = [
        "facility_id", "facility_name", "state", "hospital_type", "hospital_ownership",
        "hospital_overall_rating", "rating_label", "domain_worse_flags", "priority_tier", "four_five_star_flag",
        "mortality_worse_flag", "safety_worse_flag", "readmission_worse_flag",
    ]
    build_workbook(
        ROOT / "hospital-quality-patient-safety/tableau/hospital-quality-patient-safety.twb",
        "hospital_quality_tableau.csv", "CMS Hospital Quality", hospital_columns,
        {"hospital_overall_rating", "domain_worse_flags", "four_five_star_flag", "mortality_worse_flag", "safety_worse_flag", "readmission_worse_flag"},
        [
            {"name": "Rating by State", "title": "Average Hospital Rating by State", "rows": ["state"], "cols": ["hospital_overall_rating"], "color": ["hospital_overall_rating"], "mark": "Bar", "aggregations": {"hospital_overall_rating": "Average"}},
            {"name": "Priority Mix", "title": "Hospitals by Priority Tier", "rows": ["priority_tier"], "cols": ["facility_id"], "color": ["priority_tier"], "mark": "Bar", "aggregations": {"facility_id": "Count"}},
            {"name": "Rating Distribution", "title": "Hospitals by Overall Star Rating", "rows": ["facility_id"], "cols": ["rating_label"], "color": ["rating_label"], "text": ["facility_id"], "mark": "Bar", "aggregations": {"facility_id": "Count"}},
            {"name": "Risk Domain Summary", "title": "Total Worse-than-National Domain Flags", "rows": ["priority_tier"], "cols": ["domain_worse_flags"], "color": ["priority_tier"], "text": ["domain_worse_flags"], "mark": "Bar", "aggregations": {"domain_worse_flags": "Sum"}},
        ],
        "Hospital Quality & Patient Safety",
        "CMS Care Compare | 5,432 hospitals | Ratings, domain risk flags, and transparent review prioritization",
    )

    community_columns = [
        "locationid", "locationname", "stateabbr", "statedesc", "totalpopulation", "DIABETES", "OBESITY",
        "ACCESS2", "CHECKUP", "burden_score", "access_barrier_score", "social_needs_score",
        "priority_score", "priority_percentile", "priority_quintile", "high_priority_flag",
    ]
    numeric = {"totalpopulation", "DIABETES", "OBESITY", "ACCESS2", "CHECKUP", "burden_score", "access_barrier_score", "social_needs_score", "priority_score", "priority_percentile", "high_priority_flag"}
    build_workbook(
        ROOT / "community-health-disparities/tableau/community-health-disparities.twb",
        "community_health_tableau.csv", "CDC PLACES County Health", community_columns, numeric,
        [
            {"name": "State Priority", "title": "Average Priority Percentile by State", "rows": ["statedesc"], "cols": ["priority_percentile"], "color": ["priority_percentile"], "mark": "Bar", "aggregations": {"priority_percentile": "Average"}},
            {"name": "Burden vs Access", "title": "Disease Burden vs Access Barriers", "rows": ["burden_score"], "cols": ["access_barrier_score"], "color": ["priority_quintile"], "detail": ["locationname", "stateabbr"], "mark": "Circle", "aggregations": {"burden_score": "Average", "access_barrier_score": "Average"}},
            {"name": "Priority Quintiles", "title": "Counties by Priority Quintile", "rows": ["priority_quintile"], "cols": ["locationid"], "color": ["priority_quintile"], "mark": "Bar", "aggregations": {"locationid": "Count"}},
            {"name": "Diabetes by State", "title": "Average Diabetes Prevalence by State", "rows": ["statedesc"], "cols": ["DIABETES"], "color": ["priority_percentile"], "text": ["DIABETES"], "mark": "Bar", "aggregations": {"DIABETES": "Average", "priority_percentile": "Average"}},
        ],
        "Community Health Disparities & Access",
        "CDC PLACES | 2,957 counties | Disease burden, access barriers, social needs, and outreach prioritization",
    )


if __name__ == "__main__":
    main()
