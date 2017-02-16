DROP TABLE IF EXISTS users;

CREATE TABLE users (
  user_id text,
  first_name text,
  last_name text,
  username text unique,
  password text,
  avatar text,
  date_of_birth text,
  type text,
  room text,

  PRIMARY KEY (user_id)
);
