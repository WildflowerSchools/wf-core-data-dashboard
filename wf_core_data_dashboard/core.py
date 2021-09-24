from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader("wf_core_data_dashboard", "templates"),
    autoescape=select_autoescape()
)


def get_template(name):
    return env.get_template(name)


def single_table_page_html(
    title,
    subtitle,
    table_html
):
    page_html = HTML_TEMPLATE_SINGLE_TABLE.format(
        title=title,
        subtitle=subtitle,
        table_html=table_html
    )
    return page_html
