"""Contains e-mail templates for log submission receipts."""

OK_TEMPLATE = """We're happy to confirm that we have received your logs for
{name}. Your receipt number for this particular submission is {receipt}.

Please save this e-mail, which contains your receipt number, at least
until the scores have been released for this contest. It contains 
important confirmation that you have submitted logs through our system in
the unlikely event of a sudden loss of data.

If you have made a mistake in submitting your log, please feel free to
resubmit your logs using the same submission form. The prior entry will be
replaced and only the last submission will be candidate for scoring. As a
security consideration, we will send a notification to the email address
left in the prior submission to let them know that their submission has
been replaced.

On behalf of the contest organizers, the Contest Manager thanks you for
participating in the contest and hopes that you had great fun.

73,
The WY4RC Contest Manager
{time}
"""

DUP_TEMPLATE = """
We are letting you know that your log submission for {name} has been
replaced by a new one. If this replacement is made by you, there is no need
to take further action, and we thank you for providing corrected
information.

If you did not resubmit logs, someone else might have submitted logs on
behalf of you without authorization. We encourage you submit your log
immediately before the log due date, and provide the following receipt
number to the site administrator *immediately* in order for them to take
corrective action:

{receipt}.


73
The WY4RC Contest Manager
{time}
"""
