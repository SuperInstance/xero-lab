#!/bin/bash
# post.sh CHAR BEATNUM TAG "commit msg" — append a character's post
# to scene.md + their log.md and commit it as that character.
set -e
cd ~/workspace/xero-rpg
CHAR=$1; BEAT=$2; TAG=$3; MSG=$4
case $CHAR in
  tobin) N="Tobin Marlow";; marta) N="Marta Venn";; pell) N="Pell Sutter";;
esac
{ printf '\n## %s — Beat %s\n\n' "$N" "$BEAT"; cat "posts/$TAG-$CHAR.md"; } >> campaign/scene.md
{ printf '\n**Beat %s — my post:**\n\n' "$BEAT"; cat "posts/$TAG-$CHAR.md"; } >> "campaign/characters/$CHAR/log.md"
cd campaign
git add scene.md "characters/$CHAR/log.md"
GIT_AUTHOR_NAME="$N" GIT_AUTHOR_EMAIL="$CHAR@xero-rpg" \
GIT_COMMITTER_NAME="$N" GIT_COMMITTER_EMAIL="$CHAR@xero-rpg" \
git commit -q -m "$MSG"
echo "committed: $N beat $BEAT"
