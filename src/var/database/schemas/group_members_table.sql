DROP TABLE IF EXISTS group_members;

CREATE TABLE group_members (
  group_id text,
  member_id text,
  read int,

  FOREIGN KEY (group_id) REFERENCES groups (group_id),
  FOREIGN KEY (member_id) REFERENCES users (user_id)
);
