CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

DROP TABLE IF EXISTS Users CASCADE;
DROP TABLE IF EXISTS Pictures CASCADE;
DROP TABLE IF EXISTS Friends CASCADE;
DROP TABLE IF EXISTS Albums CASCADE;
DROP TABLE IF EXISTS Comments CASCADE;
DROP TABLE IF EXISTS Tags CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    password varchar(255),
    firstname varchar(30),
    lastname varchar(30),
    dob date,
    hometown varchar(255),
    gender varchar(6),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  album_id int4,
  INDEX upid_idx (user_id),
  CONSTRAINT abum_pk PRIMARY KEY (albums_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Friends(
   new_friend_id int4,
   follower_id int4,
CONSTRAINT following_fk FOREIGN KEY (following_id) REFERENCES Users(user_id),
CONSTRAINT follower_fk FOREIGN KEY (follower_id) REFERENCES Users(user_id)
);

CREATE TABLE Albums(
	albums_id int4 AUTO_INCREMENT,
	album_name varchar(50),
	albumDate date,
    owner_id int4,
CONSTRAINT albums_pk PRIMARY KEY(albums_id),
CONSTRAINT owner_fk FOREIGN KEY (owner_id) REFERENCES Users(user_id)
);

CREATE TABLE Comments(
	comments_id int4 AUTO_INCREMENT,
    comment_owner int4 NOT NULL,
    text varchar(255),
    commentDate date, 
CONSTRAINT comments_pk PRIMARY KEY(comments_id),
CONSTRAINT comment_owner_fk FOREIGN KEY (comment_owner) REFERENCES Users(user_id)
);

CREATE TABLE Tags
(
  tag varchar(2555),
  photo_id int4,
  Foreign key (photo_id) references Photos(photo_id)
);

INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
