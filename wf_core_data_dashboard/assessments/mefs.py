from wf_core_data_dashboard import core
import wf_core_data
import mefs_utils
import pandas as pd
import inflection
import urllib.parse
import os


def generate_mefs_table_data(
    test_events_path,
    student_info_path,
    student_assignments_path
):
    test_events = pd.read_pickle(test_events_path)
    student_info = pd.read_pickle(student_info_path)
    student_assignments = pd.read_pickle(student_assignments_path)
    students = mefs_utils.summarize_by_student(
        test_events=test_events,
        student_info=student_info,
        student_assignments=student_assignments
    )
    groups = mefs_utils.summarize_by_group(
        students=students,
        grouping_variables=[
            'school_year',
            'group_name_mefs'
        ]
    )
    return students, groups


def groups_page_html(
    groups,
    school_year=None,
    group_name_mefs=None,
    title=None,
    subtitle=None,
    include_details_link=True
):
    if title is None:
        title = 'MEFS results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                group_name_mefs
            ]
        )).replace('/', ':')
    table_html = groups_table_html(
        groups,
        school_year=school_year,
        group_name_mefs=group_name_mefs,
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
    group_name_mefs=None,
    title=None,
    subtitle=None
):
    if title is None:
        title = 'MEFS results'
    if subtitle is None:
        subtitle = ':'.join(filter(
            lambda x: x is not None,
            [
                school_year,
                group_name_mefs
            ]
        )).replace('/', ':')
    table_html = students_table_html(
        students=students,
        school_year=school_year,
        group_name_mefs=group_name_mefs
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
    group_name_mefs=None,
    include_details_link=True
):
    groups = groups.copy()
    groups['mean_ending_percentile'] = groups['mean_ending_percentile'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_total_score_growth'] = groups['mean_total_score_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth'] = groups['mean_percentile_growth'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups = groups.reindex(columns=[
        'num_valid_ending_percentile',
        'mean_ending_percentile',
        'num_valid_total_score_growth',
        'mean_total_score_growth',
        'num_valid_percentile_growth',
        'mean_percentile_growth'
    ])
    groups.columns = [
        [
            'Percentile', 'Percentile',
            'Total score growth', 'Total score growth',
            'Percentile growth', 'Percentile growth'
        ],
        [
            'N', 'Avg',
            'N', 'Avg',
            'N', 'Avg'
        ]
    ]
    index_names = list(groups.index.names)
    groups.index.names = ['School year', 'School/classroom']
    group_dict = dict()
    if school_year is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=school_year,
            level='School year'
        )
        index_names.remove('school_year')
    if group_name_mefs is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=group_name_mefs,
            level='School/classroom'
        )
        index_names.remove('group_name_mefs')
    if include_details_link:
        groups[('', '')] = groups.apply(
            lambda row: generate_students_table_link(
                row=row,
                index_columns=index_names,
                school_year=school_year,
                group_name_mefs=group_name_mefs
            ),
            axis=1
        )
    index=True
    if len(groups) < 2:
        index=False
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
    group_name_mefs=None,
    link_content='Details'
):
    query_dict = dict()
    if school_year is not None:
        query_dict['school_year']= school_year
    if group_name_mefs is not None:
        query_dict['group_name_mefs']= group_name_mefs
    for index, column_name in enumerate(index_columns):
        query_dict[column_name]  = row.name[index]
    url = '/mefs/students/?{}'.format(urllib.parse.urlencode(query_dict))
    link_html = '<a href=\"{}\">{}</a>'.format(
        url,
        link_content
    )
    return link_html

def students_table_html(
    students,
    school_year=None,
    group_name_mefs=None,
    title=None,
    subtitle=None
):
    students = students.copy()
    students = (
        students
        .reset_index()
        .set_index([
            'school_year',
            'group_name_mefs',
            'rs_id'
        ])
        .sort_index()
    )
    students['total_score_starting_date'] = students['total_score_starting_date'].apply(
        lambda x: x.strftime('%m/%d/%Y') if not pd.isna(x) else ''
    )
    students['total_score_ending_date'] = students['total_score_ending_date'].apply(
        lambda x: x.strftime('%m/%d/%Y') if not pd.isna(x) else ''
    )
    students['starting_total_score'] = students['starting_total_score'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['ending_total_score'] = students['ending_total_score'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_starting_date'] = students['percentile_starting_date'].apply(
        lambda x: x.strftime('%m/%d/%Y') if not pd.isna(x) else ''
    )
    students['percentile_ending_date'] = students['percentile_ending_date'].apply(
        lambda x: x.strftime('%m/%d/%Y') if not pd.isna(x) else ''
    )
    students['starting_percentile'] = students['starting_percentile'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['ending_percentile'] = students['ending_percentile'].apply(
        lambda x: '{:.0f}'.format(x) if not pd.isna(x) else ''
    )
    students = students.reindex(columns=[
        'first_name',
        'last_name',
        'total_score_starting_date',
        'total_score_ending_date',
        'starting_total_score',
        'ending_total_score',
        'total_score_growth',
        'percentile_starting_date',
        'percentile_ending_date',
        'starting_percentile',
        'ending_percentile',
        'percentile_growth',
    ])
    students.columns = [
        [
            'Name', 'Name',
            'Total score', 'Total score', 'Total score', 'Total score', 'Total score',
            'Percentile', 'Percentile', 'Percentile', 'Percentile', 'Percentile'
        ],
        [
            'First', 'Last',
            'Start date', 'End date', 'Starting', 'Ending', 'Growth',
            'Start date', 'End date', 'Starting', 'Ending', 'Growth'
        ]
    ]
    students.index.names = [
        'School year',
        'School/classroom',
        'ID']
    if school_year is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=school_year,
            level='School year'
        )
    if group_name_mefs is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=group_name_mefs,
            level='School/classroom'
        )
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
