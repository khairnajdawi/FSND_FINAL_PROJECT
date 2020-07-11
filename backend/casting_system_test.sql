--
-- PostgreSQL database dump
--

-- Dumped from database version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)
-- Dumped by pg_dump version 10.12 (Ubuntu 10.12-0ubuntu0.18.04.1)

-- Started on 2020-07-10 22:59:12 EEST

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 600 (class 1247 OID 17560)
-- Name: moviescategory; Type: TYPE; Schema: public; Owner: khairallah
--

CREATE TYPE public.moviescategory AS ENUM (
    'Action',
    'Adveture',
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


--
-- TOC entry 603 (class 1247 OID 17588)
-- Name: moviesrating; Type: TYPE; Schema: public; Owner: khairallah
--

CREATE TYPE public.moviesrating AS ENUM (
    'G',
    'PG',
    'PG13',
    'R'
);


--
-- TOC entry 597 (class 1247 OID 17546)
-- Name: moviestatus; Type: TYPE; Schema: public; Owner: khairallah
--

CREATE TYPE public.moviestatus AS ENUM (
    'Directing',
    'Filming',
    'Published',
    'ReadyToPublish',
    'Recruting',
    'Review'
);



SET default_tablespace = '';

SET default_with_oids = false;

--
-- TOC entry 198 (class 1259 OID 17535)
-- Name: Actors; Type: TABLE; Schema: public; Owner: khairallah
--

CREATE TABLE public."Actors" (
    id integer NOT NULL,
    name character varying NOT NULL,
    is_available boolean DEFAULT true NOT NULL,
    age integer NOT NULL,
    gender character varying NOT NULL
);



--
-- TOC entry 197 (class 1259 OID 17533)
-- Name: Actors_id_seq; Type: SEQUENCE; Schema: public; Owner: khairallah
--

CREATE SEQUENCE public."Actors_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 2957 (class 0 OID 0)
-- Dependencies: 197
-- Name: Actors_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: khairallah
--

ALTER SEQUENCE public."Actors_id_seq" OWNED BY public."Actors".id;


--
-- TOC entry 201 (class 1259 OID 17608)
-- Name: MovieActors; Type: TABLE; Schema: public; Owner: khairallah
--

CREATE TABLE public."MovieActors" (
    movie_id integer NOT NULL,
    actor_id integer NOT NULL
);



--
-- TOC entry 200 (class 1259 OID 17599)
-- Name: Movies; Type: TABLE; Schema: public; Owner: khairallah
--

CREATE TABLE public."Movies" (
    id integer NOT NULL,
    name character varying NOT NULL,
    movie_status public.moviestatus NOT NULL,
    movie_category public.moviescategory NOT NULL,
    movie_rating public.moviesrating NOT NULL
);



--
-- TOC entry 199 (class 1259 OID 17597)
-- Name: Movies_id_seq; Type: SEQUENCE; Schema: public; Owner: khairallah
--

CREATE SEQUENCE public."Movies_id_seq"
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 2958 (class 0 OID 0)
-- Dependencies: 199
-- Name: Movies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: khairallah
--

ALTER SEQUENCE public."Movies_id_seq" OWNED BY public."Movies".id;


--
-- TOC entry 2811 (class 2604 OID 17538)
-- Name: Actors id; Type: DEFAULT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."Actors" ALTER COLUMN id SET DEFAULT nextval('public."Actors_id_seq"'::regclass);


--
-- TOC entry 2813 (class 2604 OID 17602)
-- Name: Movies id; Type: DEFAULT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."Movies" ALTER COLUMN id SET DEFAULT nextval('public."Movies_id_seq"'::regclass);





--
-- TOC entry 2817 (class 2606 OID 17544)
-- Name: Actors Actors_pkey; Type: CONSTRAINT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."Actors"
    ADD CONSTRAINT "Actors_pkey" PRIMARY KEY (id);


--
-- TOC entry 2821 (class 2606 OID 17612)
-- Name: MovieActors MovieActors_pkey; Type: CONSTRAINT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_pkey" PRIMARY KEY (movie_id, actor_id);


--
-- TOC entry 2819 (class 2606 OID 17607)
-- Name: Movies Movies_pkey; Type: CONSTRAINT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."Movies"
    ADD CONSTRAINT "Movies_pkey" PRIMARY KEY (id);




--
-- TOC entry 2822 (class 2606 OID 17613)
-- Name: MovieActors MovieActors_actor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_actor_id_fkey" FOREIGN KEY (actor_id) REFERENCES public."Actors"(id);


--
-- TOC entry 2823 (class 2606 OID 17618)
-- Name: MovieActors MovieActors_movie_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: khairallah
--

ALTER TABLE ONLY public."MovieActors"
    ADD CONSTRAINT "MovieActors_movie_id_fkey" FOREIGN KEY (movie_id) REFERENCES public."Movies"(id);


-- Completed on 2020-07-10 22:59:12 EEST

--
-- PostgreSQL database dump complete
--

