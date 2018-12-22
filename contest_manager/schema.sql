BEGIN TRANSACTION;

-- a table of registered users (admins)
CREATE TABLE IF NOT EXISTS `user` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    -- login name
    `username` TEXT NOT NULL UNIQUE,
    `password` TEXT NOT NULL,
    -- human-readable name
    `name` TEXT NOT NULL
);
INSERT INTO `user` VALUES (1,'test','hunter2','Testy McTesterson');
INSERT INTO `user` VALUES (2,'cqmag','qrzdx','CQ Magazine ');

-- a table listing contests and information about them
CREATE TABLE IF NOT EXISTS `contest` (
    `id` INTEGER PRIMARY KEY AUTOINCREMENT,
    -- contest creator account id
    `created_by` INTEGER NOT NULL,
    -- a list of account ids that can admin the contest (stored as text with
        -- SQLite
    `admins` TEXT NOT NULL,
    -- the human-readable name of the contest
    `name` TEXT NOT NULL,
    -- start date and time of the contest
    `start_date` TIMESTAMP NOT NULL,
    -- end date and time of the contest
    `end_date` TIMESTAMP NOT NULL,
    -- date and time logs are due
    `log_due_date` TIMESTAMP NOT NULL,
    -- categories for the contest, as json string
    `categories` TEXT NOT NULL,
    -- formula for scoring, as text
    `score_formula` TEXT NOT NULL,
    -- the contest exchange
    `exchange` TEXT NOT NULL,
    -- modes allowed in the contest
    `modes` TEXT NOT NULL,
    -- bands allowed in the contest
    `bands` TEXT NOT NULL,
    -- a listing of multipliers as a json string
    `multipliers` TEXT NOT NULL,
    -- any other rules not covered by other columns
    `rules` TEXT NOT NULL,
    FOREIGN KEY(`created_by`) REFERENCES `user`(`id`)
);
INSERT INTO `contest` VALUES (
    1,
    1,
    '1,2',
    'YARC QSO Party',
    '2018-12-01 14:00:00',
    '2018-12-01 02:59:00',
    '2020-01-01 00:00:00',
    '{ "categories": [ "Single-Op QRP", "Single-Op Low", "Single-Op High", "Multi-Single Low", "Multi-Single High", "Multi-Multi Low", "Multi-Multi High" ], "descriptions": { "Single-Op": "One Operator, One Transmitter", "Multi-Single": "Multiple Operators, One Transmitter", "Multi-Multi": "Multiple Operators, Multiple Transmitters", "QRP": "< 15W", "Low": "< 200W", "High": "< 1500W" } }',
    '$$\text{Score} = N_{mults} \left( 3 N_{Phone QSOs} + 2 N_{CW QSOs} + 1 N_{Digital QSOs} \right)$$',
    'Age and QTH',
    'Phone, CW, Digital',
    '160, 80, 40, 20, 15, 10, 6, 2, 1.25, and 0.70 meters.',
    'list of mults',
    '# skfsjkdfkd

**AJKLSDFKLASLDASDKKSk** ja *ksdfjksdfjs* kfkk
sdfjklkt test rules');

--INSERT INTO `contest` VALUES (2,1,'Overdue QSO Party','1984-01-01 00:00:00','2000-12-31 00:00:00','2000-12-31 01:00:00','Totalitarian Government Type','');
--INSERT INTO `contest` VALUES (3,2,'CQ WW RTTY WPX Contest','2019-02-09 00:00:00','2019-02-10 23:59:00','2038-01-01 23:59:00','RST + Serial No','');

CREATE TABLE IF NOT EXISTS `uploads` (
  `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
  `contest_id`  INTEGER NOT NULL,
  `time`  TIMESTAMP NOT NULL,
  `filename`  TEXT NOT NULL,
  `email`  TEXT NOT NULL,
  `name`  TEXT NOT NULL,
  `claimed_score`  INTEGER NOT NULL,
  `callsign`  TEXT NOT NULL,
  `operator_callsigns`  TEXT NOT NULL,
  `station_callsign`  TEXT NOT NULL,
  `club_name`  TEXT,
  `category_assisted`  TEXT NOT NULL,
  `category_power`  TEXT NOT NULL,
  `category_band`  TEXT NOT NULL,
  `category_mode`  TEXT NOT NULL,
  `category_operator`  TEXT NOT NULL,
  `category_transmitter`  TEXT NOT NULL,
  `category_station`  TEXT NOT NULL,
  `category_time`  TEXT NOT NULL,
  `category_overlay`  TEXT,
  FOREIGN KEY(`contest_id`) REFERENCES `contest`(`id`)
);
COMMIT;
