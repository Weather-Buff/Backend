import base64
from datetime import datetime, timedelta
from github import Github, InputGitTreeElement
import cron.utils as utils

file_prefix = "facilities_"
aggregated_file_name = f"facilities_aggregated_{datetime.now().strftime('%Y_%U')}.csv"

# GitHub authentication
github_jwt = utils.get_github_key()
access_token = utils.get_installation_access_token(github_jwt)
github = Github(access_token)
repository = github.get_repo("Weather-Buff/Backend")

# Get reference and latest commit
ref = repository.get_git_ref("heads/data")
latest_commit = repository.get_git_commit(ref.object.sha)

# Calculate the date one week ago
since_date = datetime.now() - timedelta(days=7)

# Retrieve commits from the last week
commits = repository.get_commits(since=since_date)

# Collect files and aggregate content
file_contents = []
files_to_delete = []

for commit in commits:
    for file in commit.files:
        if file.filename.startswith(file_prefix):
            blob = repository.get_git_blob(file.sha)
            file_data = base64.b64decode(blob.content).decode('utf-8').splitlines()

            if not file_contents:
                # Include header from the first file only
                file_contents.append(file_data)
            else:
                # Exclude the header from subsequent files
                file_contents.append(file_data[1:])

            files_to_delete.append(file.filename)

# Flatten the list of lines and join them into the aggregated content
aggregated_content = '\n'.join(line for lines in file_contents for line in lines)

# Prepare new blob for the aggregated file
aggregated_blob = repository.create_git_blob(
    base64.b64encode(aggregated_content.encode('utf-8')).decode(), "utf-8"
)
tree_elements = [
    InputGitTreeElement(path=aggregated_file_name, mode="100644", type="blob", sha=aggregated_blob.sha)
]

# Add delete operations for the old files
tree_elements += [InputGitTreeElement(path=file_name, mode="100644", type="blob", sha=None) for file_name in files_to_delete]

# Create the new tree, commit, and update ref
new_tree = repository.create_git_tree(tree_elements, latest_commit.tree)
new_commit = repository.create_git_commit(
    f"Aggregate files from the last week into {aggregated_file_name} and delete originals.",
    new_tree,
    [latest_commit]
)
ref.edit(new_commit.sha)
