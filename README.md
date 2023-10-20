# waveshare-joystick
Firmware for managing a 2 axis analog joystick on a Waveshare RP2040-Zero
## Flashing

 1. Download a [release](https://github.com/tuffrabit/waveshare-joystick/releases) to your PC
 2. If you downloaded a zip, unzip it
 3. Unplug your microcontroller
 4. Hold down the joystick switch
 5. Plug in the microcontroller while holding down that switch, you should see a new drive called CIRCUITPY appear
 6. In the new downloaded and unzipped firmware folder, select everything except for the .gitignore file
 7. Copy and then paste into the CIRCUITPY drive choosing to overwrite everything
 8. The microcontroller should auto reboot
 9. Unplug and replug the microcontroller so the CIRCUITPY drive disappears

**Be sure to use the latest version of the [management app](https://github.com/tuffrabit/godot-narwhal-manager/releases) alongside the latest microcontroller firmware**
