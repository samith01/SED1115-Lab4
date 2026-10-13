# SED1115 Lab 4 - Pico Serial Chat

A simple serial chat application for two Raspberry Pi Picos using MicroPython and UART.

## Features
- UART communication (GP0 TX, GP1 RX, 115200 baud)
- XOR checksum validation for message integrity
- Keep-alive with timestamp every 5 seconds
- Non-blocking keyboard input

## Wiring
```
Pico 1 GP0 (TX) → Pico 2 GP1 (RX)
Pico 1 GP1 (RX) ← Pico 2 GP0 (TX)
GND ↔ GND
```

## Usage
1. Flash `lab4.py` to both Picos
2. Connect via USB and open serial terminals
3. Type messages and press Enter to send

## Message Format
- **Chat**: `M<message><checksum>`
- **Keep-alive**: `K<timestamp><checksum>`
- Checksum: 2-digit hex XOR of all preceding characters

## License
MIT License — Copyright (c) 2026 Samith

This project uses the MicroPython standard library (MIT licensed).