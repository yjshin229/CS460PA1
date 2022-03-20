/* Youngjin Shin & Sam Leach */

CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

-- DROP TABLE IF EXISTS Users CASCADE;
-- DROP TABLE IF EXISTS Pictures CASCADE;
-- DROP TABLE IF EXISTS Friends CASCADE;
-- DROP TABLE IF EXISTS Albums CASCADE;
-- DROP TABLE IF EXISTS Comments CASCADE;
-- DROP TABLE IF EXISTS Tags CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email varchar(255) UNIQUE,
    user_pass varchar(255),
    firstname varchar(255),
    lastname varchar(255),
    dob date,
    hometown varchar(255),
    gender varchar(30),
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Albums(
	albums_id int4 AUTO_INCREMENT,
	album_name varchar(50),
	albumDate date,
    owner_id int4,
CONSTRAINT albums_pk PRIMARY KEY(albums_id),
CONSTRAINT owner_fk FOREIGN KEY (owner_id) REFERENCES Users(user_id)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  album_id int4,
  INDEX upid_idx (user_id),
  CONSTRAINT album_fk FOREIGN KEY (album_id) references Albums(albums_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);

CREATE TABLE Friends(
   new_friend_id int4,
   follower_id int4,
CONSTRAINT new_friend_fk FOREIGN KEY (new_friend_id) REFERENCES Users(user_id),
CONSTRAINT follower_fk FOREIGN KEY (follower_id) REFERENCES Users(user_id)
);


CREATE TABLE Comments(
	comments_id int4 AUTO_INCREMENT,
  comment_owner int4 NOT NULL,
  comment_photo_id int4,
  comment_text varchar(255),
  comment_date date, 
CONSTRAINT comments_pk PRIMARY KEY(comments_id),
CONSTRAINT comment_photo_id_fk FOREIGN KEY (comment_photo_id) REFERENCES Pictures(picture_id),
CONSTRAINT comment_owner_fk FOREIGN KEY (comment_owner) REFERENCES Users(user_id)
);

CREATE TABLE Tags
(
  tag varchar(255),
  photo_id int4,
  CONSTRAINT tag_fk FOREIGN KEY (photo_id) REFERENCES Pictures(photo_id)
);

