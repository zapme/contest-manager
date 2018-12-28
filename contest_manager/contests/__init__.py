"""
This directory stores custom code for each contest, in order to provide
utilities to verify if a log submission is valid for an individual contest,
and to calculate individual scores.
"""

from contest_manager.contests.yarcqp import YARCContestSubmission, \
    YARCContestScorer

ALL_CONTESTS = {
    'yarcqp': (YARCContestSubmission, YARCContestScorer)
}