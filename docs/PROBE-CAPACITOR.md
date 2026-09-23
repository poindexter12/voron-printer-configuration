# Probe Decoupling Capacitor — Bench Reference

Wiring notes for the bulk capacitor added across the MicroProbe's power pins.
Written 2026-09-18. Background and the reasoning behind it:
[GROUNDING.md](GROUNDING.md), investigation log in
[SB2209-G0B1-SWAP.md](SB2209-G0B1-SWAP.md).

## Why

Probe actuation reproducibly adds CAN RX errors at the EBB (+11 on deploy,
+22 on stow) with the printer parked, cold and motors off. The probe's 350mA
solenoid shares **both** of the CAN transceiver's references: the EBB's
onboard 5V rail, and the EBB ground plane. The capacitor supplies that current
step locally so it is not pulled through either one.

It treats both candidate mechanisms at once — rail sag and ground bounce —
which is why it comes before the split-supply test that distinguishes them.

## The part

**As purchased 2026-09-18: 470 uF, 10 V, 105 C aluminium electrolytic.**

| Spec | Value | Note |
|---|---|---|
| Type | Aluminium electrolytic | **Polarized** - orientation matters |
| Capacitance | 470 uF | 1000 uF also fine; 470 is ample |
| Voltage | 10-25 V | **Installed: 10V.** 5V on a 10V part = 50% derating, a healthy operating point. Do not go below 10V. |
| Temperature | 105 C | **Installed: 105 C.** 85 C is acceptable if sited away from the hotend; 105 C removes the question. |

Math for the record: 350mA for ~100us into 470uF sags 74mV; into 1000uF,
35mV. Either is a non-event for the transceiver. Capacitance is not the
sensitive variable here.

## Wiring

Across the probe's **power pair only**. Nothing else changes.

```
   EBB SB2209 G0B1                                    MicroProbe V2
   P5 connector                                       350mA solenoid
   ---------------                                    --------------

                       red (5V)
   pin 2  5V   o----------+---------------------------------o  5V
                          |
                          |
                        --+--   +          470 uF electrolytic
                        -----              10 V, 105 C (as installed)
                          |     -  <-- STRIPE side is NEGATIVE
                          |
   pin 1  GND  o----------+---------------------------------o  GND
                      brown (GND)


   pin 3  PB9  o------ yellow --------------------------------o  control
   pin 4  GND         (second ground, unused - pin 1 is enough)
   pin 5  PB8  o------ white ---------------------------------o  sense
                      *** currently DISCONNECTED - restore power-off
                          before any homing ***
```

**Polarity: the stripe goes to brown (GND).** A backwards electrolytic on a
live rail vents. This is the only step in the job that can damage anything.

Either ground works - brown (pin 1) or black (pin 4). Use whichever is
easier to reach.

## Mounting

Two options, both fine:

1. **Splice into the cable** within ~2-5cm of the connector. No board
   soldering, fully reversible. Preferred.
2. **Solder to the back of P5** pins 2 and 1. Cleaner, but it is board work
   in a cramped toolhead.

Closeness matters less than it sounds. At these frequencies a few centimetres
of lead adds ~100nH, a fraction of an ohm - electrically irrelevant. Do not
run it 20cm up the harness, but siting it in a cooler spot with some air
around it costs nothing and buys electrolytic lifetime.

Once it proves out: heatshrink the joints and secure the can. The toolhead
vibrates constantly and a capacitor flapping on its leads will fatigue and
shear its legs off.

## Procedure

**Before** - verify the wire identities yourself, with power on:

```
meter DC volts, red lead on the probe's RED wire, black on BROWN
expect ~5.0 V
```

Anything other than ~5V, stop. The probe is a 5V device; P5 pin 2 is "fixed
5V" per the BTT schematic. The 24V never reaches it.

**Install** - power off. Positive leg to red, stripe leg to brown. Heatshrink.

**After** - same capture that produced the baseline:

```bash
python3 probe-can-capture.py --clearance-confirmed \
  --condition "470uF across P5 5V/GND"
```

Compare RX error deltas against the +11/+22 baseline.

- **Errors drop or vanish** -> mechanism confirmed, and this is likely the
  permanent fix. Follow with a QGL and a heat-soak capture to confirm under
  real load.
- **Errors unchanged** -> not supply-side at the connector. Next is the
  split-supply test: bench 5V to the probe, grounded at the EBB only
  (see GROUNDING.md, "Do not" section for the grounding rule).

## Result: CONFIRMED FIXED 2026-09-22

Installed the 470uF/10V/105C part across P5 pin 2 (5V, red) and pin 1 (GND,
brown). The 5V- to 24V- bond wire (GROUNDING.md Finding 3) was removed in the
same session - separate domain, on the host side of the HAT isolation barrier,
so not a confound for CAN.

Parked capture, same position as the baseline (X177.5 Y177.5 Z106, motors
disabled, heaters off):

| capture                 | before | deployed | stowed | delta |
|-------------------------|--------|----------|--------|-------|
| baseline 2026-09-13     |    197 |      208 |    230 |  +33  |
| 2026-09-22, 470uF       |      0 |        0 |      0 |  **+0** |

- `probe_enable` went 0.0 -> 1.0 -> 0.0 across the snapshots and 583 CAN
  frames were captured, so the solenoid did actuate. This is not a silent
  no-op.
- Every 09-13 baseline run wrote a 762-byte `errors.log`. The 09-22 run wrote
  **0 bytes**.
- Artifact: `~/printer_data/logs/can-probe-20260922-210006.json`

Under load, same session:

- **Cold QGL** - G28 plus 3 QGL passes over 4 points, ~13 probe actuations
  with steppers energised. Converged 2.669 -> 0.0806 -> 0.006250mm against a
  0.020 tolerance. Counters after: `rx_error=0 tx_error=0 tx_retries=0
  bytes_retransmit=0 bytes_invalid=0`.
- **Partial heat soak** - bed driven 26 -> 110C at full power with the hotend
  at 250C. Counters never moved. The structured soak capture was abandoned
  (see below), so this is an observation rather than a scripted artifact.

Zero *retransmits* matters as much as zero errors: the link is not masking
faults behind auto-retry, which was the original concern.

**Attribution: the capacitor.** The bond wire was never on the CAN path.

### Notes for the next person

- `probe-can-capture.py` refuses to run with heaters on (`assert_safe` raises
  "Heaters must be off"), so a soak capture has to be taken with the heaters
  switched off and the hardware still hot, not mid-soak.
- `M190` blocks Klipper's gcode queue. Killing the HTTP client does not stop
  it, and a queued `M140 S0` will not execute until the wait completes. Plan
  heat steps so you are not relying on cancelling one.

## Do not

- **Do not power the probe from the Pi's 5V.** Its return current would run
  the length of the umbilical and shift the CAN ground reference - injecting
  a new fault while testing for an old one.
- **Do not reinstate the old 10k pull-up resistor.** That was the MicroProbe
  issue #19 workaround for the RP2040 board's weak input. The G0B1 already
  has R31, a 4.7k pull-up to 3.3V. Adding the external 10k to 5V on top would
  bias the idle line above the 3.3V domain.
- **Do not change anything else in the same session.** One variable per
  capture or the comparison is worthless.
