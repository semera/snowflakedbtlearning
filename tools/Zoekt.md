# Zoekt

Fast code search tool from Sourcegraph. Indexes a Git repo and serves search over a web API.

## zq CLI

When searching this repo, you don't have to grep everything yourself - ask the Zoekt web server via the `zq` CLI. Can be faster.

Syntax:

```
zq "zoekt query" [--num N] [--ctx N]
```

Result: standard zoekt JSON output.

Optional:

- `--num N` - number of results returned (default 10)
- `--ctx N` - lines of context (default 0)

Example usage:

- `zq "aws"` - all occurrences of aws
- `zq "pavel" --num 1 --ctx 2` - one result with 2 lines of context
- `zq "type:repo .*"` - list of indexed repos

Do not forget to use `\b` for word boundaries especially for short words.

## Index a Repo

```powershell
$repo = "C:\git\my-repo"
$index = "C:\ooo\zoekt\index"

mkdir $index -Force

docker run --rm `
  -v "${repo}:/repo:ro" `
  -v "${index}:/data/index" `
  ghcr.io/sourcegraph/zoekt `
  zoekt-git-index -index /data/index /repo
```

## Run the Web UI / API

```powershell
docker run --rm `
  -p 6070:6070 `
  -v "${index}:/data/index" `
  ghcr.io/sourcegraph/zoekt
```

Open `http://localhost:6070`.

## Real Indexing Command

```powershell
docker run --rm `
  -v "${repo}:/repo:ro" `
  -v "${index}:/data/index" `
  ghcr.io/sourcegraph/zoekt `
  zoekt-git-index -index /data/index -incremental=true -delta=true -submodules=false -shard_prefix_override "${prefix}" /repo
```

## Indexing Parameters

- `-incremental=true` - skip re-indexing if the repo state (commit) has not changed since the last index run. Saves time on repeated runs.
- `-delta=true` - update only the changed files since the last index instead of rebuilding the whole shard from scratch. Faster updates for large repos.
- `-submodules=false` - do not follow and index Git submodules. Keeps the index limited to the main repo content.
- `-shard_prefix_override "name"` - set a custom prefix for the generated shard files instead of deriving it from the repo path. Useful to control or predict shard file names, for example when indexing multiple repos into the same `index` directory.

## Query CLI

Minimal CLI in [zoekt_query.py](zoekt_query.py). Sends a query, optional `--num` and `--ctx`, prints the raw JSON response.

```bash
python zoekt_query.py "myFunction" --num 20 --ctx 2
```

## PowerShell Function

Add to your PowerShell profile (`$PROFILE`) to call the script as `zq` from anywhere:

```powershell
function zq {
    python "C:\git\snowflakedbtlearning\tools\zoekt_query.py" @args
}
```

Reload the profile (`. $PROFILE`) or open a new terminal, then:

```powershell
zq "myFunction" --num 20 --ctx 2
```

## List Indexed Repos

A query with only `type:repo` returns repos instead of file matches.

```bash
python zoekt_query.py "type:repo .*"
```

Response shape:

```json
{
  "Repos": [
    {
      "Name": "repo-name",
      "IndexTime": "...",
      "Files": 123,
      "Branches": [{"Name": "HEAD", "Version": "..."}]
    }
  ]
}
```

Read `data["Repos"]` instead of `data["Files"]` for this kind of query.

## Query Params

- `q` - the search query string, for example `myFunction` or `f:\.py$ myFunction`.
- `num` - max number of result entries (files) to return. Controls how many matched files come back.
- `ctx` - number of context lines to include before and after each matched line.
- `format=json` - return the response as JSON instead of the HTML search page.
- `debug` - if set to `true`, includes scoring/debug info for each match. Useful for tuning queries, not needed for normal use.

