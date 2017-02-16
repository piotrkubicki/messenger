DROP TABLE IF EXISTS groups;

CREATE TABLE groups (
  group_id text,
  group_name text,
  group_leader_id text,

  PRIMARY KEY (group_id),
  FOREIGN KEY (group_leader_id) REFERENCES users (user_id)
);
