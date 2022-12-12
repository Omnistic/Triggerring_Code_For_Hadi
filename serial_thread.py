import serial, threading, time
from LuigsAndNeumannSM10.LandNSM10 import LandNSM10


# Parameters of serial connection with ARDUINO
PORT = 'COM4'
BAUDRATE = 9600

# Global flags
TRIGGER_Z_STAGE = False
COMPLETE = False

SLEEPTIME = 20

# Function to read bytes (one by one) on the ARDUINO
def read_serial(port):
    # Global flags
    global TRIGGER_Z_STAGE

    while True:
        # Read one byte on the ARDUINO
        one_byte = port.read()

        # If byte correspond to a given value change the TRIGGER flag
        # and stop the reading thread
        if one_byte == b'\x01':
            TRIGGER_Z_STAGE = True
            print('[' + time.strftime('%Y/%m/%d %H:%M:%S', time.localtime()) + '] Trigger recieved')
            break
        
        
# Function to move the Z stage
def trigger_z(device, axis, pos1, pos2):
    # Global flags
    global TRIGGER_Z_STAGE
    global COMPLETE
    
    # Wait for trigger to happen
    while not TRIGGER_Z_STAGE:
        pass
    
    # Do something
    global SLEEPTIME

    time.sleep(SLEEPTIME)

    device.approach_stored_position(axis, pos2)
    time.sleep(SLEEPTIME+5)
    device.approach_stored_position(axis, pos1)
    
    # Change completion flag
    COMPLETE = True
        

def main():
    # Global flags
    global TRIGGER_Z_STAGE

    # Create and establish serial connection to new device
    my_device = LandNSM10(verbose=3)

    # Z stage axis number
    z_stage = 15

    # Stored positions
    position_1 = 1
    position_2 = 2

    # Move to Position 1
    my_device.approach_stored_position(z_stage, position_1)

    # Open serial connection with ARDUINO
    arduino = serial.Serial(port=PORT, baudrate=BAUDRATE)
    
    # Initiate reading thread
    reading_thread = threading.Thread(target = read_serial, args=[arduino])
    reading_thread.start()
    
    # Initiate triggering thread
    triggering_thread = threading.Thread(target = trigger_z, args=[my_device, z_stage, position_1, position_2])
    triggering_thread.start()
    
    # Poll for completion at low frequency
    while not COMPLETE:
        time.sleep(.1)
    
    # Terminate threads
    reading_thread.join()
    triggering_thread.join()
    
    # Close serial connection with ARDUINO
    arduino.close()

    # Delete and terminate device connection
    del my_device

    
if __name__ == "__main__":
    main()