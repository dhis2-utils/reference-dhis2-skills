# Final recording pass — notes from last night

Setup: DHIS2 2.42 test instance at http://dhis2-test:8080 (UTC), Capture Android 3.4.2 on an
emulator on my laptop (laptop is UTC+3), Maestro 2.10, Playwright headless Chromium for web Capture.
Three design options (A, B, C), three scenario households each.

1. Android, option A, households 1–3 (started 22:10 local): all three Maestro flows reported
   "Flow passed". The app's sync screen shows a green "Synced" for all of them.
2. Android, option B, households 1–3 (started 23:40 local): household 1 passed. Households 2 and
   3 failed at sync with "Enrollment date 2026-11-12 cannot be a future date". The flows did not
   change between households.
3. Yesterday afternoon I changed the text pattern of "Household number" from
   `"HH-" + SEQUENTIAL(####)` to `ORG_UNIT_CODE(...) + "-" + SEQUENTIAL(#####)`. The
   Android flows still show numbers like HH-0042.
4. The screen recordings for option C are completely black, though the Maestro flows passed.
5. Web Capture in headless Chromium at http://dhis2-test:8080/dhis-web-capture/ shows
   "The application could not be loaded. Please make sure you are not in privacy mode".
   Adding --unsafely-treat-insecure-origin-as-secure=http://dhis2-test:8080 changed nothing.
6. This morning the instance was restarted by IT. I ran analytics on Tuesday, before the pass.
   The option A dashboard shows no data at all for the scenario households, and the
   synthetic-population charts that worked on Tuesday are empty too.
7. The households I entered on web after the pattern change got numbers OU_-00001, OU_-00002,
   OU_-00003 although they are in three different villages (codes OU_278, OU_1126, OU_559).
8. Before the pass I added a "Follow-up" stage to option C, with two program rules that hide and
   make mandatory its fields. The generator's metadata import failed with E4047 "DataElement
   … is not linked to any ProgramStageDataElement", although the new stage in the same file lists
   those data elements. I left option C's follow-up out of the pass.

Before I re-run everything: what went wrong in each case, what do I change, and how do I make
sure the next pass actually put the data on the server?
