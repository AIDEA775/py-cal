"""Run all with: $ for m in {1..12}; do python3 py-cal2.py <year> $m; done

Usage:
  py-cal.py <year> <month> [options]
  py-cal.py (-h | --help)

Options:
  -b RGB   Color of background [default: 424242]
  -c FILE  Path to icalendar of birthdays [default: birthdays.ics]
  -f FILE  Path to icalendar of holidays [default: holidays.ics]
"""
from docopt import docopt
from PIL import Image, ImageDraw, ImageFont
from icalendar import Calendar, Event
import calendar
import datetime
import locale
import os
from colour import Color

locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')
calendar.setfirstweekday(calendar.SUNDAY)

# x -> dia de semana
# y \|/ filaa
# 7016 x 4961 px is A4 at 600 DPI
width = 4961
height = 7016
week_off = 400
w_box = width / 7.0
h_box = (height - week_off) / 5.0
box_off = 10

# Init
args = docopt(__doc__, version='py-cal 2.0')

year = int(args['<year>'])
month = int(args['<month>'])
birthdays = args['-c']
holidays = args['-f']
background = '#' + args['-b']

matrix = calendar.monthcalendar(year, month)
cal = [[0 for x in range(7)] for y in range(5)] 
for y in range(5):
    for x in range(7):
        day = matrix[y][x]
        if day == 0:
            cal[y][x] = None
        else:
            cal[y][x] = datetime.date(year, month, day)

# check previous month
if month != 1:
    previous = calendar.monthcalendar(year, month-1)
    if len(previous) == 6:
        # last days from previous month
        for i, day in enumerate(previous[5]):
            if day != 0:
                cal[i][0] = datetime.date(year, month-1, day)

# Birthday list
fnt_notes = ImageFont.truetype('Lato-Medium.ttf', 44)

birth_emoji = Image.open('./birth_emoji.png', 'r')
g = open(birthdays, 'rb')
gcal = Calendar.from_ical(g.read())

birth_list = []
for c in gcal.walk():
    if c.name == "VEVENT":
        day = c.decoded('dtstart')
        birth_text = str(c.get('summary')).replace("Cumpleaños de ", "").upper()
        birth_text = birth_text[:22] + (birth_text[22:] and '…')
        birth_list.append((day, birth_text))
g.close()

g = open(holidays, 'rb')
gcal = Calendar.from_ical(g.read())
holiday_list = []
for c in gcal.walk():
    if c.name == "VEVENT":
        day = c.decoded('dtstart')
        holiday_text = str(c.get('summary')).upper()
        holiday_text = holiday_text[:24] + (holiday_text[24:] and '…')
        if day.year == year:
            holiday_list.append((day, holiday_text))
g.close()

fnt_days = ImageFont.truetype('Merriweather_Black.ttf', 400)

img = Image.new('RGB', (width, height), color=background)
d = ImageDraw.Draw(img)

def get_point(x, y, x_off, y_off=None):
    if y_off is None:
        y_off = x_off
    return (int(x*w_box + x_off), int(y*h_box + y_off + week_off))

def get_box_points(x, y):
    return [get_point(x, y, box_off), get_point(x+1, y+1, -box_off)]

def get_day_style(colum):
    if colum == 0 or colum == 6:
        return '#ff006e'
    else:
        return 'black'

def draw_day(x, y, date):
    day_text = str(date.day)
    w_day, h_day = d.textsize(day_text, font=fnt_days)
    # padding of 0.25
    w_padding = (w_box - w_day) / 4

    d.rectangle(get_box_points(x, y), fill='white')
    d.text(get_point(x, y, w_padding, -10), day_text, font=fnt_days, fill=get_day_style(x))


def draw_notes(x, y, date):
    i = 1

    for b in [b for b in holiday_list if b[0] == date]:
        holiday_text = b[1]
        h_padding = h_box-100*i
        d.text(get_point(x, y, 30, h_padding), holiday_text, font=fnt_notes, fill='black')
        i += 1

    for b in [b for b in birth_list if b[0] == date]:
        birth_text = b[1]
        h_padding = h_box-100*i
        img.paste(birth_emoji, get_point(x, y, 30, h_padding), birth_emoji)
        d.text(get_point(x, y, 100, h_padding), birth_text, font=fnt_notes, fill='black')
        i += 1


# Draw days
for y in range(5):
    for x in range(7):
        date = cal[y][x]
        if date is not None:
            draw_day(x, y, date)
            draw_notes(x, y, date)


# Draw month and year names
text_month = calendar.month_abbr[month].upper()
text_year = str(year)[-2:]

font_size = 300
fnt_month = ImageFont.truetype('NovaMono.ttf', 400)
fnt_year = ImageFont.truetype('Merriweather_Black.ttf', 600)

w_month, h_month = d.textsize(text_month, font=fnt_month)
w_year, h_year = d.textsize(text_year, font=fnt_year)

# two empty space in the first column
if sum(matrix[0]) <= sum(range(6)):
    x, y = 0, 0
else: # empty space in the last column
    x, y = 5, 4

h_padding = (h_box - h_month - h_year) / 3
w_padding = (2*w_box - max(w_month, w_year)) / 2

d.text(get_point(x, y, w_padding, h_padding), text_month, font=fnt_month, fill='white', anchor=1000)
d.text(get_point(x, y, w_padding, h_padding + h_month - 100), text_year, font=fnt_year, fill='white')


# Draw days names
fnt_week = ImageFont.truetype('NovaMono.ttf', 200)
for i in range(7):
    text_week = calendar.day_abbr[(calendar.firstweekday() + i) % 7].upper()
    w_week, h_week = d.textsize(text_week, font=fnt_week)
    d.text(get_point(i, 0, (w_box - w_week) / 2, -week_off*0.75), text_week, font=fnt_week, fill='white')


# Save
path = "{}/{}.png".format(year, month)
print('Generate into {}'.format(path))
os.makedirs(os.path.abspath(os.path.dirname(path)), exist_ok=True)

img.save(path, "PNG")