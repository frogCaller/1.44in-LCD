# 1.44in-LCD

<div style="display: flex; gap: 10px;">   
    <img src="images/writerDeck.gif" width="300">
</div>

This project uses a 1.44-inch LCD HAT with a Raspberry Pi.

# Materials
* [Raspberry pi Zero 2 WH](https://amzn.to/3VO7eu2)<br />
* [Micro SD Cards](https://amzn.to/4erXgWD)<br />
* [1.44inch LCD HAT](https://amzn.to/3Mea7yY)<br />
* [UPS Hat](https://amzn.to/4ceZp6I)<br />
<br />
(Amazon affiliate links)<br />


## **Installations**

1. **OS install:**
   - Install Raspberry Pi OS Lite (64-bit) on your Raspberry Pi <br />
   
2. **Enable SPI & I2C:**
   - Open a terminal on your Raspberry Pi.
   - Run `sudo raspi-config`
   - Navigate to Interfacing Options -> SPI -> Enable.

3. **Python libraries:**
   - sudo apt-get update -y
   - sudo apt-get install python3-pip -y
   - sudo apt-get install python3-pil -y
   - sudo apt-get install python3-numpy -y
   - sudo apt-get install python3-spidev -y
   <br />

# Wiring and Setup
1. **Connect 1.3inch LCD HAT to Raspberry Pi:**
   - Connect the 1.44inch LCD HAT to your Raspberry Pi. <br />
   - Connect the UPS Hat for continuous power supply. This will allow you to move the project anywhere without worrying about power interruptions.

2. Clone the repository:
   ```bash
   sudo apt install git -y
   git clone https://github.com/frogCaller/1.44in-LCD.git
   cd 1.44in-LCD
  
# Usage Instructions    

1. Start typing with:
   - Run the script: `python3 type.py`

2. More:
   - You can edit the buttons in the code to make them do whatever you want.
   - Modify the check_buttons() function in the script to customize the button actions according to your requirements.
   
# Troubleshooting
Common Issues:
   - Ensure SPI & I2C are enabled in the Raspberry Pi configuration.
   - Check all connections if the screen does not display anything.
   - Verify all required packages are installed correctly.
   - [More Info](https://www.waveshare.com/wiki/1.44inch_LCD_HAT)
