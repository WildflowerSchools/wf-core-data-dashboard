fmt-python:
    autopep8 --aggressive --recursive --in-place ./wf_core_data_dashboard/

lint-app:
    @pylint wf_core_data_dashboard

start-app: lint-app
    @uvicorn wf_core_data_dashboard.app:app --reload  --port 8000

