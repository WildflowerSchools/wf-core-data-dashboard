from wf_core_data_dashboard import core
import wf_core_data
import pandas as pd
import inflection
import urllib.parse
import os


def generate_fastbridge_table_data(
    test_events_path,
    student_info_path
):
    test_events = pd.read_pickle(test_events_path)
    student_info = pd.read_pickle(student_info_path)
    students = wf_core_data.summarize_by_student(
        test_events=test_events,
        student_info=student_info
    )
    groups = wf_core_data.summarize_by_group(
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
    groups['mean_percentile_growth'] = groups['mean_percentile_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups = groups.reindex(columns=[
        'num_valid_test_results',
        'frac_met_growth_goal',
        'frac_met_attainment_goal',
        'frac_met_goal',
        'num_valid_percentile_growth',
        'mean_percentile_growth'
    ])
    groups.columns = [
        ['Goals', 'Goals', 'Goals', 'Goals',
            'Percentile growth', 'Percentile growth'],
        ['N', 'Met growth goal', 'Met attainment goal',
            'Met goal', 'N', 'Percentile growth']
    ]
    index_names = list(groups.index.names)
    groups.index.names = ['School year', 'School', 'Test', 'Subtest']
    group_dict = dict()
    if school_year is not None:
        groups = groups.xs(school_year, level='School year')
        index_names.remove('school_year')
    if school is not None:
        groups = groups.xs(school, level='School')
        index_names.remove('school')
    if test is not None:
        groups = groups.xs(test, level='Test')
        index_names.remove('test')
    if subtest is not None:
        groups = groups.xs(subtest, level='Subtest')
        index_names.remove('subtest')
    if include_details_link:
        groups[('', '')] = groups.apply(
            lambda row: generate_students_table_link(
                row=row,
                index_columns=index_names,
                school_year=school_year,
                school=school,
                test=test,
                subtest=subtest
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
    for index, column_name in enumerate(index_columns):
        query_dict[column_name]  = row.name[index]
    url = '/students/?{}'.format(urllib.parse.urlencode(query_dict))
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
        ['Name', 'Name', 'Risk level', 'Risk level', 'Risk level', 'Met goal?', 'Met goal?',
            'Met goal?', 'Percentile', 'Percentile', 'Percentile', 'Percentile'],
        ['First', 'Last', 'Fall', 'Winter', 'Spring', 'Growth', 'Attainment',
            'Overall', 'Fall', 'Winter', 'Spring', 'Growth']
    ]
    students.index.names = [
        'School year',
        'School',
        'Test',
        'Subtest',
        'FAST ID']
    if school_year is not None:
        students = students.xs(school_year, level='School year')
    if school is not None:
        students = students.xs(school, level='School')
    if test is not None:
        students = students.xs(test, level='Test')
    if subtest is not None:
        students = students.xs(subtest, level='Subtest')
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
