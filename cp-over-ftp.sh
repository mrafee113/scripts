#!/usr/bin/bash

# Variables
FTP_SERVER="192.168.128.28" # Replace with your FTP server
FTP_PORT="3721"
LOCAL_DIR="/home/francis/Corridor/wd/TV Series/Invincible" # Replace with the path to your local video files
REMOTE_DIR="/Movies"                                       # Replace with the target directory on the FTP server

# Change to the local directory
cd "$LOCAL_DIR" || exit

# Start FTP session
for file in "$LOCAL_DIR"/"Season 2"/*; do
	echo "$file"
	filename="$(echo "$file" | grep -Eo '[Ss]0[0-9][Ee][0-1][0-9]')"
	fileformat="$(echo "$file" | grep -Eo 'mkv|srt|mp4')"
	[ -z "$fileformat" ] && continue
	ftp -inv "$FTP_SERVER" "$FTP_PORT" <<EOF
user "francis" "something"
binary
put "$file" "${REMOTE_DIR}/${filename}.${fileformat}"
bye
EOF
done
#  # put "$file" "$new_name";
