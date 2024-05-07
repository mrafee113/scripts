import os
import sys
import math

from typing import Union, Callable
from dataclasses import dataclass, field
from datetime import timedelta, date

@dataclass
class Chapter:
    name: str
    number: str
    sections: dict[str, "Section"] = field(default_factory=dict)
    
    def __hash__(self):
        return hash(self.number)

@dataclass
class Options:
    has_chapters: bool = True
    chapter_no_hashes: int = 4
    section_no_hashes: int = 5
    
    get_chapter_name: Union[Callable, None] = None
    get_chapter_number: Union[Callable, None] = None
    get_section_name: Union[Callable, None] = None
    get_section_number: Union[Callable, None] = None


@dataclass
class Section:
    name: str
    number: str
    pg: int = 0
    temp_pg: int = 0
    time_req: timedelta = timedelta(minutes=0)
    time_done: timedelta = timedelta(minutes=0)
    performance: int = 0
    questions: int = 0
    questions_done: int = 0
    practice_time_req: timedelta = timedelta(minutes=0)
    practice_time_done: timedelta = timedelta(minutes=0)
    p_performance: int = 0
    chapter: Chapter = None

    def __hash__(self):
        return hash(self.number)

    @property
    def done(self):
        return self.temp_pg == 0 and self.time_done != timedelta(minutes=0)

    @staticmethod
    def get_done_pages(sections: list["Section"]) -> int:
        done_pg = 0
        for section in sections:
            if section.done:
                done_pg += section.pg
            elif section.temp_pg > 0:
                done_pg += section.temp_pg
        return done_pg
    
    @staticmethod
    def get_undone_pages(sections: list["Section"]) -> int:
        undone_pg = 0
        for section in sections:
            if not section.done:
                if section.temp_pg > 0:
                    undone_pg += section.pg - section.temp_pg
                else:
                    undone_pg += section.pg
        return undone_pg
    
    @staticmethod
    def get_total_pages(sections: list["Section"]) -> int:
        return sum(map(lambda x: x.pg, sections))

    #TODO: add starting section.number filtering
    @classmethod
    def get_target(cls, sections: list["Section"],
                   deadline: date,
                   start_date: date = None,
                   pg_day_freq: int = 0) -> list["Section"]:
        if start_date is None:
            start_date = date.today()
        if pg_day_freq == 0:
            pg_day_freq = math.ceil(
                    cls.get_undone_pages(sections) / abs((deadline - start_date).days)
            )

        pages_left = pg_day_freq
        log = str()

        year = deadline.strftime('%Y')
        log += f"{year} {start_date.strftime('%m-%d')} :: {deadline.strftime('%m-%d')} :: {(deadline - start_date).days} days\n\n"
        log += f"{pages_left} pages left\n"
        for section in sections:
            if section.done:
                continue
            if pages_left <= 0:
                break

            picked_pages = 0
            if section.temp_pg > 0:
                remain_pg = section.pg - section.temp_pg
                if remain_pg <= pages_left:
                    picked_pages = remain_pg
                    pages_left -= remain_pg
                elif remain_pg > pages_left:
                    picked_pages = pages_left
                    pages_left = 0
            elif section.pg <= pages_left:
                picked_pages = section.pg
                pages_left -= section.pg
            else:
                picked_pages = pages_left
                pages_left = 0

            log += f"\t{section.number}: {section.name}\n"
            log += f"\t\t{picked_pages}/{section.pg} {round(100 * picked_pages / section.pg, 2)}%\n"

        print(log)
        return log


    @classmethod
    def total_progress(cls, sections: list["Section"]) -> float:
        done_pg = cls.get_done_pages(sections)
        undone_pg = cls.get_undone_pages(sections)
        return round(done_pg / (done_pg + undone_pg) * 100, 2)
    
    @staticmethod
    def avg_performance(sections: list["Section"]) -> float:
        performances = [section.performance for section in sections if section.done]
        return round(sum(performances) / len(performances), 2)

    @staticmethod
    def total_performance(sections: list["Section"]) -> float:
        time_req = time_done = 0
        for section in sections:
            time_req += section.time_req
            if section.done:
                time_done += section.time_done
        return round(time_req / time_done * 100, 2)


def readfile(filename):
    with open(filename) as file:
        data = file.read().split('\n')

    return data

def time_from_string(stime: str) -> int:
    hours = 0
    minutes = 0
    for each in stime.strip().split(' '):
        each = each.strip()
        if '"' in each and each.replace('"', '').isnumeric():
            minutes = int(each.replace('"', ''))
        if "'" in each and each.replace("'", '').isnumeric():
            hours = int(each.replace("'", ''))
    return hours * 60 + minutes

def time_to_string(minutes: Union[float, int]) -> str:
    s = str()

    hours = int(minutes // 60)
    if hours:
        s += f"{hours}' "

    minutes = int(math.ceil(minutes - minutes // 60 * 60))
    if minutes:
        s += f'{minutes}"'

    return s.strip()

def find_next_section(data: list, current: int,
                      chapter_hash_prefix: str,
                      section_hash_prefix: str) -> int:
    """finds the next section or chapter index number"""
    for idx, line in enumerate(data[current:]):
        if line.startswith(chapter_hash_prefix + ' ') or line.startswith(section_hash_prefix + ' '):
            return current + idx
    return len(data)

def get_info(filename, op: Options):
    chapters: dict[str, Chapter] = dict()
    sections: list[Section] = list()
    
    chapter_hash_prefix = op.chapter_no_hashes * '#'
    section_hash_prefix = op.section_no_hashes * '#'

    data = readfile(filename)
    for idx in range(len(data)):
        if op.has_chapters and data[idx].startswith(chapter_hash_prefix + ' '):
            line = data[idx].replace('#', '').strip()
            chapter_name = op.get_chapter_name(line)
            chapter_number = op.get_chapter_number(line)
            chapters[chapter_number] = Chapter(name=chapter_name, number=chapter_number)
            continue

        if not data[idx].startswith(section_hash_prefix + ' '):
                continue

        if not data[idx]:
            continue
        section_string = data[idx]
        section_string = section_string.replace('#', '').strip()
        section_name = op.get_section_name(section_string)
        section_number = op.get_section_number(section_string)
        
        section = Section(name=section_name, number=section_number)

        idl_max = find_next_section(data, idx + 1, chapter_hash_prefix, section_hash_prefix)
        for idl in range(1, idl_max - idx):
            if idx + idl >= len(data):
                break
            line = data[idx + idl]
            if not line:
                continue

            info = line.replace('>', '').replace('`', '').strip()
            if   line.startswith('> `pg: '):
                section.pg = int(info.replace('pg:', '').strip())
            elif line.startswith('> `temp pg: '):
                section.temp_pg = int(info.replace('temp pg:', '').strip())
            elif line.startswith('> `time req: '):
                section.time_req = time_from_string(info.replace('time req:', '').strip())
            elif line.startswith('> `time done: '):
                section.time_done = time_from_string(info.replace('time done:', '').strip()) 
            elif line.startswith('> `performance: '):
                section.performance = int(float(info.replace('performance:', '').replace('%', '').strip()))
            elif line.startswith('> `questions: '):
                section.questions = int(info.replace('questions:', '').strip())
            elif line.startswith('> `questions done: '):
                section.questions_done = int(info.replace('questions done:', '').strip())
            elif line.startswith('> `practice time req: '):
                section.practice_time_req = time_from_string(info.replace('practice time req', '').strip())
            elif line.startswith('> `practice time done: '):
                section.practice_time_done = time_from_string(info.replace('practice time done', '').strip())
            elif line.startswith('> `p-performance: '):
                section.p_performance = int(float(info.replace('p-performance:', '').replace('%', '').strip()))
        
        if op.has_chapters:
            chapter_number = section_number.split('.')[0]
            chapter = chapters[chapter_number]
            chapter.sections[section.number] = section

        sections.append(section)

    if op.has_chapters:
        sections.sort(key=lambda x: (
                int(x.number.split('.')[0]),
                int(x.number.split('.')[1])
        ))
    else:
        sections.sort(key=lambda x: int(x.number.strip()))
    return chapters, sections

def calculate_section_times(sections: list[Section], mpp: float):
    """
    mpp: minutes per page
    returns None: in-place
    """
    for section in sections:
        section.time_req = time_to_string(mpp * section.pg)

### side code
def get_chapter_name_1(chapter_string: str) -> str:
    return ' '.join(chapter_string.split(' ')[2:])

def get_chapter_number_1(chapter_string: str) -> str:
    return chapter_string.split(' ')[1].replace(':', '').strip()

def get_section_name_1(section_string: str) -> str:
    return ' '.join(section_string.split(' ')[1:])

def get_section_number_1(section_string: str) -> str:
    return section_string.split(' ')[0].strip()

def get_section_number_2(section_string: str) -> str:
    return section_string.split(' ')[0].replace('.', '').strip()

options_1 = Options(
    has_chapters=True,
    chapter_no_hashes=4,
    section_no_hashes=5,
    get_chapter_name=get_chapter_name_1,
    get_chapter_number=get_chapter_number_1,
    get_section_name=get_section_name_1,
    get_section_number=get_section_number_1
)

options_2 = Options(
    has_chapters=False,
    section_no_hashes=3,
    get_section_name=get_chapter_name_1,
    get_section_number=get_chapter_number_1
)

options_3 = Options(
    has_chapters=False,
    section_no_hashes=3,
    get_section_name=get_section_name_1,
    get_section_number=get_section_number_2
)

"""usage

from bookmd import *

chapters, sections = get_info('/path/to/file.md', appropriate_option)

"""
