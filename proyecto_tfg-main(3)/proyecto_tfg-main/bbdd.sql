create database clinica_dental;

use clinicadental;

create table Users (
	id_user integer PRIMARY KEY,
    username varchar(20) not null unique,
    user_password varchar(20) not null,
    image_profile varchar(200)
);