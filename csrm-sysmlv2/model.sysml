// Partial conversion. See README.md for the stop point and unconverted content.
package Data {
    public import Data::'Unit Imports'::'Basic Units'::'Basic Amount of Substance'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Acceleration'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Amount of Substance Concentration'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Area'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Electric Current'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Electric Current Density'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Length'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Luminance'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Luminous Intensity'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Magnetic Field Strength'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Mass'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Speed and Velocity'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Mass Density'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Time'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Thermodynamic Temperature'::*;
    public import Data::'Unit Imports'::'Basic Units'::'Basic Volume'::*;
    dependency from Data to CSRMExternalProjects::'CSRM Reference Information2'::'CubeSat Reference Information';
    dependency from Data to CSRMExternalProjects::'CSRM Reference Information2'::'Unit Imports';
    dependency from Data to CSRMExternalProjects::'CSRM-Profile2'::'CSRM Profile';
    dependency from Data to CSRMExternalProjects::'CSRM Profile'::'Derived Properties';
    package 'Unit Imports' {
        package 'Basic Units' {
            package 'Basic Length' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[nanometre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[millimetre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[metre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[metre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[decimetre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[kilometre]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'length'::'length[centimetre]';
                public import 'ISO-80000-Extension'::'Nautical Units'::'Quantities'::'Length'::'length[nautical mile]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Length'::'length[foot]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Length'::'length[yard]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Length'::'length[inch]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Length'::'length[mile]';
            }
            package 'Basic Mass' {
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass'::'mass';
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass'::'mass[milligram]';
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass'::'mass[gram]';
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass'::'mass[kilogram]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Mass'::'mass[ounce]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Mass'::'mass[pound]';
            }
            package 'Basic Area' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'area'::'area';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'area'::'area[square metre]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Area'::'area[acre]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Area'::'area[square foot]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Area'::'area[square inch]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Area'::'area[square yard]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Area'::'area[square mile]';
            }
            package 'Basic Volume' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'volume'::'volume';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'volume'::'volume[cubic metre]';
                public import 'ISO-80000-Extension'::'Common Units'::'Quantities'::'Volume'::'volume[litre]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[cubic foot]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[cubic yard]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[cubic inch]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[fluid ounce (UK)]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[fluid ounce (US)]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[gallon (UK)]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[gallon (US)]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[pint (UK)]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Volume'::'volume[pint (US)]';
            }
            package 'Basic Time' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'time'::'time';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'time'::'time[second]';
            }
            package 'Basic Electric Current' {
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'electric current'::'electric current[ampere]';
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'electric current'::'electric current';
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'electric current'::'electric current[milliampere]';
            }
            package 'Basic Thermodynamic Temperature' {
                public import 'ISO-80000'::'ISO80000-5 Thermodynamics'::'Quantities'::'thermodynamic temperature'::'thermodynamic temperature';
                public import 'ISO-80000'::'ISO80000-5 Thermodynamics'::'Quantities'::'thermodynamic temperature'::'thermodynamic temperature[kelvin]';
            }
            package 'Basic Amount of Substance' {
                public import 'ISO-80000'::'ISO80000-9 Physical Chemestry and Molecular Physics'::'Quantities'::'amount of substance'::'amount of substance';
                public import 'ISO-80000'::'ISO80000-9 Physical Chemestry and Molecular Physics'::'Quantities'::'amount of substance'::'amount of substance[mole]';
            }
            package 'Basic Luminous Intensity' {
                public import 'ISO-80000'::'ISO80000-7 Light'::'Quantities'::'luminous intensity'::'luminous intensity';
                public import 'ISO-80000'::'ISO80000-7 Light'::'Quantities'::'luminous intensity'::'luminous intensity[candela]';
            }
            package 'Basic Speed and Velocity' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'speed'::'speed';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'speed'::'speed[metre per second]';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'velocity'::'velocity';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'velocity'::'velocity[metre per second]';
                public import 'ISO-80000-Extension'::'Common Units'::'Quantities'::'Speed and Velocity'::'speed[kilometre per hour]';
                public import 'ISO-80000-Extension'::'Common Units'::'Quantities'::'Speed and Velocity'::'velocity[kilometre per hour]';
                public import 'ISO-80000-Extension'::'Nautical Units'::'Quantities'::'Speed and Velocity'::'speed[knot]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Speed and Velocity'::'speed[foot per second]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Speed and Velocity'::'speed[mile per hour]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Speed and Velocity'::'velocity[foot per second]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Speed and Velocity'::'velocity[mile per hour]';
            }
            package 'Basic Acceleration' {
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'acceleration'::'acceleration';
                public import 'ISO-80000'::'ISO80000-3 Space and Time'::'Quantities'::'acceleration'::'acceleration[metre per second squared]';
                public import 'ISO-80000-Extension'::'Imperial Units & US Customary Units'::'Quantities'::'Acceleration'::'acceleration[foot per second squared]';
            }
            package 'Basic Mass Density' {
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass density'::'mass density';
                public import 'ISO-80000'::'ISO80000-4 Mechanics'::'Quantities'::'mass density'::'mass density[kilogram per cubic metre]';
            }
            package 'Basic Electric Current Density' {
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'electric current density'::'electric current density';
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'electric current density'::'electric current density[ampere per square metre]';
            }
            package 'Basic Amount of Substance Concentration' {
                public import 'ISO-80000'::'ISO80000-9 Physical Chemestry and Molecular Physics'::'Quantities'::'amount of substance concentration'::'amount of substance concentration';
                public import 'ISO-80000'::'ISO80000-9 Physical Chemestry and Molecular Physics'::'Quantities'::'amount of substance concentration'::'amount of substance concentration[mole per cubic metre]';
            }
            package 'Basic Magnetic Field Strength' {
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'magnetic field strength'::'magnetic field strength';
                public import 'ISO-80000'::'IEC80000-6 Electromagnetism'::'Quantities'::'magnetic field strength'::'magnetic field strength[ampere per metre]';
            }
            package 'Basic Luminance' {
                public import 'ISO-80000'::'ISO80000-7 Light'::'Quantities'::'luminance'::'luminance';
                public import 'ISO-80000'::'ISO80000-7 Light'::'Quantities'::'luminance'::'luminance[candela per square metre]';
            }
        }
    }
    package 'CSRM Extentions' {
        package Customizations {
            // Cameo editor configuration. Values are source references, not executable rules.
            item 'KPP Param Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_785163_22408";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_785163_22408_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550674761_583894_14584");
                :>> quickApplyingFor = ("MD_customization_for_SysML.mdzip#_12_0_be00301_1164123483951_695645_2041");
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'tpmRequirement Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_820787_22404";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_820787_22404_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816634530_574230_2426");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ("http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block");
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'How To Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_492259_22409";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_492259_22409_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1617466901812_111948_7046");
                :>> quickApplyingFor = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Comment");
                :>> preferredMetatype = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Comment");
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'kppSpecification Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_66198_22406";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_66198_22406_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550607909_173509_14549");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'MoP Requirement Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920398_482622_22403";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920398_482622_22403_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816615229_751396_2399");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ("http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block");
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'tpmSpecification Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_20629_22405";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920399_20629_22405_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_601405_66134");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'MOP Param Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_573080_22411";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_573080_22411_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_289586_66140");
                :>> quickApplyingFor = ("MD_customization_for_SysML.mdzip#_12_0_be00301_1164123483951_695645_2041");
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'MOE Param Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_126738_22413";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_126738_22413_";
                :>> customizationTarget = ("SysML Profile.mdzip#_12_1_8740266_1172576734625_231808_234");
                :>> quickApplyingFor = ("MD_customization_for_SysML.mdzip#_12_0_be00301_1164123483951_695645_2041");
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'TPM Param Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_462687_22412";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_462687_22412_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588150_801304_66141");
                :>> quickApplyingFor = ("MD_customization_for_SysML.mdzip#_12_0_be00301_1164123483951_695645_2041");
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'CSRM Stakeholder' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_140336_22414";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920401_140336_22414_";
                :>> customizationTarget = ("UML_Standard_Profile.mdzip#_12_0EAPbeta_be00301_1159943470859_244302_338", "CSRM-Profile2.mdzip#_19_0_2_3880181_1574536276030_882809_13389", "UML_Standard_Profile.mdzip#_11_5EAPbeta_be00301_1148642764910_998510_268");
                :>> quickApplyingFor = ("http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block");
                :>> preferredMetatype = ();
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ("CSRM-Profile2.mdzip#_19_0_2_3880181_1574536276030_882809_13389");
                :>> hideMetatype = true;
            }
            item 'Explanation Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_458529_22410";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_458529_22410_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1617466891653_608929_7019");
                :>> quickApplyingFor = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Comment");
                :>> preferredMetatype = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Comment");
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'kppRequirement Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_635982_22407";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920400_635982_22407_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816671041_264736_2480");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ("http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.Block");
                :>> superTypes = ();
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'VerificationCust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330720_276017_23150";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330720_276017_23150_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1617463632588_168719_5413");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ();
                :>> superTypes = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Abstraction");
                :>> typesForSource = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1616859963947_857531_2330");
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
            }
            item 'Validate Cust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920397_707330_22402";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606920397_707330_22402_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601399071893_366607_14376");
                :>> quickApplyingFor = ();
                :>> preferredMetatype = ();
                :>> superTypes = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Abstraction");
                :>> typesForSource = ("CSRM-Profile2.mdzip#_18_5_2_3880181_1554842264428_327055_65039");
                :>> typesForTarget = ("http://www.omg.org/spec/SysML/20181001/SysML.xmi#SysML.AbstractRequirement");
                :>> hiddenOwnedTypes = ();
            }
            item 'ValidationActivityCust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330718_769524_23147";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330718_769524_23147_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_18_5_2_3880181_1554842264428_327055_65039");
                :>> quickApplyingFor = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity", "http://www.omg.org/spec/UML/20131001/UML.xmi#Interaction");
                :>> preferredMetatype = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity");
                :>> superTypes = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity");
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
                :>> hideMetatype = true;
            }
            item 'VerificationActivityCust' : CSRMCameoCustomization::EditorCustomization {
                :>> sourceClassRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330719_782493_23148";
                :>> sourceApplicationRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698607330719_782493_23148_";
                :>> customizationTarget = ("CSRM-Profile2.mdzip#_19_0_3_2b0010b_1616859963947_857531_2330");
                :>> quickApplyingFor = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity", "http://www.omg.org/spec/UML/20131001/UML.xmi#Interaction");
                :>> preferredMetatype = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity");
                :>> superTypes = ("http://www.omg.org/spec/UML/20131001/UML.xmi#Activity");
                :>> typesForSource = ();
                :>> typesForTarget = ();
                :>> hiddenOwnedTypes = ();
                :>> hideMetatype = true;
                :>> sourceComment = "Working";
            }
            package ValidationVerification;
        }
        package Legends; // Presentation content is deferred with diagrams.
        package 'Model Constraints' {
            package 'Measure Validation';
            package Structure;
        }
    }
    // All seventeen technical measure classes and fourteen corrected Refine links.
    package '2 - Technical Measures' {
        package '2.1 - Technical Measures - Specifications and Requirements - Population' {
            package '2.1.1 MOE' {
                package '2.1.1.2 MOE Requirements' {
                    requirement <'1'> 'MoeA Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639418195867_474428_56840";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816651776_286275_2453";
                            sourceSummary = "";
                            sourceId = "1";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.1 MOE Specifications'::'MoeA Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640979107726_954282_59123\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510572_262637_55801";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'moeRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint moeSatisfyValidation : CSRMMeasureValidation::'moeRequirement Satisfy by MoE Param' {
                            in attribute matchingMoESatisfiers : CSRMNativeMeasures::MoE [0];
                        }
                    }
                    requirement <'2'> 'MoeB Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890459085_928753_58061";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816651776_286275_2453";
                            sourceSummary = "";
                            sourceId = "2";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.1 MOE Specifications'::'MoeB Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890511416_885986_58069\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641060126355_872138_58393\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890405896_924459_58049";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'moeRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint moeSatisfyValidation : CSRMMeasureValidation::'moeRequirement Satisfy by MoE Param' {
                            in attribute matchingMoESatisfiers : CSRMNativeMeasures::MoE [0];
                        }
                    }
                }
                package '2.1.1.1 MOE Specifications' {
                    part def 'MoeA Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510572_262637_55801";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_243878_66132";
                            sourceSummary = "The system shall exhibit the property \"MOE Name\" that has a minimum of x and maximum of y,";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.2 MOE Requirements'::'MoeA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.1 MOE Specifications'::'MoeA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640979107726_954282_59123";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510572_262637_55801";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639418195867_474428_56840";
                            isRefine = true;
                        }
                    }
                    part def 'MoeB Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890405896_924459_58049";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_243878_66132";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.2 MOE Requirements'::'MoeB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.1 MOE Specifications'::'MoeB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890511416_885986_58069";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890405896_924459_58049";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890459085_928753_58061";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.2 MOE Requirements'::'MoeB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.1 MOE'::'2.1.1.1 MOE Specifications'::'MoeB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641060126355_872138_58393";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890405896_924459_58049";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640890459085_928753_58061";
                            isRefine = true;
                        }
                    }
                }
            }
            package '2.1.2 MOP' {
                package '2.1.2.2 MOP Requirements' {
                    requirement <'1'> 'MopA Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639426059464_157765_57068";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816615229_751396_2399";
                            sourceSummary = "";
                            sourceId = "1";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.1 MOP Specifications'::'MopA Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640978847584_874961_58974\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510635_112212_55836";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'mopRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint mopSatisfyValidation : CSRMMeasureValidation::'mopRequirement Satisfy by MoP Param' {
                            in attribute matchingMoPSatisfiers : CSRMNativeMeasures::MoP [0];
                        }
                    }
                    requirement <'2'> 'MopB Requirement' {
                        doc /*<html><body>Shall statement	</body></html>*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086218348_651267_58530";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816615229_751396_2399";
                            sourceSummary = "";
                            sourceId = "2";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.1 MOP Specifications'::'MopB Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086280177_84502_58538\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641088135761_443324_59290\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086056782_808571_58519";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'mopRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint mopSatisfyValidation : CSRMMeasureValidation::'mopRequirement Satisfy by MoP Param' {
                            in attribute matchingMoPSatisfiers : CSRMNativeMeasures::MoP [0];
                        }
                    }
                }
                package '2.1.2.1 MOP Specifications' {
                    part def 'MopA Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510635_112212_55836";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_300770_66133";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.2 MOP Requirements'::'MopA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.1 MOP Specifications'::'MopA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640978847584_874961_58974";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510635_112212_55836";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639426059464_157765_57068";
                            isRefine = true;
                        }
                    }
                    part def 'MopB Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086056782_808571_58519";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_300770_66133";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.2 MOP Requirements'::'MopB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.1 MOP Specifications'::'MopB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086280177_84502_58538";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086056782_808571_58519";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086218348_651267_58530";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.2 MOP Requirements'::'MopB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.2 MOP'::'2.1.2.1 MOP Specifications'::'MopB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641088135761_443324_59290";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086056782_808571_58519";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086218348_651267_58530";
                            isRefine = true;
                        }
                    }
                }
            }
            package '2.1.4 KPP' {
                package '2.1.4.2 KPP Requirements' {
                    requirement <'1'> 'KppA Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639427668110_10024_57317";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816671041_264736_2480";
                            sourceSummary = "";
                            sourceId = "1";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppA Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640976917863_158146_58516\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640977336098_259821_58559\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640977591277_247213_58579\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636392204795_245336_57575";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'kppRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint kppSatisfyValidation : CSRMMeasureValidation::'kppRequirement Satisfy & kpp stereotype' {
                            in attribute matchingKppSatisfiers : CSRMNativeMeasures::KPP [0];
                        }
                    }
                    requirement <'2'> 'KppB Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641050628893_142701_58897";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816671041_264736_2480";
                            sourceSummary = "";
                            sourceId = "2";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppB Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641137036932_313325_58832\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641258322639_376832_58601\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641136932885_191193_58826";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'kppRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint kppSatisfyValidation : CSRMMeasureValidation::'kppRequirement Satisfy & kpp stereotype' {
                            in attribute matchingKppSatisfiers : CSRMNativeMeasures::KPP [0];
                        }
                    }
                }
                package '2.1.4.1 KPP Specifications' {
                    part def 'KppA Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636392204795_245336_57575";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550607909_173509_14549";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.2 KPP Requirements'::'KppA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640976917863_158146_58516";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636392204795_245336_57575";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639427668110_10024_57317";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.2 KPP Requirements'::'KppA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640977336098_259821_58559";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636392204795_245336_57575";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639427668110_10024_57317";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.2 KPP Requirements'::'KppA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640977591277_247213_58579";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636392204795_245336_57575";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639427668110_10024_57317";
                            isRefine = true;
                        }
                    }
                    part def 'KppB Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641136932885_191193_58826";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550607909_173509_14549";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.2 KPP Requirements'::'KppB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641137036932_313325_58832";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641136932885_191193_58826";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641050628893_142701_58897";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.2 KPP Requirements'::'KppB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.4 KPP'::'2.1.4.1 KPP Specifications'::'KppB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641258322639_376832_58601";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641136932885_191193_58826";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641050628893_142701_58897";
                            isRefine = true;
                        }
                    }
                }
                part def 'KppB Spedification' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641052437130_31307_59249";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1603550607909_173509_14549";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
            }
            package '2.1.3 TPM' {
                package '2.1.3.2 TPM Requirements' {
                    requirement <'1'> 'TpmA Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639426915951_819149_57198";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816634530_574230_2426";
                            sourceSummary = "";
                            sourceId = "1";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.1 TPM Specifications'::'TpmA Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640978118184_715139_58750\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510681_890687_55869";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'tpmRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint tpmSatisfyValidation : CSRMMeasureValidation::'tpmRequirement Satisfy by TPM Param1' {
                            in attribute matchingTPMSatisfiers : CSRMNativeMeasures::TPM [0];
                        }
                    }
                    requirement <'2'> 'TpmB Requirement' {
                        doc /*Shall statement*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641056363739_293120_58627";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1615816634530_574230_2426";
                            sourceSummary = "";
                            sourceId = "2";
                        }
                        ref refinedSpecs : Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.1 TPM Specifications'::'TpmB Specification' [1] {
                            @CSRMv1Metadata::ReifiedRefineTargets {
                                sourceRefineIds = "[\"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641087141570_487929_58678\", \"CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641239239391_918252_59491\"]";
                                targetSourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086922717_230247_58652";
                            }
                        }
                        assert constraint refineValidation : CSRMMeasureValidation::'tpmRequirement Refined' {
                            in ref matchingRefineTargets = refinedSpecs;
                        }
                        // No matching measure property satisfies this requirement in the source.
                        assert constraint tpmSatisfyValidation : CSRMMeasureValidation::'tpmRequirement Satisfy by TPM Param1' {
                            in attribute matchingTPMSatisfiers : CSRMNativeMeasures::TPM [0];
                        }
                    }
                }
                package '2.1.3.1 TPM Specifications' {
                    part def 'TpmA Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510681_890687_55869";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_601405_66134";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.2 TPM Requirements'::'TpmA Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.1 TPM Specifications'::'TpmA Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1640978118184_715139_58750";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1636387510681_890687_55869";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1639426915951_819149_57198";
                            isRefine = true;
                        }
                    }
                    part def 'TpmB Specification' {
                        comment /*Technical measure description*/
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086922717_230247_58652";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1510191588135_601405_66134";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.2 TPM Requirements'::'TpmB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.1 TPM Specifications'::'TpmB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641087141570_487929_58678";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086922717_230247_58652";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641056363739_293120_58627";
                            isRefine = true;
                        }
                    }
                    dependency from Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.2 TPM Requirements'::'TpmB Requirement' to Data::'2 - Technical Measures'::'2.1 - Technical Measures - Specifications and Requirements - Population'::'2.1.3 TPM'::'2.1.3.1 TPM Specifications'::'TpmB Specification' {
                        @CSRMv1Metadata::CorrectedRefineSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641239239391_918252_59491";
                            originalClientRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641086922717_230247_58652";
                            originalSupplierRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1641056363739_293120_58627";
                            isRefine = true;
                        }
                    }
                }
            }
        }
    }
    // Converted 2025 architecture classes and their direct structure.
    package '5 - Architecture' {
        package 'L2_Segment' {
            package 'L2.1_Space Segment' {
                package 'L2.1.2_Structures' {
                    part def CubeSat :> CSRMNativeStructures::CubeSat, CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573832_997891_14609";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529602336024_394574_65284";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'mission Payload1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Mission Payload Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966495487_230824_63446";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966495487_52447_63445";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609453_690849_15836";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966495487_230824_63446";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'command and Data Handling Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Command and Data Handling Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966582896_859326_63479";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966582896_293556_63478";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609454_765346_15838";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506966582896_859326_63479";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'communication Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Communication Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967003841_585015_63529";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967003841_19190_63528";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609451_873397_15832";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967003841_585015_63529";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'attitude Determination and Control Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Attitude Determination and Control Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967218373_193109_63589";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967218373_412660_63588";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609452_913076_15834";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967218373_193109_63589";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'guidance Navigation and Control Subsystem' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Guidance Navigation and Control Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967281666_252088_63619";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967281666_243398_63618";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609456_401153_15840";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967281666_252088_63619";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'structures and Mechanisms Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Structures and Mechanisms Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967335052_176911_63649";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967335052_789344_63648";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609454_535648_15837";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967335052_176911_63649";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'power Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Power Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967716770_36116_63837";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967716770_907777_63836";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609455_663772_15839";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967716770_36116_63837";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'propulsion Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Propulsion Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967809287_3062_63919";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967809287_648878_63918";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609451_731321_15833";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967809287_3062_63919";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'thermal Subsystem1' : Data::'5 - Architecture'::L3_Subsystems::'L3.1_CubeSat Subsystems'::'L3.1.2_Structures'::'Thermal Subsystem' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967837292_646407_63949";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967837292_718711_63948";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609450_855672_15831";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1506967837292_646407_63949";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        ref part 'Orbit' : Data::'5 - Architecture'::L2_Segment::'L2.1_Space Segment'::'L2.1.2_Structures'::'CubeSat Orbit' [1..1] {
                            @CSRMv1Metadata::ChosenOrbitReference {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069689424_917266_46848";
                                chosenTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069636897_942758_46779";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                            }
                        }
                    }
                    part def 'CubeSat Orbit' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069636897_942758_46779";
                            stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        attribute 'eccentricity' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069880918_113410_46878";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'semi-major axis' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069921026_929169_46883";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'inclination' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069957335_626744_46888";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'longitude of ascending node' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069977412_427271_46893";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'argument of perigee' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493070051201_759392_46898";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'true anomaly at epoch' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493070088062_252284_46903";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                        attribute 'time of epoch' [1..1] {
                            @CSRMv1Metadata::UntypedValuePropertySource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493070115383_505128_46908";
                                sourceKind = "SysML v1 ValueProperty";
                                sourceHadType = false;
                                sourceMultiplicity = "1..1";
                                sourceAggregation = "composite";
                                quantityKindRef = "";
                                unitRef = "";
                            }
                        }
                    }
                    part def 'Space Segment' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573831_645083_14608";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529602112051_868875_65244";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'cubeSat' : 'CubeSat' [1..*] {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505161330774_139232_61542";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505161330774_608607_61541";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573832_997891_14609";
                                sourceMultiplicity = "1..*";
                            }
                        }
                        part 'cubeSat Orbit' : 'CubeSat Orbit' [1..*] {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505161434667_139876_61573";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505161434667_235639_61572";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069636897_942758_46779";
                                sourceMultiplicity = "1..*";
                            }
                        }
                        binding orbitBinding bind cubeSat.'Orbit' = 'cubeSat Orbit' {
                            @CSRMv1Metadata::ChosenOrbitBinding {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1493069689424_917266_46848";
                                chosenTargetRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505161434667_139876_61573";
                                sourceHadBinding = false;
                                interpretation = "User chose collection-level binding without per-CubeSat pairing";
                            }
                        }
                        assert constraint spacecraftCompositionValidation : CSRMStructureValidation::'Space Segment Compostion' {
                            @CSRMv1Metadata::ExpandedValidationScope {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_2022x_2_2b0010b_1698606921881_949808_22493";
                                originalScopeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1601406435362_893104_14666";
                                appliedClassRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573831_645083_14608";
                                decision = "User authorized applying the SpaceSegment rule to a Segment class";
                            }
                            in ref part directSpacecraftParts = cubeSat;
                        }
                    }
                }
            }
        package 'L2.2_Ground Segment' {
            package 'L2.2.2_Structures' {
                part def 'Ground Segment' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573820_820968_14607";
                        stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529602112051_868875_65244";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'plan and Schedule Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Plan and Schedule Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962854689_704599_59045";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962854689_718645_59044";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609449_411899_15829";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'spacecraft Command Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Spacecraft Command Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962862926_976743_59076";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962862926_568701_59075";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609442_597347_15823";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'ground Equipment Control Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Ground Equipment Control Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962895338_974852_59107";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504962895338_261511_59106";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609449_506433_15830";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'space - Ground Communication Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Space - Ground Communication Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963053369_130151_59176";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963053369_612270_59175";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609445_482519_15826";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'mission Data Processing Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Mission Data Processing Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963078577_516768_59259";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963078577_351696_59258";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609448_32689_15828";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'network Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Network Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963084625_224047_59290";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963084625_936319_59289";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609444_827746_15825";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'mission Data Dissemination Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Mission Data Dissemination Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963090313_225604_59321";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504963090313_415130_59320";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609443_348896_15824";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'facilities Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Facilities Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652560120120_870608_58712";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652560120120_387352_58711";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652559609874_213754_58531";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'telemetry Processing Subsystem' : 'Data'::'5 - Architecture'::'L3_Subsystems'::'L3.2_Ground Subsystems'::'L3.2.2_Structures'::'Telemetry Processing Subsystem' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355172430_587780_337";
                            associationRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355172430_665724_336";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731354035283_921304_77";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
            }
        }
        }
        package 'L3_Subsystems' {
            package 'L3.1_CubeSat Subsystems' {
                package 'L3.1.2_Structures' {
                    part def 'Mission Payload Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609453_690849_15836";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'instrument' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.1_Mission Payload Components'::'L4.1.1.2_Structures'::'Instrument' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966144184_867900_60691";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966144184_939766_60690";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768517309_104591_15754";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966144184_867900_60691";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.1_Mission Payload Components'::'L4.1.1.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966149576_636083_60722";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966149576_514634_60721";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768564386_78772_15756";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504966149576_636083_60722";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Command and Data Handling Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609454_765346_15838";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.2_Command and Data Handling Components'::'L4.1.2.2_Structures'::'Command, Telemetry, and Data Bus' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052868446_280959_59876";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052868446_387484_59875";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768973777_796922_15784";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052868446_280959_59876";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.2_Command and Data Handling Components'::'L4.1.2.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052908719_471437_59956";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052908719_121393_59955";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768596772_785377_15758";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505052908719_471437_59956";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Communication Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609451_873397_15832";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.3_Communication Components'::'L4.1.3.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054228737_235187_60391";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054228737_659474_60390";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768598754_969812_15760";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054228737_235187_60391";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'receive Antenna and Equipment' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.3_Communication Components'::'L4.1.3.2_Structures'::'Receive Antenna and Equipment' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054238693_563290_60421";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054238693_239871_60420";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768796319_320639_15772";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054238693_563290_60421";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'transmit Antenna and Equipment' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.3_Communication Components'::'L4.1.3.2_Structures'::'Transmit Antenna and Equipment' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054264245_356300_60503";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054264245_975433_60502";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768805478_770853_15774";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505054264245_356300_60503";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Attitude Determination and Control Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609452_913076_15834";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.4_Attitude Determination and Control Components'::'L4.1.4.2_Structures'::'Software' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051904776_715917_59468";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051904776_311150_59467";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768817190_694096_15776";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051904776_715917_59468";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'actuator' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.4_Attitude Determination and Control Components'::'L4.1.4.2_Structures'::'Actuator' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051910340_912233_59498";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051910340_225127_59497";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768900651_242105_15780";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051910340_912233_59498";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'sensor' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.4_Attitude Determination and Control Components'::'L4.1.4.2_Structures'::'Sensor' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051918826_844900_59528";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051918826_920978_59527";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768843413_403992_15778";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051918826_844900_59528";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'shared Processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.0_Shared Components'::'L4.1.0.2_Structures'::'Shared Processor and Memory' [1..1] {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051926390_570536_59558";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051926390_546978_59557";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1494340978082_527489_51171";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ExcludedRollUpContributor {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505051926390_570536_59558";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1494340978082_527489_51171";
                                reason = "Separate composite part; user kept shared processor outside mass rollup";
                            }
                        }
                    }
                    part def 'Guidance Navigation and Control Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609456_401153_15840";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'accelerometer' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.5_Guidance Navigation and Control Components'::'L4.1.5.2_Structures'::'Accelerometer' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050866981_110069_59248";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050866981_414434_59247";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769029630_744670_15786";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050866981_110069_59248";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'gNSS Receiver' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.5_Guidance Navigation and Control Components'::'L4.1.5.2_Structures'::'GNSS Receiver' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050875592_443207_59278";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050875592_54683_59277";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769039217_2330_15788";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050875592_443207_59278";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.5_Guidance Navigation and Control Components'::'L4.1.5.2_Structures'::'Software' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050917522_656849_59360";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050917522_312313_59359";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768926748_916942_15782";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050917522_656849_59360";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'shared Processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.0_Shared Components'::'L4.1.0.2_Structures'::'Shared Processor and Memory' [1..1] {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050927070_846277_59390";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050927070_389605_59389";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1494340978082_527489_51171";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ExcludedRollUpContributor {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505050927070_846277_59390";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1494340978082_527489_51171";
                                reason = "Separate composite part; user kept shared processor outside mass rollup";
                            }
                        }
                    }
                    part def 'Structures and Mechanisms Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609454_535648_15837";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'deployable Mount' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.6_Structures and Mechanisms Components'::'L4.1.6.2_Structures'::'Deployable Mount' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056669175_349972_62583";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056669175_130656_62582";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769128357_370503_15792";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056669175_349972_62583";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'static Mount' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.6_Structures and Mechanisms Components'::'L4.1.6.2_Structures'::'Static Mount' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056677364_646061_62613";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056677364_572191_62612";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769118630_914296_15790";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056677364_646061_62613";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'actuated Mount' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.6_Structures and Mechanisms Components'::'L4.1.6.2_Structures'::'Actuated Mount' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056658220_33051_62553";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056658220_929903_62552";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769142115_856032_15796";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056658220_33051_62553";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Power Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609455_663772_15839";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'batteries' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Batteries' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055429243_836355_61106";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055429243_905410_61105";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769201063_373794_15802";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055429243_836355_61106";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'regulators and Converters' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Regulators and Converters' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055437901_455231_61136";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055437901_681839_61135";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769207094_764375_15804";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055437901_455231_61136";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'solar Arrays' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Solar Arrays' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055446934_155733_61166";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055446934_975434_61165";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769190724_172852_15800";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055446934_155733_61166";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'power Circuits and Switches' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Power Circuits and Switches' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055483722_439147_61248";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055483722_375264_61247";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769219591_806033_15806";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055483722_439147_61248";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055492849_150646_61278";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055492849_804272_61277";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768621567_166101_15770";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055492849_150646_61278";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.7_Power Components'::'L4.1.7.2_Structures'::'Software' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055502585_243540_61308";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055502585_848240_61307";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769180766_666463_15798";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505055502585_243540_61308";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Propulsion Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609451_731321_15833";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part 'propellant Storage' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.9_Propulsion Components'::'L4.1.9.2_Structures'::'Propellant Storage' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056214765_70129_62115";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056214765_993952_62114";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769284909_472559_15814";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056214765_70129_62115";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'propellant Control' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.9_Propulsion Components'::'L4.1.9.2_Structures'::'Propellant Control' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056226158_314629_62145";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056226158_342495_62144";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769298016_896824_15816";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056226158_314629_62145";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'thrusters' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.9_Propulsion Components'::'L4.1.9.2_Structures'::'Thrusters' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056233128_193505_62175";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056233128_424942_62174";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769312673_631299_15818";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056233128_193505_62175";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.9_Propulsion Components'::'L4.1.9.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056241864_709528_62205";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056241864_595199_62204";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768617823_207025_15766";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056241864_709528_62205";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.9_Propulsion Components'::'L4.1.9.2_Structures'::'Software' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056252600_224208_62235";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056252584_577106_62234";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769279513_591992_15812";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505056252600_224208_62235";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                    part def 'Thermal Subsystem' :> CSRMMassRollUp::MassRollUpPattern {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609450_855672_15831";
                            stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                            sourceSummary = "";
                            sourceId = "";
                        }
                        part : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.8_Thermal Components'::'L4.1.8.2_Structures'::'Thermal Sensors, Sources, and Sinks' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057858385_254941_62958";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057858385_74662_62957";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769248111_377457_15810";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057858385_254941_62958";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'processor and Memory' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.8_Thermal Components'::'L4.1.8.2_Structures'::'Processor and Memory' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057879514_227931_62986";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057879514_545440_62985";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768619199_363897_15768";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057879514_227931_62986";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                        part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.1_CubeSat Subsystems Components'::'L4.1.8_Thermal Components'::'L4.1.8.2_Structures'::'Software' [1..1] :> subMass {
                            @CSRMv1Metadata::ConvertedPartSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057887250_36678_63016";
                                associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057887250_935444_63015";
                                sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769233008_677974_15808";
                                sourceMultiplicity = "1..1";
                            }
                            @CSRMv1Metadata::ChosenRollUpSubsetting {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505057887250_36678_63016";
                                chosenTargetRef = "MD_customization_for_SysML.mdzip#_18_3_903028d_1448291312293_317152_13890";
                                isSourceSubsetting = false;
                            }
                        }
                    }
                }
            }
        package 'L3.2_Ground Subsystems' {
            package 'L3.2.2_Structures' {
                part def 'Spacecraft Command Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609442_597347_15823";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.2_Spacecraft Command Components'::'L4.2.2.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293431375_160659_61498";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293431375_66290_61497";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244924860_272284_60944";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.2_Spacecraft Command Components'::'L4.2.2.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293443874_605502_61515";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293443874_39235_61514";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244679043_729355_60870";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.2_Spacecraft Command Components'::'L4.2.2.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293455959_433415_61532";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561293455958_286881_61531";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244973154_477653_60948";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Mission Data Dissemination Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609443_348896_15824";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.6_Mission Data Dissemination Components'::'L4.2.6.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296512193_712760_62334";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296512193_514114_62333";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245523058_466717_61091";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.6_Mission Data Dissemination Components'::'L4.2.6.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296524149_445152_62351";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296524149_135168_62350";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245478179_326375_61064";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.6_Mission Data Dissemination Components'::'L4.2.6.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296538675_354509_62368";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296538675_158786_62367";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245538412_270076_61095";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Network Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609444_827746_15825";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.7_Network Components'::'L4.2.7.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297189672_249905_62551";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297189672_41171_62550";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296853724_451978_62430";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.7_Network Components'::'L4.2.7.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297194175_555876_62568";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297194174_236329_62567";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296894472_40705_62432";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.7_Network Components'::'L4.2.7.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297200463_4555_62585";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561297200462_920593_62584";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296916180_628507_62434";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Space - Ground Communication Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609445_482519_15826";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.4_Space-Ground Communication Components'::'L4.2.4.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295566203_739735_61916";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295566203_274797_61915";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245192010_65619_60979";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.4_Space-Ground Communication Components'::'L4.2.4.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295582298_648467_61933";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295582298_771193_61932";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245140395_246710_60952";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.4_Space-Ground Communication Components'::'L4.2.4.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295590947_925097_61950";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295590947_683909_61949";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245203929_935228_60983";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Mission Data Processing Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609448_32689_15828";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'harware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.5_Mission Data Processing Components'::'L4.2.5.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295991615_753069_62125";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561295991615_827007_62124";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245353070_159433_61056";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.5_Mission Data Processing Components'::'L4.2.5.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296000323_403758_62142";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296000322_655342_62141";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245259757_759124_61027";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.5_Mission Data Processing Components'::'L4.2.5.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296007441_153519_62159";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296007441_258165_62158";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245412683_544678_61060";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Plan and Schedule Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609449_411899_15829";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.1_Plan and Schedule Components'::'L4.2.1.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561289939669_337880_61202";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561289939669_493611_61201";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140096721_590968_60364";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.1_Plan and Schedule Components'::'L4.2.1.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561290475692_665848_61259";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561290475692_914718_61258";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140112822_418165_60366";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.1_Plan and Schedule Components'::'L4.2.1.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561290969252_407635_61318";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561290969252_216890_61317";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140070160_102171_60362";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Ground Equipment Control Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151609449_506433_15830";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.3_Ground Equipment Control Components'::'L4.2.3.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294399372_972084_61707";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294399371_232485_61706";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244849588_217848_60934";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.3_Ground Equipment Control Components'::'L4.2.3.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294406758_865478_61724";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294406758_281321_61723";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244785934_257889_60907";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.3_Ground Equipment Control Components'::'L4.2.3.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294419250_317394_61741";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561294419250_279824_61740";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244880914_430932_60938";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Facilities Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652559609874_213754_58531";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'room' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.8_Facilities Components'::'L4.2.8.2_Structures'::'Room' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652710899748_143647_59315";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652710899748_489705_59314";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652708601584_552665_58684";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'room 2' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.8_Facilities Components'::'L4.2.8.2_Structures'::'Room 2' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652714498627_437226_59000";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652714498627_851997_58999";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652714230754_79149_58946";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Telemetry Processing Subsystem' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731354035283_921304_77";
                        stereotypeRef = "CSRM-Profile2.mdzip#_19_0_3_2b0010b_1620751752335_165744_787";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'procedures' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.9_Telemetry Processing Components'::'L4.2.9.2_Structures'::'Procedures' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358320483_603106_1556";
                            associationRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358320483_145735_1555";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355627901_243033_391";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'software' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.9_Telemetry Processing Components'::'L4.2.9.2_Structures'::'Software' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358328170_518891_1573";
                            associationRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358328170_148690_1572";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355618546_460316_390";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'hardware' : 'Data'::'5 - Architecture'::'L4_Components'::'L4.2_Ground Subsystems Components'::'L4.2.9_Telemetry Processing Components'::'L4.2.9.2_Structures'::'Hardware' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358333745_686899_1590";
                            associationRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731358333745_992220_1589";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355603427_185608_389";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
            }
        }
        }
        package 'L4_Components' {
            package 'L4.1_CubeSat Subsystems Components' {
                package 'L4.1.1_Mission Payload Components' {
                    package 'L4.1.1.2_Structures' {
                        part def 'Instrument' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768517309_104591_15754";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768564386_78772_15756";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.2_Command and Data Handling Components' {
                    package 'L4.1.2.2_Structures' {
                        part def 'Command, Telemetry, and Data Bus' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768973777_796922_15784";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768596772_785377_15758";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.3_Communication Components' {
                    package 'L4.1.3.2_Structures' {
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768598754_969812_15760";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Receive Antenna and Equipment' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768796319_320639_15772";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Transmit Antenna and Equipment' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768805478_770853_15774";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.4_Attitude Determination and Control Components' {
                    package 'L4.1.4.2_Structures' {
                        part def 'Software' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768817190_694096_15776";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Actuator' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768900651_242105_15780";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Sensor' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768843413_403992_15778";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.0_Shared Components' {
                    package 'L4.1.0.2_Structures' {
                        part def 'Shared Processor and Memory' {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3880181_1494340978082_527489_51171";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.5_Guidance Navigation and Control Components' {
                    package 'L4.1.5.2_Structures' {
                        part def 'Accelerometer' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769029630_744670_15786";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'GNSS Receiver' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769039217_2330_15788";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Software' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768926748_916942_15782";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.6_Structures and Mechanisms Components' {
                    package 'L4.1.6.2_Structures' {
                        part def 'Deployable Mount' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769128357_370503_15792";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Static Mount' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769118630_914296_15790";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Actuated Mount' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769142115_856032_15796";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.7_Power Components' {
                    package 'L4.1.7.2_Structures' {
                        part def 'Batteries' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769201063_373794_15802";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Regulators and Converters' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769207094_764375_15804";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Solar Arrays' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769190724_172852_15800";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Power Circuits and Switches' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769219591_806033_15806";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768621567_166101_15770";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Software' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769180766_666463_15798";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.9_Propulsion Components' {
                    package 'L4.1.9.2_Structures' {
                        part def 'Propellant Storage' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769284909_472559_15814";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Propellant Control' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769298016_896824_15816";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Thrusters' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769312673_631299_15818";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768617823_207025_15766";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Software' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769279513_591992_15812";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
                package 'L4.1.8_Thermal Components' {
                    package 'L4.1.8.2_Structures' {
                        part def 'Thermal Sensors, Sources, and Sinks' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769248111_377457_15810";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Processor and Memory' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489768619199_363897_15768";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                        part def 'Software' :> CSRMMassRollUp::MassRollUpPattern {
                            @CSRMv1Metadata::ConvertedClassSource {
                                sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1489769233008_677974_15808";
                                stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                                sourceSummary = "";
                                sourceId = "";
                            }
                        }
                    }
                }
            }
        package 'L4.2_Ground Subsystems Components' {
            package 'L4.2.1_Plan and Schedule Components' {
                package 'L4.2.1.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140070160_102171_60362";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140096721_590968_60364";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561140112822_418165_60366";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.3_Ground Equipment Control Components' {
                package 'L4.2.3.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244785934_257889_60907";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244849588_217848_60934";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244880914_430932_60938";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.4_Space-Ground Communication Components' {
                package 'L4.2.4.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245140395_246710_60952";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245192010_65619_60979";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245203929_935228_60983";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.2_Spacecraft Command Components' {
                package 'L4.2.2.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244679043_729355_60870";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244924860_272284_60944";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561244973154_477653_60948";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.5_Mission Data Processing Components' {
                package 'L4.2.5.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245259757_759124_61027";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245353070_159433_61056";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245412683_544678_61060";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.6_Mission Data Dissemination Components' {
                package 'L4.2.6.2_Structures' {
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245478179_326375_61064";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245523058_466717_61091";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561245538412_270076_61095";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.7_Network Components' {
                package 'L4.2.7.2_Structures' {
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296853724_451978_62430";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296916180_628507_62434";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561296894472_40705_62432";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.8_Facilities Components' {
                package 'L4.2.8.2_Structures' {
                    part def 'Room' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652708601584_552665_58684";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Room 2' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1652714230754_79149_58946";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
            package 'L4.2.9_Telemetry Processing Components' {
                package 'L4.2.9.2_Structures' {
                    part def 'Hardware' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355603427_185608_389";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Software' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355618546_460316_390";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                    part def 'Procedures' {
                        @CSRMv1Metadata::ConvertedClassSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_2024x_1_6350212_1731355627901_243033_391";
                            stereotypeRef = "CSRM-Profile2.mdzip#_18_5_2_3880181_1529417321789_403764_64447";
                            sourceSummary = "";
                            sourceId = "";
                        }
                    }
                }
            }
        }
        }
        package 'L0_Domain' {
            package 'L0.2_Structures' {
                part def 'CubeSat Domain' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649627280_727823_61644";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'external Constraints' : 'Data'::'5 - Architecture'::'L0_Domain'::'L0.2_Structures'::'External Constraints' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649969937_983270_61779";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649969937_95066_61778";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649651952_344595_61646";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'external Environment' : 'Data'::'5 - Architecture'::'L0_Domain'::'L0.2_Structures'::'External Environment' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649978061_109459_61795";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649978061_298291_61794";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649669768_504080_61648";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'cubeSat Mission Enterprise' : 'Data'::'5 - Architecture'::'L1_Mission'::'L1.2_Structures'::'CubeSat Mission' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561650281813_153110_61876";
                            associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561650281813_981425_61875";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562270_394124_14029";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'External Constraints' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649651952_344595_61646";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
                part def 'External Environment' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1561649669768_504080_61648";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
            }
        }
        package 'L1_Mission' {
            package 'L1.2_Structures' {
                part def 'CubeSat Mission' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562270_394124_14029";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                    part 'ground Station Services' : 'Data'::'5 - Architecture'::'L1_Mission'::'L1.2_Structures'::'Ground Station Services' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504905655515_133676_57431";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504905655515_174763_57430";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562277_880588_14035";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part : 'Data'::'5 - Architecture'::'L1_Mission'::'L1.2_Structures'::'Transport, Launch, and Deploy Services' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504905667157_847180_57462";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504905667157_874750_57461";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562278_614914_14036";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'space Segment' : 'Data'::'5 - Architecture'::'L2_Segment'::'L2.1_Space Segment'::'L2.1.2_Structures'::'Space Segment' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504907200801_528658_58027";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504907200801_906314_58026";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573831_645083_14608";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'ground Segment' : 'Data'::'5 - Architecture'::'L2_Segment'::'L2.2_Ground Segment'::'L2.2.2_Structures'::'Ground Segment' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504907579177_901684_58228";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1504907579177_641841_58227";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151573820_820968_14607";
                            sourceMultiplicity = "1..1";
                        }
                    }
                    part 'GPS' : 'Data'::'5 - Architecture'::'L1_Mission'::'L1.2_Structures'::'GNSS' [1..1] {
                        @CSRMv1Metadata::ConvertedPartSource {
                            sourceRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505138455773_514516_58522";
                            associationRef = "CSRM - 2025-11-18.mdzip#_18_5_1_3880181_1505138455773_415075_58521";
                            sourceTypeRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1491499001976_92565_16953";
                            sourceMultiplicity = "1..1";
                        }
                    }
                }
                part def 'Ground Station Services' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562277_880588_14035";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
                part def 'Transport, Launch, and Deploy Services' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_0_6_3e4019a_1472151562278_614914_14036";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
                part def 'GNSS' {
                    @CSRMv1Metadata::ConvertedClassSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_18_4_1_3e4019a_1491499001976_92565_16953";
                        stereotypeRef = "SysML Profile.mdzip#_11_5EAPbeta_be00301_1147424179914_458922_958";
                        sourceSummary = "";
                        sourceId = "";
                    }
                }
            }
        }
        package 'Facilities' {
            part def 'Development Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572366846804_193851_62673";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
                part 'design Facility' : 'Data'::'5 - Architecture'::'Facilities'::'Design Facility' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367108132_280327_62830";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367108132_719887_62829";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572366975727_175828_62749";
                        sourceMultiplicity = "1..1";
                    }
                }
                part 'production Facility' : 'Data'::'5 - Architecture'::'Facilities'::'Production Facility' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367594212_695440_62998";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367594212_876766_62997";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367018961_916810_62751";
                        sourceMultiplicity = "1..1";
                    }
                }
                part 'integration Facility' : 'Data'::'5 - Architecture'::'Facilities'::'Integration Facility' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369275230_579235_63283";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369275230_602679_63282";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367209602_64636_62841";
                        sourceMultiplicity = "1..1";
                    }
                }
                part 'test Facility' : 'Data'::'5 - Architecture'::'Facilities'::'Test Facility' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572378692581_314229_63172";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572378692581_144207_63171";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367329899_768794_62879";
                        sourceMultiplicity = "1..1";
                    }
                }
            }
            part def 'Operations Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572366903726_638065_62711";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
            part def 'Design Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572366975727_175828_62749";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
                part 'offices' : 'Data'::'5 - Architecture'::'Facilities'::'Offices' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368049259_232277_63226";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368049259_579600_63225";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368013883_850830_63183";
                        sourceMultiplicity = "1..1";
                    }
                }
            }
            part def 'Production Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367018961_916810_62751";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
                part 'clean Room' : 'Data'::'5 - Architecture'::'Facilities'::'Clean Room' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367605436_425348_63014";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367605436_283853_63013";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367563868_248933_62955";
                        sourceMultiplicity = "1..1";
                    }
                }
            }
            part def 'Integration Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367209602_64636_62841";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
            part def 'Test Facility' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367329899_768794_62879";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
                part 'thermal Vacuum Chamber' : 'Data'::'5 - Architecture'::'Facilities'::'Thermal Vacuum Chamber' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369324885_802131_63333";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369324885_373372_63332";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367464070_225299_62917";
                        sourceMultiplicity = "1..1";
                    }
                }
                part 'helmoltz Cage' : 'Data'::'5 - Architecture'::'Facilities'::'Helmoltz Cage' [1..1] {
                    @CSRMv1Metadata::ConvertedPartSource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369360182_480315_63349";
                        associationRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572369360182_259316_63348";
                        sourceTypeRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368763384_815328_63239";
                        sourceMultiplicity = "1..1";
                    }
                }
            }
            part def 'Thermal Vacuum Chamber' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367464070_225299_62917";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572365814841_548942_13459";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
            part def 'Clean Room' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572367563868_248933_62955";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
            part def 'Offices' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368013883_850830_63183";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572290137916_56175_13430";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
            part def 'Helmoltz Cage' {
                @CSRMv1Metadata::ConvertedClassSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_2_3880181_1572368763384_815328_63239";
                    stereotypeRef = "CSRM-Profile2.mdzip#_19_0_2_3880181_1572365814841_548942_13459";
                    sourceSummary = "";
                    sourceId = "";
                }
            }
        }
    }
    package 'Derived Properties' {
            item def 'Duplicate Customization' {
                @CSRMDuplicateNavigation::CustomizationSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106767_154950_10738";
                    applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106767_154950_10738_application";
                    sourceHadTarget = false;
                }
                // Chosen native input replaces the unavailable vendor-derived tag.
                ref duplicateOwnedElement : KerML::Element [0..*] ordered {
                    @CSRMDuplicateNavigation::ChosenOwnedElementInput {
                        sourceClassRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106767_154950_10738";
                        vendorProfile = "Problem extensions";
                        vendorStereotype = "Duplicate";
                        vendorTag = "ownedElement";
                        isSourceFeature = false;
                        interpretation = "User-authorized unbound reflective input; no source Duplicate target or instances";
                    }
                }
                private derived ref 'Duplicated Element' : KerML::Element [0..*] ordered = CSRMDuplicateNavigation::DuplicateOwners(duplicateOwnedElement) {
                    @CSRMDuplicateNavigation::DerivedPropertySource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106769_572101_10742";
                        applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106769_23436_10743";
                        sourceTypeRef = "http://www.omg.org/spec/UML/20131001/UML.xmi#Element";
                        sourceNavigation = "Duplicate.ownedElement.owner";
                    }
                }
                private derived attribute 'Qualified Named of Duplicate' : ScalarValues::String [0..*] ordered = CSRMDuplicateNavigation::DuplicateOwnerQualifiedNames(duplicateOwnedElement) {
                    @CSRMDuplicateNavigation::DerivedPropertySource {
                        sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836482637_253285_12867";
                        applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836482637_469693_12868";
                        sourceTypeRef = "http://www.omg.org/spec/UML/20131001/PrimitiveTypes.xmi#String";
                        sourceNavigation = "Duplicate.ownedElement.owner.qualifiedName";
                    }
                }
                private metadata 'Traceability' : CSRMDuplicateNavigation::PropertyGroupSource {
                    sourceRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106770_138885_10746";
                    applicationRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106771_937624_10747";
                    qualifierRef = "CSRM - 2025-11-18.mdzip#_19_0_3_2b0010b_1613836106773_776097_10760";
                    qualifierName = "Other";
                    showGroupInDependencyMatrix = true;
                    showGroupInElementSpecification = true;
                    showGroupInGoTo = true;
                    showGroupInQuickProperties = true;
                    showGroupInRelationMap = true;
                    useAsNode = true;
                }
            }
    }
}
