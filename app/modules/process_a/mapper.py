from datetime import date

from app.modules.process_a.model import ProcessAData
from app.services.catalog_service import (
    load_companies,
    load_areas,
)


def build_areas_text(selected_areas):
    
    if not selected_areas:
        return ""

    if len(selected_areas) == 1:
        return selected_areas[0]

    if len(selected_areas) == 2:
        return f"{selected_areas[0]} y {selected_areas[1]}"

    return (
        ", ".join(selected_areas[:-1])
        + f" y {selected_areas[-1]}"
    )

def get_spanish_month(month_number):
    months = {
        1: "enero",
        2: "febrero",
        3: "marzo",
        4: "abril",
        5: "mayo",
        6: "junio",
        7: "julio",
        8: "agosto",
        9: "septiembre",
        10: "octubre",
        11: "noviembre",
        12: "diciembre",
    }

    return months[month_number]

def map_process_a_data(data: ProcessAData):
    companies = load_companies()
    areas = load_areas()

    today = date.today()

    current_day = today.day
    current_month = get_spanish_month(today.month)
    current_year = today.year

    selected_companies = [
        company
        for company in companies
        if company["id"] in data.company_ids
    ]

    selected_areas = [
        area["name"]
        for area in areas
        if area["id"] in data.area_ids
    ]

    areas_text = build_areas_text(
        selected_areas
    )

    block_distribution = []

    for area in areas:
        area_id = area["id"]

        if area_id in data.block_percentages:
            block_distribution.append(
                {
                    "area_id": area_id,
                    "area_name": area["name"],
                    "percentage": data.block_percentages[
                        area_id
                    ],
                }
            )
    cc_companies = []

    cc_by_area = {
        "sal": [
            "YPFB Andina S.A.",
            "TotalEnergies EP Bolivie Sucursal Bolivia",
        ],
        "san": [
            "YPFB Andina S.A.",
            "TotalEnergies EP Bolivie Sucursal Bolivia",
        ],
        "itu": [
            "TotalEnergies EP Bolivie Sucursal Bolivia",
            "Shell Bolivia Corporation, Sucursal Bolivia",
            "YPFB Chaco S.A.",
        ],
        "colpa_caranda": [],
        "san_telmo_norte": [
            "YPFB Chaco S.A.",
        ],
    }

    for area_id in data.area_ids:
        for company in cc_by_area.get(
            area_id,
            [],
        ):
            if company not in cc_companies:
                cc_companies.append(company)
    mapped_data = {
        "request_file": data.request_file,
        "cite": data.cite,
        "process_number": data.process_number,
        "process_description": data.process_description,
        "annexes": data.annexes,
        "stage": data.stage,
        "destination": data.destination,
        "companies": selected_companies,
        "areas": selected_areas,
        "areas_text": areas_text,
        "billing_type": data.billing_type,
        "block_distribution": block_distribution,    
        "cc_companies": cc_companies,
        "current_day": current_day,
        "current_month": current_month,
        "current_year": current_year,
        }
    return mapped_data
