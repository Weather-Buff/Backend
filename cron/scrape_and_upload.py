import csv
import io
from datetime import datetime
from scrape import scrape

from github import Github
from github.InputGitTreeElement import InputGitTreeElement

import cron.utils as utils

# Create a timestamp for the CSV file
running_at = datetime.now()
csv_name = f"facilities_{running_at.strftime('%Y%m%d_%H%M%S')}.csv"

# Scrape the facilities data
facilities = scrape()

# Write CSV content to an in-memory string buffer
csv_buffer = io.StringIO()
writer = csv.DictWriter(csv_buffer, fieldnames=facilities[0].to_dict().keys())
writer.writeheader()
writer.writerows(facility.to_dict() for facility in facilities)

# Get the CSV content as a string (plain content)
csv_content = csv_buffer.getvalue()

# GitHub operations
github_jwt = utils.get_github_key()
access_token = utils.get_installation_access_token(github_jwt)

# Authenticate to GitHub
github = Github(access_token)
repository = github.get_repo("Weather-Buff/Backend")

# Get the reference to the "data" branch
ref = repository.get_git_ref("heads/data")
latest_commit = repository.get_git_commit(ref.object.sha)

# Get the latest tree from the latest commit (to retain previous CSVs)
latest_tree = repository.get_git_tree(sha=latest_commit.sha, recursive=True)

# Create a new blob for the new CSV content (plain text)
blob = repository.create_git_blob(csv_content, "utf-8")

# Prepare a list of tree elements, starting with the current files
tree_elements = []
for file in latest_tree.tree:
    # Retain the current files by adding them to the tree, except if it's the new file
    if file.path != csv_name:
        tree_elements.append(InputGitTreeElement(path=file.path, mode="100644", type="blob", sha=file.sha))

# Add the new CSV to the tree
tree_elements.append(InputGitTreeElement(path=csv_name, mode="100644", type="blob", sha=blob.sha))

# Create a new tree with the previous files and the new CSV
new_tree = repository.create_git_tree(tree_elements)

# Create a new commit with the new tree
commit_message = f"Update Rec Facilities at {running_at.strftime('%m/%d/%Y, %H:%M:%S')}"
new_commit = repository.create_git_commit(commit_message, new_tree, [latest_commit])

# Update the branch reference to point to the new commit
ref.edit(new_commit.sha)

print(f"Successfully uploaded {csv_name} to the data branch and retained previous CSVs.")
