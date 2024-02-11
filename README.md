# Pancake Robot (Beta)

An integration of the [Ufactory Lite 6 robot arm](https://www.ufactory.cc/lite-6-collaborative-robot/) with regular 
kitchenware to make pancakes.

Includes software for jogging the robot arm with a 3D mouse and recording sequences for playback.

## Video
https://www.youtube.com/watch?v=gNBi5sjOdsg

## Software

### Installation 

```
pip install -r requirements.txt
```

### Example Usage

```
# Make a pancake
python main.py 192.168.4.100
l
sequences/pancakes
p
```

### Input

Requires a connected spacemouse, see [hardware](#Hardware).

- Control
  - Spacemouse x/y/z/roll/pitch/yaw: move the arm.
  - `x` or `Ctrl-C`: exit
  - `l`: load sequence from file, e.g. "sequences/pancakes"
  - `p`: play sequence
  - `s`: save sequence to file
  - `c`: clear sequence
- Recording
  - `r`: record current position to sequence
  - `1`: record gripper open to sequence
  - `2`: record gripper close to sequence
  - `3`: record gripper stop to sequence
  - `4`: record pause to sequence
  - `i`: include subsequence from file, e.g. "sequences/open"
  - `[`: decrease speed to next recorded position
  - `]`: increase speed to next recorded position
  - `,`: decrease radius to next recorded position
  - `.`: increase radius to next recorded position

## Hardware

- Robot & Control
  - [Ufactory Lite 6 Robot Arm & Gripper](https://www.ufactory.cc/lite-6-collaborative-robot/)
  - [Spacemouse Compact](https://3dconnexion.com/us/product/spacemouse-compact/)
  - Windows Laptop
- Kitchenware
  - [DASH Mini Maker Electric Round Griddle for Individual Pancakes](https://www.amazon.com/Dash-Mini-Maker-Individual-Breakfast/dp/B01MTXBOA6)
  - [Salton Coffee Tea Warmer](https://www.amazon.com/dp/B0095GOBGE)
  - [Merkaunis Soup Ladle 2 oz](https://www.amazon.com/dp/B0BNVR7DXM)
  - [Pyrex Measuring Cup](https://www.amazon.com/Pyrex-Pyrex%C2%AE-1-Pint-Measuring-Cup/dp/B01L4JNR0U)
  - [Dowan 8oz Ramekin](https://www.amazon.com/gp/product/B081N57T3D)
  - Silicone Basting Brush
  - Silicone Spatula
- Fabrication Materials
  - 2' x 2' 1/2" plywood panel
  - 1/4" HDPE Sheet
  - Cyanoacrylate Glue
  - [5x2mm Magnets](https://www.amazon.com/Magnets-Refrigerator-Neodymium-Whiteboard-Kitchen/dp/B0CCXY6WBR)
  - #4 Wood Screws
  - #8 Wood Screws
- Shop Tools
  - Scroll saw
  - Belt sander
  - Hand drill