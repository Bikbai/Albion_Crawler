create table europe.item(
   internal_id bigint NOT NULL primary key generated always AS IDENTITY,
   code varchar NOT NULL,
   json_data json
);

alter table europe.item
    alter column internal_id
        set maxvalue 2147483647;

alter table europe.item
    add constraint uc_item_code
        unique (code);