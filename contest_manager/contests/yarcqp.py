"""Contest definition for the YARC QSO Party.

This version based on rules from:
https://yarc.world/events/contests/2018/09/18/winter-qso-party-2018/

"""
from contest_manager.contests.base import ContestScorer, ContestSubmission

OPERATORS = ['SINGLE-OP', 'MULTI-OP', 'CHECKLOG']
POWER_CODE = {'HIGH': 'H', 'LOW': 'L', 'QRP': 'QRP'}
# Multipliers are American states + Canadian provinces + MX for Mexico + DX.
ALL_MULTS = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
             "BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL", "YT",
             "NT", "NU", "MX", "DX"]


class YARCContestSubmission(ContestSubmission):
    """Definition of a YARC QSO Party submission."""

    def __init__(self, *args, **kwargs):
        """Initialize the submission.

        Arguments:
            See ContestSubmission constructor arguments.
        """
        super(YARCContestSubmission, self).__init__(*args, **kwargs)

    def verify(self):
        """Verify if the given submission is valid for this contest.

        Example:
            >>> good.verify()
            >>> bad.verify()
            'The only valid overlay is ROOKIE or left blank.'

        Returns:
            None: The log is considered valid and should proceed to be stored.
            str: The log is considered invalid. The reason is given in the str
                and should be presented to the user.
         """
        if self.category_operator not in OPERATORS:
            return 'Operator must be one of {}'.format(OPERATORS)

        if self.category_power not in POWER_CODE.keys():
            return 'Power must be one of {}'.format(POWER_CODE.keys())

        if self.category_operator == 'MULTI-OP' and self.category_power == 'QRP':
            return 'You may not be QRP power as a multi-op station.'

        if self.category_station not in ['FIXED', 'SCHOOL']:
            return 'Your station must be FIXED or SCHOOL'

        if self.category_overlay not in ['', 'ROOKIE']:
            return 'The only valid overlay is ROOKIE or left blank.'

        for qso in self.log.qso:
            if len(qso.dx_exch) != 2 or len(qso.de_exch) != 2:
                return 'Exchange must have 2 components only. Note that RST' \
                       ' is not part of the exchange in this contest.'

            try:
                int(qso.dx_exch[0])
                int(qso.de_exch[0])
            except ValueError as e:
                return 'Cannot convert age to integer: {}'.format(str(e))

        return None

    def make_category(self):
        """Make contest entrance category name.

        Returns:
            str: One of:
                - SO-HP
                - SO-LP
                - SO-QRP
                - MS-HP
                - MS-LP
                - MM-HP
                - MM-LP
                - CHECKLOG

        Raises:
            AssertionError: if verify() failed.
        """
        assert self.verify() is None

        if self.category_operator == 'CHECKLOG':
            return 'CHECKLOG'

        result = ''
        if self.category_operator == 'SINGLE-OP':
            result += 'SO-'
        elif self.category_operator == 'MULTI-OP':
            result += 'M'
            if self.category_transmitter == 'ONE':
                result += 'S-'
            else:
                result += 'M-'
        return result + POWER_CODE[self.category_power]


class YARCContestScorer(ContestScorer):
    """Scorer for the YARC QSO Party."""

    def __init__(self, submissions):
        """Constructs the ContestScorer with all submissions.

        Arguments:
            submissions (set): Contains unique ContestSubmission objects.
        """
        super(YARCContestScorer, self).__init__(submissions)

    def score(self):
        """Scores the contest.

        Returns:
            dict: Map from ContestSubmission to final score.
        """
        results = dict()

        # Convert all ages to integers. This is necessary due to a bug in the
        # released N1MM+ logger file that appends 0 to the string of age.
        for submission in self.submissions:
            for qso in submission.log.qso:
                qso.de_exch[0] = int(qso.de_exch[0])
                qso.dx_exch[0] = int(qso.dx_exch[0])

        for submission in self.submissions:
            mults = set()
            points = 0
            verified_qsos = list()

            # Ignore checklogs.
            if submission.category_operator == 'CHECKLOG':
                continue

            for qso in submission.log.qso:
                # If the other person submitted logs, check against it.
                cross_referenced = False
                against = next(
                    (x for x in self.submissions if x.callsign == qso.dx_call),
                    None)
                if against:
                    for dx_qso in against.log.qso:
                        if qso.match_against(dx_qso):
                            cross_referenced = True
                else:
                    # Other log not found, default to pass.
                    cross_referenced = True

                # QSO verification failed, do not give points.
                if not cross_referenced:
                    continue

                # Check for duplicates.
                if qso in verified_qsos:
                    continue

                # Add valid multiplier to set.
                if qso.dx_exch[1] in ALL_MULTS:
                    mults.add(qso.dx_exch[1])

                # Give point based on mode.
                if qso.mo in ['FM', 'PH']:
                    points += 3
                elif qso.mo == 'CW':
                    points += 2
                elif qso.mo in ['RY', 'DG']:
                    points += 1

                # Add QSO to verified QSO list for future dupe checking.
                verified_qsos.append(qso)

            # Final score is raw * mult.
            results[submission] = points * len(mults)

        return results


# PoC manual CLI scorer.
if __name__ == '__main__':
    import os

    from cabrillo.parser import parse_log_file

    submissions = set()

    directory = input("Directory? ")
    for _, _, files in os.walk(directory):
        for filename in files:
            try:
                cab = parse_log_file(os.path.join(directory, filename))
                submissions.add(
                    YARCContestSubmission(cab.callsign, '', '', '', '', '', '',
                                          '', '', '', '', '', '', '', '', cab))
            except Exception as e:
                print(filename + " excluded due to " + str(e))
    print(
        {str(x): y for x, y in YARCContestScorer(submissions).score().items()})
