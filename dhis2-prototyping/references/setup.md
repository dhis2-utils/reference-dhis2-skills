# Environment setup

> From a household enumeration PoC that compared six tracker designs (DHIS2 2.42.6, Capture Android 3.4.2, web Capture 2.42, September 2026). Scripts named here are bundled under `scripts/` (see "Bundled scripts" in SKILL.md); `scripts/<project>/` stands for the project's own generator package, which you write.

What you need before the first generator run:

- **A DHIS2 instance you can reset and dump** (see `dhis2-test-instances`): one shared instance
  for all options, and the ability to create a second, temporary one for the scale test. Database
  access (`psql`) helps: enrollment geometry and the hand-over dump both need it.
- **An Android emulator or device reachable with `adb`** (`adb devices` lists it), with the Capture
  app installed. An emulator is easier: permissions, mock GPS and time zone can be set from adb.
- **A browser automation stack** (Playwright + Chromium) for web Capture.
- **Video tooling** (ffmpeg) for the recordings.

This skill owns the Maestro, `screenrecord` and emulator-preparation recipes for recorded flows.

### Tools

| Need | Solution |
|---|---|
| Python helpers | `python3 -m venv .venv && .venv/bin/pip install requests pillow imageio-ffmpeg playwright` |
| ffmpeg | A system `ffmpeg` works. Without one (or without root), `imageio-ffmpeg` ships a static binary: `python -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())'`. The bundled scripts find it themselves, or set `FFMPEG`. That build has **no `drawtext`** filter but has **libass** (`subtitles`/`ass`), which is better for captions anyway. |
| Java (for Maestro) | Any JRE 17+. Without root, `pip install jdk4py` gives one; set `JAVA_HOME` to its `java-runtime` directory. |
| Maestro | `curl -L https://github.com/mobile-dev-inc/maestro/releases/latest/download/maestro.zip`, unzip, put `maestro/bin` on the PATH. Set `MAESTRO_CLI_NO_ANALYTICS=1`. |
| Capture APKs | From the GitHub releases of `dhis2/dhis2-android-capture-app`: the plain `dhis2-v<version>.apk`, not `-training` or `-googlePlay`. Get the version you test and one about a year older for a smoke test. |
| Chromium | `.venv/bin/playwright install chromium` |

Record where you installed tools that live outside the project, so a later session finds them.

### adb and Maestro

Maestro talks to the adb server at `localhost:5037`. If your adb server runs elsewhere (another
machine, or the host of a container you work in) and `adb` reaches it through `ADB_SERVER_SOCKET`
or `-H/-P`, Maestro does not follow: forward the port first, for example
`socat TCP-LISTEN:5037,bind=127.0.0.1,fork,reuseaddr TCP:<adb-host>:5037`. Never kill an adb
server you did not start; other sessions may depend on it.

The Android emulator reaches its host machine at `10.0.2.2`. The server URL the app logs in to is
the instance as the device sees it (for a local instance, `http://10.0.2.2:<port>`), not the URL
you use from scripts.

### Web Capture needs a secure origin

Web Capture refuses to load on plain `http` unless the origin is `localhost` ("The application could
not be loaded … privacy mode"). The Chromium flag `--unsafely-treat-insecure-origin-as-secure` did
not help in headless mode. If the instance is not already on `localhost` or https, forward it:

```bash
socat TCP-LISTEN:8089,bind=127.0.0.1,fork,reuseaddr TCP:<dhis2-host>:<port>
```

and point the web scripts at it (`D2_WEB=http://localhost:8089`). Run forwards as background
processes and record their PIDs. The same limit applies to real deployments: Capture needs https.

### Emulator preparation (do this after every `pm clear`)

```bash
for p in POST_NOTIFICATIONS ACCESS_FINE_LOCATION ACCESS_COARSE_LOCATION; do
  adb shell pm grant com.dhis2 android.permission.$p; done
# fake GPS so "my location" works; this needs only adb shell, not the emulator console
adb shell appops set com.android.shell android:mock_location allow
for p in gps network fused; do
  adb shell cmd location providers add-test-provider $p
  adb shell cmd location providers set-test-provider-enabled $p true
  adb shell cmd location providers set-test-provider-location $p --location 8.4840,-13.2299 --accuracy 5
done
```

The first `monkey -p com.dhis2 1` right after `pm clear` often does nothing: relaunch until the
login screen appears (`scripts/android/login.py` loops).

Set the device's time zone to the server's working zone before recording; see "Time zones" in
`android-flows.md`.

### Server-side Android settings (before the first login)

```bash
POST /api/dataStore/ANDROID_SETTING_APP/general_settings   {"allowScreenCapture": true, "encryptDB": false, "reservedValues": 50}
POST /api/dataStore/ANDROID_SETTING_APP/program_settings   {"globalSettings": {"settingDownload":"GLOBAL","teiDownload":20, ...}}
```

These keys are normally written by the Android Settings web app; writing them directly works, but
use `PUT` if the key already exists. Screen capture must be allowed or every screenshot and
recording is black. A low download limit keeps logins to about a minute even with thousands of
synthetic tracked entities. The app reads settings and metadata **only at login**: after any
metadata change, clear the app and log in again, or the flows test old metadata (seen with a
changed stage setting and with reserved form numbers generated under an old text pattern).

### Instances

- One instance for everything, all options side by side with code prefixes, worked well and is
  what the user wanted to share. Keep it, and label it in whatever provisions it.
- Use a **second, temporary instance** for anything that would distort the shared one (the 20k
  scale test). Importing the full metadata package into an empty instance also proves the package.
- Assign every user the flows and testers use (including `admin`) to the root org unit for
  capture, view and search, or they see no data.
- **Analytics tables can come back empty after a restart.** They are UNLOGGED by default
  (`analytics.table.unlogged = on` in `dhis.conf`), and PostgreSQL empties unlogged tables after a
  crash or unclean shutdown, which a container stop that times out is. It happened in the PoC.
  After an instance restart, run analytics again before verification or dashboard screenshots.
