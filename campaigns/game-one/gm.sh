#!/bin/bash
# gm.sh FILE "commit msg" — append a GM post to scene.md, commit as GM.
set -e
cd ~/workspace/xero-rpg
{ printf '\n'; cat "$1"; } >> campaign/scene.md
cd campaign
git add scene.md
git commit -q -m "$2"
echo "committed: GM — $2"
