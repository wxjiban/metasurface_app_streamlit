from mybuildmodel import MyModel
import math
import numpy as np
import time

class MyModelSon1(MyModel):
    """该类继承于MyModel，对建立模型的方法进行重写"""

    def __init__(self, file_name, file_path, freq, para_box, dielectric_materials):
        super().__init__(file_name, file_path, freq, para_box, dielectric_materials)

    # 对建立模型的方法进行重写
    def build_model(self):
        # 需要确保有相应的材料，有相应的参数
        self.modify_solver()
        self.init_unit()
        self.add_material_ITO()
        self.add_material_PET()

        ######################### 建立顶层ITO
        #圆环
        self.creat_cylinder('topITO', 'ITO', [0, 0], self.para_box['p'] / 2 - self.para_box['a'], self.para_box['p'] / 2 - self.para_box['a'] - self.para_box['b'], [0, self.para_box['T1']], 'z','component1')
        #画扇形
        #画弧
        center_xys = [0, 0];
        init_xys = [self.para_box['p'] / 2, 0];
        angle = self.para_box['theta_1']+ self.para_box['theta_2'];
        self.creat_2D_arc('arc1', 'curve1', center_xys, init_xys, angle)
        #画两根短线
        curve_xyzs = [[0, 0],
                      [self.para_box['p'] / 2, 0]];
        self.create_curve_polygon('line1', 'curve1', curve_xyzs)
        self.rotation_curve('line1', center=[0, 0, 0], angle=[0, 0, -(self.para_box['theta_1']+ self.para_box['theta_2'])], repetition=1,
                            enable_unite=False,
                            enable_copy=True, curve='curve1')
        # 拉伸成体
        self.extrude_curve('solid1', 'arc1', -self.para_box['T1'], 'ITO', curve_name="curve1", component="component1")
        self.rotation_structure('solid1', center=[0, 0, 0], angle=[0, 0, self.para_box['theta_1']], repetition=1,
                                enable_unite=False,
                                enable_copy=False, component='component1')
        self.mirror_structure('solid1', [1, -1, 0], enable_copy=True, enable_unite=False, component='component1')
        #圆环减掉两个扇形
        self.boolean_subtract('topITO', ['solid1'])
        self.boolean_subtract('topITO', ['solid1_1'])

        ################################# 建立中层PET
        brick_midPET = [[-self.para_box['p'] / 2, -self.para_box['p'] / 2, 0],
                        [self.para_box['p'] / 2, self.para_box['p'] / 2, - self.para_box['d1']]];
        self.create_brick('midPET', 'PET', brick_midPET)
        ################################# 建立底层ITO
        brick_lowITO = [[-self.para_box['p'] / 2, -self.para_box['p'] / 2, - self.para_box['d1']],
                        [self.para_box['p'] / 2, self.para_box['p'] / 2, - self.para_box['d1'] - self.para_box['T1']]]
        self.create_brick('lowITO', 'ITO', brick_lowITO)
        ################################# 建立顶层PET
        brick_topPET = [[-self.para_box['p'] / 2, -self.para_box['p'] / 2, self.para_box['T1']],
                        [self.para_box['p'] / 2, self.para_box['p'] / 2, self.para_box['T1'] + self.para_box['d2']]];
        self.create_brick('topPET', 'PET', brick_topPET)

        self.new_project.save(self.file_path + self.file_name + ".cst")

    def set_mesh(self):
        set_mesh_command = '''With Mesh 
                 .MeshType "Tetrahedral" 
                 .SetCreator "High Frequency"
            End With 
            With MeshSettings 
                 .SetMeshType "Tet" 
                 .Set "Version", 1%
                 'MAX CELL - WAVELENGTH REFINEMENT 
                 .Set "StepsPerWaveNear", "4" 
                 .Set "StepsPerWaveFar", "4" 
                 .Set "PhaseErrorNear", "0.02" 
                 .Set "PhaseErrorFar", "0.02" 
                 .Set "CellsPerWavelengthPolicy", "automatic" 
                 'MAX CELL - GEOMETRY REFINEMENT 
                 .Set "StepsPerBoxNear", "10" 
                 .Set "StepsPerBoxFar", "1" 
                 .Set "ModelBoxDescrNear", "maxedge" 
                 .Set "ModelBoxDescrFar", "maxedge" 
                 'MIN CELL 
                 .Set "UseRatioLimit", "0" 
                 .Set "RatioLimit", "100" 
                 .Set "MinStep", "0" 
                 'MESHING METHOD 
                 .SetMeshType "Unstr" 
                 .Set "Method", "0" 
            End With 
            With MeshSettings 
                 .SetMeshType "Tet" 
                 .Set "CurvatureOrder", "1" 
                 .Set "CurvatureOrderPolicy", "automatic" 
                 .Set "CurvRefinementControl", "NormalTolerance" 
                 .Set "NormalTolerance", "22.5" 
                 .Set "SrfMeshGradation", "1.5" 
                 .Set "SrfMeshOptimization", "1" 
            End With 
            With MeshSettings 
                 .SetMeshType "Unstr" 
                 .Set "UseMaterials",  "1" 
                 .Set "MoveMesh", "0" 
            End With 
            With MeshSettings 
                 .SetMeshType "All" 
                 .Set "AutomaticEdgeRefinement",  "0" 
            End With 
            With MeshSettings 
                 .SetMeshType "Tet" 
                 .Set "UseAnisoCurveRefinement", "1" 
                 .Set "UseSameSrfAndVolMeshGradation", "1" 
                 .Set "VolMeshGradation", "1.5" 
                 .Set "VolMeshOptimization", "1" 
            End With 
            With MeshSettings 
                 .SetMeshType "Unstr" 
                 .Set "SmallFeatureSize", "0" 
                 .Set "CoincidenceTolerance", "1e-06" 
                 .Set "SelfIntersectionCheck", "1" 
                 .Set "OptimizeForPlanarStructures", "0" 
            End With 
            With Mesh 
                 .SetParallelMesherMode "Tet", "maximum" 
                 .SetMaxParallelMesherThreads "Tet", "1" 
            End With 
            '''
        self.modeler.add_to_history("set_mesh", set_mesh_command)

    def modify_solver(self):
        modify_solver_command = '''Mesh.SetCreator "High Frequency" 

            With FDSolver
                 .Reset 
                 .SetMethod "Tetrahedral", "General purpose" 
                 .OrderTet "Second" 
                 .OrderSrf "First" 
                 .Stimulation "List", "List" 
                 .ResetExcitationList 
                 .AddToExcitationList "Zmax", "TE(0,0);TM(0,0)" 
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
                 .LowFrequencyStabilization "False" 
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
                 .MaxCPUs "128"
                 .MaximumNumberOfCPUDevices "2"
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


    def init_unit(self):
        unit_set_command = '''With Units
                .Geometry "mm"
                .Frequency "GHz"
                .Time "ns"
                .TemperatureUnit "Kelvin"
                .Voltage "V"
                .Current "A"
                .Resistance "Ohm"
                .Conductance "Siemens"
                .Capacitance "F"
                .Inductance "H"
                .SetResultUnit "frequency", "frequency", ""
            End With'''
        self.modeler.add_to_history("set the units", unit_set_command)

