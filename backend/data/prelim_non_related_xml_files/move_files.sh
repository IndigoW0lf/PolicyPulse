#!/bin/bash

source_dir="/Users/indigowolf/workspace/PolicyPulse/backend/data/filtered_xml_files"
dest_dir="/Users/indigowolf/workspace/PolicyPulse/backend/data/failed_xml_files"

while IFS= read -r file
do
  cp "$source_dir/$file" "$dest_dir"
done < files_to_move.txt
