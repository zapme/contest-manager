BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS `user` (
  `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
  `username`  TEXT NOT NULL UNIQUE,
  `password`  TEXT NOT NULL,
  `name`  TEXT NOT NULL
);
INSERT INTO `user` VALUES (1,'test','hunter2','Testy McTesterson');
INSERT INTO `user` VALUES (2,'cqmag','qrzdx','CQ Magazine ');
CREATE TABLE IF NOT EXISTS `contest` (
  `id`  INTEGER PRIMARY KEY AUTOINCREMENT,
  `created_by`  INTEGER NOT NULL,
  `name`  TEXT NOT NULL,
  `start_date`  TIMESTAMP NOT NULL,
  `end_date`  TIMESTAMP NOT NULL,
  `log_due_date`  TIMESTAMP NOT NULL,
  `exchange`  TEXT NOT NULL,
  `rules`  TEXT NOT NULL,
  FOREIGN KEY(`created_by`) REFERENCES `user`(`id`)
);
INSERT INTO `contest` VALUES (1,1,'YARC QSO Party','2018-12-01 14:00:00','2018-12-01 02:59:00','2020-01-01 00:00:00','Name','# skfsjkdfkd

    **AJKLSDFKLASLDASDKKSk** ja *ksdfjksdfjs* kfkk
    sdfjklkt test rules');
INSERT INTO `contest` VALUES (2,1,'Overdue QSO Party','1984-01-01 00:00:00','2000-12-31 00:00:00','2000-12-31 01:00:00','Totalitarian Government Type','');
INSERT INTO `contest` VALUES (3,2,'CQ WW RTTY WPX Contest','2019-02-09 00:00:00','2019-02-10 23:59:00','2038-01-01 23:59:00','RST + Serial No','');
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