# WLKATA Mirobot Apple Picking System
This project was inspired by the __[WLKATA Mirobot Fruit Picking Cell](https://www.wlkata.com/products/wlkata-mirobot-fruit-picking-cell-ai-vision-smart-farming-training-solution?srsltid=AfmBOoqAc8YDDn7FQlc3SLJ9pG7SN-iGf-ZfR0vqHMXYsWzJBoCJjYRc)__, where it demonstrates a standard agricultural robotic picking process integrated with the __OpenMV__ vision system. The robot utilises AI vision and colour recognition to identify red apples, then operates its robotic arm to pick the apples and place them into a collection cart.

# Components
This setup uses [Mirobot Education Kit](https://www.wlkata.com/products/wlkata-best-6-axis-stem-educational-robot-arm-kit) and [AI Vision Set](https://www.wlkata.com/products/wlkata-ai-vision-set); additional components such as a tree stand, apples, and a cart, are printed out using a 3D printer, provided in the _print_ folder. The following shows all components needed for this setup:

| Mirobot Education Kit | AI Vision Set | Printed Components |
| --------------------- | ------------- | ------------------ |
| Mirobot robot arm | Vision stand | m_cam-stand.stl
| Power supply & USB cable & IDC cable | Vision camera module | m_rail.stl
| Suction cup | Light ring | m_main.stl
| Multifunctional box | Display screen | m_tree-stand.stl

# Set up
<details>
  <summary>Click to see explaination on how to setup the system</summary>

  #### 1. Camera stand - m_cam-stand.stl <br>
  For this setup, the vision module should be mounted sideways instead of the default top-down configuration. Mount the camera stand on the side without the flange. Secure the vision stand, followed by the light ring. Ensure both components are centered to the apples to provide proper alignment during operation. <br>
![cam-stand](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/cam-stand.jpg?raw=true)

  #### 2. Rail - m_rail.stl <br>
  Attach the rail to the calibration board. The placement is flexible; in our setup, it is positioned at the edge. If a different location is desired, the corresponding adjustments can be made directly in the code. <br>
![rail](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/rail.jpg?raw=true)

  #### 3. Tree and Apples - m_main.stl <br>
  To attach the apples securely to the tree, use magnet tape. Place the tape around the perimeter of each apple and on the tree at positions matching the apples’ size. This allows the apple to be easily attached and removed during the picking process. <br>
![main](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/main.jpg?raw=true)

  #### 4. Tree stand - m_tree-stand.stl <br>
  Use the flange as a guide for positioning the curved sections of the stand. Begin by attaching the base, securing the clip and locking the assembly in place as illustrated. <br>
![tree-stand](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/tree-stand.jpg?raw=true)

_Once you have completed the assembly, it should come together like this:_ <br>
![setup-3d](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/setup-3d.jpg?raw=true)
![setup](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/setup.jpg?raw=true)
</details>

# Code Explanation
<details>
  <summary>Click to see explaination on the code</summary>

  ### Imports and Initialisations
  Before running the system, necessary modules must be imported: 
  - `sensor` controls the camera sensor.
  - `display` manages the LCD screen.
  - `pyb` handles communication between the OpenMV and robotic arm.
	The camera settings must also be configured during this stage to ensure reliable detection.
  ```
  import sensor, pyb, display
  from pyb import UART

  uart = UART(3, 115200)
  
  sensor.reset()
  sensor.set_pixformat(sensor.RGB565) 
  sensor.skip_frames                  
  sensor.set_auto_gain(False)         
  sensor.set_auto_whitebal(False)     
  
  sensor.set_framesize(sensor.LCD)
  sensor.skip_frames(time=2000)
  lcd = display.SPIDisplay()
  ```

  ### Functions
  Functions are used to organise the code and perform a specific repetitive task. In this project, two functions are created:
  - `write(command, wait=True)` sends a command to the robot through UART and, if specified, waits for the robot to finish its movement before sending another command.
  - `linear_regression(x, y)` to convert camera coordinates into robot position coordinates.<br>

The function `write()` streamlines communication with the robotic arm. Instead of relying on `pyb.delay(1000)`, which is inconsistent (too long or too short), `write()` directly checks the robot’s responses to ensure each command is completed before the next is sent. It also eliminates the need to write `\n` after every command, making it more readable.
```
def write(command, wait = True):
uart.write(command + "\n")
if wait == True:
    inBytes = b''
    for i in range(100):            
        while uart.any() > 0:
            inBytes += uart.read()
        if b'>' in inBytes:
            break
        pyb.delay(5)
```
  Having the function `linear_regression()` makes it easier to debug in the case of the robot moving to the wrong coordinates. This function can be used to test the robot manually with known inputs and see if it gives out the expected output. Since we are using linear regression twice, it is cleaner to write the logic once.
  ```
  def linear_regression(x, y):
  n = len(x)
  sx = sum(x)
  sy = sum(y)
  sx2 = sum(x[i]**2 for i in range(n))
  sxsy = sum(x[i] * y[i] for i in range(n))
  
  m = (n * sxsy - sx * sy) / (n * sx2 - sx**2)
  b = (sy - m * sx) / n
  return m, b
  ```
  ### Default Values
  Specific parameters are configured to ensure smooth and accurate operation. By providing a reliable baseline, the system is able to ensure consistent behaviour across multiple attempts. It also simplifies troubleshooting as it will always be attributed to dynamic inputs rather than the systems’ initialisation. <br>

  | Functions | Code |
  | --------- | ---- |
  | Tree center coordinates | `bx = 55`<br>`by = 107` |
  | Colour thresholds | `colour = [(20, 71, 15, 45, -15, 40)]` |
  | Region of Interest (ROI) | `tree_roi = (bx - 20, by - 60, 80, 62)`<br>`lcd_roi = (0, 0, 128, 160)` |
  
  The camera and robot do not share the same coordinate system. The camera detects objects in the x and y axes, while the robot moves along the x and z axes. To align them, we use calibration datasets to map camera pixel values to real robot positions. These mapping are then processed using linear regression to establish a mathematical relationship between the two coordinate systems.

This calibration ensures that when the camera detects an apple, the robot can correctly interpret its real world location and move towards the exact position: <br>

  | X-Axis Calibration | Z-Axis Calibration |
  | ------------------ | ------------------ |
  | `camera_x = [43, 61, 84, 80]` | `camera_y = [93, 105, 105, 100]` |
  | `robot_x = [197, 215, 231, 247]` | `robot_z = [126, 100, 132, 100]` |

  ### Linear Regressions
  Linear regression is a simple method used to model the relationship between a dependent variable and one or more independent variables. In this case, the linear relationship determines the correlation between the camera’s x and y coordinates and the robot’s x and z coordinates . This involves performing two separate linear regressions: 
  
  1. Mapping the camera’s _x-axis_ to the robot’s _x-axis_ <br>
  ![linear-x](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/calc/linear-x.jpg?raw=true)
  2. Mapping the camera’s _y-axis_ to the robot's _z-axis_ <br>
  ![linear-y](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/calc/linear-y.jpg?raw=true)

  The steps for performing linear regression are outlined below:
  | Calculation | Mathematical Process | Coding Process |
  | ----------- | -------------------- | -------------- |
  | Slope _m_ | (math) | `n = len(x)`<br>`sx = sum(x)`<br>`sy = sum(y)`<br>`sx2 = sum(xi**2 for xi in x)`<br>`sxsy = sum(x[i] * y[i] for i in range(n))`<br><br>`m = (n * sxsy - sx * sy) / (n * sx2 - sx**2)` |
  | Intercept _b_ | (math) | `b = (sy / n) - m * (sx / n)` |
  | Equation | (math) | `for i in range (n):`<br>`  robot_x_pos = b_x + m_x * x[i] + offset_x`<br>`  robot_z_pos = b_z + m_z * y[i] + offset_y` |
  
  Calibration values are the slope and intercept obtained from these regressions. They are crucial as they translate the camera coordinates into accurate robot coordinates. They ensure it moves accurately based on camera input. Without them, the robot may overshoot, undershoot, or move to completely wrong positions.
  
  ### Robot Commands
  Before allowing the robot to move on with detection, certain conditions must be met:
  1. Enable feedback communication so responses are tracked.
  2. Reset the robot to its home position.
  3. Set the movement mode to absolute positioning with linear motion commands _(assuming robot has been previously used)_.
  4. Switch off suction pump to ensure safe starting state.
  ```
  write("$40 = 1", False)
  write("$H")
  pyb.delay(8000)
  write("M20 G90 G00 F1000", False)
  write("M3S0")
  ```
  Once these conditions are satisfied, the robot performs the following workflow:<br>
  ![workflow](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/calc/workflow.jpg?raw=true)<br>
  
  The robot repeats this workflow until all apples have been collected, then returns to its home position to conclude the operation. The following shows how the robot should look like while collecting, suctioning, and placing apples into the cart.

  OpenMV uses UART _(Universal Asynchronous Receiver Transmitter)_ to directly communicate and exchange data between the computer and the robot. Below are common UART commands that correspond to __[Mirobot API functions](https://document.wlkata.com/?doc=/wlkata-mirobot-user-manual-platinum/)__ used in Wlkata Studio.
  | Functions | Mirobot API Command | UART Command |
  | --------- | ------------------- | ------------ |
  | Initialisation | `from mirobot`<br>`import MirobotAPI` | `uart = UART(3, 115200)` |
  | Homing | `api.home_simultaneous()` | `uart.write("$H\n")` |
  | Coordinate moving axis | `api.go_to_cartesian_lin(Motion.MOVJ, X, Y, Z, A, B, C)` | `uart.write("M20 G90 G1 X0 Y0 Z0\n")` |
  | Joint moving axis | `api.move_to_axis(MirobotJoint.Joint1, RevolveDirection.cw, 0)` | `uart.write("A0 B0 C0\n")` |
  | Open the suction cup | `api.suction_cup_on()` | `uart.write("M3 S1000\n”)` |
  | Close the suction cup | `api.suction_cup_off()` | `uart.write("M3 S0\n")` |
  | Set delay time | `sleep(1)` | `pyb.delay(1000)` |
  
</details>

# Troubleshooting
### 1. Camera Not Recognising the Tree <br>
In the _‘Default Values’_ section, the camera uses the pre-defined coordinates for the center of the tree `bx = 55, by = 107`. If these values are incorrect, the camera may fail to detect the tree.

___Fix:___ Use OpenMV and click the middle point of the tree through the _‘Frame Buffer’_ found on the right side of the interface.
You may also need to adjust the region of interest (ROI) for both the tree and the LCD display:
1. Tree ROI: `tree_roi = (bx - 20, by - 60, 80, 62)`
2. LCD display area: `lcd_roi = (0, 0, 128, 160)`

Highlight the surface area where you want the camera to detect apples and adjust the values accordingly to ensure accurate detection.

### 2. Camera Not Recognising the Apple <br>
Due to varying lighting conditions, the camera may sometimes fail to detect apples correctly.

___Fix:___ Use OpenMV to highlight the apple in the Frame Buffer on the right side of the interface. Then, switch the histogram to  _‘LAB Colour Space’_  and note the minimum and maximum values for each channel displayed on the screen.

Replace the default threshold values in the _‘Default Values’ section_ (`colour = [(20, 71, 15, 45, -15, 40)]`) with your observed values, using the format: `[(L(Min), L(Max), A(Min), A(Max), B(Min), B(Max)]`.

### 3. Robot Not Moving to Target Location
The robot moves based on the coordinates obtained from apple detection. If it does not reach the expected position, the offset values may be incorrect.

___Fix:___ Check the LCD or the robot’s screen monitor to verify the detected coordinates. Adjust the offset values in the _‘Default Values’_ section as needed:
1. `offset_x = -2.5`
2. `offset_y = 1.2.`

### 4. Robot Unable to Suction the Apples
If the robot fails to suction the apples, this usually indicates that the robot does not lower itself enough to reach the apples. 

___Fix:___ Adjust the Y values in the robot movement commands in the _‘Robot Communication: Moving the robot’_ section:
1. `write("Y+20")`
2. `write("Y-20")`

### 5. Robot Not Following Movement Instructions
The code utilises the `write()` function to ensure each robot instruction is completed before moving onto the next command. In the case of the robot skipping or ignoring its commands, it may need more time.

___Fix:___ Increase the limit of check loops and the delay speed in the _‘Functions’_ section. 
1. `for i in range(100):`
2. `pyb.delay(5)`

This gives the robot more time to process each instruction safely.
