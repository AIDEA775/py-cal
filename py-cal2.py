"""Run all with: $ for m in {1..12}; do python3 py-cal.py <year> $m; done

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

# x -> day of week
# y \|/ row
# 7016 x 4961 px is A4 at 600 DPI
width = 4961
height = 7016
week_off = 400
w_box = width / 7.0
h_box = (height - week_off) / 5.0
box_off = 4

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
                cal[0][i] = datetime.date(year, month-1, day)

# Birthday list
g = open(birthdays, 'rb')
gcal = Calendar.from_ical(g.read())

birth_list = []
for c in gcal.walk():
    if c.name == "VEVENT":
        day = c.decoded('dtstart')
        day = day.replace(year = year)
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
        holiday_text = str(c.get('summary')).upper().split()

        # split long holidays
        i = 0
        text = [""]
        for h in holiday_text:
            if len(text[i]) + len(h) + 1 < 24:
                text[i] += " " + h
            else:
                i += 1
                text.append(h)
        if day.year == year:
            for t in text:
                holiday_list.append((day, t))
g.close()


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


fnt_days = ImageFont.truetype('fonts/Lato-Regular.ttf', 400)

def draw_day(x, y, date):
    day_text = str(date.day)
    w_day, h_day = d.textsize(day_text, font=fnt_days)

    w_padding = (w_box - w_day) / 2

    d.rectangle(get_box_points(x, y), fill='white')
    d.text(get_point(x, y, w_padding, -30), day_text, font=fnt_days, fill=get_day_style(x))


fnt_notes = ImageFont.truetype('fonts/Lato-Medium.ttf', 50)
birth_emoji = Image.open('./birth_emoji.png', 'r')

def draw_notes(x, y, date):
    i = 1

    today_births = [b for b in birth_list if b[0] == date]
    for b in today_births:
        birth_text = b[1]
        w_name, h_name = d.textsize(birth_text, font=fnt_notes)
        h_padding = h_box-80*i
        d.text(get_point(x, y, (w_box-w_name)/2, h_padding), birth_text, font=fnt_notes, fill='black')
        i += 1

    if today_births:
        img.paste(birth_emoji, get_point(x, y, (w_box-64)/2, h_box-80*i), birth_emoji)
    
    i = 1
    for b in [b for b in holiday_list if b[0] == date]:
        holiday_text = b[1]
        w_text, h_text = d.textsize(holiday_text, font=fnt_notes)
        h_padding = 350+80*i
        d.text(get_point(x, y, (w_box-w_text)/2, h_padding), holiday_text, font=fnt_notes, fill='black')
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
text_year = str(year)

font_size = 300
fnt_month = ImageFont.truetype('fonts/Lato-Bold.ttf', 500)
fnt_year = ImageFont.truetype('fonts/Lato-Thin.ttf', 400)

w_month, h_month = d.textsize(text_month, font=fnt_month)
w_year, h_year = d.textsize(text_year, font=fnt_year)

# find empty spaces and center if there are 3 free
sum_row = sum([not d for d in cal[4]])
if sum_row >= 2:
    # two empty space in the last column
    y, x = 4, 4.5 if sum_row >= 3 else 5
else:
    # empty space in the first column
    y, x = 0, 0.5 if sum([not d for d in cal[0]]) >= 3 else 0

h_padding = h_box/2 - h_month
w_padding = (2*w_box - w_month) / 2

w_diff = (w_year - w_month) / 2

d.text(get_point(x, y, w_padding, h_padding), text_month, font=fnt_month, fill='white', anchor=1000)
d.text(get_point(x, y, w_padding - w_diff, h_padding + h_month), text_year, font=fnt_year, fill='white')


# Draw days names
fnt_week = ImageFont.truetype('fonts/Lato-Semibold.ttf', 200)
for i in range(7):
    text_week = calendar.day_abbr[(calendar.firstweekday() + i) % 7].capitalize()
    w_week, h_week = d.textsize(text_week, font=fnt_week)
    d.text(get_point(i, 0, (w_box - w_week) / 2, -week_off*0.75), text_week, font=fnt_week, fill='white')


# Save
path = "{}/{}.png".format(year, month)
print('Generate into {}'.format(path))
os.makedirs(os.path.abspath(os.path.dirname(path)), exist_ok=True)

img.save(path, "PNG")
