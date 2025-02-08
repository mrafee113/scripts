#!/bin/bash

if ! printf "%s\n" "$@" | xargs -I{} bash -c 'if [ ! -f "{}" ]; then exit 1; fi'; then
	echo "arg file must be give."
	exit 1
fi

lines="$(cat "$@")"
echo there are a total of "$(echo "$lines" | wc -l)" lines
cleaned="$(echo "$lines" | sed -E 's|^: [0-9]*:0;||')"
echo there are a total of "$(echo "$cleaned" | wc -l)" cleaned lines
dedupd="$(echo "$cleaned" | awk '!seen[$0]++')"
echo there are a total of "$(echo "$dedupd" | wc -l)" deduplicated lines

tmp="$(mktemp)"
echo "$dedupd" > "$tmp"
echo exported all lines to "$tmp"
