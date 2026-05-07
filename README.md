
<div align=center>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="imgs/logos/TonaFlow_DarkMode.png">
  <source media="(prefers-color-scheme: light)" srcset="imgs/logos/TonaFlow_LightMode.png">
  <img alt="" src="https://user-images.githubusercontent.com/25423296/163456779-a8556205-d0a5-45e2-ac17-42d089e3c3f8.png">
</picture>
</div>




<h1 align='center'>TonaFlow  - A Free Program for ECG Processing</h1>
<!-- <h2 align='center'> Authors</h2> -->
<h2 align="center" style="margin-bottom: 4px;">
Manash Sahoo<sup>1,2</sup>, Katherine D. Rhodes<sup>1,2</sup>, Natasha Mbajonas, Jeremy I. Borjon<sup>1,2,3,4</sup>
</h2>

<h4 align="center" style="margin: 2px 0;">
<sup>1</sup> Department of Psychology, University of Houston, USA
</h4>

<h4 align="center" style="margin: 2px 0;">
<sup>2</sup> Texas Institute for Measurement, Evaluation, and Statistics, University of Houston, USA
</h4>

<h4 align="center" style="margin: 2px 0;">
<sup>3</sup> Texas Center for Learning Disorders, USA
</h4>

<h4 align="center" style="margin-top: 2px;">
<sup>4</sup> Department of Child and Adolescent Psychiatry and Psychotherapy, Heidelberg University Hospital, Heidelberg University, German Center for Mental Health (DZPG)
</h4>







<h1>
    About
</h1>


<img src="doc/imgs/Screenshots/TF_Full.png">


<p>
Deriving heart rate from a raw electrocardiogram (ECG) signal is not trivial. Efficient and effective processing for ECG signals requires a multi-stage pipeline that involves manual inspection and making analytically informed decisions regarding parameter adjustments for filtering, R-peak detection, and noise removal. Currently, a large amount of the software that exists to facilitate this multi-stage process is expensive and closed-source, while free and open-source solutions require programming experience and are thus not conducive to accessibility. Here, we present <i> TonaFlow </i>, a one-click application that is free, open-source, and accessible to researchers of all career stages and technical backgrounds.
</p>







# Installation
TonaFlow is easy to install! We provide both portable executables (.exe / .dmg) for a one-click launch, as well as the ability to build from source code:
## Executables
[Grab the latest TonaFlow executable here! (Linux, OSX, Windows)](https://github.com/borjonlab/TonaFlowPy/releases/tag/Latest)
## Running from Source
```
# Clone the repo.
git clone https://github.com/borjonlab/TonaFlowPy.git
cd TonaFlowPy

# Create a virtual environment, install dependencies.
python -m venv ./venv
source ./venv/bin/activate 
pip install -r requirements.txt

# Run and have fun!
python TonaFlow.py
```

## Building from Source
```
git clone https://github.com/borjonlab/TonaFlowPy.git
cd TonaFlowPy

# Create a virtual environment, install dependencies.
python -m venv ./venv
source ./venv/bin/activate 
pip install -r requirements.txt

# Run the PyInstaller build script 
python3 build_tonaflow.py

# After completion, obtain the executable from '/dists/'
```

# Have Thoughts?
<p> 
We want TonaFlow to make things easier, not harder. Let us know what you love, hate, or would like in the next release of TonaFlow by filling out this short survey!
</p>

# License
This project is licensed under **GNU GPLv3**, and is provided to the user "As is."








