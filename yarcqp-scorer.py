#!/usr/bin/env python3
# (c) 2018 Young Amateurs Radio Club
# Released under the MIT License
# Contributors:
#     - busbr
#     - galengold

import os

# Multipliers are American states + Canadian provinces + DX.
ALL_MULTS = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
             "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
             "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
             "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
             "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY",
             "BC", "AB", "SK", "MB", "ON", "QC", "NB", "NS", "PE", "NL", "YT", "NT", "NU",
             "MX", "DX"]
DEBUG = False


class LogReadException(Exception):
    pass


class Candidate:
    def __init__(self, callsign, cat_op=None, cat_pwr=None, cat_txr=None,
            ops=None, qth=None, qsos=None):
        self.callsign = callsign
        self.qth = qth
        self.qsos = qsos
        self.cat = (cat_op, cat_pwr, cat_txr)
        self.ops = ops

    def verify(self, other_qso):
        for qso in self.qsos:
            if qso.match(other_qso):
                return True

        return False

    def calculate_score(self, all_candidates):
        mults = set()
        points = 0
        verified_qsos = list()
        for qso in self.qsos:
            # If the other person submitted logs, check against it.
            against = None
            for candidate in all_candidates:
                if candidate.callsign == qso.dx:
                    against = candidate

            if against is not None and not against.verify(qso):
                # Checklog failed, skipping.
                if DEBUG:
                    print('{} {} {} skipped due to cross-reference failure.'.format(qso.de, qso.dx, qso.time))
                continue
            elif DEBUG and against is not None:
                print('{} {} {} cross-reference OK.'.format(qso.de, qso.dx, qso.time))

            if qso.de_age > 30 and qso.dx_age > 30:
                if DEBUG:
                    print('{} {} {} skipped due to {} OM working {} OM.'.format(qso.de, qso.dx, qso.time, qso.de_age,
                                                                                qso.dx_age))
                continue

            dupe = False
            for old_qso in verified_qsos:
                # TODO: upgrade checking reliability.
                if old_qso.freq == qso.freq and old_qso.dx == qso.dx and old_qso.mode == qso.mode:
                    # Duplicate QSO found.
                    dupe = True
                    continue
            if dupe:
                if DEBUG:
                    print('{} {} {} skipped due to dupe.'.format(qso.de, qso.dx, qso.time))
                continue

            if qso.dx_qth not in ALL_MULTS:
                # Invalid location exchange, skipping.
                if DEBUG:
                    print('{} {} {} skipped due to invalid location {}.'.format(qso.de, qso.dx, qso.time, qso.dx_qth))
                continue
            else:
                mults.add(qso.dx_qth)

            addition = 0
            if qso.mode in ['FM', 'PH']:
                addition = 3
            elif qso.mode == 'CW':
                addition = 2
            elif qso.mode in ['RY', 'DG']:
                addition = 1
            points += addition
            verified_qsos.append(qso)
            if DEBUG:
                print('{} {} {} +{}pts'.format(qso.de, qso.dx, qso.time, addition))

        if DEBUG:
            print('Raw {}pts * {} Mults {}'.format(points, len(mults), mults))
        return points * len(mults)


class QSO:
    def __init__(self, de, dx, freq, mode, date, time, de_age, de_qth, dx_age, dx_qth):
        self.de = de
        self.dx = dx
        self.freq = freq
        self.mode = mode
        self.date = date
        self.time = time
        self.de_age = int(de_age)
        self.de_qth = de_qth
        self.dx_age = int(dx_age)
        self.dx_qth = dx_qth

    def match(self, qso):
        if qso.dx_age != self.de_age or qso.dx_qth != self.de_qth or qso.mode != self.mode:
            return False

        # This is the most primitive band matching mechanism that
        # you have ever laid your eyes on.
        if self.freq == qso.freq:
            return True
        if len(str(self.freq)) != len(str(qso.freq)):
            return False
        # Yes, there will be edge cases, but hams are honest, right?
        if len(self.freq) < 5:
            # 7200 vs 7100, 3830 vs 3900, etc.
            return str(self.freq)[0:1] == str(qso.freq)[0:1]
        else:
            # 14313 vs 14200, 146520 vs 146500, etc.
            return str(self.freq)[0:2] == str(qso.freq)[0:2]


def load(filename):
    f = open(filename, 'r')

    if not f.readline().startswith('START-OF-LOG'):
        raise LogReadException('Not a Cabrillo file OM.')

    lines = [x.replace('\r', '').split(':') for x in f.read().splitlines()]

    candidate = None
    cat = {'op': '', 'pwr': '', 'txr': '', 'overlay': ''}
    ops = None
    qsos = list()
    for line in lines:
        # Invalid key/value pair.
        if len(line) is not 2:
            raise Exception('Invalid line: ' + str(line))

        # If we caught the callsign, initialize the OM.
        key = line[0].strip()
        value = line[1].strip()
        if key == 'CALLSIGN':
            candidate = Candidate(value)
        elif key == 'CATEGORY-OPERATOR':
            cat['op'] = value
        elif key == 'CATEGORY-POWER':
            cat['pwr'] = value
        elif key == 'CATEGORY-TRANSMITTER':
            cat['txr'] = value
        elif key == 'CATEGORY-OVERLAY':
            cat['overlay'] = value
        elif key == 'OPERATORS':
            ops = value
        elif key == 'QSO':
            qsos.append(parse_qso_line(value))

    if candidate is None:
        raise LogReadException('Never found the son-of-a-gun\'s callsign.')
    candidate.cat = cat
    candidate.ops = ops
    candidate.qsos = qsos

    return candidate


def parse_qso_line(line):
    components = line.split()
    if len(components) is not 10:
        raise LogReadException("Expecting 10 components in QSO line " + str(components))

    return QSO(freq=components[0], mode=components[1], date=components[2],
               time=components[3], de=components[4], de_age=components[5],
               de_qth=components[6], dx=components[7], dx_age=components[8],
               dx_qth=components[9])

def format_results(results):
    call_len_max = max([len(x[0].callsign) for x in results])
    # header
    print(f'| {"Callsign":<10} | {"Overlay":<16} | {"Score":<10} |')
    print(f'|-' + '-'*10 + '-|-' + '-'*16 + '-|-' + '-'*10 + '-|')
    for result in results:
        print(f'| {result[0].callsign:<10} | {result[0].cat["overlay"]:<16} | {result[1]:<10} |')

if __name__ == '__main__':
    candidates = list()

    # directory = input("Directory? ")
    directory = 'yarcqp-w18-logs'
    for _, _, files in os.walk(directory):
        for filename in files:
            try:
                candidates.append(load(os.path.join(directory, filename)))
            except Exception as e:
                print(filename + " excluded due to " + str(e))

    results = [(x, x.calculate_score(candidates)) for x in candidates]
    print("==== DRUM ROLL ====")
    format_results(results)
