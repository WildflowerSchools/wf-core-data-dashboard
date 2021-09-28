from wf_core_data_dashboard import core
import wf_core_data
import pandas as pd
import os


def generate_fastbridge_table_data(
    test_events_path,
    student_info_path
):
    test_events = pd.read_pickle(test_events_path)
    student_info = pd.read_pickle(student_info_path)
    students_tests = wf_core_data.summarize_by_student_test_school_year(
        test_events=test_events,
        student_info=student_info
    )
    student_groups = wf_core_data.summarize_by_student_group(
        students_tests=students_tests
    )
    return students_tests, student_groups


def student_groups_page_html(
    student_groups,
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
    table_html = student_groups_table_html(
        student_groups,
        school_year=school_year,
        school=school,
        test=test,
        subtest=subtest
    )
    template = core.get_template("student_groups_table.html")
    return template.render(
       title=title,
       subtitle=subtitle,
       table_html=table_html
   )


def students_tests_page_html(
    students_tests,
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
    table_html = students_tests_table_html(
        students_tests=students_tests,
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


def student_groups_table_html(
    student_groups,
    school_year=None,
    school=None,
    test=None,
    subtest=None
):
    student_groups = student_groups.copy()
    student_groups['frac_met_growth_goal'] = student_groups['frac_met_growth_goal'].apply(
        lambda x: '{:.0f}%'.format(round(100 * x))
    )
    student_groups['frac_met_attainment_goal'] = student_groups['frac_met_attainment_goal'].apply(
        lambda x: '{:.0f}%'.format(100 * x)
    )
    student_groups['frac_met_goal'] = student_groups['frac_met_goal'].apply(
        lambda x: '{:.0f}%'.format(100 * x)
    )
    student_groups['mean_percentile_growth'] = student_groups['mean_percentile_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    student_groups = student_groups.reindex(columns=[
        'num_valid_test_results',
        'frac_met_growth_goal',
        'frac_met_attainment_goal',
        'frac_met_goal',
        'num_valid_percentile_growth',
        'mean_percentile_growth'
    ])
    student_groups.columns = [
        ['Goals', 'Goals', 'Goals', 'Goals',
            'Percentile growth', 'Percentile growth'],
        ['N', 'Met growth goal', 'Met attainment goal',
            'Met goal', 'N', 'Percentile growth']
    ]
    student_groups.index.names = ['School year', 'School', 'Test', 'Subtest']
    if school_year is not None:
        student_groups = student_groups.xs(school_year, level='School year')
    if school is not None:
        student_groups = student_groups.xs(school, level='School')
    if test is not None:
        student_groups = student_groups.xs(test, level='Test')
    if subtest is not None:
        student_groups = student_groups.xs(subtest, level='Subtest')
    table_html = student_groups.to_html(
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


def students_tests_table_html(
    students_tests,
    school_year=None,
    school=None,
    test=None,
    subtest=None,
    title=None,
    subtitle=None
):
    students_tests = students_tests.copy()
    students_tests = (
        students_tests
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
    students_tests['risk_level_fall'] = students_tests['risk_level_fall'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students_tests['risk_level_winter'] = students_tests['risk_level_winter'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students_tests['risk_level_spring'] = students_tests['risk_level_spring'].replace({
        'lowRisk': 'Low',
        'someRisk': 'Some',
        'highRisk': 'High'
    })
    students_tests['met_growth_goal'] = students_tests['met_growth_goal'].replace({
        False: 'N',
        True: 'Y'
    })
    students_tests['met_attainment_goal'] = students_tests['met_attainment_goal'].replace({
        False: 'N',
        True: 'Y'
    })
    students_tests['met_goal'] = students_tests['met_goal'].replace({
        False: 'N',
        True: 'Y'
    })
    students_tests['percentile_fall'] = students_tests['percentile_fall'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students_tests['percentile_winter'] = students_tests['percentile_winter'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students_tests['percentile_spring'] = students_tests['percentile_spring'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students_tests = students_tests.reindex(columns=[
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
    students_tests.columns = [
        ['Risk level', 'Risk level', 'Risk level', 'Met goal?', 'Met goal?',
            'Met goal?', 'Percentile', 'Percentile', 'Percentile', 'Percentile'],
        ['Fall', 'Winter', 'Spring', 'Growth', 'Attainment',
            'Overall', 'Fall', 'Winter', 'Spring', 'Growth']
    ]
    students_tests.index.names = [
        'School year',
        'School',
        'Test',
        'Subtest',
        'FAST ID']
    if school_year is not None:
        students_tests = students_tests.xs(school_year, level='School year')
    if school is not None:
        students_tests = students_tests.xs(school, level='School')
    if test is not None:
        students_tests = students_tests.xs(test, level='Test')
    if subtest is not None:
        students_tests = students_tests.xs(subtest, level='Subtest')
    table_html = students_tests.to_html(
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
