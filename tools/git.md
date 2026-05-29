# Git SSH Key

Create an SSH key and add it to your Git account.

## Create Key

```bash
ssh-keygen -t ed25519 -C "your-email@example.com"
```

Use default path:

```text
~/.ssh/id_ed25519
```

## Show Public Key

```bash
cat ~/.ssh/id_ed25519.pub
```

Copy the output.

## Add to Git Account

Add the public key in your Git hosting account:

- GitHub: Settings -> SSH and GPG keys -> New SSH key
- GitLab: Preferences -> SSH Keys
- Bitbucket: Personal settings -> SSH keys

## Test

GitHub:

```bash
ssh -T git@github.com
```

GitLab:

```bash
ssh -T git@gitlab.com
```
