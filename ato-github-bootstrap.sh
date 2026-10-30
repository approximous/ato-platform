#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

echo "=== ATO GitHub Bootstrap (API + gh auth) ==="

# ---------- 1. Install tools ----------
pkg update -y
pkg install -y gh git curl jq python

# ---------- 2. Authenticate with GitHub CLI ----------
echo ""
echo "Starting GitHub authentication..."
echo "A browser or device-code flow will open. Follow the prompts."
echo ""

gh auth login --hostname github.com --git-protocol https --web

# Verify we are logged in
gh auth status

# ---------- 3. Configuration ----------
read -p "GitHub username: " GITHUB_USER
read -p "Repository name [ato-platform]: " REPO_NAME
REPO_NAME=${REPO_NAME:-ato-platform}

echo ""
echo "Will create private repository: $GITHUB_USER/$REPO_NAME"
read -p "Continue? [y/N] " CONFIRM
[[ "\( CONFIRM" =\~ ^[Yy] \) ]] || { echo "Aborted."; exit 1; }

# ---------- 4. Create repository via API (through gh) ----------
echo "Creating private repository (no README, no .gitignore, no license)..."

gh repo create "$REPO_NAME" \
  --private \
  --description "ATO Operation Orchestrator – Stage 0/1 baseline" \
  --confirm

# ---------- 5. Push local Stage 0/1 tree ----------
PROJECT_DIR="$HOME/ato-work/ato-platform"

if [ ! -d "$PROJECT_DIR" ]; then
  echo "ERROR: Project not found at $PROJECT_DIR"
  echo "Run the earlier restore/unzip steps first."
  exit 1
fi

cd "$PROJECT_DIR"

# Ensure we are on main
git init -b main 2>/dev/null || true
git add .
git -c user.email="$(gh api user --jq .email // .login)" \
    -c user.name="$(gh api user --jq .name // .login)" \
    commit -m "Stage 0/1: ATO Operation Orchestrator core + mock GitHub bootstrap" \
    || echo "Nothing new to commit (already committed)"

# Set remote and push
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
git push -u origin main

echo "Push complete."

# ---------- 6. Apply branch protection via API ----------
echo "Applying branch protection on main..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$GITHUB_USER/$REPO_NAME/branches/main/protection" \
  -f enforce_admins=true \
  -f required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  -F allow_force_pushes=false \
  -F allow_deletions=false \
  --input - <<EOF
{
  "required_status_checks": null,
  "restrictions": null
}
EOF

# ---------- 7. Set Actions permissions to read-only ----------
echo "Setting Actions workflow permissions to read-only..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  "/repos/$GITHUB_USER/$REPO_NAME/actions/permissions/workflow" \
  -f default_workflow_permissions=read \
  -F can_approve_pull_request_reviews=false

# ---------- 8. Independent verification (read-back) ----------
echo ""
echo "=== Independent Verification ==="

echo "Repository:"
gh repo view "$GITHUB_USER/$REPO_NAME" --json name,visibility,defaultBranchRef,url

echo ""
echo "Branch protection:"
gh api "/repos/$GITHUB_USER/$REPO_NAME/branches/main/protection" \
  --jq '{enforce_admins, allow_force_pushes, allow_deletions, required_pull_request_reviews}'

echo ""
echo "Actions permissions:"
gh api "/repos/$GITHUB_USER/$REPO_NAME/actions/permissions/workflow"

echo ""
echo "=== Bootstrap complete ==="
echo "Repository: https://github.com/$GITHUB_USER/$REPO_NAME"
