## RQ2-1

The CubeSat Conceptual Design Tool will be built around a central interface, referred to as the Main GUI (graphical user interface), with individual Subsystem Design Modules built for each CubeSat subsystem. The tool will be able to integrate with a CubeSat Model, developed off of the CubeSat System Reference Model (CSRM) [7]. (p. 21)

This thesis focuses on how the core of the tool operates, interacts with the user, interfaces with the design modules, and works with the MBSE CubeSat Model. The definitions for the key elements of this work are found in Table 2 and the interaction between those elements is shown in Figure 2. In particular, this thesis included the development of the Electrical and Power Subsystem (EPS) Design Module as a first step for the development of all Subsystem Design Modules and a demonstration for future work. (p. 22)

The CSRM is a model of a CubeSat developed in MBSE by the INCOSE Space Systems Working Group (SSWG) [29]. It consists of a modeled architecture for a CubeSat program accounting for elements across an entire system life cycle. It was developed to be a starting point for CubeSat developers who wish to utilize MBSE, in order to promote the rigorous application of system engineering practices in their CubeSat programs [30]. The CSRM was partially deemed necessary in order to address the high failure rates for CubeSats, as discussed in Section 2.1.1. (p. 36)

The CubeSat Model was based on the CSRM that was discussed in Section 2.3. The CSRM does not currently work with open-source MBSE software, so the model needed to be recreated for this thesis. Furthermore, this new model, referred to as the CubeSat Model, is not a pure recreation of the CSRM, as the CubeSat Model requires adaptations to interface with the parameters coming from the Conceptual Design Tool. The resulting model includes a more detailed level of design for the CubeSat. These changes in the CubeSat Model mean it will not be fully developed, however, as expansion is limited to the package structure and the thread of development for whichever Subsystem Design Module is being implemented. This is due to the lack of knowledge over the values that will need to be added to the model. Therefore, as other modules are worked on, they will have control over what needs to go within their respective domains. (pp. 51-52)

This chapter presents the EPS Module that was developed for the CubeSat Conceptual Design Tool. This is the first subsystem module to be implemented for the tool. As such, its development is both test case for the overall tool and a pathway for future subsystems. The EPS Design Module is comprised of two separate classes, stored in two different Python scripts. One of these classes is for the EPS GUI, while the other is for the EPS Design Tool. (p. 55)

As mentioned earlier, the outputs from the Conceptual Design Tool are saved to a CSV Output File. Table 14 shows the raw data from an Output File generated from a single development test of the Conceptual Design Tool, copied from the CSV viewed in table form. Note that the output includes the variables, variable names, and units alongside the value to enable readability of the CSV for easy access to design outputs. Currently, the tool does not take into consideration the required precision for the different values, and this should be addressed in later work. (p. 72)

The elements of the CSRM replicated in depth and then changed for this thesis were primarily those related to the EPS for the CubeSat. Those modifications to the EPS portion of the model to suit the tool primarily consisted of developing a table to input the parameters from the tool. Specifically, these changes were made within Architecture package, including the Level 3 CubeSat Subsystems Package and Level 4 CubeSat Subsystems Components packages. Furthermore, a Level 5 CubeSat Subsystem Parameters package was made for holding the newly entered parameters and storing the values, as shown in Figure 17. (p. 74)

The code for CubeSat Conceptual Design Tool and files for the CubeSat Model are available in the linked GitHub repository:

https://github.com/snogrady/NogradyThesis_CubeSatConceptualDesignTool (p. 105)

## RQ2-1.2

The CubeSat Conceptual Design Tool is being created in Python, specifically Python 3.9. Python was chosen over other programming languages for several reasons. First, Python is a free, open-source language, unlike MATLAB, another commonly used language for design analysis [36][37]. As a high-level programming language, Python makes use of natural language abstraction and minimizes syntax requirements, which maximizes code readability. These features of Python are critical on a project that will see numerous code developers work on it over time by lowering the barriers to entry for people without Python experience and enabling easier comprehension of others code. (p. 45)

The original CSRM was created in Cameo Systems Modeler, which is proprietary software currently published by Dassault Systèmes [31]. The CubeSat Model based on the CSRM had to utilize open-source software. This was done by using Eclipse 4.18 as the IDE and Papyrus 5.0 as the modeling environment plug-in, utilizing SysML 1.4 for Papyrus as the modeling language. The full breakdown of software that was used can be found in Table 8. (pp. 46-47)

Table 8. Software Utilized (p. 47)

## RQ2-1.4

A General Integrated Design Process involves a tool that is not developed for a single mission, but rather is generic and can be used repeatedly across differing missions. It also sees all the subsystems designed within one tool, rather than being designed separately and integrated later by the conceptual designers [22]. The tool can automatically use a unified set assumptions and design parameters, enabling a more powerful and faster design process. Creating a tool for this process does require a greater level of initial development, however, as it needs encompass all required subsystems and a range of varying mission profiles. (p. 31)

These modifications fit into the intention of the CSRM's creators, which was to allow for future users to use the CubeSat Model as a building block for their CubeSat specific models [29]. With the CubeSat Model being developed, however, the customization is going to be a generalized model itself, allowing for instances of the model to be created based for future CubeSat missions. (pp. 51-52)

## RQ2-2.1

[Figure 2.](../../../pdfs/review-reports/review-report-1009/figure_002.png) Overview of Tool and Model Interaction (p. 21)

[Figure 7.](../../../pdfs/review-reports/review-report-1009/figure_009.png) CSRM Overview Package Diagram [31] (p. 37)

[Figure 8.](../../../pdfs/review-reports/review-report-1009/figure_010.png) Package View of Space Segment of CSRM [31] (p. 38)

[Figure 9.](../../../pdfs/review-reports/review-report-1009/figure_011.png) Original Tool Architecture (p. 40)

[Figure 10.](../../../pdfs/review-reports/review-report-1009/figure_012.png) Final Tool Architecture (p. 43)

Table 9. Headers for a Sample Assumption File (p. 48)

[Figure 11.](../../../pdfs/review-reports/review-report-1009/figure_013.png) Main GUI Opening Page (p. 49)

[Figure 12.](../../../pdfs/review-reports/review-report-1009/figure_014.png) CubeSat Model Overview Package Diagram (p. 52)

The recreation of the CSRM as the CubeSat Model has progressed in the following manner. First, a focus was made on creating the package structure for the model, shown in Figure 12. The packages create the backbone of the model. Other elements, from package diagrams to individual values, fall into these packages. Accordingly, the next step was to make the necessary package diagrams that fall into different packages, of which many of the primary ones were recreated. Figure 13 shows one of these diagrams, the Architecture Hierarchy diagram for the Architecture segment of the model. The Architecture package is where the changes were made compared to the original CSRM in order to accommodate the parameters being output by the Conceptual Design Tool. The primary change shown here is the addition of the 'L5 Parameters' package and its contents to the architecture package. (pp. 52-53)

[Figure 13.](../../../pdfs/review-reports/review-report-1009/figure_015.png) CubeSat Model Architecture Hierarchy (p. 53)

A full list of parameters with associated units found in the EPS Design Module is presented in Table 10. This list includes the type of values they are. (p. 55)

Table 10. Parameters Utilized (pp. 55-56)

Table 11. Assumed Values for Design Options (p. 57)

[Figure 14.](../../../pdfs/review-reports/review-report-1009/figure_016.png) Use Case 1 Power Budget Tab (p. 60)

The first tab, Power Budget Input, shown in Figure 14, is where the power budget is input. If a user leaves any power value blank, it automatically sets the value to zero. This is also the tab where the total EPS power margin gets chosen. The user can name the different power modes and supply their duty cycles. There are also options for declaring a mode to be the standby mode or eclipse mode. The standby and eclipse modes set the duty cycle to a calculated value, which is covered in Section 4.3. A user can choose to use or forgo any of the modes and the tool will still work. (p. 60)

[Figure 15.](../../../pdfs/review-reports/review-report-1009/figure_017.png) Use Case 1 EPS Design Tab (p. 61)

[Figure 16.](../../../pdfs/review-reports/review-report-1009/figure_018.png) Use Case 2 EPS Design Tab (p. 62)

The equations used in the EPS Design Tool come from a variety of sources, but all follow the same general process. These include Space Mission Engineering: The New SMAD, Spacecraft Power Systems, and numerous CubeSat papers [46][50][47][51]. (p. 63)

Table 14. Sample Output CSV Values (p. 72)

A table was created for the convenient transfer of the values for these parameters from the Output File into the CubeSat Model. This table contains all of the parameters for the EPS in the same order as the Output File, allowing them to be copied and pasted directly from the CSV into the MBSE parameter table. This input table is shown in Figure 18. (p. 74)

Figure 17. Model Explorer View of Parameters Package (p. 75)

Figure 18. Power Parameters Table (p. 75)

## RQ2-3

A General Integrated Design Process involves a tool that is not developed for a single mission, but rather is generic and can be used repeatedly across differing missions. It also sees all the subsystems designed within one tool, rather than being designed separately and integrated later by the conceptual designers [22]. The tool can automatically use a unified set assumptions and design parameters, enabling a more powerful and faster design process. Creating a tool for this process does require a greater level of initial development, however, as it needs encompass all required subsystems and a range of varying mission profiles. (p. 31)

As shown in Figure 10, the Assumptions Files are in a separate CSV rather than coded into the Conceptual Design Tool. This was done for two primary reasons. First, it allows users easily to access and view the assumptions. Secondly, some assumed values can change over time, so an advanced tool user can update values as technology evolves or even customize sets of assumptions for individual design campaigns. Table 9 shows an example of what the header would look like for an assumption list CSV. "Variable" is the plain text name of the parameter being looked at, "Variable Name" is what that value is called in the code, and "Units" include the unit used for each parameter. There are multiple options for "Values", however, corresponding to the multiple Design Options for a user to select based on their desired level of customization or their available technology level. The Assumptions Files are in the same folder as the rest of the CubeSat Conceptual Design Tool. This is important, as it allows for a consistent path to importing the parameters. (p. 48)

Each subsystem has its own Subsystem Design Module within the CubeSat Conceptual Design Tool. This allows the modules to be developed in a piecewise manner, reducing the amount of work required by a single developer and allowing them to go more in-depth into their work. The development of a module includes all of the necessary assumptions, GUIs, design calculations, and outputs for a subsystem. While not explicitly part of a Subsystem Design Module, the corresponding elements of the CubeSat Model should be developed alongside the module. The Assumptions and Output Files are outside of the Python code as well, but they are read into or created by the module. (pp. 49-50)

The CubeSat Model was based on the CSRM that was discussed in Section 2.3. The CSRM does not currently work with open-source MBSE software, so the model needed to be recreated for this thesis. Furthermore, this new model, referred to as the CubeSat Model, is not a pure recreation of the CSRM, as the CubeSat Model requires adaptations to interface with the parameters coming from the Conceptual Design Tool. The resulting model includes a more detailed level of design for the CubeSat. These changes in the CubeSat Model mean it will not be fully developed, however, as expansion is limited to the package structure and the thread of development for whichever Subsystem Design Module is being implemented. This is due to the lack of knowledge over the values that will need to be added to the model. Therefore, as other modules are worked on, they will have control over what needs to go within their respective domains. (pp. 51-52)

There are three selectable Design Options within the Conceptual Design Tool's EPS Design Module. Each of these results in a different version of the initial parameter list. Specifically, the Design Options each have different columns of values within the EPS Assumptions File. The calculated values remain empty in the Assumptions File for all options, while the permanent assumptions are constant. The three options are: Custom, Standard, and Advanced. (pp. 56-57)

The first option is a Custom design. Custom design enables the user to input completely custom design sizing parameters. However, if data is not input for a parameter, the program will fall back to a default assumed parameter; thus, the program can still run. The EPS GUI does this by using try and except blocks in Python when reading the values input into the GUI. The try block first tries to run reading an input from the entry box, and if that is not successful, the except block will assign the default parameter. The default parameters currently correspond to the assumed values in the Standard Design Option. (pp. 57-58)

Use Case 2 enables a user to operate the Conceptual Design Tool without already having all the information about the power budget. It does this by developing the power parameters internally in other subsystems, through inputs or calculations by them. The values from other subsystems are then utilized in the EPS Design Tool, as all subsystems can use values from all other subsystems with this tool architecture. As seen in Figure 16, this means it only needs a single tab for the GUI. The power margin input is moved into the EPS Design Input tab for Use Case 2, as it is still needed. (pp. 61-62)

For the power budget in Use Case 2, the power modes and their subsystem specific power levels are assigned based on values developed in the other subsystems, rather than directly input into the EPS Design Module. This means the primary difference between Use Case 1 and Use Case 2 is the addition of assignment statements in the latter. Values for subsystem power levels, duty cycles, and operational mode names, are generated in other subsystems and then assigned to the same set of variables that are in Use Case 1. Currently, this is based around other subsystems providing values for nominal, communications, desaturation, and eclipse modes, although these could be changed in the future. Once these values are assigned, the existing framework for the power budget's full development, shown in Section 4.3.1, is followed. (p. 66)

In association with architecting the tool, the EPS Design Module was implemented successfully. It supports the tool by providing a method for sizing a CubeSat's EPS that can work either independently or interconnected with other subsystems. The EPS Design Module also lays the groundwork for future Subsystem Design Modules. These can be based off replications of the EPS Design Module and modified for those subsystems. The architecture of multiple Subsystem Design Tools operating around the Main GUI was demonstrated to be sound as well. (p. 92)

The CubeSat Conceptual Design Tool was designed to have a long operational life cycle, meaning the tool can function and evolve over the years as CubeSats and the needs of their developers evolve. To enable this, the Design Options within the Assumption File of this tool are designed to easily be changed as technology matures over time, with a simple modification to a CSV file. Also, the Subsystem Design Modules were implemented so they run largely independent from each other, containing their own GUI, running their own calculations, and outputting their own results. Such an architecture allows for the tool to be gradually built and upgraded one subsystem at a time, improving the long-term sustainability of the tool. (pp. 95-96)

Furthermore, there are changes that can be made to how data is read into the tool and how variables are assigned to be written out of it. Currently, this is done in a location-driven manner, meaning that the locations of variables in the CSVs have to be permanently coded into the Subsystem Design Module. However, this is a delicate approach, and one that is readily broken if changes are made to the tool's code or the Assumption File for that module. A better way to access variables from the CSVs would be to use a name-driven look up method, where the tool looks for the variable's name in the CSV file and then assigns the variable to the adjacent data. This method is an improvement over a location-driven process because it allows for modifications to be made to an Assumptions File or a Subsystem Design Module without errors being introduced causing the wrong values to be read into one or more variables. This also makes adding to or modifying the parameters used in a subsystem significantly easier. Fortunately, the Assumption Files already contain the variable names for each parameter, and these are already read into the tool as well. Therefore, it is only a minor change to make the variable assignments based on a name-driven approach rather than using a specific location of an array that is coded into the tool. All future Subsystem Design Modules should follow this adaptable name-driven approach to reading and writing data to the CSVs rather than the inflexible location-driven approach. (p. 97)

## RQ2-3.1

The CubeSat Conceptual Design Tool is being created in Python, specifically Python 3.9. Python was chosen over other programming languages for several reasons. First, Python is a free, open-source language, unlike MATLAB, another commonly used language for design analysis [36][37]. As a high-level programming language, Python makes use of natural language abstraction and minimizes syntax requirements, which maximizes code readability. These features of Python are critical on a project that will see numerous code developers work on it over time by lowering the barriers to entry for people without Python experience and enabling easier comprehension of others code. (p. 45)

The original CSRM was created in Cameo Systems Modeler, which is proprietary software currently published by Dassault Systèmes [31]. The CubeSat Model based on the CSRM had to utilize open-source software. This was done by using Eclipse 4.18 as the IDE and Papyrus 5.0 as the modeling environment plug-in, utilizing SysML 1.4 for Papyrus as the modeling language. The full breakdown of software that was used can be found in Table 8. (pp. 46-47)

The EPS Design Module has its subsystem design tool in a separate python module. This was done for ease of development of the module, as a single class with functions for the Subsystem GUI and Subsystem Design Tool would have been extremely long, making it harder to make edits and work simultaneously between the two. It is possible for the Subsystem Design Tool function(s) to be in the same class as the Subsystem GUI function. However, to reduce the size of the Python class, such an implementation would best work for a subsystem with low number of parameters, limited calculation complexity, a single use case, and a simple GUI. (p. 63)

## RQ3-1

This chapter covers how the tool was tested to validate the results of thesis. There were two primary routes of validation executed. The first method involved functional testing of the CubeSat Conceptual Design Tool's architecture. Next, the EPS Design Module was tested within the tool for the accuracy of its performance in sizing a CubeSat's EPS. (p. 76)

The Orbit Test Module is a single class that contains a constructor that initializes the variables in the Orbit module and a function that runs the GUI, similar to the EPS GUI module. However, it also has the design tool within as a function in the same class. The compressed nature of a test module enables them to be in the same file. For code readability and access on large modules, it is still recommended to have a Subsystem GUI class and Subsystem Design Tool class within the Subsystem Design Module. (pp. 76-77)

Other subsystems had test modules created as well, but none to the extent of the Orbit Test Module. These test modules were present for a few main reasons: to ensure the Main GUI worked creating instances of all of them, to ensure their data could passed into the EPS Design Module, and to test EPS Use Case 2. (p. 79)

The architecture testing sees the development of a test matrix that looks at different ways a user could operate the Conceptual Design Tool. As seen in Table 15, this includes different Use Cases, orbits, Design Methods, and missing information. There is also an expected outcome for each of these tests. While the tool is supposed to run nominally in most cases, some missing information or lack of selections should return an error in the tool, either through a written command line statement or through a pop-up window. Each of these test cases are to be run to see if their outcome is as expected. (pp. 79-80)

The testing plan for the CubeSat Conceptual Design Tool's EPS Design Module sees the development of test cases for the system. These test cases are already existing CubeSat designs, that have already gone through a conceptual design process or further design development. The inputs are found from published work, and then used within the Conceptual Design Tool. (pp. 82-83)

To begin the EPS Module validation, reference documents and component specification sheets were looked at for the test cases to compile all the necessary inputs and expected outputs for the conceptual design process. This data was compiled into files similar to the current EPS Assumption File in order to facilitate accurate transfer of data into the tool. Due to their extensive lengths, the full list of parameters utilized are shown in Appendix B in the form of the Output Files, as these includes all input values as well. (p. 84)

The resulting Output Files were saved and compared to the expected outcome for each test case. The highlights of the results will be presented here. Note that different values were looked at for each case, as a result of what calculated outputs had directly corresponding values in the source for the test case. For example, Test Case 1's source included minimal information on the actual power generation requirements of the solar panels even though it had the power budget and component sizing well developed. (p. 89)

## RQ3-1.2

Within Python, three main packages were used: Tkinter, csv, and math. Tkinter is a Python version of the open-source Tk GUI [41]. This was the package that was used in the creation of the various GUIs in this Conceptual Design Tool. The csv package allows CSV files to be read from and written to by Python, which is necessary for this tool's architecture [42]. The math package comes standard with math functions to perform trigonometric and other operations, which are necessary to performing the mathematical operations needed in a design process [43]. (p. 46)

The original CSRM was created in Cameo Systems Modeler, which is proprietary software currently published by Dassault Systèmes [31]. The CubeSat Model based on the CSRM had to utilize open-source software. This was done by using Eclipse 4.18 as the IDE and Papyrus 5.0 as the modeling environment plug-in, utilizing SysML 1.4 for Papyrus as the modeling language. The full breakdown of software that was used can be found in Table 8. (pp. 46-47)

## RQ3-2

[Figure 7.](../../../pdfs/review-reports/review-report-1009/figure_009.png) CSRM Overview Package Diagram [31] (p. 37)

[Figure 12.](../../../pdfs/review-reports/review-report-1009/figure_014.png) CubeSat Model Overview Package Diagram (p. 52)

[Figure 19.](../../../pdfs/review-reports/review-report-1009/figure_019.png) Orbit Test Module GUI (p. 77)

The architecture testing sees the development of a test matrix that looks at different ways a user could operate the Conceptual Design Tool. As seen in Table 15, this includes different Use Cases, orbits, Design Methods, and missing information. There is also an expected outcome for each of these tests. While the tool is supposed to run nominally in most cases, some missing information or lack of selections should return an error in the tool, either through a written command line statement or through a pop-up window. Each of these test cases are to be run to see if their outcome is as expected. (pp. 79-80)

Table 15. Conceptual Design Tool Test Matrix (pp. 80-81)

[Figure 20.](../../../pdfs/review-reports/review-report-1009/figure_020.png) Pop-up Error Messages (p. 82)

[Figure 21.](../../../pdfs/review-reports/review-report-1009/figure_021.png) Test Case 2 Main GUI (p. 84)

[Figure 22.](../../../pdfs/review-reports/review-report-1009/figure_022.png) Test Case 2 Orbit Test Module (p. 85)

[Figure 23.](../../../pdfs/review-reports/review-report-1009/figure_023.png) Test Case 2 EPS Use Case Selection (p. 86)

[Figure 24.](../../../pdfs/review-reports/review-report-1009/figure_024.png) Test Case 2 Power Budget (p. 87)

[Figure 25.](../../../pdfs/review-reports/review-report-1009/figure_025.png) Test Case 2 EPS Design Inputs (p. 88)

[Figure 26.](../../../pdfs/review-reports/review-report-1009/figure_026.png) Test Case 2 Finish and Run Tool (p. 89)

Table 16. EPS Test Case 1 Results (p. 89)

Table 17. EPS Test Case 2 Results (p. 90)

## RQ3-2.2

Within Python, three main packages were used: Tkinter, csv, and math. Tkinter is a Python version of the open-source Tk GUI [41]. This was the package that was used in the creation of the various GUIs in this Conceptual Design Tool. The csv package allows CSV files to be read from and written to by Python, which is necessary for this tool's architecture [42]. The math package comes standard with math functions to perform trigonometric and other operations, which are necessary to performing the mathematical operations needed in a design process [43]. (p. 46)

The original CSRM was created in Cameo Systems Modeler, which is proprietary software currently published by Dassault Systèmes [31]. The CubeSat Model based on the CSRM had to utilize open-source software. This was done by using Eclipse 4.18 as the IDE and Papyrus 5.0 as the modeling environment plug-in, utilizing SysML 1.4 for Papyrus as the modeling language. The full breakdown of software that was used can be found in Table 8. (pp. 46-47)

## RQ3-3

The Orbit Test Module had to see a higher level of development due to the significance that orbital parameters play in developing the EPS system. Many of the equations in Section 4.3 required values such as time in eclipse or number of orbits which would normally be developed in the full Orbit Design Module. It would be inconsistent with the goal of this project to temporarily include those inputs and necessary parametric equations within the EPS Module. Fortunately, this thesis is laying the foundation for the prompt development of other modules, so Orbit Test Module could be rapidly developed. (p. 76)

Use Case 2 requires these modules to be developed, as it receives the power budget values from individual Subsystem Design Modules. Hence, testing Use Case 2 required values in other subsystems to be passed into the EPS Design Tool. These modules are being simulated by hardcoding parameters into the constructor of each test Subsystem Design Module. Like the Orbit Test Module, these are all monolithic modules of only one file. The parameters that are in each test module currently include power values for nominal, communications, desaturation, and eclipse modes, as well as duty cycles and mode names in some of the modules. (p. 79)

Note that the testing of Use Case 2 requires the use of the test modules for other subsystems. For the missing information, parameters were just set to zero within them. This is because in the full development of the modules, values will be initialized to some default value. These tests are for seeing what happens with the EPS module if postinitialization a subsystem fails to develop that value. Removing the variables entirely causes an expected error where the function is unable to find the relevant variable within an associated instance of a subsystem while trying to create the power budget. (p. 80)

To test this fairly and accurately, the tool was reopened after each run. For the Orbit Selection when "any" was specified, an ISS Orbit was chosen. When the Design Option column called for "any", Standard was used. This is noted for the record, but those tests cases were not necessarily testing those respective portions of the design tool. When an "EPS Parameter" was called to be missing, one or more parameters in the EPS Design Input tab were left unfilled. (p. 81)

Two test cases were formally chosen for this step, comprised of CubeSat conceptual design studies rather than finalized CubeSat EPS designs. This was a result of the differing level of development between the two scenarios. For fully implemented CubeSats, the EPS papers delve into much more detailed design and their concept of operations for a mission gets fully expanded, resulting in parameters that are significantly more complex and nuanced than the Conceptual Design Tool is able to handle. For example, one mission had 14 modes in there nominal reference orbit alone [56]. (p. 83)

To begin the EPS Module validation, reference documents and component specification sheets were looked at for the test cases to compile all the necessary inputs and expected outputs for the conceptual design process. This data was compiled into files similar to the current EPS Assumption File in order to facilitate accurate transfer of data into the tool. Due to their extensive lengths, the full list of parameters utilized are shown in Appendix B in the form of the Output Files, as these includes all input values as well. (p. 84)

The CubeSat Conceptual Design Tool is opened by running the Main GUI using the main.py script for the program. This results in the GUI seen in Figure 21. The design name testCase1 was chosen and submitted in the Main tab within the Main GUI, which will be the name of the resulting Output File for this process. (p. 85)

Within the Orbits tab, the Orbit Test Module GUI is opened by selecting the "Input Orbit" button. From there, the Orbits Test Module opens up, and the selections for Test Case 2 are entered as is shown in Figure 22. That information is then saved into the program by clicking "Submit", before closing the window with either the "Close" button or the close window button in the upper corner of the window. The user is not affected if they do not close the window prior to operating other modules or running the conceptual design tools. (pp. 85-86)

Skipping over to the EPS tab now, seen in Figure 23, the Use Case options are presented, with Use Case 1 being selected for this test. This allows the user to input the power budget directly into the program. Note that if a user wants an explanation of a particular use case, they can select "More Info" for a pop-up with greater detail. After clicking "Select", the Power Budget Input tab within the EPS GUI is now presented. The collected data for the Test Case 2 power budget is then input into the GUI, as demonstrated in Figure 24. (p. 86)

Next, the design options from PowerSat are used to fill out the EPS Design Input tab. The Custom Design Option is selected within the tab to allow custom parameters to be used. As shown in Figure 25, the values that are available are input into the EPS GUI. Then, the user hits "Submit" to load the values of both tabs and assign them to the already initialized variables for the EPS Design Module. From there, "Close" may be clicked to exit the GUI. (p. 87)

Finally, the Conceptual Design Tool reaches the step where the design process of the tool can be executed. This is done by going to the Finish tab, shown in Figure 26, and clicking "Run" to have the Subsystem Design Modules execute their design tools. The final product gets saved in this conceptual design's corresponding Output File, testCase2.csv. (p. 88)

The resulting Output Files were saved and compared to the expected outcome for each test case. The highlights of the results will be presented here. Note that different values were looked at for each case, as a result of what calculated outputs had directly corresponding values in the source for the test case. For example, Test Case 1's source included minimal information on the actual power generation requirements of the solar panels even though it had the power budget and component sizing well developed. (p. 89)

Test Case 2 saw accurate values for the power budget and solar sizing, as seen in Table 17. However, the tool's results in Test Case 2 came out to require three battery cells, while the actual design called for two. This was a result of the Conceptual Design Tool considering battery degradation, along with a slightly off actual battery size that was utilized in the comparison. Due to the two cells barely meeting the energy storage requirements, this slight change caused an outsized effect on the number of cells required, increasing it by 50%. The low margin within for the battery capacity was realized in the actual PowerSat conceptual design, and CPCL ended up proposing the use of an upsized 4 cell battery [57]. (pp. 90-91)

Another important aspect of building robustness into the tool is validating the values being input by the user. Currently, input validation only exists in a few places in the tool, mainly in the form of ensuring the user has made a selection where one is required. However, it has been found that Tkinter has validation attributes available for their data entry widgets that allows the program to check whether the entered values fit within predefined parameters, including numerical ranges and data types [41]. Implementing data entry validation for the current EPS Design Module and with all future subsystems should be completed to ensure the tool is usable even with imperfect users who are likely to mistype something while inputting large amounts of data. (p. 96)

With many subsystems remaining to be developed, the Subsystem Design Module validation testing will only get more challenging as users have to include more comprehensive test cases that cover all available subsystems. Therefore, a set of universal test cases, that cover the inputs and outputs for every subsystem, would greatly assist future validation campaigns, especially if they could be automatically ran through a test script rather than physically entered into the tool. However, it is recognized that such automation may not be possible under the existing software architecture. (p. 99)

## RQ3-3.1

The CubeSat Conceptual Design Tool is being created in Python, specifically Python 3.9. Python was chosen over other programming languages for several reasons. First, Python is a free, open-source language, unlike MATLAB, another commonly used language for design analysis [36][37]. As a high-level programming language, Python makes use of natural language abstraction and minimizes syntax requirements, which maximizes code readability. These features of Python are critical on a project that will see numerous code developers work on it over time by lowering the barriers to entry for people without Python experience and enabling easier comprehension of others code. (p. 45)

Within Python, three main packages were used: Tkinter, csv, and math. Tkinter is a Python version of the open-source Tk GUI [41]. This was the package that was used in the creation of the various GUIs in this Conceptual Design Tool. The csv package allows CSV files to be read from and written to by Python, which is necessary for this tool's architecture [42]. The math package comes standard with math functions to perform trigonometric and other operations, which are necessary to performing the mathematical operations needed in a design process [43]. (p. 46)

The original CSRM was created in Cameo Systems Modeler, which is proprietary software currently published by Dassault Systèmes [31]. The CubeSat Model based on the CSRM had to utilize open-source software. This was done by using Eclipse 4.18 as the IDE and Papyrus 5.0 as the modeling environment plug-in, utilizing SysML 1.4 for Papyrus as the modeling language. The full breakdown of software that was used can be found in Table 8. (pp. 46-47)
