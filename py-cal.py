"""Run all with: $ for m in {1..12}; do python3 py-cal.py <year> $m; done

Usage:
  py-cal.py <year> <month> [options]
  py-cal.py (-h | --help)

Options:
  -b RGB   Color of background [default: c9c9c9]
  -a RGB   Color of accent [default: 424242]
  -c FILE  Path to icalendar of birthdays [default: birthdays.ics]
  -f FILE  Path to icalendar of holidays [default: holidays.ics]
"""
from docopt import docopt
from PIL import Image, ImageDraw, ImageFont
from icalendar import Calendar
import calendar
from datetime import date
import datetime
import locale
import os
import numpy as np
from itertools import chain
import textwrap

locale.setlocale(locale.LC_ALL, "es_AR.UTF-8")
calendar.setfirstweekday(calendar.SUNDAY)

"""
x -> day of week
y \|/ row
"""
# A4 at 600 DPI
# width, height = 4961, 7016

# A4 at 300 DPI
width, height = 2480, 3508

week_off = 200
box_off = 1
box_w = (width - box_off) / 7.0
box_h = (height - week_off) / 5.0
box_text_len = 18
reserved = "year_month"

# Init
args = docopt(__doc__, version="py-cal 2.0")

year = int(args["<year>"])
month = int(args["<month>"])
birthdays = args["-c"]
holidays = args["-f"]
background = args["-b"]
accent = args["-a"]

def get_point(x, y):
    return (int(x * box_w + box_off), int(y * box_h + week_off))


def get_calendar():
    """
    Returns a matrix with the days of month
    """
    f = np.vectorize(lambda day: date(year, month, day) if day != 0 else None)

    matrix = calendar.monthcalendar(year, month)
    cal = f(matrix)[:5]

    # check previous month
    if month != 1:
        prev = calendar.monthcalendar(year, month - 1)
        if len(prev) == 6:
            to_date = np.vectorize(
                lambda day: date(year, month - 1, day) if day != 0 else None
            )
            cal[0] = np.where(cal[0] == None, to_date(prev[5]), cal[0])

    # Reserve space for banner
    first_row = sum([not d for d in cal[0]])
    if first_row >= 2:
        # reserve space in the first column
        size = min(first_row, 3)
        cal[0][:size] = reserved
    else:
        # reserve space in the last column
        last_row = sum([not d for d in cal[-1]])
        size = min(last_row, 3)
        cal[-1][-size:] = reserved
    # print(cal)
    return cal


def get_all_birtdays():
    """
    Return a list with birthdays
    """
    g = open(birthdays, "rb")
    gcal = Calendar.from_ical(g.read())

    birth_list = []
    for c in gcal.walk():
        if c.name == "VEVENT":
            day = c.decoded("dtstart")
            day = day.replace(year=year)
            text = "• " + str(c.get("summary"))
            lines = textwrap.wrap(text, box_text_len)
            birth_list.append((day, "\n".join(lines)))
    g.close()
    return birth_list


def get_all_holidays():
    g = open(holidays, "rb")
    gcal = Calendar.from_ical(g.read())
    holiday_list = []
    for c in gcal.walk():
        if c.name == "VEVENT":
            day = c.decoded("dtstart")
            if day.month != month:
                continue

            text = "• " + c.get("summary")
            lines = textwrap.wrap(text, box_text_len)
            holiday_list.append((day, "\n".join(lines)))
    g.close()
    return holiday_list


def center_pad(long, short):
    return (long - short) / 2


class CalendarDraw:
    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.img = Image.new("RGBA", (int(self.width), int(self.height)))
        self.d = ImageDraw.Draw(self.img)


class Empty(CalendarDraw):
    def __init__(self):
        super(Empty, self).__init__(box_w - box_off, box_h - box_off)

    def draw(self):
        return Image.new("RGBA", (int(self.width), int(self.height)), color="white")


class DayNumber(CalendarDraw):
    font_day = ImageFont.truetype("fonts/RobotoMono-Regular.ttf", 200)
    font_notes = ImageFont.truetype("fonts/RobotoSlab-Regular.ttf", 36)
    birth_emoji = Image.open("./birth_emoji.png", "r")

    def __init__(self, xy, date, holidays=[], birthdays=[]):
        self.xy = xy
        self.number = str(date.day)
        self.holidays = holidays
        self.birthdays = birthdays
        super(DayNumber, self).__init__(box_w - box_off, box_h - box_off)

    def draw(self):
        # Background
        self.d.rectangle(self.box_points(), fill="white")

        # Day number
        self.d.text(
            (self.center_w(), -30),
            self.number,
            font=self.font_day,
            fill=self.day_fill(),
            anchor="ma",
        )

        # Holydays
        self.draw_top_note()

        # Birthdays
        if len(self.birthdays) > 0:
            self.draw_bottom_note()
        return self.img

    def box_points(self):
        return [0, 0, self.width, self.height]

    def day_size(self):
        return self.d.textsize(self.number, font=self.font_day)

    def day_fill(self):
        column = self.xy[0]
        if column == 0 or column == 6:
            return "#ff006e"
        else:
            return "black"

    def draw_top_note(self):
        text = "\n".join([t for (_, t) in self.holidays])
        _, day_h = self.day_size()
        self.d.multiline_text(
            (self.center_w(), day_h),
            text,
            font=self.font_notes,
            fill="black",
            anchor="ma",
            align="center",
        )

    def draw_bottom_note(self):
        text = "\n".join([t for (_, t) in self.birthdays])
        _, text_h = self.note_size(text)
        self.d.multiline_text(
            (self.center_w(), self.height - text_h),
            text,
            font=self.font_notes,
            fill="black",
            anchor="ms",
            align="center",
        )
        _, line_h = self.note_size("a")
        emoji_point = [
            int(center_pad(self.width, self.birth_emoji.width)),
            int(self.height - text_h - line_h * 1.5 - self.birth_emoji.height),
        ]
        self.img.paste(self.birth_emoji, emoji_point, mask=self.birth_emoji)

    def note_size(self, text):
        return self.d.multiline_textsize(text, font=self.font_notes)

    def center_w(self):
        return self.width / 2


class YearMonth(CalendarDraw):
    font_month = ImageFont.truetype("fonts/Lato-Bold.ttf", 250)
    font_year = ImageFont.truetype("fonts/Lato-Thin.ttf", 200)

    def __init__(self, size):
        self.text_month = calendar.month_abbr[month].upper()
        self.text_year = str(year)
        super(YearMonth, self).__init__(box_w * size, box_h)

    def draw(self):
        self.d.text(
            self.center(),
            self.text_month,
            font=self.font_month,
            fill="white",
            anchor="mb",
        )
        self.d.text(
            self.center(),
            self.text_year,
            font=self.font_year,
            fill="white",
            anchor="ma",
        )
        return self.img

    def center(self):
        return [self.width / 2, self.height / 2]


class DayName(CalendarDraw):
    font = ImageFont.truetype("fonts/RobotoMono-Light.ttf", 100)

    def __init__(self, pos, name):
        self.pos = pos
        self.name = name
        super(DayName, self).__init__(width, week_off)

    def draw(self):
        self.d.text(self.point(), self.name, font=self.font, fill="white", anchor="mm")
        return self.img

    def point(self):
        return (box_w * (self.pos + 0.5), self.height / 2)


class CoolCirle(CalendarDraw):
    """
    Make a image with one circle with diameter = diameter
    and one ring with diameter = diameter + padding
    """

    def __init__(self, diameter, padding, line=10):
        self.diameter = diameter
        self.padding = padding
        self.line = line
        size = int(diameter + line)
        super(CoolCirle, self).__init__(size, size)

    def draw(self):
        self.d.ellipse(self.fill_point(), fill=accent)
        self.d.ellipse(self.oultline_point(), outline=accent, width=self.line)
        return self.img

    def fill_point(self):
        size = self.diameter - self.padding
        return [self.padding, self.padding, size, size]

    def oultline_point(self):
        return [0, 0, self.diameter, self.diameter]


class CoolBackground(CalendarDraw):
    font = ImageFont.truetype("fonts/RobotoSlab-ExtraBold.ttf", 1000)

    def __init__(self, size):
        self.size = size
        self.text = f"{month:02}"
        super(CoolBackground, self).__init__(box_w * size, box_h + week_off)

    def draw(self):
        self.d.text(self.box(), self.text, font=self.font, anchor="mb", fill=accent)
        return self.img

    def box(self):
        return [self.width / 2, self.height]


cal = get_calendar()
birth_list = get_all_birtdays()
holiday_list = get_all_holidays()


def get_next_day():
    for y, week in enumerate(cal):
        for x, day in enumerate(week):
            box = get_point(x, y)
            if isinstance(day, datetime.date):
                births = [b for b in birth_list if b[0] == day]
                holidays = [h for h in holiday_list if h[0] == day]
                draw = DayNumber((x, y), day, holidays, births).draw()
                yield (box, draw)
            elif day is None:
                draw = Empty().draw()
                yield (box, draw)


def get_year_month():
    sum_row = sum([d == reserved for d in cal[0]])
    size = max(sum_row, 3)
    if sum_row >= 2:
        # empty space in the first column
        box = get_point(0, 0)
    else:
        # empty space in the last column
        box = get_point(7 - size, len(cal) - 1)

    # First circle
    background = CoolBackground(size).draw()
    yield (box, background)

    # Later the words
    draw = YearMonth(size).draw()
    yield (box, draw)


def get_day_names():
    for i in range(7):
        text = calendar.day_abbr[(calendar.firstweekday() + i) % 7].upper()
        draw = DayName(i, text).draw()
        yield ((0, 0), draw)


img = Image.new("RGB", (width, height), color=background)
d = ImageDraw.Draw(img)

for (box, draw) in chain(get_year_month(), get_next_day(), get_day_names()):
    # print(box, draw)
    img.paste(draw, box, draw)

# Save
path = "{}/{}.png".format(year, month)
print("Generate into {}".format(path))
os.makedirs(os.path.abspath(os.path.dirname(path)), exist_ok=True)

img.save(path, "PNG")
