#!/bin/python
"""

Generate calendar in ./calendar_<year>/<month_num>_<month_name>.svg

Docs
calendar: https://docs.python.org/2/library/calendar.html
locale: https://docs.python.org/2/library/locale.html#locale.setlocale
svgwrite: https://svgwrite.readthedocs.io/en/master/index.html
color-palette: https://material.io/guidelines/style/color.html

"""
import calendar
import json
import locale
import svgwrite
import os
from collections import defaultdict
from svgwrite.mixins import Transform

year = 2017

calendar.setfirstweekday(calendar.SUNDAY)
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

month_list = calendar.month_name
day_list = list(calendar.day_abbr)
day_list.insert(0, day_list.pop())

width = 1052
height = 744

box_size = 129
box_offset = 5

color_gray = '#bdbdbd'
color_blue = '#546e7a'
color_day = '#424242'
color_weekend = '#ce93d8'

font = "font-family:'Noto Sans';"\
       "text-align:center;"\
       "text-anchor:middle;"

font_title = font + "font-size:90px;"\
                    "fill:" + color_blue + ";"\
                    "fill-opacity:0.39215687;"
font_day_name = font + "font-size:44;"\
                    "fill:" + color_blue + ";"\
                    "fill-opacity:1;"
font_day = font + "font-size:30px;"\
                  "fill:" + color_day + ";"\
                  "fill-opacity:1;"
font_day_bg = font + "font-size:100px;"\
                     "fill:" + color_day + ";"\
                     "fill-opacity:0.19607843;"
font_weekend = font + "font-size:30px;"\
                      "fill:" + color_weekend + ";"\
                      "fill-opacity:1;"
font_weekend_bg = font + "font-size:100px;"\
                         "fill:" + color_weekend + ";"\
                         "fill-opacity:0.3137255;"
font_birthday = font + "font-size:13px;"\
                  "fill:#B71C1C;"\
                  "fill-opacity:1;"

birthday_icon = '🎂 '

with open('birthdays.json') as file:
    data = json.load(file)

birthday_list = defaultdict(list)
for people in data:
    birthday_list[people['birthday']].append(people['name'])


def get_box_coor(x, y):
    return x * (box_size + box_offset), y * (box_size + box_offset)


def get_filename(month):
    return 'calendar_{}/{}_{}.svg'.format(year, month, month_list[month])


def get_day_style(colum):
    if colum == 0 or colum == 6:
        return font_weekend, font_weekend_bg
    else:
        return font_day, font_day_bg


def draw_line(dwg, group):
    group.add(dwg.line(start=(0, box_size),
                       end=(box_size, 0),
                       stroke=color_gray,
                       stroke_width=2))


def draw_box(dwg, group):
    group.add(dwg.rect(insert=(0, 0),
                       size=(box_size, box_size),
                       stroke=color_gray,
                       stroke_width=2))
    group.update({'fill-opacity': 0})


def draw_birthday(dwg, group, month, day):
    birthdays = birthday_list.get('{}-{}'.format(month, day))
    if birthdays:
        for i in range(len(birthdays)):
            group.add(dwg.text(birthday_icon + birthdays[i],
                               insert=(64, 120 - 20 * i),
                               style=font_birthday))


def draw_split_day(dwg, group, number, x):
    box = group.add(dwg.g(id='box_split_{}_{}'.format(x, 4)))
    box.translate(get_box_coor(x, 4))

    draw_box(dwg, box)
    draw_line(dwg, box)

    style, style_bg = get_day_style(x)

    box.add(dwg.text(str(number), insert=(107, 120), style=style))
    return box


def draw_normal_day(dwg, group, number, x, y):
    box = group.add(dwg.g(id='box_{}_{}'.format(x, y)))
    box.translate(get_box_coor(x, y))

    draw_box(dwg, box)

    style, style_bg = get_day_style(x)

    box.add(dwg.text(str(number), insert=(25, 30), style=style))
    box.add(dwg.text(str(number), insert=(64.6, 100), style=style_bg))
    return box


def draw_day_matix(dwg, month):
    group = dwg.add(dwg.g(id='day_matix'))
    group.translate(20, 62)

    matrix = calendar.monthcalendar(year, month)

    for week in range(len(matrix)):
        for day in range(7):
            number = matrix[week][day]
            if number != 0:
                if week == 5:
                    box = draw_split_day(dwg, group, number, day)
                else:
                    box = draw_normal_day(dwg, group, number, day, week)

                draw_birthday(dwg, box, month, number)


def draw_day_names(dwg):
    group = dwg.add(dwg.g(id='day_names'))
    group.translate(75, 48)

    for i in range(0, len(day_list)):
        group.add(dwg.text(day_list[i],
                           insert=(i * (box_size + box_offset), 0),
                           style=font_day_name))


def draw_month(dwg, month):
    dwg.add(dwg.text(month_list[month],
                     insert=(250, -962),
                     style=font_title)).rotate(90)


def draw_year(dwg):
    dwg.add(dwg.text(str(year),
                     insert=(614, -962),
                     style=font_title)).rotate(90)


def make_canvas(month):
    return svgwrite.Drawing(get_filename(month), (width, height), debug=True)


def draw(month):
    print('Generating {}...'.format(month_list[month]))
    dwg = make_canvas(month)

    draw_year(dwg)
    draw_month(dwg, month)
    draw_day_names(dwg)
    draw_day_matix(dwg, month)

    dwg.save()


def main():
    path = os.path.abspath(os.path.dirname(get_filename(0)))
    print('Generate into {}\n'.format(path))
    os.makedirs(path, exist_ok=True)

    for month in range(1, 13):
        draw(month)

    print('\nDone.')


if __name__ == '__main__':
    main()
