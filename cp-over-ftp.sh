#!/usr/bin/bash

# Variables
FTP_SERVER="192.168.43.65" # Replace with your FTP server
FTP_PORT="3721"
LOCAL_DIR="/home/francis/Corridor/wd/Anime/Mob Psycho 100" # Replace with the path to your local video files
REMOTE_DIR="/Movies"                                       # Replace with the target directory on the FTP server

# Change to the local directory
cd "$LOCAL_DIR" || exit

# Start FTP session
for file in "$LOCAL_DIR"/*2/*.ass; do
	echo "$file"
	filename="S02E$(echo "$file" | grep -Eo '[0-1][0-9]\.en' | grep -Eo '[0-1][0-9]').ass"
	ftp -inv "$FTP_SERVER" "$FTP_PORT" <<EOF
user "francis" "something"
binary
put "$file" "${REMOTE_DIR}/$filename"
bye
EOF
done
#  # put "$file" "$new_name";
