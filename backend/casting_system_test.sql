
CREATE TYPE public.moviescategory AS ENUM (
    'Action',
    'Adventure',
    'Animation',
    'Comedy',
    'Crime',
    'Documentary',
    'Drama',
    'Family',
    'History',
    'Horror',
    'Musical',
    'Romance',
    'SciFi'
);


CREATE TYPE public.moviesrating AS ENUM (
    'G',
    'PG',
    'PG13',
    'R'
);

CREATE TABLE public."Actors" (
    id integer NOT NULL,
    name character varying NOT NULL,
    age integer NOT NULL,
    gender character varying NOT NULL
);


CREATE SEQUENCE public."Actors_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



ALTER SEQUENCE public."Actors_id_seq" OWNED BY public."Actors".id;


CREATE TABLE public."MovieActors" (
    movie_id integer NOT NULL,
    actor_id integer NOT NULL
);


CREATE TABLE public."Movies" (
    id integer NOT NULL,
    title character varying NOT NULL,
    release_date timestamp without time zone NOT NULL,
    movie_category public.moviescategory NOT NULL,
    movie_rating public.moviesrating NOT NULL
);


CREATE SEQUENCE public."Movies_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public."Movies_id_seq" OWNED BY public."Movies".id;



ALTER TABLE ONLY public."Actors" ALTER COLUMN id SET DEFAULT nextval('public."Actors_id_seq"'::regclass);



ALTER TABLE ONLY public."Movies" ALTER COLUMN id SET DEFAULT nextval('public."Movies_id_seq"'::regclass);



COPY public."Actors" (id, name, age, gender) FROM stdin;
1	Will Smith	51	Male
2	Leonardo DiCaprio	45	Male
3	Scarlett Johansson	35	Female
4	Brad Pitt	56	Male
5	Angelina Jolie	45	Femal
6	Robert Downey Jr	55	Male
\.


COPY public."Movies" (id, title, release_date, movie_category, movie_rating) FROM stdin;
1	I Am Legend	2007-12-05 00:00:00	SciFi	PG
2	The Revenant	2016-01-06 00:00:00	Adventure	PG
3	The Black Widow	2020-04-24 00:00:00	Action	PG13
4	Ad Astra	2019-09-19 00:00:00	SciFi	PG
5	Salt	2010-09-19 00:00:00	Action	R
\.


COPY public."MovieActors" (movie_id, actor_id) FROM stdin;
1	1
2	2
3	3
4	4
5	5
\.



SELECT pg_catalog.setval('public."Actors_id_seq"', 6, true);


SELECT pg_catalog.setval('public."Movies_id_seq"', 5, true);



ALTER TABLE ONLY public."Actors"
    ADD CONSTRAINT "Actors_pkey" PRIMARY KEY (id);



ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_pkey" PRIMARY KEY (movie_id, actor_id);


ALTER TABLE ONLY public."Movies"
    ADD CONSTRAINT "Movies_pkey" PRIMARY KEY (id);


ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_actor_id_fkey" FOREIGN KEY (actor_id) REFERENCES public."Actors"(id);

ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES public."Movies"(id);

