from google.cloud import resourcemanager_v3
from googleapiclient import discovery

def move_folder_projects(source_org_id, source_folder_id, dest_org_id, dest_folder_id):
    """Moves projects from a folder in one GCP organization to another."""

    # Initialize clients
    rm_client = resourcemanager_v3.ProjectsClient()
    service = discovery.build('cloudresourcemanager', 'v3')

    # Fetch projects within the source folder
    request = service.projects().list(parent=f"folders/{source_folder_id}")
    response = request.execute()

    project_ids = [item['projectId'] for item in response.get('projects', [])]

    # Ensure destination folder exists
    try:
        service.folders().get(name=f"folders/{dest_folder_id}").execute()
    except:
        print(f"Destination folder not found in organization {dest_org_id}. Please create it first.")
        return

    # Move projects to the destination folder
    for project_id in project_ids:
        project_name = f"projects/{project_id}"

        # Check current organization
        project = rm_client.get_project(name=project_name)
        if project.parent.type != "folder" or not project.parent.id == source_folder_id:
            print(f"Project {project_id} is not in source folder. Skipping...")
            continue

        # Move the project
        move_request = resourcemanager_v3.MoveProjectRequest(
            name=project_name,
            destination_parent=f"folders/{dest_folder_id}"
        )

        try:
            operation = rm_client.move_project(request=move_request)
            operation.result()  # Wait for the operation to complete
            print(f"Moved project {project_id} successfully!")
        except Exception as e:
            print(f"Error moving project {project_id}: {e}")


if __name__ == "__main__":
    source_org_id = "X"  
    source_folder_id = "X" 
    dest_org_id = "X"       
    dest_folder_id = "X" 

    move_folder_projects(source_org_id, source_folder_id, dest_org_id, dest_folder_id)
