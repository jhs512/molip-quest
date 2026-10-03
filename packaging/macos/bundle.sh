#!/usr/bin/env bash
# Wrap the release binary in an .app bundle, ad-hoc sign it, and pack a .dmg.
# Apple Silicon refuses to launch unsigned arm64 binaries, so the ad-hoc signature is
# required even without a Developer ID. The image is not notarized: first launch needs
# right-click → Open (or `xattr -cr`), which docs/releases.md explains to students.
set -euo pipefail
cd "$(dirname "$0")/../.."

version=$(sed -n 's/^version = "\([^"]*\)"/\1/p' Cargo.toml | head -n 1)
app="target/bundle/몰입 퀘스트.app"
rm -rf target/bundle target/installers/molip-quest-macos-arm64.dmg
mkdir -p "$app/Contents/MacOS" "$app/Contents/Resources" target/installers

cp target/release/molip-quest "$app/Contents/MacOS/molip-quest"
sed "s/APP_VERSION/$version/g" packaging/macos/Info.plist > "$app/Contents/Info.plist"
cp README.md requirements-learning.txt "$app/Contents/Resources/"

codesign --force --deep --sign - "$app"

ln -s /Applications target/bundle/Applications
hdiutil create -volname "몰입 퀘스트" -srcfolder target/bundle -ov -format UDZO \
  target/installers/molip-quest-macos-arm64.dmg
