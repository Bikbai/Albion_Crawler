drop table europe.legendary;
create table europe.legendary
(
    internal_id integer generated always as identity
        constraint pk_legendary
            primary key,
    item_id integer not null
        constraint fk_legendary_item
            references europe.item (internal_id),
    data json not null,
    event_id bigint not null,
    id uuid not null,
    kill_event bool not null
);