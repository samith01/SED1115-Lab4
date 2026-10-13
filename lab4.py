"""
Simple Pico serial chat (MicroPython).

Wiring: GP0 (TX) -> partner GP1 (RX), GP1 (RX) <- partner GP0 (TX), GND to GND.

Each line sent is:  M<message>XX  or  K<time>XX
where XX is a two-digit hex XOR checksum of everything before it.

Sources: MicroPython documentation for the RP2 port (machine.UART, machine.RTC,
select.poll, time). See the list at the end of the answer.
"""

import sys                      # USB console input and printing
import time                     # ticks_ms / ticks_diff for timing, sleep_ms for pauses
import select                   # poll() lets us check the keyboard without blocking

from machine import UART, Pin, RTC  # hardware serial, GPIO pins, real-time clock

KEEPALIVE_MS = 5000             # send a keep-alive if nothing was sent for 5 seconds

# UART 0 , using GP0 for TX and GP1 for RX.
uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))

# Register the keyboard so we can ask "is a key waiting?" without blocking.
keyboard = select.poll()
keyboard.register(sys.stdin, select.POLLIN)


def checksum(text):
    """Return a two-digit hex XOR of all characters in text."""
    c = 0
    for ch in text:
        c ^= ord(ch)            # XOR each character's code into the running value
    return "%02X" % c           # format as two uppercase hex digits


def send(msgType, text):
    """Build and transmit one frame: msgType + text + checksum + newline."""
    body = msgType + text                              # e.g. "Mhello" or "K2025-01-01 ..."
    uart.write((body + checksum(body) + "\n").encode())  # UART sends bytes, so encode to bytes


def parse(line):
    """Return (msgType, text) for a valid line, or None if it is corrupt."""
    
    # need at least msgType + 1 char + checksum
    if len(line) < 3:                               
        return None
    
    # split off the last two characters
    body, chk = line[:-2], line[-2:]
    
    # recompute checksum and compare with the one received
    if checksum(body) != chk:
        # if not the same then the message was corrupted
        return None
    #return msgType , text
    return body[0], body[1:]                       


def timeNow():
    """Return the Pico's RTC time as 'YYYY-MM-DD HH:MM:SS'."""
    y, mo, d, _, h, mi, s, _ = RTC().datetime() 
    return "%04d-%02d-%02d %02d:%02d:%02d" % (y, mo, d, h, mi, s)


def read_uart():
    """Return a list of valid (msgType, text) messages received so far."""
    messages = []
    
    # any() > 0 means there is a message waiting
    while uart.any():
        #read the message
        raw = uart.readline()
        #exit if full message wasnt received
        if raw is None:                      
            break
        
        # decoding the bytes to text
        line = raw.decode("ascii", "ignore").strip()
        
        #do a checksum check and parse the message
        result = parse(line)
        # only keep frames that passed the check
        if result:                                  
            messages.append(result)
    return messages


def show(msgType, text):
    """Print a received frame, then redraw the input prompt."""
    
    #checking if its a message
    if msgType == "M":
        print("\nPico 2: " + text)
        
    #if its just the keep-alive ping
    else:
        print("\nkeep-alive time: " + text)
    #Ask the user for a new message
    sys.stdout.write("> ")                        


def main():
    #what the user typed is saved here
    typed = ""
    # keep track of the latest time
    last_sent = time.ticks_ms()
    
    sys.stdout.write("> ")                  

    while True:
        # Show anything received from the other pico.
        for msgType, text in read_uart():
            show(msgType, text)

        # Read users input typing without blocking.
        while keyboard.poll(0):
            # read exactly one character
            ch = sys.stdin.read(1)
            # Enter key ends the message
            if ch in ("\n", "\r"):                 
                if typed.strip():
                    # send the message
                    send("M", typed.strip())
                    # reset the keep-alive timer
                    last_sent = time.ticks_ms()
                # clear the buffer for the next message
                typed = ""
                
            else:
                # add the character to the buffer
                typed += ch                         
                 

        # Keep-alive when nothing has been sent recently.
        if time.ticks_diff(time.ticks_ms(), last_sent) >= KEEPALIVE_MS:
            # send our local time as a keep-alive
            send("K", timeNow())
            # reset the timer
            last_sent = time.ticks_ms()             
        
        
        #time.sleep_ms(10)                           


main()                                              # start the program