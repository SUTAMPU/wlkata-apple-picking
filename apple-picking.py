import sensor, pyb, display
from pyb import UART

# ================================ Initialisation ================================
# OpenMV and robot
uart = UART(3, 115200)                  # Set the serial port for UART communication

# Camera sensor
sensor.reset()                          # Initialise the camera sensor
sensor.set_pixformat(sensor.RGB565)     # Set the image color format to RGB565 colour graph
sensor.skip_frames                      # Wait for the setting to take effect
sensor.set_auto_gain(False)             # If color recognition is used, it must be turned off
sensor.set_auto_whitebal(False)         # If color recognition is used, it must be turned off

# Screen
sensor.set_framesize(sensor.LCD)        # Set the frame size for LCD (128x160)
sensor.skip_frames(time=2000)           # Let the camera image stabilise after 2000ms
lcd = display.SPIDisplay()              # Driving the LCD

# ================================ Functions ================================
# To command the robot
def write(command, wait = True):
    uart.write(command + "\n")
    # To wait for robot to finish its movement
    if wait == True:
        inBytes = b''
        #print('wait')
        for i in range(100):                # Set the amount of limit check loop
            while uart.any() > 0:
                inBytes += uart.read()
            if b'>' in inBytes:
                break
            pyb.delay(5)
        '''
        if b'>' not in inBytes:             # Print this during debugging
            print("No response")
        print(inByte)
        print('finish')
        '''

# To find the robot position
def linear_regression(x, y):
    n = len(x)
    sx = sum(x)
    sy = sum(y)
    sx2 = sum(x[i]**2 for i in range(n))        # Sum of all x^2
    sxsy = sum(x[i] * y[i] for i in range(n))   # Sum of all xy

    # Calculate slope (m) and intercept (b)
    m = (n * sxsy - sx * sy) / (n * sx2 - sx**2)
    b = (sy - m * sx) / n
    return m, b

# ================================ Default Values ================================
# Center x,y coordinates for the tree area
bx = 55
by = 107

# Colour threshold for red apples (L Min, L Max, A Min, A Max, B Min, B Max)
colour = [(20, 71, 15, 45, -15, 40)]

# Region of interest
tree_roi = (bx - 20, by - 60, 80, 62)   # Tree area
lcd_roi = (0, 0, 128, 160)              # LCD display area

# Linear Regression 1: Calibration dataset for x-axis
camera_x = [43, 61, 84, 80]             # X-axis
robot_x = [197, 215, 231, 247]          # Y-axis

# Linear Regression 2: Calibration dataset for z-axis
# (The robot moves in z-axis instead of y-axis from the camera)
camera_y = [93, 105, 105, 100]          # X-axis
robot_z = [126, 100, 132, 100]          # Y-axis

# Default x,y coordinates offset for the robot position
offset_x = -2.5
offset_y = 1.2

# ================================ Robot Communication ================================
# ==== Preparing the robot ===
write("$40 = 1", False)                 # Let the arm return messages (feedback)
write("$H")                             # Reset the arm to default position (home)
pyb.delay(8000)                         # Make sure the action is complete
write("M20 G90 G00 F1000", False)       # Set the coordinate mode of the robotic arm to absolute (G90) and linear move (G00)
write("M3S0")                           # Make sure air pump is off

# ==== Finding the apples ====
while(True):
    img = sensor.snapshot() # Get an image from the camera

    # Show the bounding box of the tree and its center
    img.draw_cross(bx, by, color = (0, 0, 0), size = 10, thickness = 1)
    img.draw_rectangle(32, 70, 60, 50, color = (0, 0, 0), thickness = 1, fill = False)
    lcd.write(img, roi = lcd_roi)

    # Find colour blobs (red apples) within the tree_roi
    blobs = img.find_blobs(colour, roi = tree_roi, x_stride = 5, y_stride = 5, pixels_threshold = 50)
    print(f"Red apples found: {len(blobs)}")

    # If no blobs are found, continue to the next loop
    if len(blobs) == 0:
            print("No red apples detected")
            continue

    # Lists initialisation to store apples' coordinates
    x = []
    y = []

    for blob in blobs:
        # Highlight red apples found on the lcd display
        img.draw_string(blob.x(), blob.y() + 20, 'Red Apple')
        img.draw_cross(blob.cx(), blob.cy())
        img.draw_rectangle(blob.rect())
        lcd.write(img, roi = lcd_roi)

        # Store found coordinates into the lists
        x.append(blob.cx())
        y.append(blob.cy())

    # Exit the loop once all red apples have been found
    break

print('All apples coordinates')
print('x-axis: ', x)
print('y-axis: ', y)
print('')

# ==== Moving the robot ====
# Calculate coefficients
m_x, b_x = linear_regression(camera_x, robot_x) # Finding x-position
m_z, b_z = linear_regression(camera_y, robot_z) # Finding z-position

# Number of detected red apples
n = len(x)

# For each detected red apples, move the robotic arm according to the calibrated apples
for i in range (n):
    robot_x_pos = b_x + m_x * x[i] + offset_x   # Predicting x-position
    robot_z_pos = b_z + m_z * y[i] + offset_y   # Predicting z-position

    # Send instructions to the robotic arm
    output_str = "X{:.2f} Y70 Z{:.2f}\r\n".format(robot_x_pos, robot_z_pos)
    print(f"Apple {i+1}:")
    print(f"Detected at: {x[i]}, {y[i]}")
    print(f"Output position: {output_str}")

    write(output_str)                           # Move arm above the apple
    write("A90 B0 C0")                          # Rotate joint
    write("M20 G91")                            # Change to relative position mode
    write("Y+20")                               # Adjust height of the suction cup (downwards)
    write("M3 S1000", False)                    # Activate the suction
    write("Y-20")                               # Adjust height of the suction cup (upwards)
    write("M20 G90")                            # Change to absolute position mode
    write("X295 Y10 Z120")                      # Move to the cart area
    write("A0 B0 C0")                           # Rotate joint
    write("M3 S0", False)                       # Deactivate the suction

# ==== Returning the robot ====
print("Returning to home position")
write("$H")
