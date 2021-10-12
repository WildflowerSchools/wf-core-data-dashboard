from wf_core_data_dashboard import core
import fastbridge_utils
import wf_core_data
import pandas as pd
import inflection
import urllib.parse
import os

def generate_fastbridge_table_data(
    test_events_path,
    student_info_path,
    student_assignments_path
):
    test_events = pd.read_pickle(test_events_path)
    student_info = pd.read_pickle(student_info_path)
    student_assignments = pd.read_pickle(student_assignments_path)
    students = fastbridge_utils.summarize_by_student(
        test_events=test_events,
        student_info=student_info,
        student_assignments=student_assignments
    )
    groups = fastbridge_utils.summarize_by_group(
        students=students
    )
    return students, groups


def groups_page_html(
    groups,
    school_year=None,
    school=None,
    test=None,
    subtest=None,
    title=None,
    subtitle=None,
    include_details_link=True
):
    if title is None:
        title = 'FastBridge results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                school,
                test,
                subtest
            ]
        ))
    table_html = groups_table_html(
        groups,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest,
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
    test=None,
    subtest=None,
    title=None,
    subtitle=None
):
    if title is None:
        title = 'FastBridge results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                school,
                test,
                subtest
            ]
        ))
    table_html = students_table_html(
        students=students,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
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
    test=None,
    subtest=None,
    include_details_link=True
):
    groups = groups.copy()
    groups['frac_met_growth_goal'] = groups['frac_met_growth_goal'].apply(
        lambda x: '{:.0f}%'.format(round(100 * x))
    )
    groups['frac_met_attainment_goal'] = groups['frac_met_attainment_goal'].apply(
        lambda x: '{:.0f}%'.format(100 * x)
    )
    groups['frac_met_goal'] = groups['frac_met_goal'].apply(
        lambda x: '{:.0f}%'.format(100 * x)
    )
    groups['mean_ending_percentile'] = groups['mean_ending_percentile'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth'] = groups['mean_percentile_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups = groups.reindex(columns=[
        'num_valid_goal_info',
        'frac_met_growth_goal',
        'frac_met_attainment_goal',
        'frac_met_goal',
        'num_valid_ending_percentile',
        'mean_ending_percentile',
        'num_valid_percentile_growth',
        'mean_percentile_growth'
    ])
    groups.columns = [
        [
            'Goals', 'Goals', 'Goals', 'Goals',
            'Percentile', 'Percentile',
            'Percentile growth', 'Percentile growth'
        ],
        [
            'N', 'Met growth goal', 'Met attainment goal', 'Met goal',
            'N', 'Avg',
            'N', 'Avg'
        ]
    ]
    group_dict = dict()
    if school_year is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=school_year,
            level='school_year'
        )
    if school is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=school,
            level='school'
        )
    if test is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=test,
            level='test'
        )
    if subtest is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=subtest,
            level='subtest'
        )
    if include_details_link:
        groups[('', '')] = groups.apply(
            lambda row: generate_students_table_link(
                row=row,
                index_columns=groups.index.names,
                school_year=school_year,
                school=school,
                test=test,
                subtest=subtest
            ),
            axis=1
        )
    if len(groups) < 2:
        index=False
    else:
        index=True
        index_name_mapper_all = {
            'school_year': 'School year',
            'school': 'School',
            'test': 'Test',
            'subtest': 'Subtest'
        }
        index_name_mapper = {old_name: new_name for old_name, new_name in index_name_mapper_all.items() if old_name in groups.index.names}
        groups = groups.rename_axis(index=index_name_mapper)
    table_html = groups.to_html(
        table_id='results',
        classes=[
            'table',
            'table-striped',
            'table-hover',
            'table-sm'
        ],
        index=index,
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
    test=None,
    subtest=None,
    link_content='Details'
):
    query_dict = dict()
    if school_year is not None:
        query_dict['school_year']= school_year
    if school is not None:
        query_dict['school']= school
    if test is not None:
        query_dict['test']= test
    if subtest is not None:
        query_dict['subtest']= subtest
    if len(index_columns) == 1:
        query_dict[index_columns[0]] = row.name
    if len(index_columns) > 1:
        for column_position, column_name in enumerate(index_columns):
            query_dict[column_name]  = row.name[column_position]
    url = '/fastbridge/students/?{}'.format(urllib.parse.urlencode(query_dict))
    link_html = '<a href=\"{}\">{}</a>'.format(
        url,
        link_content
    )
    return link_html

def students_table_html(
    students,
    school_year=None,
    school=None,
    test=None,
    subtest=None,
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
            'test',
            'subtest',
            'fast_id'
        ])
        .sort_index()
    )
    students['risk_level_fall'] = students['risk_level_fall'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students['risk_level_winter'] = students['risk_level_winter'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students['risk_level_spring'] = students['risk_level_spring'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students['met_growth_goal'] = students['met_growth_goal'].replace({
        False: 'N',
        True: 'Y'
    })
    students['met_attainment_goal'] = students['met_attainment_goal'].replace({
        False: 'N',
        True: 'Y'
    })
    students['met_goal'] = students['met_goal'].replace({
        False: 'N',
        True: 'Y'
    })
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
        'risk_level_fall',
        'risk_level_winter',
        'risk_level_spring',
        'met_growth_goal',
        'met_attainment_goal',
        'met_goal',
        'percentile_fall',
        'percentile_winter',
        'percentile_spring',
        'percentile_growth'
    ])
    students.columns = [
        [
            'Name', 'Name',
            'Risk level', 'Risk level', 'Risk level',
            'Met goal?', 'Met goal?', 'Met goal?',
            'Percentile', 'Percentile', 'Percentile', 'Percentile'
        ],
        [
            'First', 'Last',
            'Fall', 'Winter', 'Spring',
            'Growth', 'Attainment', 'Overall',
            'Fall', 'Winter', 'Spring', 'Growth'
        ]
    ]
    if school_year is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=school_year,
            level='school_year'
        )
    if school is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=school,
            level='school'
        )
    if test is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=test,
            level='test'
        )
    if subtest is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=subtest,
            level='subtest'
        )
    index_name_mapper_all = {
        'school_year': 'School year',
        'school': 'School',
        'test': 'Test',
        'subtest': 'Subtest',
        'fast_id': 'FAST ID'
    }
    index_name_mapper = {old_name: new_name for old_name, new_name in index_name_mapper_all.items() if old_name in students.index.names}
    students = students.rename_axis(index=index_name_mapper)
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
