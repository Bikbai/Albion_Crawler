create table public.player
(
    internal_id bigint NOT NULL primary key generated always AS IDENTITY,
    id varchar NOT NULL,
    guild_id varchar NULL,
    player_name varchar NOT NULL,
    kill_fame bigint,
    death_fame bigint,
    pve_fame bigint,
    gathering_fame bigint,
    crafting_fame bigint,
    fishing_fame bigint,
    last_updated timestamp default now()
);
alter table player
    alter column internal_id
        set maxvalue 2147483647;

alter table player
    add constraint uc_player_id
        unique (id);

alter table player
    add constraint fk_player_guild
        foreign key (guild_id) references guild (id);