#!/usr/bin/python3

import csv
import click
import re
import math
import tomli
import os
import subprocess
import pprint


from watson2sf import configFiles
from string import Template
from datetime import datetime, timedelta, date
from pathlib import Path
from importlib.metadata import version
__version__ = version(__package__)


entryTemplate = Template(('[\\"$name\\",\\"$caseNumber\\",\\"$minutes\\",'
                          '\\"$date\\",\\"9:00 AM\\",\\"$note\\"]'))
projectCaseFormat = re.compile(r"^sf-([0-9]{8})$")
tagCaseFormat = re.compile(r"^[0-9]{8}$")
roundingDelta = timedelta(minutes=15)
pp = pprint.PrettyPrinter()


def round_dt(dt, delta):
    return datetime.min + math.ceil((dt - datetime.min) / delta) * delta


def extractCaseNumber(project, tags):
    caseNumber = None

    if projectCaseFormat.match(project):
        caseNumber = projectCaseFormat.match(project).group(1)
    elif tagCaseFormat.match(tags):
        caseNumber = tags
    else:
        print(f"No valid case number found for {project} or {tags}")
        while not caseNumber:
            caseNumberInput = input("Enter case number: ")
            if tagCaseFormat.match(caseNumberInput):
                caseNumber = caseNumberInput
            else:
                print(f"{caseNumberInput} isn't a valid SalesForce case")

    return caseNumber


def extractMinutesWorked(startTimeStr, stopTimeStr):
    startTime = datetime.strptime(startTimeStr, '%Y-%m-%d %H:%M:%S')
    roundedStart = round_dt(startTime, roundingDelta)
    stopTime = datetime.strptime(stopTimeStr, '%Y-%m-%d %H:%M:%S')
    roundedStop = round_dt(stopTime, roundingDelta)

    minutes = int((roundedStop - roundedStart).total_seconds() / 60)

    return minutes


def extractDate(dateString):
    dateObject = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S')

    return dateObject.strftime('%-m/%-d/%Y')


def generate_json_output(ctx, timecards: dict) -> str:
    json_output = '"['
    for key, value in timecards.items():
        case_number = key[1]
        minutes = value[0]
        notes = ', '.join([*set(value[1])])
        work_date = key[0]

        json_output += entryTemplate.substitute(name=ctx.obj['NAME'],
                                                caseNumber=case_number,
                                                minutes=minutes,
                                                date=work_date,
                                                note=notes)
        json_output += ','

        if ctx.obj['DEBUG']:
            print(f'{work_date}, {case_number}, {minutes}, {notes}')

    # Remove comma after last entry
    json_output = json_output.rstrip(',')
    json_output += ']"'

    if ctx.obj['DEBUG']:
        print(json_output)

    return json_output


def generateSeleniumScript(ctx, timecards: dict):

    jsonOutput = generate_json_output(ctx, timecards)
    with open(ctx.obj['TEMPLATE'], "r") as timecards:
        lines = timecards.readlines()
    if not ctx.obj['OUTPUT']:
        filename = f"{os.environ.get('HOME')}/timecards.side"
    else:
        filename = ctx.obj['OUTPUT']
    with open(filename, "w") as timecards:
        for line in lines:
            timecards.write(re.sub(r'^#TIMECARDS_JSON#$', jsonOutput, line))
    print(f"New Selenium script can be found here: {filename}")


def firstRun():
    configDir = Path("~/.config/watson2sf").expanduser()
    configFile = Path("~/.config/watson2sf/config.toml").expanduser()
    templateFile = Path("~/.config/watson2sf/new-timecards.side").expanduser()

    if not configDir.exists():
        print(f"Creating directory {configDir}")
        configDir.mkdir()
    if not configFile.exists():
        print(f"Creating file {configFile}")
        name = input("Enter SalesForce display name for config file: ")
        configTemplate = Template(configFiles.configFileContents)
        with configFile.open('w') as f:
            f.write(configTemplate.substitute(sfname=name, templatePath=templateFile))
    if not templateFile.exists():
        print(f"Creating file {templateFile}")
        with templateFile.open('w') as f:
            f.write(configFiles.templateFileContents)


def ignore_frame(ctx, row):
    # row['tags'] is either a comma-separated string of tags or a single tag
    row_tags = [x.strip() for x in row['tags'].split(',')]
    for tag in row_tags:
        if tag in ctx.obj['CONFIG']['ignore']['tags']:
            print('Found ignore tag, skipping')
            return True
    return False


def processCSV(ctx, csvLines):
    reader = csv.DictReader(csvLines)

    timecards = dict()
    total_minutes = 0
    for row in reader:
        if not ignore_frame(ctx, row):
            caseNumber = extractCaseNumber(row['project'], row['tags'])
            minutes = extractMinutesWorked(row['start'], row['stop'])
            workDate = extractDate(row['start'])
            total_minutes += minutes

            if (workDate, caseNumber) not in timecards.keys():
                timecards[(workDate, caseNumber)] = (minutes, [row['note']])
                if ctx.obj['DEBUG']:
                    print(f'Creating timecards[({workDate}, {caseNumber})] = {timecards[(workDate, caseNumber)]}')
            else:
                new_note = timecards[(workDate, caseNumber)][1]
                new_note.append(row['note'])
                new_minutes = timecards[(workDate, caseNumber)][0] + minutes
                timecards[(workDate, caseNumber)] = (new_minutes, new_note)
                if ctx.obj['DEBUG']:
                    print(f'Updated timecards[({workDate}, {caseNumber})] = {timecards[(workDate, caseNumber)]}')

    if ctx.obj['DEBUG']:
        pp.pprint(timecards)
        print(f'Total minutes: {total_minutes}')

    generateSeleniumScript(ctx, timecards)


@click.group(invoke_without_command=True)
@click.option('-n', '--name', help='Full SF username')
@click.option('-t', '--template', help='Path to Selenium template')
@click.option('-o', '--output', help='File to write Selenium script to')
@click.option('-d', '--debug', help='Debug output', is_flag=True, show_default=True, default=False)
@click.option('-v', '--version', help='Print version', is_flag=True, show_default=True, default=False)
@click.pass_context
def cli(ctx, name, template, output, debug, version):
    if version:
        click.echo(__version__)
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())        

    ctx.ensure_object(dict)

    # Check if we have ever run before, and if not, setup the initial config files
    firstRun()

    # Try to read configuration file
    config = None
    try:
        with open(f'{os.environ.get("HOME")}/.config/watson2sf/config.toml', 'rb') as inputFile:
            config = tomli.load(inputFile)
    except IOError as e:
        print('Configuration file not found, using sane defaults')

    # Default to command line first
    if not name and config:
        # Try for the config file
        name = config['user']['name']
    else:
        # Prompt the user
        name = input("Enter SalesForce display name: ")

    # Default to command line
    if not template and config:
        # Try for the config file
        template = config['watson2sf']['template']
    else:
        # Prompt the user
        template = input("Full path to template: ")

    ctx.obj['NAME'] = name
    ctx.obj['TEMPLATE'] = template
    ctx.obj['OUTPUT'] = output
    ctx.obj['DEBUG'] = debug
    ctx.obj['CONFIG'] = config


@cli.command()
@click.pass_context
def today(ctx):
    # get CSV lines by running `watson log -d -s`
    lines = subprocess.run(['watson', 'log', '-d', '-s'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    processCSV(ctx, lines)


@cli.command()
@click.argument('file', type=click.File('r'))
@click.pass_context
def file(ctx, file):
    # read csv file and create array of lines, just like the output
    processCSV(ctx, file)


@cli.command()
@click.argument('start')
@click.argument('end')
@click.pass_context
def range(ctx, start, end):
    lines = subprocess.run(['watson', 'log', '--from', start, '--to', end, '-s'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    processCSV(ctx, lines)


@cli.command()
@click.argument('day')
@click.pass_context
def day(ctx, day):
    lines = subprocess.run(['watson', 'log', '--from', day, '--to', day, '-s'], stdout=subprocess.PIPE).stdout.decode('utf-8').splitlines()
    processCSV(ctx, lines)
