# Hardware ladder — deployment rungs for a zero agent

*Xero Research Library · 2026-10-12*
*Framing: addition layers. Each rung is a place Zero may be put —
hardware is a deployment choice, not part of what Zero is.*
*Prices are street/list as found 2026-10-12 and move; treat as ±30%.*

## The ladder at a glance

| Rung | Representative | Compute / RAM | AI accel | Power (typical) | Price | Agent tier it can host |
|---|---|---|---|---|---|---|
| MCU | ESP32-S3 | Xtensa LX7 dual-core 240 MHz · 512 KB SRAM (+≤8 MB PSRAM) | Vector (SIMD) instructions for NN; no TOPS rating | Deep sleep ~8 µA; active ≈0.3–1 W | $5–15 (dev board) | **Reflex-only** + tiny classifier / wake-word |
| Classic MCU board | Arduino UNO-class | 8/32-bit MCU, KBs of SRAM | None | <1 W | $10–30 | **Reflex-only** (state machines, gates) |
| Dual-brain | Arduino UNO Q | QRB2210 A53×4 2.0 GHz + STM32U585 · 2–4 GB | GPU + DSP (no published TOPS) | ≤15 W ceiling (5 V/3 A) | $45–59 | **Hybrid**: reflex on MCU + small-model deliberation on Linux — see `uno-q.md` |
| SBC | Raspberry Pi 4 | BCM2711 A72×4 1.8 GHz · 1–8 GB LPDDR4 | None (CPU only) | ≈3–7 W | $55–75 (4–8 GB) | Full agent runtime; **small local model** (1–3B quantized, slow) |
| SBC | Raspberry Pi 5 | BCM2712 A76×4 2.4 GHz · 1–16 GB LPDDR4X | None (VideoCore VII GPU, no NPU) | 5 V/5 A supply; ≈5–12 W under load (UNVERIFIED) | $45–145 by RAM (official brief; volatile) | **Small local model**, comfortable (3–8B quantized); good agent home base |
| AI SBC | Jetson Orin Nano Super Dev Kit | A78AE×6 · 8 GB LPDDR5 @ 102 GB/s | **67 TOPS** (sparse INT8) Ampere GPU, 32 tensor cores | 7–25 W modes | ~€390 listing found; US price UNVERIFIED this pass | **Talk**: local 7B-class LLM + speech + vision concurrently |

## Rung notes

### ESP32-S3 (the metal)
Dual-core Xtensa LX7 @ 240 MHz, 512 KB SRAM, 384 KB ROM; modules
commonly add 8 MB octal PSRAM and 16 MB flash. Its vector
instructions accelerate small neural nets (keyword spotting, person
detection) — enough for a *perception check with a tiny judge*, not
for language. Wi-Fi 4 + Bluetooth 5 LE on-chip. Sleep currents are
the point: it can watch a bilge for months on a battery and wake on
an event. Sources: https://www.cnx-software.com/2022/01/12/esp32-s3-esp32-c3-esp8266-modules-comparison/ ·
https://www.cnx-software.com/2022/10/31/lilygo-t7-s3-esp32-s3-board-16mb-flash-8mb-psram-lipo-battery/?amp=1

### Raspberry Pi 4 / 5 (the boat computer class)
Pi 4: BCM2711, quad Cortex-A72 @ 1.8 GHz, up to 8 GB — from the
comparison table in: https://www.tomshardware.com/reviews/raspberry-pi-5?ref=selfh.st
Pi 5: BCM2712, quad Cortex-A76 @ 2.4 GHz, LPDDR4X-4267 in
1/2/4/8/16 GB, dual 4Kp60 HDMI, PCIe 2.0 ×1, 5 V/5 A USB-C supply.
Official product-brief list prices: $45/$55/$70/$95/$145 by RAM —
but other datasheet copies circulating show markedly higher figures;
memory-market prices in 2025–26 are volatile, so re-check before
budgeting. Neither Pi has an NPU: local LLM speed is CPU-bound,
which is why the Pi tier is "small model, patient answers."
Sources: https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-008348-DS-4-raspberry-pi-5-product-brief.pdf?disposition=inline ·
https://www.raspberrypi.com/products/raspberry-pi-5/

### Jetson Orin Nano Super (the talk tier)
67 TOPS sparse INT8 (the "Super" software update lifted the
original 40 TOPS), 1024 CUDA cores + 32 tensor cores, 6-core
Cortex-A78AE, 8 GB LPDDR5 at 102 GB/s, configurable 7/15/25 W. This
is the first rung where a *conversational* local agent is realistic:
7B-class quantized LLM plus STT/TTS plus a camera pipeline at once.
Sources: https://www.kiwi-electronics.com/en/nvidia-jetson-orin-nano-super-developer-kit-11461 ·
https://thinkrobotics.com/products/nvidia-jetson-orin-nano-developer-kit?_pos=2&_sid=6088d01b9&_ss=r

## How to choose a rung (builder's rule)

1. **What must survive a brain failure?** Whatever it is runs on the
   lowest rung that can hold it — reflexes sink to MCU, always.
2. **What is the power envelope?** Battery/solar ⇒ ESP32-S3 class or
   UNO Q with the Linux side asleep. Shore power ⇒ Pi/Jetson free.
3. **Does it need to talk, or only to signal?** Signalling is cheap
   (any rung). Conversation is the Jetson rung — or reach out.
4. **Reaching out is a rung too.** A $10 MCU with a radio and a good
   contract to a cloud frontier model out-thinks a lonely Jetson on
   judgment calls; it just can't do it offline or at 3 a.m. with the
   network down. Choose per failure mode, not per benchmark.

## Open questions

- UNO Q vs Pi 5 as the "home base" tier: the Q's MCU reflex layer
  vs the Pi's RAM headroom — needs a bench comparison on the actual
  filing-loop workload.
- Jetson Orin Nano street price in the US as of late 2026:
  UNVERIFIED in this pass (only an EU listing was captured).

*Status: specs high confidence; power figures for Pi boards are
typical/approximate; prices volatile.*
