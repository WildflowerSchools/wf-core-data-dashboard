import datetime
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from wf_core_data_dashboard.core import get_template

import wf_core_data_dashboard.assessments.fastbridge
import wf_core_data_dashboard.assessments.nwea
import wf_core_data_dashboard.assessments.mefs

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

data_directory_mefs = "./data/analysis/mefs_analysis/mefs_analysis_20211008"

test_events_path_mefs = os.path.join(
    data_directory_mefs,
    'test_events_20211008.pkl'
)

student_info_path_mefs = os.path.join(
    data_directory_mefs,
    'student_info_20211008.pkl'
)

student_assignments_path_mefs = os.path.join(
    data_directory_mefs,
    'student_assignments_20211008.pkl'
)

students_mefs, groups_mefs = wf_core_data_dashboard.assessments.mefs.generate_mefs_table_data(
    test_events_path_mefs,
    student_info_path_mefs,
    student_assignments_path_mefs
)


########################################################################
# Routes
########################################################################
@router.get("/", response_class=HTMLResponse)
async def index():
    template = get_template("index.html")
    return template.render(title="Assessment results",
                           subtitle="Available assessments")

@router.get("/fastbridge", response_class=HTMLResponse)
async def fastbridge_overview():
    template = get_template("fastbridge_overview.html")
    return template.render(title="FastBridge results",
                           subtitle="Available reports")

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

@router.get("/nwea", response_class=HTMLResponse)
async def fastbridge_overview():
    template = get_template("nwea_overview.html")
    return template.render(title="NWEA results",
                           subtitle="Available reports")

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

@router.get("/mefs", response_class=HTMLResponse)
async def fastbridge_overview():
    template = get_template("mefs_overview.html")
    return template.render(title="MEFS results",
                           subtitle="Available reports")

@router.get("/mefs/groups/", response_class=HTMLResponse)
async def mefs_groups_page(
    school_year: Optional[str]=None,
    group_name_mefs: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.mefs.groups_page_html(
        groups_mefs,
        school_year=school_year,
        group_name_mefs=group_name_mefs
    )

@router.get("/mefs/students/", response_class=HTMLResponse)
async def mefs_students_page(
    school_year: Optional[str]=None,
    group_name_mefs: Optional[str]=None
):
    return wf_core_data_dashboard.assessments.mefs.students_page_html(
        students=students_mefs,
        school_year=school_year,
        group_name_mefs=group_name_mefs
    )
