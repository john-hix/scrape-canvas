#!bin/python3
import argparse
import os
import re

from pathvalidate import sanitize_filename
from canvasapi import Canvas
from canvasapi.course import Course
from canvasapi.exceptions import Unauthorized, ResourceDoesNotExist
from canvasapi.file import File
from canvasapi.module import Module, ModuleItem


def extract_files(text):
    text_search = re.findall("/files/(\\d+)", text, re.IGNORECASE)
    groups = set(text_search)
    return groups

def get_course_files(course):
    modules = course.get_modules()

    files_downloaded = set() # Track downloaded files for this course to avoid duplicates

    for module in modules:
        module: Module = module
        module_items = module.get_module_items()
        for item in module_items:
            item: ModuleItem = item

            path = f"{output}/" \
                f"{sanitize_filename(course.attributes['name'])}/" \
                f"{sanitize_filename(module.attributes['name'])}/"
            if not os.path.exists(path):
                os.makedirs(path)

            item_type = item.attributes["type"]
            print(f"{course.attributes['name']} - "
                  f"{module.attributes['name']} - "
                  f"{item.attributes['title']} ({item_type})")

            if item_type == "File":
                file = canvas.get_file(item.attributes["content_id"])
                files_downloaded.add(item.attributes["content_id"])
                file.download(path + sanitize_filename(file.attributes['filename']))
            elif item_type == "Page":
                page = course.get_page(item.attributes["page_url"])
                with open(path + sanitize_filename(item.attributes['title']) + ".html", "w", encoding="utf-8") as f:
                    f.write(page.attributes["body"] or "")
                files = extract_files(page.attributes["body"] or "")
                for file_id in files:
                    if file_id in files_downloaded:
                        continue
                    try:
                        file = course.get_file(file_id)
                        files_downloaded.add(file_id)
                        file.download(path + sanitize_filename(file.attributes['filename']))
                    except ResourceDoesNotExist:
                        pass
            elif item_type == "ExternalUrl":
                url = item.attributes["external_url"]
                with open(path + sanitize_filename(item.attributes['title']) + ".url", "w") as f:
                    f.write("[InternetShortcut]\n")
                    f.write("URL=" + url)
            elif item_type == "Assignment":
                assignment = course.get_assignment(item.attributes["content_id"])
                with open(path + sanitize_filename(item.attributes['title']) + ".html", "w", encoding="utf-8") as f:
                    f.write(assignment.attributes["description"] or "")
                files = extract_files(assignment.attributes["description"] or "")
                for file_id in files:
                    if file_id in files_downloaded:
                        continue
                    try:
                        file = course.get_file(file_id)
                        files_downloaded.add(file_id)
                        file.download(path + sanitize_filename(file.attributes['filename']))
                    except ResourceDoesNotExist:
                        pass

    try:
        files = course.get_files()
        for file in files:
            file: File = file
            if not file.attributes["id"] in files_downloaded:
                print(f"{course.attributes['name']} - {file.attributes['filename']}")
                path = f"{output}/{sanitize_filename(course.attributes['name'])}/" \
                    f"{sanitize_filename(file.attributes['filename'])}"
                file.download(path)
    except Unauthorized:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download all content from Canvas")
    parser.add_argument("url", help="URL to the Canvas website, e.g. https://canvas.utwente.nl")
    parser.add_argument("token", help="Token generated in the settings page on Canvas")
    parser.add_argument("output", help="Path to the output folder, e.g. output/")
    parser.add_argument("courses", help="Comma-separated course IDs or 'all'", nargs="?", const="all")
    args = parser.parse_args()

    # Handle args
    output = args.output.rstrip("/") + "/"

    if args.courses is None:
        args.courses = "all"
        print("No courses specified. Scraping all courses.")

    canvas = Canvas(args.url, args.token)

    courses = [] # courses to scrape

    # Select courses to scrape, default to all
    if args.courses != "all":
        courses = []
        ids = args.courses.split(",")
        for id in ids:
            courses.append(canvas.get_course( int(id) ))
    else:
        courses = canvas.get_courses()

    # Perform scrape
    for course in courses:
        course: Course = course
        get_course_files(course)
