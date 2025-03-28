use car_service;
drop table if exists user;

CREATE TABLE user (
    user_id VARCHAR(13) PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
	username VARCHAR(30) NOT NULL,
    email varchar(50) not null,
    password VARCHAR(256) NOT NULL
);

select * from user;