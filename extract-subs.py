import re
import sys
import pysubs2
import subprocess


def get_mkv_track_id(file_path):
    """ Returns the track ID of the SRT subtitles track"""
    try:
        raw_info = subprocess.check_output(["mkvmerge", "-i", file_path],
                                           stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as ex:
        print(ex)
        sys.exit(1)
    pattern = re.compile('.* (\d+): subtitles \(SubRip/SRT\).*', re.DOTALL)
    m = pattern.match(str(raw_info))
    if m:
        return raw_info, m.group(1)
    else:
        return raw_info, None


def extract_mkv_subs(file):
    print("    Extracting embedded subtitles...")
    try:
        subprocess.call(["mkvextract", "tracks", file['full_path'],
                         file['srt_track_id'] + ":" + file['srt_full_path']])
        print("    OK.")
    except subprocess.CalledProcessError:
        print("    ERROR: Could not extract subtitles")


def remove_duplicates(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        srt_path = file_path.replace(file_path[file_path.rfind('.') + 1:], 'srt')
        _, track_id = get_mkv_track_id(file_path)
        if track_id is None:
            print('This file has not embedded subtitles.')
            return
        extract_mkv_subs({
            'full_path': file_path,
            'srt_track_id': track_id,
            'srt_full_path': srt_path
        })
        subs = pysubs2.load(srt_path)

        with open(srt_path, 'w') as file:
            file.write("\n".join(remove_duplicates([line.text.replace(r'\N', ' ') for line in subs])))
    else:
        print('No arguments provided.', file=sys.stderr)


if __name__ == '__main__':
    main()
