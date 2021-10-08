import datetime
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wf_core_data_dashboard.core import get_template

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

student_assignments_path = os.path.join(
    data_directory,
    'student_assignments_20210916.pkl'
)

students, groups = wf_core_data_dashboard.assessments.fastbridge.generate_fastbridge_table_data(
    test_events_path,
    student_info_path,
    student_assignments_path
)


########################################################################
# Routes
########################################################################
@router.get("/", response_class=HTMLResponse)
async def index():
    template = get_template("index.html")
    return template.render(title="Assessment Results",
                           subtitle="Available Reports")


@router.get("/fastbridge/groups/", response_class=HTMLResponse)
async def groups_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    test: Optional[str]=None,
    subtest: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.fastbridge.groups_page_html(
        groups,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
    )

@router.get("/fastbridge/students/", response_class=HTMLResponse)
async def students_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    test: Optional[str]=None,
    subtest: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.fastbridge.students_page_html(
        students=students,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
    )
