# GitHub Gist Manager

A command-line tool to create, update, list, and manage GitHub gists from local files.

## Setup

1. **Get a GitHub Personal Access Token:**
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with `gist` scope
   - Copy the token

2. **Add to your `.env` file:**
   ```bash
   GITHUB_TOKEN=your_token_here
   ```

3. **Install dependencies:**
   ```bash
   uv add requests
   ```
   Note: `rich` is already in the project dependencies.

## Usage

### Create a Gist

Create a new gist from a local file:

```bash
# Private gist (default)
python scripts/gist_manager.py create lesson-17/articles/guardrails_validation_deepdive.md

# Public gist
python scripts/gist_manager.py create lesson-17/articles/guardrails_validation_deepdive.md --public

# With custom description and filename
python scripts/gist_manager.py create myfile.md \
  --description "My awesome article" \
  --filename "article.md" \
  --public
```

### Update a Gist

Update an existing gist:

```bash
python scripts/gist_manager.py update <gist_id> myfile.md

# Update description too
python scripts/gist_manager.py update <gist_id> myfile.md \
  --description "Updated description"
```

### List Your Gists

List all your gists:

```bash
python scripts/gist_manager.py list
```

### Get Gist Details

View details and content of a specific gist:

```bash
python scripts/gist_manager.py get <gist_id>
```

### Delete a Gist

Delete a gist (with confirmation):

```bash
python scripts/gist_manager.py delete <gist_id>

# Skip confirmation
python scripts/gist_manager.py delete <gist_id> --force
```

## Examples

### Quick Share a Tutorial

```bash
# Create a public gist from your tutorial
python scripts/gist_manager.py create \
  lesson-17/tutorials/06_phase_logger_deep_dive.md \
  --description "Phase Logger Deep Dive Tutorial" \
  --public

# The tool will output the gist URL - share it!
```

### Update Documentation

```bash
# Update an existing gist when you make changes
python scripts/gist_manager.py update abc123def456 \
  lesson-17/articles/guardrails_validation_deepdive.md \
  --description "Updated: GuardRails Validation Deep Dive"
```

### Find a Gist ID

```bash
# List all gists to find the ID
python scripts/gist_manager.py list

# Or get details if you have the URL
# Gist URLs look like: https://gist.github.com/username/abc123def456
# The ID is the last part: abc123def456
```

## Features

- ✅ Create public or private gists
- ✅ Update existing gists
- ✅ List all your gists with details
- ✅ View gist contents
- ✅ Delete gists (with safety confirmation)
- ✅ Beautiful CLI output with Rich
- ✅ Error handling and helpful messages

## Requirements

- Python 3.8+
- `requests` library
- `rich` library (for beautiful CLI output)
- GitHub Personal Access Token with `gist` scope

## Troubleshooting

**"GITHUB_TOKEN not set" error:**
- Make sure you've added `GITHUB_TOKEN=your_token` to your `.env` file
- Or export it: `export GITHUB_TOKEN=your_token`

**"401 Unauthorized" error:**
- Check that your token is valid
- Ensure the token has the `gist` scope enabled
- Token might have expired - generate a new one

**"404 Not Found" error:**
- Check that the gist ID is correct
- The gist might have been deleted
- You might not have access to that gist
