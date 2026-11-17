# Replaced and renamed apps (pass H)

Grep the in-scope text for every name below, in every form (bold, "X app",
"X ->", anchors such as `maintenance_app`). Add to the list when you find a
new one.

- **Maintenance app → Metadata Management app (MMA).** MMA is the app to
  send readers to. It needs core 41 or later and is installed from the App
  Hub, so some instances still have only Maintenance. Search for
  `Maintenance` in every form (`**Maintenance**`, `Maintenance app`,
  `Maintenance ->`, `maintenance_app` anchors).
- **Data Entry → Data Entry (Legacy)**, with the new aggregate app taking
  the name "Data Entry".
- **Datastore Management**: no references to any older name.

One grep for all of them:

```sh
grep -n -i -E 'maintenance|data entry|data store|datastore' <page.md>
```

For each hit, record a register row of type "App reference" and settle five
things:

1. Which app should the reader use now?
2. Does the object or screen exist in that app? Check the app's own source
   or docs and the live UI. For example, MMA has validation rules,
   validation rule groups, validation notifications, data element groups,
   indicator groups, organisation unit groups and data sets. Do not assume a
   replacement covers every screen of the old app.
3. Does the page need a fallback for instances without the new app? Put it
   in one note near the first mention, for example "If your instance does
   not have the Metadata Management app, use the Maintenance app instead."
   Do not repeat a bracket or fallback in every sentence.
4. Do the text, nav path, screenshot and link target all name the same app?
   A screenshot of the old app under text for the new one is a finding (open
   that screenshot: this is a pass E trigger).
5. Is the page that holds the detailed steps the right target for the link,
   so the steps live in one place?

A new app name beside an old screenshot, an old name left in a note or a
"Related information" list, and a link only to the old app are all doc
errors (S3, or S2 if the reader cannot complete the task without the old
app).
