#% [markdown]
"""
## Concept of Operations

The mission consists of a main CubeSat and a camera payload. The payload takes pictures of the CubeSat from the point of view of a proximal spacecraft that can be used by stakeholders to develop and test object recognition, pose estimation, depth estimation, proximity operations, docking, etc. algorithms and systems, which in turn have applications in active debris removal, and in-orbit maintenance, manufacturing, and assembly.
As the mission experiences different space conditions throughout its orbit and lifespan, different picture datasets can be created.

The ideal case is that we can take a picture of the main CubeSat from any point on a ball centered on it, at any orientation. The required poses could be requested by the stakeholders as a function of time and current pose.

There is no other proposed data collection task proposed for the payload. Gyroscope or accelerometer data is measured only to move the camera to the requested poses (e.g. by applying inverse kinematics). Stakeholders would only need to know that the pose was reached with an approved tolerance.

## Problem definition

The radius $r$ of the ball is to be determined from the resolution $p_{max}$ of the camera that can be fit into the payload and the minimum resolution $p_{min}$ needed so that the pictures are useful to the stakeholders. In practice, we would only need to take pictures from the radius of the ball (maximum separation, $r_{max}$) down to a nonzero minimum $r_{min}$ that avoids collisions and captures a minimum volume of interest of the CubeSat, so actually a ball shell.

Just like a point on the surface of the Earth, the point from which the camera observes the CubeSat can be described by two angles $\theta$ and $\phi$ (e.g. latitude and longitude).
These two angles could be constrained to a practical range (e.g. one hemisphere).

It isn't trivial how the camera boresight can always pass through the center of the ball to keep the CubeSat perfectly centered, or whether this is needed by the stakeholders, so we may also care about the pitch $\alpha$ and yaw $\gamma$ of the camera. Camera roll about the boresight $\beta$ matters when it changes what is captured in the scene (e.g. a non-circular FOV shape places different parts of the background inside or outside the picture depending on roll, and it can also change the captured volume if the CubeSat isn't fully within the frame). The orientation is also practically constrained, since for a given camera FOV, spherical angles, and radius many possible states can result in pictures that capture an insufficient or even null volume of the CubeSat.

Whichever physical means is used to mechanically link the CubeSat and the camera can become an undesired obstruction in the pictures. A camera array (e.g. flower topology) and image processing algorithms could be used to artificially remove the obstructions, which introduces an on-board image processing power vs. downlink data volume tradeoff depending on whether the pictures are downlinked edited or raw.

Let's propose a set of alternatives based on the amount of DOFs relevant to the picture capturing problem:
1. Maximum control and complexity: pitch, yaw of the camera boresight, camera roll about the boresight, and latitude, longitude, and radius of the camera center of projection, 6 degrees of freedom.
2. Roll irrelevant, non-centered: pitch, yaw of the camera boresight, and latitude, longitude, and radius of the camera center of projection, 5 degrees of freedom.
3. Centered: camera FOV roll about the boresight, latitude, longitude, and radius of the camera center of projection, 4 degrees of freedom.
4. Roll irrelevant, centered: latitude, longitude, and radius of the camera center of projection, 3 degrees of freedom.

The alternatives admit constraining all degrees of freedom to individual operational ranges. It must be validated whether the achievable ranges cover all poses, either individually specified or as part of a trajectory, necessary to generate the datasets that stakeholders need, with the resolution and captured CubeSat volume that they need.
"""

#% [markdown]
"""
## Literature review

In order to map the needs of potential stakeholders and existing enablers, metadata searches were conducted in IEEE Xplore.

For each relevant paper, the minimum and maximum values for the following variables of the camera were extracted, in the original units:
- ball radius
- spherical angles
- pitch, roll, and yaw

Each of the above variables was coded as actively controlled (with original wording for how, including mechanisms, algorithms, and closed-loop variables), passively controlled (with original wording for how), irrelevant (with original wording for why), not controlled (with any original wording for why), or unreported (range limits left blank).
All of the evidence related to the variable ranges was highlighted in Green in the source PDFs, while the evidence related to the control means was highlighted in Blue.

The following camera properties were extracted, in the original units:
- resolution
- resolution for image processing
- FOV

Unreported values were left blank.

The following categories were extracted:
- demonstration or proposal (highlighted in Pink)
- enabler (source describes how to generate a dataset), application (source describes an application of a dataset), or both (highlighted in Pink)
- applications: what the dataset can be or was used for (original wording) (highlighted in Purple)
- FOV shape: circular, square, rectangular, other (original wording)
- camera topology (highlighted in blue): single camera, array (with any original wording), other (original wording)
- image processing algorithm(s) (original wording)
- pose function: discrete set, parametric trajectory, active control, other (original wording) (highlighted in Green)
- image subject (highlighted in Blue): CubeSat (recording how many U), other spacecraft (original wording)
- camera type (highlighted in Blue): payload (recording how many U), spacecraft (original wording), non-orbital (original wording), synthetic

Unreported categories were left blank.

The following yes/no/unreported questions were answered:
- is the picture subject intended to be always perfectly centered?
- is the picture subject intended to be always fully within the frame?
- was the camera or an element mechanically linked to it described as a possible or actual obstruction in the pictures?
- did the content of the background matter?

All the evidence for these yes/no questions was highlighted in Blue.

Whenever highlight color is not specified, Yellow was used. Colors refer to the defaults in Apple Preview. When figures where relevant, their captions were highlighted.

The following keyword search query was used to discover the needs of potential stakeholders:

> `(spacecraft OR satellite OR CubeSat) AND (image OR picture OR camera OR vision) AND (dataset OR "data set" OR database OR benchmark OR collection) AND (pose OR rendezvous OR docking OR proximity OR debris OR "spacecraft
 detection" OR "spacecraft segmentation")`

The following keyword search query was used to discover potential enabling technologies:

> `(spacecraft OR satellite OR CubeSat) AND (camera OR imaging) AND ("robotic arm" OR manipulator OR gimbal OR boom OR tether OR testbed)`
"""