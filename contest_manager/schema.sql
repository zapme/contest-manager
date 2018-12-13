DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS contest;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  name TEXT NOT NULL
);

CREATE TABLE contest (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created_by INTEGER NOT NULL,
  name TEXT NOT NULL,
  start_date TIMESTAMP NOT NULL,
  end_date TIMESTAMP NOT NULL,
  log_due_date TIMESTAMP NOT NULL,
  exchange TEXT NOT NULL,
  rules TEXT NOT NULL,
  FOREIGN KEY (created_by) REFERENCES user (id)
);

INSERT INTO user (
    username,
    password,
    name
) VALUES (
    'test',
    'hunter2',
    'Testy McTesterson'
);


INSERT INTO contest (
    created_by,
    name,
    start_date,
    end_date,
    log_due_date,
    exchange,
    rules
) VALUES (
    '1',
    'Test Contest',
    DATETIME('2018-01-01 03:00'),
    DATETIME('2018-01-03 02:59'),
    DATETIME('2018-01-07 03:00'),
    'Name',
    '# skfsjkdfkd

    **AJKLSDFKLASLDASDKKSk** ja *ksdfjksdfjs* kfkk
    sdfjklkt test rules'
);

