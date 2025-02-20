from mybuildmodel import MyModel
import math
import numpy as np


class MyModelSon1(MyModel):
    """该类继承于MyModel，对建立模型的方法进行重写"""

    def __init__(self, file_name, file_path, freq, para_box, dielectric_materials):
        super().__init__(file_name, file_path, freq, para_box, dielectric_materials)

    # 对建立模型的方法进行重写
    def build_model(self):
        # 需要确保有相应的材料，有相应的参数
        self.modify_solver()
        self.add_material_ITO()
        self.add_material_PET()
        self.add_material_PDMS()
        # # 建立中间层PDMS
        # 建立中间层PDMS
        brick_toppdms = [[-self.para_box['p'], -self.para_box['p'], 0],
                         [self.para_box['p'], self.para_box['p'], self.para_box['H1']]]
        self.create_brick('midpdms', 'PDMS', brick_toppdms)

        brick_toppdms2 = [[-self.para_box['p'], -self.para_box['p'], self.para_box['H1']+self.para_box['D']],
                         [self.para_box['p'], self.para_box['p'], self.para_box['H1']+self.para_box['H2']]]
        self.create_brick('midpdms2', 'PDMS', brick_toppdms2)
        # # 建立中间层PET1
        # 建立中间层PET1
        brick_midpet1 = [[-self.para_box['p'], -self.para_box['p'], self.para_box['H1']],
                         [self.para_box['p'], self.para_box['p'], self.para_box['D'] + self.para_box['H1']]]
        self.create_brick('midpet1', 'PET', brick_midpet1)
        brick_midpet2 = [[-self.para_box['p'], -self.para_box['p'],0],
                         [self.para_box['p'], self.para_box['p'], -self.para_box['D'] ]]
        self.create_brick('midpet2', 'PET', brick_midpet2)
        brick_botito = [
            [-self.para_box['d'], -self.para_box['l'], self.para_box['H1'] +self.para_box['D']],
            [self.para_box['d'], self.para_box['l'], self.para_box['H1'] + self.para_box['D'] + self.para_box['T1']]]
        self.create_brick('topITO2', 'ITO', brick_botito)
        self.rotation_structure('topITO2', center=[0, 0, 0], angle=[0, 0, 45], repetition=1, enable_unite=False,
                                enable_copy=False, component='component1')

        brick_botito = [
            [-self.para_box['d1'], -self.para_box['r3']*math.sqrt(2)+0.1, self.para_box['H1'] +self.para_box['D']],
            [self.para_box['d1'], self.para_box['r3']*math.sqrt(2)+0.1, self.para_box['H1'] + self.para_box['D'] + self.para_box['T1']]]
        self.create_brick('topITO1', 'ITO', brick_botito)
        self.rotation_structure('topITO1', center=[0, 0, 0], angle=[0, 0, -45], repetition=1, enable_unite=False,
                                enable_copy=False, component='component1')



        outetR = self.para_box['r3']
        innerR = self.para_box['r3']-self.para_box['r4']
        zRange = [self.para_box['H1']+self.para_box['D'], self.para_box['H1']+self.para_box['D']+self.para_box['T1']]

        self.creat_phoenix('topITO3', 'ITO', (0, 0), outetR, innerR, zRange, number="4")
        self.rotation_structure('topITO3', center=[0, 0, 0], angle=[0, 0, -45], repetition=1, enable_unite=False,
                                enable_copy=False, component='component1')
        self.boolean_subtract('topITO3', ['topITO1'])
        self.boolean_add('topITO2', ['topITO3'])

        # # 建立底 层ITO

        outetR = self.para_box['r1']
        innerR = self.para_box['r1']-self.para_box['r2']
        zRange = [self.para_box['H1']+self.para_box['D'], self.para_box['H1']+self.para_box['D']+self.para_box['T1']]

        self.creat_phoenix('topITO4', 'ITO', (0, 0), outetR, innerR, zRange, number="4")
        self.rotation_structure('topITO4', center=[0, 0, 0], angle=[0, 0, 45], repetition=1, enable_unite=False,
                                enable_copy=False, component='component1')

        brick_botito = [
            [-self.para_box['p1'], -self.para_box['p1'], self.para_box['H1'] + self.para_box['D']],
            [ self.para_box['p1'] , self.para_box['p1'] ,self.para_box['H1'] + self.para_box['D'] + self.para_box['T1']]]
        self.create_brick('topITO5', 'ITO', brick_botito)

        brick_botito = [
            [-self.para_box['p1']+self.para_box['p2'], -self.para_box['p1']+self.para_box['p2'], self.para_box['H1'] + self.para_box['D']],
            [self.para_box['p1']-self.para_box['p2'] , self.para_box['p1']-self.para_box['p2'] ,self.para_box['H1'] + self.para_box['D'] + self.para_box['T1']]]
        self.create_brick('topITO6', 'ITO', brick_botito)
        self.boolean_subtract('topITO5', ['topITO6'])
        brick_botito = [
            [-self.para_box['p'], -self.para_box['p'], self.para_box['H1'] +self.para_box['D']],
            [-self.para_box['p2']+self.para_box['p3'], -self.para_box['p2']+self.para_box['p3'], self.para_box['H1'] + self.para_box['D'] + self.para_box['T1']]]
        self.create_brick('topITO7', 'ITO', brick_botito)
        self.rotation_structure('topITO7', center=[0, 0, 0], angle=[0, 0, 180], repetition=1, enable_unite=False,
                                enable_copy=True, component='component1')
        self.boolean_subtract('topITO5', ['topITO7'])
        self.boolean_subtract('topITO5', ['topITO7_1'])
        self.boolean_add('topITO2', ['topITO4'])
        self.boolean_add('topITO2', ['topITO5'])
        self.boolean_add('topITO2', ['topITO7'])
        self.boolean_add('topITO2', ['topITO7_1'])
        brick_lowITO1 = [[-self.para_box['p'], -self.para_box['p'],-self.para_box['D'] - self.para_box['T1']],
                         [self.para_box['p'], self.para_box['p'], - self.para_box['D']]]
        self.create_brick('lowITO1', 'ITO', brick_lowITO1)
        # self.rotation_structure('topITO2', center=[0, 0, 0], angle=[0, 0, 90], repetition=1, enable_unite=False,
        #                         enable_copy=False, component='component1')#后加改90°
        self.define_frequency_domain_solver_parameters()
        self.new_project.save(self.file_path + self.file_name + ".cst")

    def modify_solver(self):
        modify_solver_command = ''''set the units
        With Units
            .Geometry "mm"
            .Frequency "GHz"
            .Voltage "V"
            .Resistance "Ohm"
            .Inductance "H"
            .TemperatureUnit  "Kelvin"
            .Time "ns"
            .Current "A"
            .Conductance "Siemens"
            .Capacitance "F"
        End With

        '----------------------------------------------------------------------------

        'set the frequency range
        Solver.FrequencyRange "0", "40"

        '----------------------------------------------------------------------------

        Plot.DrawBox True

        With Background
             .Type "Normal"
             .Epsilon "1.0"
             .Mu "1.0"
             .Rho "1.204"
             .ThermalType "Normal"
             .ThermalConductivity "0.026"
             .HeatCapacity "1.005"
             .XminSpace "0.0"
             .XmaxSpace "0.0"
             .YminSpace "0.0"
             .YmaxSpace "0.0"
             .ZminSpace "0.0"
             .ZmaxSpace "0.0"
        End With

        ' define Floquet port boundaries

        With FloquetPort
             .Reset
             .SetDialogTheta "0"
             .SetDialogPhi "0"
             .SetSortCode "+beta/pw"
             .SetCustomizedListFlag "False"
             .Port "Zmin"
             .SetNumberOfModesConsidered "2"
             .Port "Zmax"
             .SetNumberOfModesConsidered "2"
        End With

        MakeSureParameterExists "theta", "0"
        SetParameterDescription "theta", "spherical angle of incident plane wave"
        MakeSureParameterExists "phi", "0"
        SetParameterDescription "phi", "spherical angle of incident plane wave"

        ' define boundaries, the open boundaries define floquet port

        With Boundary
             .Xmin "unit cell"
             .Xmax "unit cell"
             .Ymin "unit cell"
             .Ymax "unit cell"
             .Zmin "expanded open"
             .Zmax "expanded open"
             .Xsymmetry "none"
             .Ysymmetry "none"
             .Zsymmetry "none"
             .XPeriodicShift "0.0"
             .YPeriodicShift "0.0"
             .ZPeriodicShift "0.0"
             .PeriodicUseConstantAngles "False"
             .SetPeriodicBoundaryAngles "theta", "phi"
             .SetPeriodicBoundaryAnglesDirection "inward"
             .UnitCellFitToBoundingBox "True"
             .UnitCellDs1 "0.0"
             .UnitCellDs2 "0.0"
             .UnitCellAngle "90.0"
        End With

        ' set tet mesh as default

        With Mesh
             .MeshType "Tetrahedral"
        End With

        ' FD solver excitation with incoming plane wave at Zmax

        With FDSolver
             .Reset
             .Stimulation "List", "List"
             .ResetExcitationList
             .AddToExcitationList "Zmax", "TE(0,0);TM(0,0)"
             .LowFrequencyStabilization "False"
        End With

        '----------------------------------------------------------------------------

        With MeshSettings
             .SetMeshType "Tet"
             .Set "Version", 1%
        End With

        With Mesh
             .MeshType "Tetrahedral"
        End With

        'set the solver type
        ChangeSolverType("HF Frequency Domain")

        '----------------------------------------------------------------------------'''

        self.modeler.add_to_history("modify solver", modify_solver_command)

    def define_frequency_domain_solver_parameters(self):
        modify_solver_command = '''
               Mesh.SetCreator "High Frequency" 
        With FDSolver
             .Reset 
             .SetMethod "Tetrahedral", "General purpose" 
             .OrderTet "Second" 
             .OrderSrf "First" 
             .Stimulation "List", "List" 
             .ResetExcitationList 
             .AddToExcitationList "Zmax", "TE(0,0)" 
             .AutoNormImpedance "False" 
             .NormingImpedance "50" 
             .ModesOnly "False" 
             .ConsiderPortLossesTet "True" 
             .SetShieldAllPorts "False" 
             .AccuracyHex "1e-6" 
             .AccuracyTet "1e-4" 
             .AccuracySrf "1e-3" 
             .LimitIterations "False" 
             .MaxIterations "0" 
             .SetCalcBlockExcitationsInParallel "True", "True", "" 
             .StoreAllResults "False" 
             .StoreResultsInCache "False" 
             .UseHelmholtzEquation "True" 
             .LowFrequencyStabilization "True" 
             .Type "Auto" 
             .MeshAdaptionHex "False" 
             .MeshAdaptionTet "True" 
             .AcceleratedRestart "True" 
             .FreqDistAdaptMode "Distributed" 
             .NewIterativeSolver "True" 
             .TDCompatibleMaterials "False" 
             .ExtrudeOpenBC "False" 
             .SetOpenBCTypeHex "Default" 
             .SetOpenBCTypeTet "Default" 
             .AddMonitorSamples "True" 
             .CalcPowerLoss "True" 
             .CalcPowerLossPerComponent "False" 
             .StoreSolutionCoefficients "True" 
             .UseDoublePrecision "False" 
             .UseDoublePrecision_ML "True" 
             .MixedOrderSrf "False" 
             .MixedOrderTet "False" 
             .PreconditionerAccuracyIntEq "0.15" 
             .MLFMMAccuracy "Default" 
             .MinMLFMMBoxSize "0.3" 
             .UseCFIEForCPECIntEq "True" 
             .UseFastRCSSweepIntEq "false" 
             .UseSensitivityAnalysis "False" 
             .RemoveAllStopCriteria "Hex"
             .AddStopCriterion "All S-Parameters", "0.01", "2", "Hex", "True"
             .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Hex", "False"
             .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Hex", "False"
             .RemoveAllStopCriteria "Tet"
             .AddStopCriterion "All S-Parameters", "0.01", "2", "Tet", "True"
             .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Tet", "False"
             .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Tet", "False"
             .AddStopCriterion "All Probes", "0.05", "2", "Tet", "True"
             .RemoveAllStopCriteria "Srf"
             .AddStopCriterion "All S-Parameters", "0.01", "2", "Srf", "True"
             .AddStopCriterion "Reflection S-Parameters", "0.01", "2", "Srf", "False"
             .AddStopCriterion "Transmission S-Parameters", "0.01", "2", "Srf", "False"
             .SweepMinimumSamples "3" 
             .SetNumberOfResultDataSamples "1001" 
             .SetResultDataSamplingMode "Automatic" 
             .SweepWeightEvanescent "1.0" 
             .AccuracyROM "1e-4" 
             .AddSampleInterval "", "", "1", "Automatic", "True" 
             .AddSampleInterval "", "", "", "Automatic", "False" 
             .MPIParallelization "False"
             .UseDistributedComputing "False"
             .NetworkComputingStrategy "RunRemote"
             .NetworkComputingJobCount "3"
             .UseParallelization "True"
             .MaxCPUs "8"
             .MaximumNumberOfCPUDevices "1"
        End With
        With IESolver
             .Reset 
             .UseFastFrequencySweep "True" 
             .UseIEGroundPlane "False" 
             .SetRealGroundMaterialName "" 
             .CalcFarFieldInRealGround "False" 
             .RealGroundModelType "Auto" 
             .PreconditionerType "Auto" 
             .ExtendThinWireModelByWireNubs "False" 
        End With
        With IESolver
             .SetFMMFFCalcStopLevel "0" 
             .SetFMMFFCalcNumInterpPoints "6" 
             .UseFMMFarfieldCalc "True" 
             .SetCFIEAlpha "0.500000" 
             .LowFrequencyStabilization "False" 
             .LowFrequencyStabilizationML "True" 
             .Multilayer "False" 
             .SetiMoMACC_I "0.0001" 
             .SetiMoMACC_M "0.0001" 
             .DeembedExternalPorts "True" 
             .SetOpenBC_XY "True" 
             .OldRCSSweepDefintion "False" 
             .SetRCSOptimizationProperties "True", "100", "0.00001" 
             .SetAccuracySetting "Custom" 
             .CalculateSParaforFieldsources "True" 
             .ModeTrackingCMA "True" 
             .NumberOfModesCMA "3" 
             .StartFrequencyCMA "-1.0" 
             .SetAccuracySettingCMA "Default" 
             .FrequencySamplesCMA "0" 
             .SetMemSettingCMA "Auto" 
             .CalculateModalWeightingCoefficientsCMA "True" 
        End With

          '''

        self.modeler.add_to_history("modify solver", modify_solver_command)
