from jinja2 import Environment, PackageLoader, select_autoescape


env = Environment(
    loader=PackageLoader("wf_core_data_dashboard", "templates"),
    autoescape=select_autoescape()
)


def get_template(name):
    return env.get_template(name)
