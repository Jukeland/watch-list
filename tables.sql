create table movies(
	movie_id int auto_increment primary key,
	name_ varchar(50),
    type_ varchar(20),
    duration_ time,
    status_ varchar(20)
);

create table genres(
	genre_id int auto_increment primary key,
    genre varchar(25)
);

create table movie_genres(
	movie_genres_id int auto_increment primary key,
    movie_id int,
    genre_id int,
    foreign key (movie_id) references movies(movie_id),
    foreign key (genre_id) references genres(genre_id)
);