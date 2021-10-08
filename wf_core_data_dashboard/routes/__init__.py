import datetime
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wf_core_data_dashboard.core import get_template

import wf_core_data_dashboard.assessments.fastbridge
import wf_core_data_dashboard.assessments.nwea

class StatusResponse(BaseModel):
    status: str = "OK"


router = APIRouter()


########################################################################
# HACK - stand in for a database
########################################################################
data_directory_fastbridge = "./data/analysis/fastbridge_analysis/fastbridge_analysis_20210916"

test_events_path_fastbridge = os.path.join(
    data_directory_fastbridge,
    'test_events_20210916.pkl'
)

student_info_path_fastbridge = os.path.join(
    data_directory_fastbridge,
    'student_info_20210916.pkl'
)

student_assignments_path_fastbridge = os.path.join(
    data_directory_fastbridge,
    'student_assignments_20210916.pkl'
)

students_fastbridge, groups_fastbridge = wf_core_data_dashboard.assessments.fastbridge.generate_fastbridge_table_data(
    test_events_path_fastbridge,
    student_info_path_fastbridge,
    student_assignments_path_fastbridge
)

data_directory_nwea = "./data/analysis/nwea_analysis/nwea_analysis_20210930"

test_events_path_nwea = os.path.join(
    data_directory_nwea,
    'test_events_20210930.pkl'
)

student_info_path_nwea = os.path.join(
    data_directory_nwea,
    'student_info_20210930.pkl'
)

student_assignments_path_nwea = os.path.join(
    data_directory_nwea,
    'student_assignments_20210930.pkl'
)

students_nwea, groups_nwea = wf_core_data_dashboard.assessments.nwea.generate_nwea_table_data(
    test_events_path_nwea,
    student_info_path_nwea,
    student_assignments_path_nwea
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
async def fastbridge_groups_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    test: Optional[str]=None,
    subtest: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.fastbridge.groups_page_html(
        groups_fastbridge,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
    )

@router.get("/fastbridge/students/", response_class=HTMLResponse)
async def fastbridge_students_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    test: Optional[str]=None,
    subtest: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.fastbridge.students_page_html(
        students=students_fastbridge,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
    )

@router.get("/nwea/groups/", response_class=HTMLResponse)
async def nwea_groups_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    subject: Optional[str]=None,
    course: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.nwea.groups_page_html(
        groups_nwea,
        school_year=school_year,
        school=school,
        subject=subject,
        course=course
    )

@router.get("/nwea/students/", response_class=HTMLResponse)
async def nwea_students_page(
    school_year: Optional[str]=None,
    school: Optional[str]=None,
    subject: Optional[str]=None,
    course: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.nwea.students_page_html(
        students=students_nwea,
        school_year=school_year,
        school=school,
        subject=subject,
        course=course
    )
