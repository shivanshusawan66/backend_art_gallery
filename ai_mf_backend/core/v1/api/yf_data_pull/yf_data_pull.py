from fastapi import APIRouter
from ai_mf_backend.core.v1.tasks.yf_data_pull.yf_main import Command

router = APIRouter()


@router.get("/Yahoo_finance_pull_data")
def run_command():
    command = Command()  # Initialize the Django command
    command.handle()  # Call the handle() method to execute the command

    return {"message": "Command executed successfully!"}
