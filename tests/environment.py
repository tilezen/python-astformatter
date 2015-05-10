
import sys
import re

def before_scenario(context, scenario):
    skipped = True
    for tag in scenario.tags:
        tagvers = re.match(r'^v([0-9]+)[.]([0-9]+)$', tag)
        if tagvers:
            tagvers = [int(v) for v in tagvers.groups()]
            tagversnext = tagvers[:]
            tagversnext[-1] += 1
            if tuple(tagvers) <= sys.version_info < tuple(tagversnext):
                skipped = False
    if skipped:
        scenario.skip(reason='Incorrect python version', require_not_executed=True)
