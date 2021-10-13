from wf_core_data_dashboard import core
import wf_core_data
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
    groups['mean_rit_score_growth_range'] = groups.apply(
        lambda row: '{:+.1f} - {:+.1f}'.format(
            row['mean_rit_score_growth'] - row['mean_rit_score_growth_se'],
            row['mean_rit_score_growth'] + row['mean_rit_score_growth_se'],
        ) if not pd.isna(row['mean_rit_score_growth']) and not  pd.isna(row['mean_rit_score_growth_se']) else '',
        axis=1
    )
    groups['mean_percentile_growth_range'] = groups.apply(
        lambda row: '{:+.1f} - {:+.1f}'.format(
            row['mean_percentile_growth'] - row['mean_percentile_growth_se'],
            row['mean_percentile_growth'] + row['mean_percentile_growth_se'],
        ) if not pd.isna(row['mean_percentile_growth']) and not  pd.isna(row['mean_percentile_growth_se']) else '',
        axis=1
    )
    groups['mean_percentile_growth_per_school_year_range'] = groups.apply(
        lambda row: '{:+.1f} - {:+.1f}'.format(
            row['mean_percentile_growth_per_school_year'] - row['mean_percentile_growth_per_school_year_se'],
            row['mean_percentile_growth_per_school_year'] + row['mean_percentile_growth_per_school_year_se'],
        ) if not pd.isna(row['mean_percentile_growth_per_school_year']) and not  pd.isna(row['mean_percentile_growth_per_school_year_se']) else '',
        axis=1
    )
    groups['mean_ending_percentile'] = groups['mean_ending_percentile'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_ending_percentile_se'] = groups['mean_ending_percentile_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_rit_score_growth'] = groups['mean_rit_score_growth'].apply(
        lambda x: '{:+.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_rit_score_growth_se'] = groups['mean_rit_score_growth_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth'] = groups['mean_percentile_growth'].apply(
        lambda x: '{:+.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth_se'] = groups['mean_percentile_growth_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth_per_school_year'] = groups['mean_percentile_growth_per_school_year'].apply(
        lambda x: '{:+.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups['mean_percentile_growth_per_school_year_se'] = groups['mean_percentile_growth_per_school_year_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    groups = groups.reindex(columns=[
        'num_valid_ending_percentile',
        'mean_ending_percentile',
        'mean_ending_percentile_se',
        'num_valid_rit_score_growth',
        'mean_rit_score_growth',
        'mean_rit_score_growth_se',
        'mean_rit_score_growth_range',
        'num_valid_percentile_growth',
        'mean_percentile_growth',
        'mean_percentile_growth_se',
        'mean_percentile_growth_range',
        'mean_percentile_growth_per_school_year',
        'mean_percentile_growth_per_school_year_se',
        'mean_percentile_growth_per_school_year_range'
    ])
    groups.columns = [
        [
            'Percentile', 'Percentile', 'Percentile',
            'RIT score growth', 'RIT score growth', 'RIT score growth', 'RIT score growth',
            'Percentile growth', 'Percentile growth', 'Percentile growth', 'Percentile growth',
            'Percentile growth per school year', 'Percentile growth per school year', 'Percentile growth per school year'
        ],
        [
            'N', 'Avg', 'SE',
            'N', 'Avg', 'SE', 'Range',
            'N', 'Avg', 'SE', 'Range',
            'Avg', 'SE', 'Range'
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
    if subject is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=subject,
            level='subject'
        )
    if course is not None:
        groups = wf_core_data.select_index_level(
            dataframe=groups,
            value=course,
            level='course'
        )
    if include_details_link:
        groups[('', '')] = groups.apply(
            lambda row: generate_students_table_link(
                row=row,
                index_columns=groups.index.names,
                school_year=school_year,
                school=school,
                subject=subject,
                course=course
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
            'subject': 'Subject',
            'course': 'Course',
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
    if len(index_columns) == 1:
        query_dict[index_columns[0]] = row.name
    if len(index_columns) > 1:
        for column_position, column_name in enumerate(index_columns):
            query_dict[column_name]  = row.name[column_position]
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
    students['rit_score_growth'] = students['rit_score_growth'].apply(
        lambda x: '{:+.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['rit_score_growth_se'] = students['rit_score_growth_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    students['rit_score_growth_per_school_year'] = students['rit_score_growth_per_school_year'].apply(
        lambda x: '{:+.0f}'.format(x) if not pd.isna(x) else ''
    )
    students['rit_score_growth_per_school_year_se'] = students['rit_score_growth_per_school_year_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
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
    students['percentile_growth'] = students['percentile_growth'].apply(
        lambda x: '{:+.1f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_growth_se'] = students['percentile_growth_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_growth_per_school_year'] = students['percentile_growth_per_school_year'].apply(
        lambda x: '{:+.1f}'.format(x) if not pd.isna(x) else ''
    )
    students['percentile_growth_per_school_year_se'] = students['percentile_growth_per_school_year_se'].apply(
        lambda x: '{:.1f}'.format(x) if not pd.isna(x) else ''
    )
    students = students.reindex(columns=[
        'first_name',
        'last_name',
        'rit_score_fall',
        'rit_score_winter',
        'rit_score_spring',
        'rit_score_growth',
        'rit_score_growth_se',
        'rit_score_growth_per_school_year',
        'rit_score_growth_per_school_year_se',
        'percentile_fall',
        'percentile_winter',
        'percentile_spring',
        'percentile_growth',
        'percentile_growth_se',
        'percentile_growth_per_school_year',
        'percentile_growth_per_school_year_se'
    ])
    students.columns = [
        [
            'Name', 'Name',
            'RIT score', 'RIT score', 'RIT score', 'RIT score', 'RIT score', 'RIT score', 'RIT score',
            'Percentile', 'Percentile', 'Percentile', 'Percentile', 'Percentile', 'Percentile', 'Percentile'
        ],
        [
            'First', 'Last',
            'Fall', 'Winter', 'Spring', 'Growth', 'SE', 'Growth per school year', 'SE',
            'Fall', 'Winter', 'Spring', 'Growth', 'SE', 'Growth per school year', 'SE'
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
    if subject is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=subject,
            level='subject'
        )
    if course is not None:
        students = wf_core_data.select_index_level(
            dataframe=students,
            value=course,
            level='course'
        )
    index_name_mapper_all = {
        'school_year': 'School year',
        'school': 'School',
        'subject': 'Subject',
        'course': 'Course',
        'student_id_nwea': 'ID'
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
