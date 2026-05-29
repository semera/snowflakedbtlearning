# VS Code in WSL

Run VS Code-like editor in WSL with `code-server`.

## Install

```bash
curl -fsSL https://code-server.dev/install.sh | sh
```

## Start

```bash
code-server --bind-addr 127.0.0.1:8080
```

Open:

```text
http://localhost:8080
```

## Password

```bash
cat ~/.config/code-server/config.yaml
```

## Open Project Folder

```bash
cd ~/work/my-project
code-server --bind-addr 127.0.0.1:8080 .
```

## Disable Password

Edit config:

```bash
nano ~/.config/code-server/config.yaml
```

Use:

```yaml
bind-addr: 127.0.0.1:8080
auth: none
cert: false
```

Start again:

```bash
code-server
```
