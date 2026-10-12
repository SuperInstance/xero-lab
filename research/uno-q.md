# UNO Q — identification and agent placement

*Xero Research Library · 2026-10-12*
*Framing: an addition layer — a deployment target Zero may be added
onto. Zero itself is the blank page; this board is not part of it.*

## Verdict: hypothesis CONFIRMED

The "Uno Q" is the **Arduino UNO Q** — a dual-brain board launched by Arduino
(October 2025, alongside the Qualcomm acquisition of Arduino): a Qualcomm
Dragonwing Linux microprocessor plus an ST STM32U585 real-time microcontroller
on one UNO-form-factor board. Every element of the working hypothesis checked
out against Arduino's own datasheet text.

## Verified specifications

| Item | Value |
|---|---|
| MPU | Qualcomm Dragonwing QRB2210 — quad-core Arm Cortex-A53 @ 2.0 GHz, 64-bit |
| GPU | Adreno 702 @ 845 MHz |
| AI acceleration | GPU + Hexagon QDSP6 v66 DSP in the SoC. **No official TOPS figure is published** in the datasheet or reviews found — treat any TOPS number as UNVERIFIED |
| RAM / storage | 2 GB LPDDR4X + 16 GB eMMC (ABX00162); 4 GB + 32 GB eMMC (ABX00173) |
| Linux side | Debian OS (upstream support), Docker / Docker Compose supported |
| MCU | STM32U585 — Arm Cortex-M33 @ up to 160 MHz, 2 MB flash, 786 KB SRAM |
| MCU runtime | Arduino Core on Zephyr OS |
| Radios | Wi-Fi 5 (802.11a/b/g/n/ac, dual-band) + Bluetooth 5.1 (Qualcomm WCN3980 module) |
| Power | USB-C PD, **5 V / 3 A contract only** (no higher-voltage profiles); or VIN 7–24 V |
| I/O highlights | USB 3.1-C with DisplayPort alt-mode, MIPI-CSI/DSI headers, Qwiic I2C, classic UNO headers (MCU owns ADC, PWM, CAN, LED matrix) |
| Extras | 8×13 blue LED matrix, 4 RGB LEDs, dual ISP (13 MP + 13 MP or 25 MP @ 30 fps) |
| Price | ~$45–55 for the 2 GB model at launch (reports vary by region); 4 GB variant announced January 2026 at **$59** |
| Release status | Shipping since late 2025; 4 GB variant followed Jan 2026 |

Development is through **Arduino App Lab**, which unifies Arduino sketches
(C on the MCU), Python apps (Linux side), and containerized AI models;
Arduino ships pre-built models for object detection, image classification,
sound recognition, anomaly detection, and keyword spotting.

Sources:
- Arduino UNO Q datasheet (official text, rev. 05/11/2025): https://github.com/am4l-babu/mira/blob/HEAD/docs/manuals/Arduino%20UNO%20Q%20datasheet.md
- Tom's Hardware review + spec table: https://www.tomshardware.com/raspberry-pi/arduino-uno-q-review
- Retail spec listing: http://thepihut.com/products/arduino-uno-q
- 4 GB variant, DSP detail, $59: https://abit.ee/en/motherboards/arduino-uno-q-4gb-ram-32gb-storage-single-board-computer-linux-qualcomm-dragonwing-stm32u585-price-5-en
- App Lab pre-built AI models: https://maker.pro/mouser/win-an-arduino-uno-q

## What the dual-brain split means for placing an agent

The board is a physical version of the two-layer agent split Casey designs
on paper: a fast, dumb, always-on layer and a slow, smart, Linux layer,
with a defined bridge between them.

- **Metal / MCU side (STM32U585, Zephyr, C).** This is the reflex layer:
  GPIO, ADC, PWM, CAN, the LED matrix, watchdogs and timing loops that
  must not depend on Linux being awake or sane. 2 MB flash / 786 KB SRAM
  means hand-written C state machines, sensor polling, deadband/gate
  logic — "perception checks" at wire speed. If the agent must never
  miss a bilge alarm, the checking loop lives here, not in Python.
- **Linux side (QRB2210, Debian).** This is the deliberation layer:
  the agent's files (git working copy, active log), the filing/index
  loop, Docker containers, Python orchestration, small local models
  (keyword spotting, anomaly detection via App Lab models; small
  quantized LLMs are possible but the A53 + 2–4 GB RAM makes them a
  reach — see `hardware-ladder.md`). This side can crash and reboot
  without the reflex layer noticing.
- **The bridge is the design surface.** MPU↔MCU comms (serial/RPC-style
  bridge in Arduino's tooling) is where contracts live: what the Linux
  side may ask the MCU to do, what the MCU reports up, and — per the
  alarm definition in `nuggets.md` — what the MCU signals on its own
  when readings leave the region it was told to expect.
- **Reached-out cloud.** Wi-Fi 5 is the sync pipe: the board holds a
  sealed, complete reality of its last-synced build (see the
  sync-as-perception-check nugget) and reaches out for the frontier
  call when the local tiers can't close a question. Power budget is
  the constraint: 5 V/3 A USB-C only, so plan for ≤15 W total system
  power; there is no battery story on the board itself.

## Placement rule of thumb

| Question | Put it on |
|---|---|
| Must it run while Linux is down/rebooting? | MCU |
| Is it timing- or safety-critical I/O? | MCU |
| Does it touch files, git, indexes, models? | Linux MPU |
| Does it need judgment beyond a small model? | Reach out (Wi-Fi) |
| Must it survive a total board brain failure? | It can't — escalate the alarm off-board |

## Open questions

- What is the real sustained power draw of the 4 GB variant under
  App Lab AI workloads? (Datasheet gives the 5 V/3 A ceiling, not a
  typical figure — UNVERIFIED.)
- How reliable is the MPU↔MCU bridge under load, and what is its
  latency? Needs bench time, not datasheets.
- Can the MCU hold a useful signed "last known good" state so the
  Linux side can verify its own files after a crash?

*Status: identification high-confidence; performance/power details approximate.*
