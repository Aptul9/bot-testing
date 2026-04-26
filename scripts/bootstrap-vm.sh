#!/bin/bash
# bootstrap-vm.sh
#
# StackScript / cloud-init equivalent script. Runs on first boot of an
# antibot fleet VM (Ubuntu 24.04 LTS).
#
# Behavior:
#   1. Update apt + install Docker + git
#   2. Clone the bot-testing repo (default: github.com/Aptul9/bot-testing main)
#   3. Build the waf-bots Docker image
#   4. Write a sentinel file when done
#
# UDF parameters (consumed when uploaded as Linode StackScript):
# <UDF name="repo_url" Label="Bot repo URL" default="https://github.com/Aptul9/bot-testing.git" />
# <UDF name="bot_branch" Label="Branch" default="main" />
#
# Logs:
#   /var/log/stackscript.log     all output
#   /var/log/stackscript.done    written on success with timestamp
#
# Manual invocation (local dry-run testing on a fresh VM):
#   REPO_URL=https://github.com/Aptul9/bot-testing.git BOT_BRANCH=main bash bootstrap-vm.sh

set -euo pipefail
exec > /var/log/stackscript.log 2>&1

REPO_URL="${REPO_URL:-https://github.com/Aptul9/bot-testing.git}"
BOT_BRANCH="${BOT_BRANCH:-main}"

echo "[$(date -u +%FT%TZ)] starting bootstrap repo=$REPO_URL branch=$BOT_BRANCH"

apt-get update
apt-get install -y --no-install-recommends ca-certificates curl gnupg git

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

UBUNTU_CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y --no-install-recommends \
  docker-ce docker-ce-cli containerd.io docker-buildx-plugin

systemctl enable --now docker

mkdir -p /opt/waf-bots
cd /opt/waf-bots
if [ ! -d repo/.git ]; then
  git clone --depth 1 -b "$BOT_BRANCH" "$REPO_URL" repo
else
  cd repo && git fetch origin "$BOT_BRANCH" && git reset --hard "origin/$BOT_BRANCH" && cd ..
fi

cd /opt/waf-bots/repo
docker build -t waf-bots:dev .

echo "stackscript-done $(date -u +%FT%TZ)" > /var/log/stackscript.done
echo "[$(date -u +%FT%TZ)] bootstrap complete"
