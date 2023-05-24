#!/usr/bin/python3

import csv
import click
import re
import math
import tomli
import os
import sys
import subprocess


from watson2sf import configFiles
from string import Template
from datetime import datetime, timedelta, date
from pathlib import Path
from string import Template


entryTemplate = Template(('[\\"$name\\",\\"$caseNumber\\",\\"$minutes\\",'
                          '\\"$date\\",\\"9:00 AM\\",\\"$note\\"]'))
projectCaseFormat = re.compile(r"^sf-([0-9]{8})$")
tagCaseFormat = re.compile(r"^[0-9]{8}$")
roundingDelta = timedelta(minutes=15)


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


def generateSeleniumScript(jsonOutput, template, output):
    with open(template, "r") as timecards:
        lines = timecards.readlines()
    if not output:
        filename = f"{os.environ.get('HOME')}/timecards-{date.today().strftime('%Y-%m-%d')}.side"
    else:
        filename = output
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


def processCSV(ctx, csvLines):
    jsonOutput = '"['

    reader = csv.DictReader(csvLines)

    for row in reader:
        caseNumber = extractCaseNumber(row['project'], row['tags'])
        minutes = extractMinutesWorked(row['start'], row['stop'])
        workDate = extractDate(row['start'])
        jsonOutput += entryTemplate.substitute(name=ctx.obj['NAME'],
                                               caseNumber=caseNumber,
                                               minutes=minutes,
                                               date=workDate,
                                               note=row['note'])
        jsonOutput += ','

    # Remove comma after last entry
    jsonOutput = jsonOutput.rstrip(',')
    jsonOutput += ']"'

    generateSeleniumScript(jsonOutput, ctx.obj['TEMPLATE'], ctx.obj['OUTPUT'])


@click.group()
@click.option('-n', '--name', help='Full SF username')
@click.option('-t', '--template', help='Path to Selenium template')
@click.option('-o', '--output', help='File to write Selenium script to')
@click.pass_context
def cli(ctx, name, template, output):
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
