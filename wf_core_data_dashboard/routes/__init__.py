import datetime
import os
from typing import List

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wf_core_data_dashboard.core import get_template
from wf_core_data_dashboard import generate_fastbridge_table_data, groups_page_html, students_page_html

class StatusResponse(BaseModel):
    status: str = "OK"


router = APIRouter()


########################################################################
# HACK - stand in for a database
########################################################################
data_directory = "./data/analysis/fastbridge_analysis/fastbridge_analysis_20210916"

test_events_path = os.path.join(
    data_directory,
    'test_events_20210916.pkl'
)
student_info_path = os.path.join(
    data_directory,
    'student_info_20210916.pkl'
)

students, groups = generate_fastbridge_table_data(
    test_events_path,
    student_info_path
)


########################################################################
# Routes
########################################################################
@router.get("/", response_class=HTMLResponse)
async def index():
    template = get_template("index.html")
    return template.render(title="Assessment Results",
                           subtitle="Available Reports")


@router.get("/group/{years}", response_class=HTMLResponse)
async def groups_page(years: str):
    return groups_page_html(
            groups,
            school_year=years
        )

@router.get("/students/{years}", response_class=HTMLResponse)
async def students_page(years: str):
    return students_page_html(
            students=students,
            school_year=years
        )
