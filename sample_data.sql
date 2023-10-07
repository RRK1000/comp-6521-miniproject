--
-- PostgreSQL database dump
--

-- Dumped from database version 14.9 (Debian 14.9-1.pgdg120+1)
-- Dumped by pg_dump version 14.9 (Debian 14.9-1.pgdg120+1)

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
-- Name: products; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_type character varying NOT NULL,
    ann character varying NOT NULL
);


ALTER TABLE public.products OWNER TO admin;

--
-- Name: regions; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.regions (
    region_id integer NOT NULL,
    region_name character varying NOT NULL,
    ann character varying NOT NULL
);


ALTER TABLE public.regions OWNER TO admin;

--
-- Name: routes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.routes (
    route_id integer NOT NULL,
    region_from integer NOT NULL,
    region_to integer NOT NULL,
    supplier integer NOT NULL,
    product integer NOT NULL,
    ann character varying
);


ALTER TABLE public.routes OWNER TO admin;

--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    supplier_name character varying NOT NULL,
    ann character varying
);


ALTER TABLE public.suppliers OWNER TO admin;

--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.products (product_id, product_type, ann) FROM stdin;
1	ELECTRONICS	p1
2	MEDICAL	p2
3	APPLIANCES	p3
4	ELECTRONICS	p4
5	APPLIANCES	p5
6	BEAUTY	p6
7	BEAUTY	p7
8	MEDICAL	p8
9	APPLIANCES	p9
10	MEDICAL	p10
11	BEAUTY	p11
12	HOUSEHOLD	p12
13	ELECTRONICS	p13
14	APPLIANCES	p14
15	MEDICAL	p15
16	BEAUTY	p16
17	ELECTRONICS	p17
18	APPLIANCES	p18
19	HOUSEHOLD	p19
20	MEDICAL	p20
21	HOUSEHOLD	p21
22	APPLIANCES	p22
23	HOUSEHOLD	p23
24	ELECTRONICS	p24
25	MEDICAL	p25
26	APPLIANCES	p26
27	HOUSEHOLD	p27
28	APPLIANCES	p28
29	ELECTRONICS	p29
30	ELECTRONICS	p30
31	ELECTRONICS	p31
32	APPLIANCES	p32
33	APPLIANCES	p33
34	BEAUTY	p34
35	MEDICAL	p35
36	HOUSEHOLD	p36
37	ELECTRONICS	p37
38	ELECTRONICS	p38
39	HOUSEHOLD	p39
40	ELECTRONICS	p40
41	MEDICAL	p41
42	HOUSEHOLD	p42
43	BEAUTY	p43
44	ELECTRONICS	p44
45	APPLIANCES	p45
46	BEAUTY	p46
47	BEAUTY	p47
48	HOUSEHOLD	p48
49	APPLIANCES	p49
\.


--
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.regions (region_id, region_name, ann) FROM stdin;
1	AMERICAS	r1
2	EUROPE	r2
3	ASIA	r3
4	AFRICA	r4
5	OCEANIA	r5
\.


--
-- Data for Name: routes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.routes (route_id, region_from, region_to, supplier, product, ann) FROM stdin;
1	3	2	1	26	x1
2	5	3	2	30	x2
3	3	2	3	38	x3
4	2	2	4	44	x4
5	3	4	5	22	x5
6	3	4	6	11	x6
7	1	2	7	34	x7
8	2	2	8	5	x8
9	5	3	9	29	x9
10	2	1	10	43	x10
11	4	2	11	16	x11
12	5	5	12	24	x12
13	5	2	13	7	x13
14	1	4	14	41	x14
15	1	3	15	17	x15
16	3	4	16	21	x16
17	2	1	17	5	x17
18	1	5	18	9	x18
19	2	5	19	34	x19
20	4	2	20	27	x20
21	2	5	21	24	x21
22	4	3	22	32	x22
23	2	4	23	23	x23
24	1	3	24	28	x24
25	4	1	25	14	x25
26	5	5	26	6	x26
27	1	4	27	31	x27
28	5	5	28	7	x28
29	1	5	29	16	x29
30	3	4	30	6	x30
31	4	2	31	1	x31
32	1	5	32	3	x32
33	1	5	33	40	x33
34	1	4	34	20	x34
35	3	3	35	47	x35
36	2	2	36	9	x36
37	3	4	37	14	x37
38	5	1	38	48	x38
39	5	5	39	8	x39
40	4	5	40	49	x40
41	1	1	41	46	x41
42	1	2	42	3	x42
43	5	2	43	26	x43
44	1	5	44	13	x44
45	1	4	45	1	x45
46	3	5	46	11	x46
47	3	5	47	9	x47
48	4	2	48	25	x48
49	1	2	49	48	x49
50	5	3	50	8	x50
51	5	2	51	3	x51
52	5	1	52	11	x52
53	4	2	53	36	x53
54	1	2	54	24	x54
55	1	5	55	28	x55
56	1	5	56	14	x56
57	4	1	57	46	x57
58	5	1	58	45	x58
59	1	1	59	37	x59
60	2	3	60	28	x60
61	4	5	61	29	x61
62	3	2	62	29	x62
63	2	1	63	24	x63
64	4	2	64	29	x64
65	4	3	65	26	x65
66	4	1	66	33	x66
67	1	5	67	45	x67
68	4	1	68	3	x68
69	2	2	69	43	x69
70	2	3	70	31	x70
71	4	1	71	39	x71
72	1	1	72	38	x72
73	1	5	73	46	x73
74	2	1	74	9	x74
75	3	3	75	31	x75
76	3	4	76	27	x76
77	5	5	77	14	x77
78	1	5	78	36	x78
79	5	1	79	3	x79
80	4	3	80	13	x80
81	2	5	81	7	x81
82	4	2	82	28	x82
83	1	1	83	17	x83
84	3	5	84	42	x84
85	4	4	85	37	x85
86	1	3	86	30	x86
87	1	1	87	49	x87
88	1	1	88	35	x88
89	5	2	89	5	x89
90	2	4	90	30	x90
91	1	2	91	8	x91
92	4	5	92	28	x92
93	2	3	93	25	x93
94	4	2	94	41	x94
95	5	4	95	43	x95
96	5	5	96	14	x96
97	3	1	97	7	x97
98	3	3	98	33	x98
99	3	2	99	48	x99
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.suppliers (supplier_id, supplier_name, ann) FROM stdin;
1	SUPPLIER_1	s1
2	SUPPLIER_2	s2
3	SUPPLIER_3	s3
4	SUPPLIER_4	s4
5	SUPPLIER_5	s5
6	SUPPLIER_6	s6
7	SUPPLIER_7	s7
8	SUPPLIER_8	s8
9	SUPPLIER_9	s9
10	SUPPLIER_10	s10
11	SUPPLIER_11	s11
12	SUPPLIER_12	s12
13	SUPPLIER_13	s13
14	SUPPLIER_14	s14
15	SUPPLIER_15	s15
16	SUPPLIER_16	s16
17	SUPPLIER_17	s17
18	SUPPLIER_18	s18
19	SUPPLIER_19	s19
20	SUPPLIER_20	s20
21	SUPPLIER_21	s21
22	SUPPLIER_22	s22
23	SUPPLIER_23	s23
24	SUPPLIER_24	s24
25	SUPPLIER_25	s25
26	SUPPLIER_26	s26
27	SUPPLIER_27	s27
28	SUPPLIER_28	s28
29	SUPPLIER_29	s29
30	SUPPLIER_30	s30
31	SUPPLIER_31	s31
32	SUPPLIER_32	s32
33	SUPPLIER_33	s33
34	SUPPLIER_34	s34
35	SUPPLIER_35	s35
36	SUPPLIER_36	s36
37	SUPPLIER_37	s37
38	SUPPLIER_38	s38
39	SUPPLIER_39	s39
40	SUPPLIER_40	s40
41	SUPPLIER_41	s41
42	SUPPLIER_42	s42
43	SUPPLIER_43	s43
44	SUPPLIER_44	s44
45	SUPPLIER_45	s45
46	SUPPLIER_46	s46
47	SUPPLIER_47	s47
48	SUPPLIER_48	s48
49	SUPPLIER_49	s49
50	SUPPLIER_50	s50
51	SUPPLIER_51	s51
52	SUPPLIER_52	s52
53	SUPPLIER_53	s53
54	SUPPLIER_54	s54
55	SUPPLIER_55	s55
56	SUPPLIER_56	s56
57	SUPPLIER_57	s57
58	SUPPLIER_58	s58
59	SUPPLIER_59	s59
60	SUPPLIER_60	s60
61	SUPPLIER_61	s61
62	SUPPLIER_62	s62
63	SUPPLIER_63	s63
64	SUPPLIER_64	s64
65	SUPPLIER_65	s65
66	SUPPLIER_66	s66
67	SUPPLIER_67	s67
68	SUPPLIER_68	s68
69	SUPPLIER_69	s69
70	SUPPLIER_70	s70
71	SUPPLIER_71	s71
72	SUPPLIER_72	s72
73	SUPPLIER_73	s73
74	SUPPLIER_74	s74
75	SUPPLIER_75	s75
76	SUPPLIER_76	s76
77	SUPPLIER_77	s77
78	SUPPLIER_78	s78
79	SUPPLIER_79	s79
80	SUPPLIER_80	s80
81	SUPPLIER_81	s81
82	SUPPLIER_82	s82
83	SUPPLIER_83	s83
84	SUPPLIER_84	s84
85	SUPPLIER_85	s85
86	SUPPLIER_86	s86
87	SUPPLIER_87	s87
88	SUPPLIER_88	s88
89	SUPPLIER_89	s89
90	SUPPLIER_90	s90
91	SUPPLIER_91	s91
92	SUPPLIER_92	s92
93	SUPPLIER_93	s93
94	SUPPLIER_94	s94
95	SUPPLIER_95	s95
96	SUPPLIER_96	s96
97	SUPPLIER_97	s97
98	SUPPLIER_98	s98
99	SUPPLIER_99	s99
\.


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (region_id);


--
-- Name: routes routes_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pk PRIMARY KEY (route_id);


--
-- Name: suppliers suppliers_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pk PRIMARY KEY (supplier_id);


--
-- Name: routes routes_products_product_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_products_product_id_fk FOREIGN KEY (product) REFERENCES public.products(product_id);


--
-- Name: routes routes_regions_region_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_regions_region_id_fk FOREIGN KEY (region_from) REFERENCES public.regions(region_id);


--
-- Name: routes routes_regions_region_id_fk2; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_regions_region_id_fk2 FOREIGN KEY (region_to) REFERENCES public.regions(region_id);


--
-- Name: routes routes_suppliers_supplier_id_fk; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_suppliers_supplier_id_fk FOREIGN KEY (supplier) REFERENCES public.suppliers(supplier_id);


--
-- PostgreSQL database dump complete
--

