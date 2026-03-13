from studio_core.core.config import resolve_storage_path

def get_project_output_folder(project_id):
    path = resolve_storage_path("exports", project_id)
    path.mkdir(parents=True, exist_ok=True)
    return str(path)
