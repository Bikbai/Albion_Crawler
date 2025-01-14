create table guild
(
    internal_id bigint primary key generated always AS IDENTITY NOT NULL,
    id varchar NOT NULL,
    guild_name varchar NOT NULL,
    founder_id varchar,
    founder_name varchar,
    founded timestamp,
    alliance_tag varchar,
    alliance_name varchar,
    kill_fame bigint,
    death_fame bigint,
    member_count bigint,
    last_updated timestamp default now()
);
alter table guild
    alter column internal_id
        set maxvalue 2147483647;

alter table guild
    add constraint uc_id
        unique (id);