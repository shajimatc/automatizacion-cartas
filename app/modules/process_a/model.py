from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProcessAData:
    request_file: str = ""
    cite_number: str = ""
    cite_year: str = ""
    stage: str = ""
    destination: str = ""

    company_ids: List[str] = field(
        default_factory=list
    )

    billing_type: Optional[str] = None
    block_distribution: str = ""
    block_percentages: dict = field(
        default_factory=dict
    )

    area_ids: List[str] = field(
        default_factory=list
    )
    process_number: str = ""
    process_description: str = ""
    annexes: List[str] = field(default_factory=list)
    authorization_reference: str = ""
    sincop_registration: str = ""
