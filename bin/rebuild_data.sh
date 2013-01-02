#!/bin/sh

BASE_PATH="$HOME/webapps/calebcc_bottle"

PROJECT_PATH="$BASE_PATH/project"

SOURCE_PATH="$BASE_PATH/site_data"
BUILDS_PATH="$BASE_PATH/compiled_data_builds"
DESTINATION_PATH="$BASE_PATH/compiled_data"

BUILD_ID=`date "+%Y%m%d%H%M%S"`
BUILD_PATH="$BUILDS_PATH/$BUILD_ID"

# Make sure the we can put the builds somewhere
mkdir -p "$BUILDS_PATH"

# Update the data
cd "$SOURCE_PATH"
hg pull -u

# Rebuild the content
cd "$PROJECT_PATH"
env/bin/python calebcc.py --parse -s "$SOURCE_PATH" -d "$BUILD_PATH"

# Symlink the rebuilt content
ln -sfn "$BUILD_PATH" "$DESTINATION_PATH"
