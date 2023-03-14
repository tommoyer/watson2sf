#!/usr/bin/python3

import csv
import click


@click.command()
@click.option('-n', '--name', help='Full SF username')
@click.option('-d', '--date',
              help='Date to create input for, defaults to today')
def cli(name, date):
    with open('timecards.2023-03-14.csv', 'r', ) as csvInput:
        reader = csv.DictReader(csvInput)
        for row in reader:
            print(f"{row['project']} : {row['start']} - {row['stop']}")


