# The plugin shelf

Plugins are authored and proven **here, in the lab**, and
production agents grab them from here. This folder is the
shelf; the grabber contract lives in zero-poc's
`plugins/README.md` (SuperInstance/zero-poc) and is the
authority on what a plugin is:

- a folder `plugins/<name>/` with a `PLUGIN.md` (what it does,
  its kind — **skill** or **vault-service** — the exact recipe,
  its failure modes and honest fallbacks, and the exact
  `TOOLS.md` row it adds);
- self-contained: an agent that has never seen the underlying
  API must succeed on the first try from the folder alone;
- grabbed whole and unedited — a snapshot. Improvements land
  here first, get proven here, and are then re-grabbed.

## On the shelf

| Plugin | Kind | What it does |
|---|---|---|
| weather | skill | Current conditions + today/tomorrow outlook for a named place (default Sitka, Alaska) from wttr.in. Measured numbers only; a failed lookup is reported as failed, never estimated. First grabbed by zero-poc 2026-10-28. |
