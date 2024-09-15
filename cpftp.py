#!/usr/bin/env python3

import os
import re
import ftplib
import logging
import argparse

from typing import List, Tuple


def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    return logging.getLogger(__name__)


def parse_arguments():
    parser = argparse.ArgumentParser(description="FTP File Upload Script")
    parser.add_argument(
        "-f", "--format", type=str, action="append", help="Supported file formats"
    )
    parser.add_argument(
        "-p",
        "--path",
        type=str,
        action="append",
        default=list(),
        help="Local paths to search for files",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="Recursively search directories"
    )
    parser.add_argument("--ftp-server", type=str, required=True, help="FTP server address")
    parser.add_argument("--ftp-port", type=int, default=3721, help="FTP server port")
    parser.add_argument("--ftp-user", type=str, default="francis", help="FTP username")
    parser.add_argument("--ftp-pass", type=str, default="something", help="FTP password")
    parser.add_argument(
        "--remote-dir", type=str, required=True, help="Remote directory on FTP server"
    )

    args = parser.parse_args()
    if not args.path:
        args.path.append(".")

    return args


def connect_to_ftp(server: str, port: int, username: str, password: str) -> ftplib.FTP:
    logger.info(f"Connecting to FTP server {server}:{port}")
    ftp = ftplib.FTP()
    ftp.connect(server, port)
    ftp.login(username, password)
    ftp.set_pasv(True)
    ftp.voidcmd("TYPE I")
    return ftp


def get_file_info(file_path: str) -> Tuple[str, str]:
    filename = os.path.basename(file_path)
    _, file_extension = os.path.splitext(filename)
    return filename, file_extension.lstrip(".")


def create_remote_directory(ftp: ftplib.FTP, remote_path: str):
    dirs = remote_path.split("/")
    for dir in dirs:
        if dir:
            try:
                ftp.cwd(dir)
            except ftplib.error_perm:
                logger.info(f"Creating remote directory: {dir}")
                ftp.mkd(dir)
                ftp.cwd(dir)
    ftp.cwd("/")


def upload_file(ftp: ftplib.FTP, local_file: str, remote_file: str):
    logger.info(f"Uploading: {local_file} to {remote_file}")
    with open(local_file, "rb") as file:
        ftp.storbinary(f"STOR {remote_file}", file)


# TODO: support relative paths and resolve them for absolutes
def process_directory(
    ftp: ftplib.FTP,
    local_dir: str,
    remote_dir: str,
    formats: List[str],
    recursive: bool,
):
    for item in os.listdir(local_dir):
        local_path = os.path.join(local_dir, item)
        remote_path = os.path.join(remote_dir, item).replace("\\", "/")

        logger.info(f"{local_path} -> {remote_path}")
        if os.path.isfile(local_path):
            _, file_format = get_file_info(local_path)
            if not formats or file_format in formats:
                create_remote_directory(ftp, os.path.dirname(remote_path))
                upload_file(ftp, local_path, remote_path)
        elif os.path.isdir(local_path) and recursive:
            logger.info(f"Entering directory: {local_path}")
            create_remote_directory(ftp, remote_path)
            process_directory(ftp, local_path, remote_path, formats, recursive)

def process_directory(
    ftp: ftplib.FTP,
    local_dir: str,
    remote_dir: str,
    formats: List[str],
    recursive: bool,
    base_dir: str,
):
    for root, dirs, files in os.walk(local_dir):
        for file in files:
            local_path = os.path.join(root, file)
            _, file_format = get_file_info(local_path)
            
            if not formats or file_format in formats:
                relative_path = os.path.relpath(local_path, base_dir)
                remote_path = os.path.join(remote_dir, relative_path).replace("\\", "/")

                create_remote_directory(ftp, os.path.dirname(remote_path))
                upload_file(ftp, local_path, remote_path)
        
        if not recursive:
            break

def main():
    args = parse_arguments()
    ftp = connect_to_ftp(args.ftp_server, args.ftp_port, args.ftp_user, args.ftp_pass)

    try:
        if args.path == ["."]:
            logger.info(f"Processing current directory")
            process_directory(ftp, ".", args.remote_dir, args.format, args.recursive, ".")
        else:
            for path in args.path:
                logger.info(f"Processing path: {path}")
                remote_subdir = os.path.join(args.remote_dir, os.path.basename(path)).replace("\\", "/")
                process_directory(ftp, path, remote_subdir, args.format, args.recursive, path)
    finally:
        logger.info("Closing FTP connection")
        ftp.quit()

if __name__ == "__main__":
    logger = setup_logging()
    main()