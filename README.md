Strava club

## Triggering the sync from macOS cron

GitHub's scheduled workflows are disabled for this repo. The workflow is now triggered only through `workflow_dispatch`, and a local cron job on your Mac can call GitHub to start it.

### 1. Create a GitHub token

Create a personal access token that can run Actions in `erlendthune/strava`.

- Fine-grained token: repository access to `erlendthune/strava` with `Actions: Read and write`
- Classic token: `repo` scope

Export it in your shell profile:

```sh
export STRAVA_GITHUB_TOKEN=your_token_here
```

Reload your shell after updating the profile.

### 2. Test the trigger manually

Run:

```sh
./scripts/trigger_strava_sync.sh
```

This dispatches `.github/workflows/strava_sync.yml` on the `main` branch.

### 3. Install the cron entry

Edit your crontab:

```sh
crontab -e
```

Add a schedule like this:

```cron
17,47 8-15 * * * cd /Users/erlend.thune/git/strava && STRAVA_GITHUB_TOKEN="$STRAVA_GITHUB_TOKEN" ./scripts/trigger_strava_sync.sh >> /Users/erlend.thune/git/strava/cron.log 2>&1
```

That matches the previous Oslo daytime cadence of `:17` and `:47` between 08:00 and 15:59 local time. Adjust it if you want a different schedule.

### 4. Verify it works

List the installed cron entries:

```sh
crontab -l
```

Check the dispatch log after the next run:

```sh
tail -n 50 /Users/erlend.thune/git/strava/cron.log
```
