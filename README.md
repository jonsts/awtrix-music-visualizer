# AWTRIX Music Visualizer

Real-time music visualizer for the **Ulanzi TC001** smart clock running AWTRIX 3.

Your PC captures the audio, runs an FFT, maps it to frequency bands, and streams
frames to the clock's 32x8 RGB matrix over HTTP or MQTT.



https://github.com/user-attachments/assets/a4b555e2-87de-4772-aaa3-3da5b9e66836




```
PC (capture audio -> FFT -> bands -> color) --HTTP/MQTT--> TC001 (renders frame)
```

## How it works

The clock has no audio input exposed through its API, so all the signal
processing happens on the host. Each tick, the app:

1. Captures a block of audio (system loopback on Windows, or a mic/line-in).
2. Computes an FFT and groups bins into log-spaced bands.
3. Applies log compression, normalization, gain, and an envelope follower
   (instant attack, smooth release).
4. Renders the bands into an AWTRIX custom-app payload and sends it.

## Requirements

- Python 3.11+ (uses the stdlib `tomllib`)
- A TC001 on the same network running AWTRIX 3
- Dependencies: `pip install -r requirements.txt`
  - System-audio capture uses [`soundcard`](https://github.com/bastibe/SoundCard)
    for WASAPI loopback (python-sounddevice has no high-level loopback API).

## Setup

1. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

2. Create your config from the example and edit it:

   ```
   copy config.example.toml config.toml    # Windows
   cp config.example.toml config.toml      # macOS/Linux
   ```

   - Set `device.ip` to your clock's IP address.
   - Choose `device.transport` = `"http"` or `"mqtt"` (HTTP is simplest).
   - If using MQTT, fill in the `[mqtt]` section (host, port, prefix, creds).

   `config.toml` is gitignored so your IP and credentials stay local. If it's
   missing, the app falls back to `config.example.toml`.

3. (Windows) Find your audio device for system-audio capture:

   ```
   python -m visualizer --list-devices
   ```

   This lists speakers and microphones. For system-audio capture keep
   `audio.loopback = true` and set `audio.device` to a substring of one of the
   **speaker** names (e.g. `Speakers (Realtek`). To capture a real mic instead,
   set `loopback = false` and match a microphone name. `device = "auto"` follows
   the Windows default output device automatically.

## Run

```
python -m visualizer
```

Stop with `Ctrl+C`; the display is cleared on exit. A web control panel starts
at <http://localhost:8888> (disable with `--no-web`, change port with `--port`).

<img width="557" height="826" alt="image" src="https://github.com/user-attachments/assets/fb1a2225-670b-4fcb-8824-9e749b1421b5" />


To keep the visualizer pinned on screen instead of cycling through apps, disable
auto-transition on the clock (Settings: `ATRANS = false`).

## Visualization modes

Set `render.mode` in config, switch live in the web UI, or cycle with the clock's
right button.
<img width="1052" height="260" alt="mario2" src="" />

| Mode | Description |
| :--- | :--- |
| `draw` | Vertical spectrum bars with peak-hold dots <br> <img src="https://github.com/user-attachments/assets/6f94217b-5bb0-4d03-bc1b-739c411d3648" width="300" alt="rainbow"> |
| `horizontal` | Bars growing outward from the center, one row per band <br> <img src="https://github.com/user-attachments/assets/88368603-a082-4282-816b-7684bdcf09fe" width="300" alt="horizontal"> |
| `ltr` | Horizontal bars growing left to right, one row per band <br> <img src="https://github.com/user-attachments/assets/fd5a374b-aa2e-44dd-8a9c-7745c3481184" width="300" alt="ltr"> | 
| `waves` | Joy Division / *Unknown Pleasures* scrolling waveform landscape <br> <img src="https://github.com/user-attachments/assets/ad9bffe8-5b0d-4efb-96c4-6b3175b2ac99" width="300" alt="joy division"> |
| `mario` | Super Mario overworld – green pipes, sky, ground, clouds <br> <img src="https://github.com/user-attachments/assets/f879e4a8-f520-42c7-a5b8-5ff032c7ad63" width="300" alt="mario overworld"> |
| `mario_underground` | Mario underground – teal blocks on black, gold question block <br> <img src="https://github.com/user-attachments/assets/6b66f116-3bc4-413c-a725-63778ea76305" width="300" alt="mario underground"> |
| `dancer` | A stick figure that dances and walks across the screen on the beat <br> <img src="https://github.com/user-attachments/assets/d656fe3e-2b61-4a4c-b66b-7c2018c4b25a" width="300" alt="dancer"> |
| `fractal` | Audio-reactive plasma or Julia set (`fractal_type`) <br> <img src="https://github.com/user-attachments/assets/b0bd7cd6-432d-49e9-91e7-0a798e718ed0" width="300" alt="fractal"> |
| `bar` | AWTRIX's built-in bar graph (simple, max 16 bands) |



## Color schemes

`spectrum` (rainbow), `outrun` (synthwave), `fire`, `ocean`, `forest`, `ice`,
`neon`, `sunset`, `matrix`, and `solid` (custom color). Enable `color_cycle` to
smoothly rotate the palette over time.

## Physical buttons

The clock's three buttons control the visualizer over MQTT (requires MQTT
configured and the clock connected to the same broker):

| Button | Action |
| ------ | ------ |
| **Left** | Cycle color scheme |
| **Middle** | Toggle the visualizer on/off |
| **Right** | Cycle render mode |

To stop the buttons from also navigating the clock's built-in apps, set
`BLOCKN = true` in the AWTRIX settings (the buttons still publish to MQTT).

## Web control panel

Open <http://localhost:8888> while running. Adjust gain, smoothing, fps, mode,
color scheme, frequency range, overlay text, idle behavior, and the enable
toggle — all live, no restart. Changes are saved back to `config.toml`.

## Auto-start on login (Windows)

```
python install_autostart.py            # register a Task Scheduler task
python install_autostart.py --remove   # remove it
```

## Configuration reference (`config.toml`)

| Section    | Key           | Meaning |
| ---------- | ------------- | ------- |
| `device`   | `ip`          | TC001 IP address |
|            | `transport`   | `"http"` or `"mqtt"` |
|            | `app_name`    | Custom app name created on the clock |
| `mqtt`     | `host`/`port` | Broker address (MQTT transport / buttons) |
|            | `username`/`password` | Broker credentials |
|            | `prefix`      | AWTRIX MQTT topic prefix |
| `audio`    | `device`      | Substring match for the speaker (loopback) or mic; `"auto"` follows default output |
|            | `loopback`    | Capture system audio (Windows WASAPI loopback) |
|            | `samplerate`  | Capture sample rate (Hz) |
|            | `blocksize`   | Samples per capture block |
| `render`   | `enabled`     | Master on/off toggle |
|            | `bands`       | Number of bands (`bar` mode max 16, others up to 32) |
|            | `mode`        | See the modes table above |
|            | `fps`         | Target frames per second |
|            | `smoothing`   | Release smoothing 0..1 (higher = slower decay) |
|            | `min_freq`/`max_freq` | Frequency range spread across the bands |
|            | `gain`        | Sensitivity multiplier |
|            | `scheme`      | Color scheme (see list above) |
|            | `solid_color` | Hex color for `solid` scheme |
|            | `peak_dots`   | Draw peak-hold markers |
|            | `color_cycle`/`color_cycle_speed` | Animate the palette over time |
|            | `overlay_text`/`overlay_color` | Text knocked out of the spectrum |
|            | `fractal_type` | `"plasma"` or `"julia"` |
|            | `idle_seconds`/`idle_app` | Switch to this app after N seconds of silence |

## Notes & limits

- **Frame rate** is the main bottleneck: frames go over WiFi to an ESP32. HTTP
  realistically does ~15-20 fps. Start at `fps = 20`.
- The matrix is **32x8** — keep draw command counts reasonable; heavy payloads
  can stress the device's RAM and cause stutter or reboots.
- Frames are never saved to flash (no `save: true`), to protect the ESP's limited
  write cycles.

## Project layout

```
visualizer/
  __main__.py   # CLI entry point and main loop
  config.py     # config loader
  audio.py      # capture + FFT band analysis
  render.py     # bands -> AWTRIX JSON payloads, color schemes
  transport.py  # HTTP and MQTT senders
  web.py        # web control panel server
  ui.html       # web control panel page
  buttons.py    # physical button -> action mapping (MQTT)
  waves.py      # Joy Division waveform mode
  mario.py      # Mario overworld/underground modes
  dancer.py     # dancing stick figure mode
  fractals.py   # plasma / Julia fractal modes
config.example.toml   # template — copy to config.toml
install_autostart.py  # Windows Task Scheduler auto-start
requirements.txt
```
