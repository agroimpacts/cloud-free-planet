--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: SouthAfrica; Type: DATABASE; Schema: -; Owner: ***REMOVED***
--

CREATE DATABASE "SouthAfrica" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE "SouthAfrica" OWNER TO ***REMOVED***;

\connect "SouthAfrica"

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: topology; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA topology;


ALTER SCHEMA topology OWNER TO postgres;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


--
-- Name: ***REMOVED***; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS ***REMOVED*** WITH SCHEMA public;


--
-- Name: EXTENSION ***REMOVED***; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION ***REMOVED*** IS 'PostGIS geometry, geography, and raster spatial types and functions';


--
-- Name: ***REMOVED***_topology; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS ***REMOVED***_topology WITH SCHEMA topology;


--
-- Name: EXTENSION ***REMOVED***_topology; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION ***REMOVED***_topology IS 'PostGIS topology spatial types and functions';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: assignment_data; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE assignment_data (
    assignment_id character varying(120) NOT NULL,
    hit_id character varying(120) NOT NULL,
    worker_id character varying(120) NOT NULL,
    accept_time timestamp without time zone,
    completion_time timestamp without time zone,
    completion_status character varying(20),
    score real,
    comment character varying(2048)
);


ALTER TABLE public.assignment_data OWNER TO ***REMOVED***;

--
-- Name: COLUMN assignment_data.completion_status; Type: COMMENT; Schema: public; Owner: ***REMOVED***
--

COMMENT ON COLUMN assignment_data.completion_status IS 'Should be ''Accepted'', ''Submitted'', ''Abandoned'', ''Returned'', or ''Unsaved''';


--
-- Name: configuration; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE configuration (
    key character varying NOT NULL,
    value character varying,
    comment character varying
);


ALTER TABLE public.configuration OWNER TO ***REMOVED***;

--
-- Name: hit_data; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE hit_data (
    hit_id character varying(120) NOT NULL,
    name character varying(80) NOT NULL,
    create_time timestamp without time zone NOT NULL,
    delete_time timestamp without time zone,
    hit_expired boolean DEFAULT false
);


ALTER TABLE public.hit_data OWNER TO ***REMOVED***;

--
-- Name: kml_data; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE kml_data (
    gid integer NOT NULL,
    kml_type character(1) NOT NULL,
    name character varying(80),
    CONSTRAINT kml_type_check CHECK ((kml_type = ANY (ARRAY['N'::bpchar, 'Q'::bpchar, 'I'::bpchar])))
);


ALTER TABLE public.kml_data OWNER TO ***REMOVED***;

--
-- Name: COLUMN kml_data.kml_type; Type: COMMENT; Schema: public; Owner: ***REMOVED***
--

COMMENT ON COLUMN kml_data.kml_type IS 'Should be N (normal), Q (QAQC), I (initial training)';


--
-- Name: kml_data_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE kml_data_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.kml_data_gid_seq OWNER TO ***REMOVED***;

--
-- Name: kml_data_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE kml_data_gid_seq OWNED BY kml_data.gid;


--
-- Name: newqaqc_sites; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE newqaqc_sites (
    gid integer NOT NULL,
    id numeric,
    name character varying(80) NOT NULL,
    geom geometry(MultiPolygon,97490),
    fields character(1),
    avail character(1)
);


ALTER TABLE public.newqaqc_sites OWNER TO ***REMOVED***;

--
-- Name: newqaqc_sites_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE newqaqc_sites_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.newqaqc_sites_gid_seq OWNER TO ***REMOVED***;

--
-- Name: newqaqc_sites_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE newqaqc_sites_gid_seq OWNED BY newqaqc_sites.gid;


--
-- Name: qaqcfields; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE qaqcfields (
    gid integer NOT NULL,
    __gid numeric(10,0),
    catname character varying(10),
    irrigation character varying(5),
    field_id numeric,
    areaha numeric,
    strata character varying(25),
    mapper character varying(25),
    digitised character varying(100),
    gid_1 numeric(10,0),
    catname_1 character varying(10),
    irrigati_1 character varying(5),
    field_id_1 numeric,
    areaha_1 numeric,
    strata_1 character varying(25),
    mapper_1 character varying(25),
    digitise_1 character varying(100),
    gid_2 numeric(10,0),
    id numeric,
    name character varying(80),
    fldyn numeric(10,0),
    geom geometry(MultiPolygon,97490)
);


ALTER TABLE public.qaqcfields OWNER TO ***REMOVED***;

--
-- Name: qaqcfields_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE qaqcfields_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.qaqcfields_gid_seq OWNER TO ***REMOVED***;

--
-- Name: qaqcfields_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE qaqcfields_gid_seq OWNED BY qaqcfields.gid;


--
-- Name: sa1kgrid; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE sa1kgrid (
    gid integer NOT NULL,
    id numeric,
    name character varying(80),
    fwts numeric,
    geom geometry(MultiPolygon,97490),
    avail character(1)
);


ALTER TABLE public.sa1kgrid OWNER TO ***REMOVED***;

--
-- Name: sa1kgrid_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE sa1kgrid_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sa1kgrid_gid_seq OWNER TO ***REMOVED***;

--
-- Name: sa1kgrid_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE sa1kgrid_gid_seq OWNED BY sa1kgrid.gid;


--
-- Name: sa1kilo; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE sa1kilo (
    gid integer NOT NULL,
    id numeric(10,0),
    name character varying(80),
    geom geometry(MultiPolygon,97490)
);


ALTER TABLE public.sa1kilo OWNER TO ***REMOVED***;

--
-- Name: sa1kilo_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE sa1kilo_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sa1kilo_gid_seq OWNER TO ***REMOVED***;

--
-- Name: sa1kilo_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE sa1kilo_gid_seq OWNED BY sa1kilo.gid;


--
-- Name: sa_flds_wgs_alb_wgs84; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE sa_flds_wgs_alb_wgs84 (
    gid integer NOT NULL,
    catname character varying(10),
    irrigation character varying(5),
    field_id numeric,
    areaha numeric,
    strata character varying(25),
    mapper character varying(25),
    digitised character varying(100),
    geom geometry(MultiPolygon,97490)
);


ALTER TABLE public.sa_flds_wgs_alb_wgs84 OWNER TO ***REMOVED***;

--
-- Name: sa_flds_wgs_alb_wgs84_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE sa_flds_wgs_alb_wgs84_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sa_flds_wgs_alb_wgs84_gid_seq OWNER TO ***REMOVED***;

--
-- Name: sa_flds_wgs_alb_wgs84_gid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: ***REMOVED***
--

ALTER SEQUENCE sa_flds_wgs_alb_wgs84_gid_seq OWNED BY sa_flds_wgs_alb_wgs84.gid;


--
-- Name: system_data; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE system_data (
    key character varying NOT NULL,
    value character varying,
    comment character varying
);


ALTER TABLE public.system_data OWNER TO ***REMOVED***;

--
-- Name: user_maps_gid_seq; Type: SEQUENCE; Schema: public; Owner: ***REMOVED***
--

CREATE SEQUENCE user_maps_gid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_maps_gid_seq OWNER TO ***REMOVED***;

--
-- Name: user_maps; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE user_maps (
    gid integer DEFAULT nextval('user_maps_gid_seq'::regclass) NOT NULL,
    name character varying(80) NOT NULL,
    geom geometry(Polygon,4326) NOT NULL,
    completion_time timestamp without time zone NOT NULL,
    assignment_id character varying(120)
);


ALTER TABLE public.user_maps OWNER TO ***REMOVED***;

--
-- Name: worker_data; Type: TABLE; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE TABLE worker_data (
    worker_id character varying(120) NOT NULL,
    first_time timestamp without time zone NOT NULL,
    last_time timestamp without time zone NOT NULL,
    cumulative_score real DEFAULT 0
);


ALTER TABLE public.worker_data OWNER TO ***REMOVED***;

--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY kml_data ALTER COLUMN gid SET DEFAULT nextval('kml_data_gid_seq'::regclass);


--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY newqaqc_sites ALTER COLUMN gid SET DEFAULT nextval('newqaqc_sites_gid_seq'::regclass);


--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY qaqcfields ALTER COLUMN gid SET DEFAULT nextval('qaqcfields_gid_seq'::regclass);


--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY sa1kgrid ALTER COLUMN gid SET DEFAULT nextval('sa1kgrid_gid_seq'::regclass);


--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY sa1kilo ALTER COLUMN gid SET DEFAULT nextval('sa1kilo_gid_seq'::regclass);


--
-- Name: gid; Type: DEFAULT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY sa_flds_wgs_alb_wgs84 ALTER COLUMN gid SET DEFAULT nextval('sa_flds_wgs_alb_wgs84_gid_seq'::regclass);


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: ***REMOVED***
--

INSERT INTO spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) VALUES (97490, 'sr-org', 7490, 'PROJCS["Albers_Equal_Area_Conic_South_Africa",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["Degree,0.017453292519943295]],PROJECTION["Albers"],PARAMETER["False_Easting",0],PARAMETER["False_Northing",0],PARAMETER["central_meridian",24],PARAMETER{"Standard_Parallel_1",-18],PARAMETER["Standard_Parallel_2",-32],PARAMETER["latitude_of_origin",0],UNIT["Meter",1]]', '+proj=aea +lat_1=-18 +lat_2=-32 +lat_0=0 +lon_0=24 +x_0=0 +y_0=0 +ellps=WGS84 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs');


SET search_path = topology, pg_catalog;

--
-- Data for Name: layer; Type: TABLE DATA; Schema: topology; Owner: postgres
--



--
-- Data for Name: topology; Type: TABLE DATA; Schema: topology; Owner: postgres
--



SET search_path = public, pg_catalog;

--
-- Name: assignment_id_key; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY assignment_data
    ADD CONSTRAINT assignment_id_key PRIMARY KEY (assignment_id);


--
-- Name: configuration_key; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY configuration
    ADD CONSTRAINT configuration_key PRIMARY KEY (key);


--
-- Name: hit_id_pk; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY hit_data
    ADD CONSTRAINT hit_id_pk PRIMARY KEY (hit_id);


--
-- Name: kml_data_key; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY kml_data
    ADD CONSTRAINT kml_data_key PRIMARY KEY (kml_type, gid);


--
-- Name: newqaqc_sites_gid_pk; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY newqaqc_sites
    ADD CONSTRAINT newqaqc_sites_gid_pk PRIMARY KEY (gid);


--
-- Name: qaqcfields_pkey; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY qaqcfields
    ADD CONSTRAINT qaqcfields_pkey PRIMARY KEY (gid);


--
-- Name: sa1kgrid_pkey; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY sa1kgrid
    ADD CONSTRAINT sa1kgrid_pkey PRIMARY KEY (gid);


--
-- Name: sa1kilo_pkey; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY sa1kilo
    ADD CONSTRAINT sa1kilo_pkey PRIMARY KEY (gid);


--
-- Name: sa_flds_wgs_alb_wgs84_pkey; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY sa_flds_wgs_alb_wgs84
    ADD CONSTRAINT sa_flds_wgs_alb_wgs84_pkey PRIMARY KEY (gid);


--
-- Name: system_data_key; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY system_data
    ADD CONSTRAINT system_data_key PRIMARY KEY (key);


--
-- Name: user_maps_gid_pk; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY user_maps
    ADD CONSTRAINT user_maps_gid_pk PRIMARY KEY (gid);


--
-- Name: worker_data_worker_id_pk; Type: CONSTRAINT; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

ALTER TABLE ONLY worker_data
    ADD CONSTRAINT worker_data_worker_id_pk PRIMARY KEY (worker_id);


--
-- Name: assignment_data_worker_id_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE INDEX assignment_data_worker_id_idx ON assignment_data USING btree (worker_id);


--
-- Name: hit_data_delete_time_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE INDEX hit_data_delete_time_idx ON hit_data USING btree (delete_time);


--
-- Name: name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE UNIQUE INDEX name_idx ON kml_data USING btree (name);


--
-- Name: newqaqc_sites_name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE UNIQUE INDEX newqaqc_sites_name_idx ON newqaqc_sites USING btree (name);


--
-- Name: qaqcfields_name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE INDEX qaqcfields_name_idx ON qaqcfields USING btree (name);


--
-- Name: sa1kgrid_name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE UNIQUE INDEX sa1kgrid_name_idx ON sa1kgrid USING btree (name);


--
-- Name: sa1kilo_name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE UNIQUE INDEX sa1kilo_name_idx ON sa1kilo USING btree (name);


--
-- Name: user_maps_name_idx; Type: INDEX; Schema: public; Owner: ***REMOVED***; Tablespace: 
--

CREATE INDEX user_maps_name_idx ON user_maps USING btree (name);


--
-- Name: geometry_columns_delete; Type: RULE; Schema: public; Owner: ***REMOVED***
--

CREATE RULE geometry_columns_delete AS ON DELETE TO geometry_columns DO INSTEAD NOTHING;


--
-- Name: geometry_columns_insert; Type: RULE; Schema: public; Owner: ***REMOVED***
--

CREATE RULE geometry_columns_insert AS ON INSERT TO geometry_columns DO INSTEAD NOTHING;


--
-- Name: geometry_columns_update; Type: RULE; Schema: public; Owner: ***REMOVED***
--

CREATE RULE geometry_columns_update AS ON UPDATE TO geometry_columns DO INSTEAD NOTHING;


--
-- Name: assignment_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY user_maps
    ADD CONSTRAINT assignment_id_fk FOREIGN KEY (assignment_id) REFERENCES assignment_data(assignment_id) ON DELETE RESTRICT;


--
-- Name: hit_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY assignment_data
    ADD CONSTRAINT hit_id_fk FOREIGN KEY (hit_id) REFERENCES hit_data(hit_id) ON DELETE RESTRICT;


--
-- Name: name_fk; Type: FK CONSTRAINT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY hit_data
    ADD CONSTRAINT name_fk FOREIGN KEY (name) REFERENCES kml_data(name) ON DELETE RESTRICT;


--
-- Name: worker_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: ***REMOVED***
--

ALTER TABLE ONLY assignment_data
    ADD CONSTRAINT worker_id_fk FOREIGN KEY (worker_id) REFERENCES worker_data(worker_id) ON DELETE RESTRICT;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

