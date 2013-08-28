create or replace function eval_join(param text[],
  object pgmapcss_object, current pgmapcss_current, render_context pgmapcss_render_context)
returns text
as $$
#variable_conflict use_variable
declare
  list text[];
begin
  if array_upper(param, 1) < 2 then
    return '';
  end if;

  list := string_to_array(param[1], ';');

  return array_to_string(list, param[2]);
end;
$$ language 'plpgsql' immutable;
