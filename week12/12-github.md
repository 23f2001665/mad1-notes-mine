# Remote Collaboration with GitHub

As a project grows and more developers contribute to it, it's important to have a way to collaborate effectively. GitHub is a popular platform that provides hosting for Git repositories and offers various features for collaboration, such as pull requests, code reviews, and issue tracking.

In this section, we will learn how to use GitHub to collaborate on a project with other developers. We will cover different workflows/situations that may arise when working with GitHub, such as:

1. **Creating a new repository**: We will learn how to create a new repository on GitHub and set it up for collaboration.
1. **Cloning a repository**: We will learn how to clone an existing repository from GitHub to our local machine so that we can work on it.
1. **Forking a repository**: We will learn how to fork a repository on GitHub, which allows us to create our own copy of the repository that we can work on independently.
1. **Pull requests**: We will learn how to create a pull request on GitHub, which allows us to propose changes to a repository and collaborate with other developers to review and merge those changes.
1. **Code reviews**: We will learn how to conduct code reviews on GitHub to ensure that changes are of high quality and meet the project's standards.
1. **Issue tracking**: We will learn how to use GitHub's issue tracking system to manage bugs, feature requests, and other tasks related to the project.

By the end of this section, you should have a good understanding of how to use GitHub for remote collaboration and be able to effectively work with other developers on a shared codebase.

## Setting up Github in our local system

Before we can start collaborating on GitHub, we need to set up Git on our local machine and connect it to our GitHub account. This involves configuring Git with our username and email, generating an SSH key for authentication, and adding the SSH key to our GitHub account.

### Configuring Git

To configure Git with your username and email, you can use the following commands in your terminal:

```bash
git config --global user.name "Your Name"
git config --global user.email "Your Email"
```

We also need to set up the remote configuration for our Git repository to connect it to GitHub. This can be done using the following command:

```bash
git remote add origin <repository-url>
```

Here `remote` is the command to manage remote repositories. `origin` is the default name for the remote repository. Replace `<repository-url>` with the URL of your GitHub repository (either HTTPS or SSH).

### Generating an SSH Key

To generate an SSH key, you can use the following command in your terminal:

```bash
ssh-keygen
```

This command will prompt you to enter a file name for the SSH key and a passphrase (optional). After you generate the SSH key, you can find it in your home directory under the `.ssh` folder.

### Adding the SSH Key to GitHub

To add the SSH key to your GitHub account, follow these steps:

1. Go to [GitHub](https://github.com) and sign in to your account.
1. Click on your profile picture in the top right corner and select "Settings".
1. In the left sidebar, click on "SSH and GPG keys".
1. Click on the "New SSH key" button.
1. Enter a title for the SSH key (e.g., "My Laptop") and paste the contents of your SSH key (found in the `.ssh` folder) into the "Key" field.
1. Click "Add SSH key" to save the key to your GitHub account.

Now that we have set up Git and connected it to our GitHub account, we can start collaborating on projects using GitHub's features.

```bash
git add .
git commit -m "message"
git push origin main
```

```bash
git pull origin main
```

These commands will allow you to push your changes to GitHub and pull changes from GitHub to your local machine, enabling you to collaborate with other developers on the same codebase.

:::info fine-grain-token

SSH keys are secure, but if someone gains access to your private key file, they can authenticate as you. This method of ssh key authentication is giving our entire github account access to anyone who has access to our local machine. So, it's important to keep our SSH keys secure and not share them with others.

There is another of way of authenticating with GitHub using Personal Access Tokens (PATs)(fine-grain-token), which provide more fine-grained control over the permissions granted to the token. PATs can be used for specific actions (e.g., pushing code, managing issues) and can be revoked at any time without affecting other access to your GitHub account.

You can also use PATs for authentication when using Git over HTTPS instead of SSH. When prompted for your username and password, you can enter your GitHub username and the PAT as the password.

```bash

git clone https://github.com/username/repository.git
```

:::

## Creating a New Repository

To create a new repository on GitHub, follow these steps:

1. Go to [GitHub](https://github.com) and sign in to your account.
2. Click on the "+" icon in the top right corner and select "New repository".
3. Enter a name for your repository and add a description (optional).
4. Choose whether to make the repository public or private.
5. Initialize the repository with a README file (recommended).
6. Click "Create repository".

## Cloning a Repository

Cloning a repository allows you to create a local copy of a GitHub repository on your machine, which you can then work on and push changes back to GitHub.

To clone an existing repository from GitHub to your local machine, follow these steps:

1. Go to the repository you want to clone on GitHub.
2. Click on the "Code" button and copy the URL of the repository (either HTTPS or SSH).
3. Open your terminal and navigate to the directory where you want to clone the repository.
4. Use the following command to clone the repository:

    `git clone <repository-url>`

    Replace `<repository-url>` with the URL you copied from GitHub.

## Forking a Repository

Forking a repository allows you to create your own copy of a repository on GitHub, which you can work on independently. This is useful when you want to contribute to a project but don't have write access to the original repository.

To fork a repository on GitHub, follow these steps:

1. Go to the repository you want to fork on GitHub.
2. Click on the "Fork" button in the top right corner of the repository page.
3. Choose the account where you want to fork the repository (if you have multiple accounts).
4. After the repository is forked, you will have your own copy of the repository under your GitHub account, which you can work on independently.

## Pull Requests

Pull requests are a way to propose changes to a repository on GitHub. They allow you to collaborate with other developers by reviewing and discussing the proposed changes before they are merged into the main codebase.

To create a pull request on GitHub, follow these steps:

1. Make changes to your local copy of the repository and commit those changes.
2. Push your changes to your forked repository on GitHub.
3. Go to the original repository on GitHub and click on the "Pull requests" tab
4. Click on the "New pull request" button.
5. Select the branch you want to merge your changes into (usually the main branch) and the branch you want to merge from (your forked repository).
6. Add a title and description for your pull request, explaining the changes you made and why they are important.
7. Click "Create pull request" to submit your pull request for review.

## Code Reviews

Code reviews are an important part of the software development process, as they help ensure that changes to the codebase are of high quality and meet the project's standards. GitHub provides tools for conducting code reviews, such as inline comments and review requests.

To conduct a code review on GitHub, follow these steps:

1. Go to the pull request you want to review on GitHub.
2. Review the changes proposed in the pull request by looking at the code diffs and any comments made by the author.
3. If you have feedback or suggestions for improvement, you can leave inline comments on specific lines of code or general comments on the pull request.
4. If you approve the changes, you can click the "Approve" button to indicate that you are satisfied with the changes.
5. If you have concerns or require changes, you can click the "Request changes" button and provide feedback on what needs to be addressed before the pull request can be merged.

## Issue Tracking

GitHub's issue tracking system allows you to manage bugs, feature requests, and other tasks related to the project. You can create issues to track work that needs to be done and assign them to specific team members.

To create an issue on GitHub, follow these steps:

1. Go to the repository where you want to create an issue on GitHub.
2. Click on the "Issues" tab and then click on the "New issue" button.
3. Enter a title and description for the issue, explaining the problem or feature request in detail.
4. Optionally, you can add labels to categorize the issue, assign it to a specific team member, and set a milestone for when the issue should be resolved.
5. Click "Submit new issue" to create the issue and add it to the repository's issue tracker.

## Common Problems and Solutions

### Merge Conflicts

When multiple developers are working on the same codebase, it's possible that they may make changes to the same lines of code, which can lead to merge conflicts when trying to merge their changes. To resolve merge conflicts, you will need to manually edit the conflicting files and decide how to combine the changes. GitHub provides tools to help you identify and resolve merge conflicts, such as highlighting the conflicting lines of code and providing options for how to resolve the conflict.

### Reverting Changes

If you need to undo changes that have been made to the codebase, you can use the `git revert` command to create a new commit that undoes the changes introduced by a previous commit. This is a safe way to revert changes, as it preserves the commit history and allows you to easily track when and why changes were reverted.

Alternatively, you can use the `git reset` command to move the current branch pointer back to a previous commit, effectively discarding any commits that came after it. However, this method can be dangerous if not used carefully, as it can permanently delete commits and their associated changes from the repository history.

### Stash Changes

If you have made changes to your local repository that you are not ready to commit yet, but you need to switch to a different branch or pull changes from the remote repository, you can use the `git stash` command to temporarily save your changes without committing them. This allows you to switch branches or pull changes without losing your work. You can later apply the stashed changes back to your working directory using the `git stash apply` command.

### Reverting to a Previous Commit

If you need to revert your codebase to a previous commit, you can use the `git reset` command to move the current branch pointer back to a specific commit. This will effectively discard any commits that came after the specified commit. However, it's important to understand the implications of using `git reset`, as it can permanently delete commits and their associated changes from the repository history if not used carefully. There are different options for `git reset` that determine how the changes are handled:

- `--soft`: This option keeps the changes staged, allowing you to review and commit them again if needed.
- `--mixed`: This option unstages the changes, but keeps them in your working directory, allowing you to review and modify them before committing.
- `--hard`: This option deletes all changes in the working directory and resets the branch pointer to the specified commit, effectively discarding all changes made after that commit. Use this option with caution, as it can lead to data loss if you have uncommitted changes that you want to keep.

## Summary

- GitHub is a popular platform for remote collaboration on software projects, providing features such as pull requests, code reviews, and issue tracking.
- To collaborate on GitHub, you need to set up Git on your local machine and connect it to your GitHub account using SSH keys or Personal Access Tokens (PATs).
- You can create a new repository, clone an existing repository, or fork a repository on GitHub to start collaborating with other developers.
- Pull requests allow you to propose changes to a repository and collaborate with other developers to review and merge those changes.
- Code reviews help ensure that changes to the codebase are of high quality and meet the project's standards.
- GitHub's issue tracking system allows you to manage bugs, feature requests, and other tasks related to the project.

### References

- [GitHub Documentation](https://docs.github.com/)
- [GitHub Guides](https://guides.github.com/)
- [GitHub Learning Lab](https://lab.github.com/)
