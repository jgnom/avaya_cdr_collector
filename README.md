# avaya_cdr_collector
Script and stored procedure on Postgres plpython3u for received cdr detail from tcp socket Avaya Communication Manager 8.

Checked for Ubuntu Server 18.04 LTS PostgreSQL 14.1
user for work `postgres` with right on db `cdr_collector`

While lose connection beetwin Avaya Communication Manager and server with script, Avaya CM collect on local disk cdr dump. 
And post up connection send all dump in tcp socket.

Confihure service systemctl on linux:
examlpe:
```
[Unit]
Description=cdr_collector service
After=syslog.target

[Service]
Type=simple
ExecStart=/home/user/project/cdr/env/bin/python /home/user/project/cdr/main.py
WorkingDirectory=/home/user/project/cdr/
Restart=always
StandardOutput=syslog
StandardError=syslog

[Install]
WantedBy=multi-user.target

```
## For start and autostart service type:

`systemctl start cdr_collector.service`
`systemctl enable cdr_collector.service`

## table for cdr_collector on postgres:

```
-- Table: public.cdr_collector

-- DROP TABLE IF EXISTS public.cdr_collector;

CREATE TABLE IF NOT EXISTS public.cdr_collector
(
    id bigint NOT NULL DEFAULT nextval('cdr_collector_id_seq'::regclass),
    date date NOT NULL DEFAULT now(),
    "time" character(5) COLLATE pg_catalog."default",
    dur text COLLATE pg_catalog."default",
    calling_number text COLLATE pg_catalog."default",
    dialed_number text COLLATE pg_catalog."default",
    cond_code text COLLATE pg_catalog."default",
    frl integer,
    account_code text COLLATE pg_catalog."default",
    inc_circ_id text COLLATE pg_catalog."default",
    out_circ_id text COLLATE pg_catalog."default",
    access_code_dialed text COLLATE pg_catalog."default",
    access_code_used text COLLATE pg_catalog."default",
    auth_code text COLLATE pg_catalog."default",
    inc_tac text COLLATE pg_catalog."default",
    feat_flag text COLLATE pg_catalog."default",
    att_console text COLLATE pg_catalog."default",
    ins text COLLATE pg_catalog."default",
    ixc text COLLATE pg_catalog."default",
    node_number text COLLATE pg_catalog."default",
    bcc text COLLATE pg_catalog."default",
    ma_uui text COLLATE pg_catalog."default",
    resource_flag text COLLATE pg_catalog."default",
    packet_count text COLLATE pg_catalog."default",
    tsc_flag text COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.cdr_collector
    OWNER to cdr;
```


## plpython3u function for postgresql:

```
-- FUNCTION: public.cdr_unformatted_func_py(text[])

-- DROP FUNCTION IF EXISTS public.cdr_unformatted_func_py(text[]);

CREATE OR REPLACE FUNCTION public.cdr_unformatted_func_py(
	VARIADIC arr text[])
    RETURNS boolean
    LANGUAGE 'plpython3u'
    COST 100
    VOLATILE PARALLEL UNSAFE
AS $BODY$

def put_db_rows(msg):    
    timing = f"{msg[0:2]}:{msg[2:4]}"
    dur = f"{msg[4]}:{msg[5:7]}:{int(msg[7])*6}"
    cond_code = msg[8]
    access_code_dialed = msg[9:13]
    access_code_dialed = access_code_dialed.strip()
    access_code_used = msg[13:17]
    access_code_used = access_code_used.strip()
    dialed_number = msg[17:32]
    dialed_number = dialed_number.strip()
    calling_number = msg[32:42]
    calling_number = calling_number.strip()
    account_code = msg[42:57]
    account_code = account_code.strip()
    auth_code = msg[57:64]
    auth_code = auth_code.strip()
    frl = msg[66]
    frl = frl.strip()
    inc_circ_id = msg[67:70]
    inc_circ_id = inc_circ_id.strip()
    out_circ_id = msg[70:73]
    out_circ_id = out_circ_id.strip()
    feat_flag = msg[73]
    feat_flag = feat_flag.strip()
    att_console = msg[74:78]
    att_console = att_console.strip()
    inc_tac = msg[77:81]
    inc_tac = inc_tac.strip()
    node_number = msg[82:84]
    node_number = node_number.strip()
    ins = msg[84:89]
    ins = ins.strip()
    ixc = msg[89:92]
    ixc = ixc.strip()
    bcc = msg[92]
    bcc = bcc.strip()
    ma_uui = msg[93]
    ma_uui = ma_uui.strip()
    resource_flag = msg[94]
    resource_flag = resource_flag.strip()
    packet_count = msg[95:99]
    packet_count = packet_count.strip()
    tsc_flag = msg[99]
    tsc_flag = tsc_flag.strip()

    plan = plpy.prepare(f"INSERT INTO cdr_collector (time, \
    dur, \
    cond_code, \
    access_code_dialed, \
    access_code_used, \
    dialed_number, \
    calling_number, \
    account_code, \
    auth_code, \
    frl, \
    inc_circ_id, \
    out_circ_id, \
    feat_flag, \
    att_console, \
    inc_tac, \
    node_number, \
    ins, \
    ixc, \
    bcc, \
    ma_uui, \
    resource_flag, \
    packet_count, \
    tsc_flag) \
    VALUES ('{timing}', \
    '{dur}', \
    {cond_code}, \
    '{access_code_dialed}', \
    '{access_code_used}', \
    '{dialed_number}', \
    '{calling_number}', \
    '{account_code}', \
    '{auth_code}', \
    '{frl}', \
    '{inc_circ_id}', \
    '{out_circ_id}', \
    '{feat_flag}', \
    '{att_console}', \
    '{inc_tac}', \
    '{node_number}', \
    '{ins}', \
    '{ixc}', \
    '{bcc}', \
    '{ma_uui}', \
    '{resource_flag}', \
    '{packet_count}', \
    '{tsc_flag}')")

    plpy.execute(plan)

for i in arr:
	put_db_rows(i)

$BODY$;

ALTER FUNCTION public.cdr_unformatted_func_py(text[])
    OWNER TO postgres;

```

## For logging create directory in path /var/log/cdr_collector
`mkdir /var/log/cdr_collector`
`chown user:user /var/log/cdr_collector`
