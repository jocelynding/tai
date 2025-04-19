from app.api.v1.endpoints import completions, courses, file_completions, files
from fastapi import APIRouter

router = APIRouter()

router.include_router(
    file_completions.router,
    prefix="/files/{fileId}/completions",
    tags=["file completions"],
)

router.include_router(completions.router, prefix="/completions", tags=["completions"])

router.include_router(courses.router, prefix="/courses", tags=["courses"])

router.include_router(files.router, prefix="/files", tags=["files"])

# TODO: Implement summarization
# router.include_router(
#     summarization.router,
#     prefix="/summarization",
#     tags=["summarization"]
# )
