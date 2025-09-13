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
  For this setup, the vision module should be mounted sideways instead of the default top-down configuration. Mount the camera stand on the side without the flange. Secure the vision stand, followed by the light ring. Ensure both components are centered to the apples to provide proper alignment during operation.
![cam-stand](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/cam-stand.jpg?raw=true)

  #### 2. Rail - m_rail.stl <br>
  Attach the rail to the calibration board. The placement is flexible; in our setup, it is positioned at the edge. If a different location is desired, the corresponding adjustments can be made directly in the code.
![rail](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/rail.jpg?raw=true)

  #### 3. Tree and Apples - m_main.stl <br>
  To attach the apples securely to the tree, use magnet tape. Place the tape around the perimeter of each apple and on the tree at positions matching the apples’ size. This allows the apple to be easily attached and removed during the picking process.
![main](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/main.jpg?raw=true)

  #### 4. Tree stand - m_tree-stand.stl <br>
  Use the flange as a guide for positioning the curved sections of the stand. Begin by attaching the base, securing the clip and locking the assembly in place as illustrated.
![tree-stand](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/tree-stand.jpg?raw=true)

__Once you have completed the assembly, it should come together like this:__
![setup-3d](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/setup3d.jpg?raw=true)
![setup](https://github.com/SUTAMPU/wlkata-apple-picking/blob/main/setup/setup.jpg?raw=true)
