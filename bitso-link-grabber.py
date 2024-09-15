#!/usr/bin/env python3

import os
import logging

from urllib.parse import urljoin, urlparse

import requests

from lxml import html


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


def login(session, login_url, username, password):
	"""Perform login and return the session with cookies."""

	payload = {
		"LoginForm[username]": username,
		"LoginForm[password]": password,
		"login-button": "",
	}
	headers = {
		"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:129.0) Gecko/20100101 Firefox/129.0",
		"Content-Type": "application/x-www-form-urlencoded",
		"Origin": "https://panel.bitso.ir",
		"Referer": "https://panel.bitso.ir/login",
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/png,image/svg+xml,*/*;q=0.8",
		"Accept-Language": "en-US,en;q=0.5",
		"Accept-Encoding": "gzip, deflate, br, zstd",
		"Connection": "keep-alive",
		"Upgrade-Insecure-Requests": "1",
	}

	response = session.post(login_url, data=payload, headers=headers)
	if response.status_code == 200 or response.status_code == 302:
		logging.debug("Login successful!")
	else:
		logging.error("Login failed!", response.status_code)
		logging.error(response.text)

	return session


def fetch_and_parse(session, url):
	try:
		response = session.get(url)
		if response.status_code == 200:
			return html.fromstring(response.content)
	except requests.RequestException as e:
		logging.error(f"Error fetching {url}: {e}")
	return None


def extract_links(tree, base_url):
	return {urljoin(base_url, link) for link in tree.xpath("//a/@href")}


def is_same_domain(url, root_domain):
	return urlparse(url).netloc == root_domain


def sanitize_filename(url):
	return urlparse(url).path.strip("/").replace("/", "_")


def save_structure(url, structure, base_dir):
	filename = sanitize_filename(url) or "index"
	file_path = os.path.join(base_dir, f"{filename}.txt")

	with open(file_path, "w") as file:
		for link in structure:
			file.write(link + "\n")


def crawl(session, url, base_dir, root_domain, visited=None):
	if visited is None:
		visited = set()

	if url in visited:
		return

	visited.add(url)
	print(f"Processing {url}")

	tree = fetch_and_parse(session, url)
	if tree is None:
		return

	links = extract_links(tree, url)
	same_domain_links = {link for link in links if is_same_domain(link, root_domain)}

	# Save the links in a structured manner
	save_structure(url, same_domain_links, base_dir)

	for link in same_domain_links:
		crawl(session, link, base_dir, root_domain, visited)


def main():
	root_url = input("Enter the root URL: ")
	login_url = input("Enter the login URL: ")
	username = input("Enter your username: ")
	password = input("Enter your password: ")

	base_dir = "website_structure"

	if not os.path.exists(base_dir):
		os.makedirs(base_dir)

	session = requests.Session()
	session = login(session, login_url, username, password)

	root_domain = urlparse(root_url).netloc
	crawl(session, root_url, base_dir, root_domain)


if __name__ == "__main__":
	main()
