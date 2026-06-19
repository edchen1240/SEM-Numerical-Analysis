====================
Notes on Git
====================


# Initializing a Git Locally
How to initialize a Git repository locally, and sync to GitHub.

First, create a new repository on GitHub webpage. Do not add a README, .gitignore, or license file, since we will be importing an existing project, and this will cause a merge conflict.

Then use the following commands in your terminal to initialize a Git repository, commit your files, and push to GitHub:

```
git init
git add .
git commit -m "Initial commit: import current MIT Athena website"
git branch -M main
git remote add origin git@github.com:edchen1240/mit-athena-online-cv-edchen93.git
git push -u origin main
```

Here's a breakdown of each command:

0. Create a new repository on GitHub webpage. Do not add a README, .gitignore, or license file, since we will be importing an existing project, and this will cause a merge conflict.
1. Use "git init" to initialize a Git repository in the current directory.
2. Use "git add ." to stage all files for commit.
3. Use "git commit -m 'Initial commit: import current MIT Athena website'" to commit the staged files with a message.
4. Use "git branch -M main" to rename the default branch to "main". To check, type "git status"and you will see "(HEAD -> master)" change to "(HEAD -> main)".
5. Use "git remote add origin git@github.


## Special Case: If GitHub Repo is Not Empty
Note: If there are already files in the GitHub repository (for example, a README.md created during repo setup), the remote repository is no longer empty. In that case, your first \`git push -u origin main\` may be rejected because GitHub already has a different commit history.  

After **step 4**, use the following commands to connect your local branch to the remote branch, pull the remote content, merge the histories, and then push again:  
  
```
git branch --set-upstream-to=origin/main main
git pull origin main \--allow-unrelated-histories
git add .  
git commit \-m "Merge remote GitHub repo with local website history"
git push \-u origin main
```

Breakdown of each command in routed case:
5. Set the upstream branch.
6. Pull and merge the remote history.
7. If Git asks you to resolve merge conflicts, edit the conflicted files, then run add and commit to complete the merge.
8. Push again.
    



## Git Repo Naming Conventions
- Use lowercase letters and hyphens to separate words (e.g., "athena-website").
- Avoid using spaces, underscores, or special characters in the repository name.
- The typical length of a repository name should be concise and descriptive, ideally between 3 to 50 characters.





# Note


## LF vs CRLF Warning
When you see a warning like this:
```
warning: in the working copy of 'cgi-bin/visit_log.csv', LF will be replaced by CRLF the next time Git touches it.
``` 

There are two newline conventions: LF (Line Feed) and CRLF (Carriage Return + Line Feed). LF is used by Linux, macOS, MIT Athena, and most servers, while CRLF is used by Windows.

The warning means that your file currently has LF, but Git on Windows is configured to convert it to CRLF in your working copy later. This is a common issue when working with cross-platform projects, and it can be resolved by configuring Git to handle line endings appropriately.


















