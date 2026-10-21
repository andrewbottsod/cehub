-- CE Hub database setup. Paste this whole file into Supabase → SQL Editor → New query → Run.
-- Safe to run more than once.

-- 1) Each user's private data: favorites, licenses, home base and CE transcript.
create table if not exists public.user_data (
  user_id    uuid primary key references auth.users(id) on delete cascade,
  profile    jsonb not null default '{}'::jsonb,
  transcript jsonb not null default '{"rows":[]}'::jsonb,
  updated_at timestamptz not null default now()
);
alter table public.user_data enable row level security;

drop policy if exists "read own data"   on public.user_data;
drop policy if exists "insert own data" on public.user_data;
drop policy if exists "update own data" on public.user_data;
drop policy if exists "delete own data" on public.user_data;
create policy "read own data"   on public.user_data for select to authenticated using (auth.uid() = user_id);
create policy "insert own data" on public.user_data for insert to authenticated with check (auth.uid() = user_id);
create policy "update own data" on public.user_data for update to authenticated using (auth.uid() = user_id) with check (auth.uid() = user_id);
create policy "delete own data" on public.user_data for delete to authenticated using (auth.uid() = user_id);

-- 2) Meeting suggestions and corrections from visitors (write-only for the public;
--    you read them in Supabase → Table Editor → suggestions).
create table if not exists public.suggestions (
  id         bigint generated always as identity primary key,
  created_at timestamptz not null default now(),
  user_id    uuid default auth.uid(),
  name       text check (char_length(name) <= 200),
  url        text check (char_length(url)  <= 500),
  note       text check (char_length(note) <= 1000),
  status     text not null default 'new'
);
alter table public.suggestions enable row level security;
drop policy if exists "anyone can suggest" on public.suggestions;
create policy "anyone can suggest" on public.suggestions for insert to anon, authenticated with check (status = 'new');
