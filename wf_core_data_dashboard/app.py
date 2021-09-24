from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

from wf_core_data_dashboard import routes


app = FastAPI()

# this may not be needed.
# origins = [
#     "http://localhost:3000",
#     "https://dashboard.api.wildflower-tech.org",
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

app.include_router(routes.router)
