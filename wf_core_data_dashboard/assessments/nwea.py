from wf_core_data_dashboard import core
import nwea_utils
import pandas as pd
import inflection
import urllib.parse
import os


def generate_nwea_table_data(
    test_events_path,
    student_info_path,
    student_assignments_path
):
    test_events = pd.read_pickle(test_events_path)
    student_info = pd.read_pickle(student_info_path)
    student_assignments = pd.read_pickle(student_assignments_path)
    students = nwea_utils.summarize_by_student(
        test_events=test_events,
        student_info=student_info,
        student_assignments=student_assignments
    )
    groups = nwea_utils.summarize_by_group(
        students=students,
        grouping_variables=[
            'school_year',
            'school',
            'subject',
            'course'
        ]
    )
    return students, groups


def groups_page_html(
    groups,
    school_year=None,
    school=None,
    subject=None,
    course=None,
    title=None,
    subtitle=None,
    include_details_link=True
):
    if title is None:
        title = 'NWEA results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                school,
                subject,
                course
            ]
        ))
    table_html = groups_table_html(
        groups,
        school_year=school_year,
        school=school,
        subject=subject,
        course=course,
        include_details_link=include_details_link
    )
    template = core.get_template("groups_table.html")
    return template.render(
       title=title,
       subtitle=subtitle,
       table_html=table_html
   )


def students_page_html(
    students,
    school_year=None,
    school=None,
    subject=None,
    course=None,
    title=None,
    subtitle=None
):
    if title is None:
        title = 'NWEA results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                school,
                subject,
                course
            ]
        ))
    table_html = students_table_html(
        students=students,
        school_year=school_year,
        school=school,
        subject=subject,
        course=course
    )
    template = core.get_template("students_table.html")
    return template.render(
       title=title,
       subtitle=subtitle,
       table_html=table_html
   )


def groups_table_html(
    groups,
    school_year=None,
    school=None,
    subject=None,
    course=None,
    include_details_link=True
):
    groups = groups.copy()
    groups['mean_rit_score_growth'] = groups['mean_rit_score_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth'] = groups['mean_percentile_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups = groups.reindex(columns=[
        'num_test_results',
        'num_valid_rit_score_growth',
        'mean_rit_score_growth',
        'num_valid_percentile_growth',
        'mean_percentile_growth'
    ])
    groups.columns = [
        ['Test results', 'RIT score growth', 'RIT score growth',
            'Percentile growth', 'Percentile growth'],
        ['N', 'N', 'Avg growth',
            'N', 'Avg growth']
    ]
    index_names = list(groups.index.names)
    groups.index.names = ['School year', 'School', 'Subject', 'Course']
    group_dict = dict()
    if school_year is not None:
        groups = groups.xs(school_year, level='School year')
        index_names.remove('school_year')
    if school is not None:
        groups = groups.xs(school, level='School')
        index_names.remove('school')
    if subject is not None:
        groups = groups.xs(subject, level='Subject')
        index_names.remove('subject')
    if course is not None:
        groups = groups.xs(course, level='Course')
        index_names.remove('course')
    if include_details_link:
        groups[('', '')] = groups.apply(
            lambda row: generate_students_table_link(
                row=row,
                index_columns=index_names,
                school_year=school_year,
                school=school,
                subject=subject,
                course=course
            ),
            axis=1
        )
    table_html = groups.to_html(
        table_id='results',
        classes=[
            'table',
            'table-striped',
            'table-hover',
            'table-sm'
        ],
        bold_rows=False,
        na_rep='',
        escape=False
    )
    return table_html

def generate_students_table_link(
    row,
    index_columns,
    school_year=None,
    school=None,
    subject=None,
    course=None,
    link_content='Details'
):
    query_dict = dict()
    if school_year is not None:
        query_dict['school_year']= school_year
    if school is not None:
        query_dict['school']= school
    if subject is not None:
        query_dict['subject']= subject
    if course is not None:
        query_dict['course']= course
    for index, column_name in enumerate(index_columns):
        query_dict[column_name]  = row.name[index]
    url = '/nwea/students/?{}'.format(urllib.parse.urlencode(query_dict))
    link_html = '<a href=\"{}\">{}</a>'.format(
        url,
        link_content
    )
    return link_html

def students_table_html(
    students,
    school_year=None,
    school=None,
    subject=None,
    course=None,
    title=None,
    subtitle=None
):
    students = students.copy()
    students = (
        students
        .reset_index()
        .set_index([
            'school_year',
            'school',
            'subject',
            'course',
            'student_id_nwea'
        ])
        .sort_index()
    )
    students['rit_score_fall'] = students['rit_score_fall'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['rit_score_winter'] = students['rit_score_winter'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['rit_score_spring'] = students['rit_score_spring'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_fall'] = students['percentile_fall'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_winter'] = students['percentile_winter'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_spring'] = students['percentile_spring'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students = students.reindex(columns=[
        'first_name',
        'last_name',
        'rit_score_fall',
        'rit_score_winter',
        'rit_score_spring',
        'rit_score_growth',
        'percentile_fall',
        'percentile_winter',
        'percentile_spring',
        'percentile_growth'
    ])
    students.columns = [
        ['Name', 'Name', 'RIT score', 'RIT score', 'RIT score', 'RIT score',
        'Percentile', 'Percentile', 'Percentile', 'Percentile'],
        ['First', 'Last', 'Fall', 'Winter', 'Spring', 'Growth',
        'Fall', 'Winter', 'Spring', 'Growth']
    ]
    students.index.names = [
        'School year',
        'School',
        'Subject',
        'Course',
        'ID']
    if school_year is not None:
        students = students.xs(school_year, level='School year')
    if school is not None:
        students = students.xs(school, level='School')
    if subject is not None:
        students = students.xs(subject, level='Subject')
    if course is not None:
        students = students.xs(course, level='Course')
    table_html = students.to_html(
        table_id='results',
        classes=[
            'table',
            'table-striped',
            'table-hover',
            'table-sm'
        ],
        bold_rows=False,
        na_rep=''
    )
    return table_html