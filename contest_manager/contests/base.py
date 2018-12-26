"""Base classes for a contest definition file."""


class ContestSubmission:
    """ContestSubmission represents an individual log upload entry. It
    contains attributes necessary to verify its validity for the individual
    contest.

    Attributes:
        callsign (str): Callsign exchanged in contest.
        name (str): Name of the (legal) person of the station.
        claimed_score (int): User-submitted claimed score.
        operator_callsigns (str): Operator callsigns delimited by space.
        station_callsign (str): Station's actual callsign.
        club_name (str): Contest club name.
        category_assisted (str)
        category_power (str)
        category_band (str)
        category_mode (str)
        category_operator (str)
        category_transmitter (str)
        category_station (str)
        category_time (str)
        category_overlay (str)
        log (cabrillo.Cabrillo): The parsed log file containing QSOs.

    """

    def __init__(self, callsign, name, claimed_score, operator_callsigns,
                 station_callsign, club_name, category_assisted,
                 category_power, category_band, category_mode,
                 category_operator, category_transmitter, category_station,
                 category_time, category_overlay, log):
        """The constructor ensures all needed class attributes are set.

        Arguments:
            cf. class attributes.
        """
        self.callsign = callsign
        self.name = name
        self.claimed_score = claimed_score
        self.operator_callsigns = operator_callsigns
        self.station_callsign = station_callsign
        self.club_name = club_name
        self.category_assisted = category_assisted
        self.category_power = category_power
        self.category_band = category_band
        self.category_mode = category_mode
        self.category_operator = category_operator
        self.category_transmitter = category_transmitter
        self.category_station = category_station
        self.category_time = category_time
        self.category_overlay = category_overlay
        self.log = log

    def verify(self):
        """Verify if the given submission is valid for this contest.

        Category validity checks etc. should be done here.

        Example:
            >>> good.verify()
            >>> bad.verify()
            'Invalid power category HIGH. This is a QRP contest'

        Returns:
            None: The log is considered valid and should proceed to be stored.
            str: The log is considered invalid. The reason is given in the str
                and should be presented to the user.
        """
        raise NotImplementedError

    def make_category(self):
        """Generate a prettified category string based on given categories.

        As most contests do not use all valid Cabrillo categories, this method
        provides an opportunity to generate a short-form name of the entrance
        category.

        Example:
            >>> submission.make_category()
            'SINGLE-OP SCHOOL'

        Returns:
            str: Name of category.
        """
        raise NotImplementedError

    def __eq__(self, other):
        """Provides implementation of submission equality.

        To facilitate deduplication, two submissions of the same callsign
        sent during the contest is considered to be equal.

        Arguments:
            other (ContestSubmission): Object compared against.

        Returns:
            boolean
        """
        return self.callsign == other.callsign

    def __hash__(self):
        """Provides hash code for deduplication.

        Returns:
            int
        """
        return id(self.callsign)

    def __str__(self):
        """Provides client-friendly names for the class.

        Returns:
            str: <ClassName C4LLSIGN>
        """
        return '<{} {}>'.format(self.__class__.__name__, self.callsign)


class ContestScorer:
    """ContestScorer holds all submissions of the contest to be scored.

    This class is made necessary by the convention that QSOs must be
    cross-referenced and it is not enough to simply score by a station itself.

    Attribute:
        submissions (set): Contains unique ContestSubmission objects.
    """

    def __init__(self, submissions):
        """Constructs the ContestScorer with all submissions.

        Arguments:
            submissions (set): Contains unique ContestSubmission objects.
        """
        self.submissions = submissions

    def score(self):
        """Scores the contest.

        Example:
            >>> scorer.score()
            {<ContestSubmission object at 0xabcde>: 12345}

        Returns:
            dict: Map from ContestSubmission to final score.
        """
        raise NotImplementedError
