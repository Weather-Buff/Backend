import base64
import csv
import io
from datetime import datetime
from scrape import scrape

from github import Github
from github.InputGitTreeElement import InputGitTreeElement

import cron.utils as utils

running_at = datetime.now()
csv_name = f"facilities_{running_at.strftime('%Y%m%d_%H%M%S')}.csv"
facilities = scrape()

# Write CSV content to an in-memory string buffer
csv_buffer = io.StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=facilities[0].to_dict().keys())
writer.writeheader()
writer.writerows(facility.to_dict() for facility in facilities)

# Get the CSV content as a string and encode it
csv_content = csv_buffer.getvalue().encode('utf-8')
encoded_content = base64.b64encode(csv_content).decode()

# GitHub operations
github_jwt = utils.get_github_key()
access_token = utils.get_installation_access_token(github_jwt)

github = Github(access_token)
repository = github.get_repo("Weather-Buff/Backend")
ref = repository.get_git_ref("heads/data")
latest_commit = repository.get_git_commit(ref.object.sha)

# Create the blob and commit
blob = repository.create_git_blob(encoded_content, "utf-8")
tree_element = InputGitTreeElement(path=csv_name, mode="100644", type="blob", sha=blob.sha)
tree = repository.create_git_tree([tree_element], latest_commit.tree)

commit = repository.create_git_commit(
    f"Update Rec Facilities at {running_at.strftime('%m/%d/%Y, %H:%M:%S')}",
    tree,
    [latest_commit]
)

ref.edit(commit.sha)