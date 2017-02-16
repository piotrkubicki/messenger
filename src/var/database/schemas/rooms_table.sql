DROP TABLE IF EXISTS rooms;

CREATE TABLE rooms (
  room_id text,
  first_user_id text,
  second_user_id text,
  room_name text,

  PRIMARY KEY (room_id),
  FOREIGN KEY (first_user_id) REFERENCES users (user_id),
  FOREIGN KEY (second_user_id) REFERENCES users (user_id)
);
