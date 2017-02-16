DROP TABLE IF EXISTS friend_requests;

CREATE TABLE friend_requests (
  request_id text,
  sender_id text,
  reciever_id text,
  status int,

  PRIMARY KEY (request_id),
  FOREIGN KEY (sender_id) REFERENCES users (user_id),
  FOREIGN KEY (reciever_id) REFERENCES users (user_id)
);
