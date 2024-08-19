#!/usr/bin/env python3

import os
import time
import logging
import argparse
import subprocess

from datetime import datetime

import yaml


class ColoredFormatter(logging.Formatter):
	# Define color codes for each log level
	COLORS = {
		"DEBUG": "\033[0;34m",  # Gray
		"INFO": "\033[0;32m",  # Green
		"WARNING": "\033[0;33m",  # Yellow
		"ERROR": "\033[0;31m",  # Red
		"CRITICAL": "\033[1;31m",  # Bright Red
	}
	RESET = "\033[0m"

	def format(self, record):
		log_color = self.COLORS.get(record.levelname, self.RESET)
		record.levelname = f"{log_color}{record.levelname}{self.RESET}"
		return super().format(record)


def setup_logging(log_file):
	os.makedirs(os.path.dirname(log_file), exist_ok=True)

	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	file_handler = logging.FileHandler(log_file)
	file_handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	file_handler.setFormatter(formatter)
	logger.addHandler(file_handler)

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.DEBUG)
	colored_formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
	stream_handler.setFormatter(colored_formatter)
	logger.addHandler(stream_handler)


def parse_args():
	parser = argparse.ArgumentParser(
		description="Download files using aria2c based on a YAML configuration."
	)
	parser.add_argument(
		"yaml_path", type=str, help="Path to the YAML configuration file."
	)
	return parser.parse_args()


def load_yaml(filepath):
	with open(filepath, "r") as file:
		return yaml.safe_load(file)


def build_aria2c_command(url, opts):
	cmd = ["aria2c"]

	cmd.append(f"--conf={opts['conf']}")
	cmd.append(f"--dir={opts['dir']}")

	if opts["out"]:
		cmd.append(f"--out={opts['out']}")

	if opts["retry-file"]:
		cmd.append(f"--max-tries={opts['retry-file']}")

	cmd.extend(["--console-log-level=notice", "--summary-interval=60"])

	cmd.append(url)
	return cmd


def run_download(url, opts):
	cmd = build_aria2c_command(url, opts)
	os.makedirs(opts["dir"], exist_ok=True)
	logging.debug(f"Starting download for :: {' '.join(cmd)}")

	process = subprocess.Popen(
		cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
	)

	while True:
		output = process.stdout.readline()
		if output == "" and process.poll() is not None:
			break
		if output:
			print(output.strip())  # Directly output to Python's stdout

	process.stdout.close()

	if process.returncode == 0:
		logging.debug(f"Download successful for {url}")
		return True
	else:
		logging.error(f"Download failed for {url} with error: {process.returncode}")
		return False


def populate_defaults(defaults: dict):
	defaults.setdefault(
		"base-dir",
		os.path.join(
			os.getcwd(),
			f"aria2c-night-owl--{datetime.now().strftime("%Y-%m-%d--%H-%M")}",
		),
	)
	defaults.setdefault(
		"log",
		os.path.join(
			defaults["base-dir"], f"{datetime.now().strftime("%Y-%m-%d--%H-%M-%S")}"
		),
	)
	defaults.setdefault("retry", 1)
	defaults.setdefault("proxify", True)

	defaults.setdefault("conf", "~/.aria2c")
	defaults["conf"] = os.path.expanduser(os.path.expandvars(defaults["conf"]))

	defaults.setdefault("start-time", "")
	if defaults["start-time"]:
		defaults["start-time"] = datetime.strptime(
			defaults["start-time"], "%H:%M"
		).time()

	defaults.setdefault("end-time", "")
	if defaults["end-time"]:
		defaults["end-time"] = datetime.strptime(defaults["end-time"], "%H:%M").time()


def resolve_opts(defaults: dict, values: dict) -> dict:
	opts = dict()

	if "dir" in values and values["dir"]:
		opts["dir"] = os.path.join(defaults["base-dir"], values["dir"])
	else:
		opts["dir"] = defaults["base-dir"]

	opts["out"] = values.get("out", "")
	opts["conf"] = values.get("conf", defaults["conf"])
	opts["retry-file"] = values.get("retry-file", "")
	opts["proxify"] = values.get("proxify", defaults["proxify"])

	return opts


def main():
	args = parse_args()
	yaml_path = args.yaml_path
	urls = load_yaml(yaml_path)

	defaults = urls.get("defaults", dict())
	if "defaults" in urls:
		del urls["defaults"]
	populate_defaults(defaults)

	proxy_vars = dict()
	for var in ["HTTP_PROXY", "http_proxy", "HTTPS_PROXY", "https_proxy"]:
		proxy_vars[var] = os.environ.get(var, "")

	setup_logging(defaults["log"])

	while defaults["start-time"] and datetime.now().time() < defaults["start-time"]:
		time.sleep(30)

	for tc in range(defaults["retry"]):
		logging.debug(f"--- Starting try number {tc}")
		success = True
		for url in urls:
			if isinstance(urls[url], dict) and "opts" in urls[url]:
				opts = urls[url]["opts"]
			else:
				if isinstance(urls[url], str):
					urls[url] = {"dir": urls[url]}
				elif not isinstance(urls[url], dict):
					logging.error(f"Invalid options for URL {url}: {urls[url]}")
					urls[url] = {"status": "invalid"}
					continue

				opts = resolve_opts(defaults, urls[url])
				urls[url]["opts"] = opts

			for var in proxy_vars:
				if opts["proxify"]:
					os.environ[var] = proxy_vars[var]
				elif var in os.environ:
					del os.environ[var]

			if defaults["end-time"] and datetime.now().time() > defaults["end-time"]:
				logging.debug("End time reached. Exiting.")
				return

			if run_download(url, opts):
				urls[url]["status"] = "success"
			else:
				urls[url]["status"] = "failed"
				success = False

		if success:
			logging.debug("All downloads successful.")
			break
		else:
			logging.debug("Retrying downloads...")
			time.sleep(30)

	logging.debug("Finished all retries.")


if __name__ == "__main__":
	main()
