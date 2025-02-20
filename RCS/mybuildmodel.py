import cst.interface
import math


class MyModel:
    """关于CST模型一些操作的类"""

    def __init__(self, file_name, file_path, freq, para_box, dielectric_materials):
        self.file_name = file_name  # 文件名
        self.file_path = file_path  # 文件存储路径
        self.freq = freq  # 工作频率，一个二元列表或者元组表示开始和结束的频率
        self.para_box = para_box
        self.dielectric_materials = dielectric_materials  # 字典类型{'名称':[介电常数, 损耗角正切值]}

        # 启动CST环境，并创建一个mws项目
        self.cst_environment = cst.interface.DesignEnvironment()
        self.new_project = self.cst_environment.new_mws()

        # 新的project里建模，返回一个Modeler类对象的实例
        self.modeler = self.new_project.modeler

        # 按照路径保存新建的项目
        # new_project.save(file_path + file_name + ".cst")

    # 初始化模型
    def init_model(self):
        self.init_unit()
        self.init_freq()
        self.init_solver()
        # self.define_parameter()
        self.define_boundary()
        self.add_dielectric_material()
        self.add_material_copper()
        self.define_background()

    # 建立模型，需要对建模的方法进行重写
    def build_model(self):
        pass
    def set_mesh(self):
        pass
    # 端口设置
    def set_port(self, deembed_distance, enable_circular_polarazation=False):
        floquet_port_command = f'''With FloquetPort
            .Reset
            .SetDialogTheta "0"
            .SetDialogPhi "0"
            .SetSortCode "+beta/pw"
            .SetCustomizedListFlag "False"
            .Port "Zmin"
            .SetNumberOfModesConsidered "2"
            .Port "Zmax"
            .SetNumberOfModesConsidered "2"
        End With'''
        self.modeler.add_to_history("set Floquet port", floquet_port_command)

    # 运行仿真
    def run(self):
        self.modeler.run_solver()

    # 初始化单位
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
            .Capacitance "PikoF"
            .Inductance "NanoH"
            .SetResultUnit "frequency", "frequency", ""
        End With'''
        self.modeler.add_to_history("set the units", unit_set_command)

    # 初始化频率
    def init_freq(self):
        fre_set_command = f"Solver.FrequencyRange {self.freq[0]},{self.freq[1]}"
        self.modeler.add_to_history('define frequency range', fre_set_command)

    # 初始化求解器，此处默认为四面体网格的F求解器
    def init_solver(self):
        solver_set_command = '''With MeshSettings
            .SetMeshType "Tet"
            .Set "Version", 1%
            End With
            With Mesh
            .MeshType "Tetrahedral"
            End With
            'set the solver type
            ChangeSolverType("HF Frequency Domain")'''
        self.modeler.add_to_history('define solver', solver_set_command)

    # 添加自定义的材料，可以直接添加很多种材料
    def add_dielectric_material(self):
        for dielectric_material_name, dielectric_material_value in self.dielectric_materials.items():
            # 传入为字典元素，.items()返回值为字典的键和值的二元元组。
            material_description_command = f'''With Material 
                .Reset 
                .Name "{dielectric_material_name}"
                .Type "Normal"
                .Epsilon "{dielectric_material_value[0]}"
                .Mu "1"
                .Sigma "0"
                .TanD "{dielectric_material_value[1]}"
                .TanDFreq "0"
                .TanDGiven "True"
                .TanDModel "ConstTanD"
                .Colour "0", "0.25098", "0" 
                .Wireframe "False" 
                .Reflection "False" 
                .Allowoutline "True" 
                .Transparentoutline "False" 
                .Transparency "0" 
                .Create
            End With'''
            self.modeler.add_to_history("add a dielectric material", material_description_command)

    # 添加材料铜
    def add_material_copper(self):
        copper_description_command = '''With Material
            .Reset
            .Name "Copper (annealed)"
            .Folder ""
            .FrqType "static"
            .Type "Normal"
            .SetMaterialUnit "Hz", "mm"
            .Epsilon "1"
            .Mu "1.0"
            .Kappa "5.8e+007"
            .TanD "0.0"
            .TanDFreq "0.0"
            .TanDGiven "False"
            .TanDModel "ConstTanD"
            .KappaM "0"
            .TanDM "0.0"
            .TanDMFreq "0.0"
            .TanDMGiven "False"
            .TanDMModel "ConstTanD"
            .DispModelEps "None"
            .DispModelMu "None"
            .DispersiveFittingSchemeEps "Nth Order"
            .DispersiveFittingSchemeMu "Nth Order"
            .UseGeneralDispersionEps "False"
            .UseGeneralDispersionMu "False"
            .FrqType "all"
            .Type "Lossy metal"
            .SetMaterialUnit "GHz", "mm"
            .Mu "1.0"
            .Kappa "5.8e+007"
            .Rho "8930.0"
            .ThermalType "Normal"
            .ThermalConductivity "401.0"
            .HeatCapacity "0.39"
            .MetabolicRate "0"
            .BloodFlow "0"
            .VoxelConvection "0"
            .MechanicsType "Isotropic"
            .YoungsModulus "120"
            .PoissonsRatio "0.33"
            .ThermalExpansionRate "17"
            .Colour "1", "1", "0"
            .Wireframe "False"
            .Reflection "False"
            .Allowoutline "True"
            .Transparentoutline "False"
            .Transparency "0"
            .Create
        End With'''
        self.modeler.add_to_history("add a copper", copper_description_command)

    # 添加材料ITO
    def add_material_ITO(self):
        ITO_description_command = '''With Material
            .Reset 
            .Name "ITO"
            .Folder ""
            .Rho "0.0"
            .ThermalType "Normal"
            .ThermalConductivity "0"
            .SpecificHeat "0", "J/K/kg"
            .DynamicViscosity "0"
            .Emissivity "0"
            .MetabolicRate "0.0"
            .VoxelConvection "0.0"
            .BloodFlow "0"
            .MechanicsType "Unused"
            .FrqType "all"
            .Type "Lossy metal"
            .MaterialUnit "Frequency", "GHz"
            .MaterialUnit "Geometry", "mm"
            .MaterialUnit "Time", "ns"
            .MaterialUnit "Temperature", "Kelvin"
            .OhmicSheetImpedance "8", "0"
            .OhmicSheetFreq "0"
            .ReferenceCoordSystem "Global"
            .CoordSystemType "Cartesian"
            .NLAnisotropy "False"
            .NLAStackingFactor "1"
            .NLADirectionX "1"
            .NLADirectionY "0"
            .NLADirectionZ "0"
            .Colour "1", "0.501961", "0.25098"  
            .Wireframe "False" 
            .Reflection "False" 
            .Allowoutline "True" 
            .Transparentoutline "False" 
            .Transparency "0" 
            .Create
        End With'''
        self.modeler.add_to_history("add a ITO", ITO_description_command)

    # 添加材料PET
    def add_material_PET(self):
        PET_description_command = '''With Material
            .Reset 
            .Name "PET"
            .Folder ""
            .Rho "0.0"
            .ThermalType "Normal"
            .ThermalConductivity "0"
            .SpecificHeat "0", "J/K/kg"
            .DynamicViscosity "0"
            .Emissivity "0"
            .MetabolicRate "0.0"
            .VoxelConvection "0.0"
            .BloodFlow "0"
            .MechanicsType "Unused"
            .FrqType "all"
            .Type "Normal"
            .MaterialUnit "Frequency", "GHz"
            .MaterialUnit "Geometry", "mm"
            .MaterialUnit "Time", "ns"
            .MaterialUnit "Temperature", "Kelvin"
            .Epsilon "3.05"
            .Mu "1"
            .Sigma "0.0"
            .TanD "0.006"
            .TanDFreq "0.0"
            .TanDGiven "True"
            .TanDModel "ConstTanD"
            .EnableUserConstTanDModelOrderEps "False"
            .ConstTanDModelOrderEps "1"
            .SetElParametricConductivity "False"
            .ReferenceCoordSystem "Global"
            .CoordSystemType "Cartesian"
            .SigmaM "0"
            .TanDM "0.0"
            .TanDMFreq "0.0"
            .TanDMGiven "False"
            .TanDMModel "ConstTanD"
            .EnableUserConstTanDModelOrderMu "False"
            .ConstTanDModelOrderMu "1"
            .SetMagParametricConductivity "False"
            .DispModelEps "None"
            .DispModelMu "None"
            .DispersiveFittingSchemeEps "Nth Order"
            .MaximalOrderNthModelFitEps "10"
            .ErrorLimitNthModelFitEps "0.1"
            .UseOnlyDataInSimFreqRangeNthModelEps "False"
            .DispersiveFittingSchemeMu "Nth Order"
            .MaximalOrderNthModelFitMu "10"
            .ErrorLimitNthModelFitMu "0.1"
            .UseOnlyDataInSimFreqRangeNthModelMu "False"
            .UseGeneralDispersionEps "False"
            .UseGeneralDispersionMu "False"
            .NLAnisotropy "False"
            .NLAStackingFactor "1"
            .NLADirectionX "1"
            .NLADirectionY "0"
            .NLADirectionZ "0"
            .Colour "0", "0", "1" 
            .Wireframe "False" 
            .Reflection "False" 
            .Allowoutline "True" 
            .Transparentoutline "False"  
            .Transparency "0" 
            .Create
        End With'''
        self.modeler.add_to_history("add a PET", PET_description_command)

    def add_material_PDMS(self):
        PDMS_description_command = '''With Material
            .Reset 
            .Name "PDMS"
            .Folder ""
            .Rho "0.0"
            .ThermalType "Normal"
            .ThermalConductivity "0"
            .SpecificHeat "0", "J/K/kg"
            .DynamicViscosity "0"
            .Emissivity "0"
            .MetabolicRate "0.0"
            .VoxelConvection "0.0"
            .BloodFlow "0"
            .MechanicsType "Unused"
            .FrqType "all"
            .Type "Normal"
            .MaterialUnit "Frequency", "GHz"
            .MaterialUnit "Geometry", "mm"
            .MaterialUnit "Time", "ns"
            .MaterialUnit "Temperature", "Kelvin"
            .Epsilon "2.35"
            .Mu "1"
            .Sigma "0"
            .TanD "0.06"
            .TanDFreq "0.0"
            .TanDGiven "True"
            .TanDModel "ConstTanD"
            .EnableUserConstTanDModelOrderEps "False"
            .ConstTanDModelOrderEps "1"
            .SetElParametricConductivity "False"
            .ReferenceCoordSystem "Global"
            .CoordSystemType "Cartesian"
            .SigmaM "0"
            .TanDM "0.0"
            .TanDMFreq "0.0"
            .TanDMGiven "False"
            .TanDMModel "ConstTanD"
            .EnableUserConstTanDModelOrderMu "False"
            .ConstTanDModelOrderMu "1"
            .SetMagParametricConductivity "False"
            .DispModelEps "None"
            .DispModelMu "None"
            .DispersiveFittingSchemeEps "Nth Order"
            .MaximalOrderNthModelFitEps "10"
            .ErrorLimitNthModelFitEps "0.1"
            .UseOnlyDataInSimFreqRangeNthModelEps "False"
            .DispersiveFittingSchemeMu "Nth Order"
            .MaximalOrderNthModelFitMu "10"
            .ErrorLimitNthModelFitMu "0.1"
            .UseOnlyDataInSimFreqRangeNthModelMu "False"
            .UseGeneralDispersionEps "False"
            .UseGeneralDispersionMu "False"
            .NLAnisotropy "False"
            .NLAStackingFactor "1"
            .NLADirectionX "1"
            .NLADirectionY "0"
            .NLADirectionZ "0"
            .Colour "0", "1", "1" 
            .Wireframe "False" 
            .Reflection "False" 
            .Allowoutline "True" 
            .Transparentoutline "False" 
            .Transparency "0" 
            .Create
        End With'''
        self.modeler.add_to_history("add a PDMS", PDMS_description_command)

    # 定义参数
    def define_parameter(self):
        for para_name, para_value in self.para_box.items():
            self.modeler.add_to_history('StoreParameter', f'MakeSureParameterExists("{para_name}", "{para_value}")')

    # 定义四边形边界条件
    def define_boundary(self):
        boundary_command = '''With Boundary
            .Xmin "unit cell"
            .Xmax "unit cell"
            .Ymin "unit cell"
            .Ymax "unit cell"
            .Zmin "expanded open"
            .Zmax "expanded open"
            .ApplyInAllDirections "False"
            .XPeriodicShift "0.0"
            .YPeriodicShift "0.0"
            .ZPeriodicShift "0.0"
            .PeriodicUseConstantAngles "False"
            .SetPeriodicBoundaryAngles "0.0", "0.0"
            .SetPeriodicBoundaryAnglesDirection "outward"
            .UnitCellFitToBoundingBox "True"
            .UnitCellDs1 "0.0"
            .UnitCellDs2 "0.0"
            .UnitCellAngle "90.0"
        End With'''
        self.modeler.add_to_history('define boundary', boundary_command)

        # 定义六边形边界

    # def define_boundary(self, thetax=0, phix=0, jiaodux=3*6, jiaoduy=math.sqrt(3)*6):
    #     boundary_command = f'''With Boundary
    #         .Xmin "unit cell"
    #         .Xmax "unit cell"
    #         .Ymin "unit cell"
    #         .Ymax "unit cell"
    #         .Zmin "expanded open"
    #         .Zmax "expanded open"
    #         .Xsymmetry "none"
    #         .Ysymmetry "none"
    #         .Zsymmetry "none"
    #         .ApplyInAllDirections "False"
    #         .OpenAddSpaceFactor "0.5"
    #         .XPeriodicShift "0.0"
    #         .YPeriodicShift "0.0"
    #         .ZPeriodicShift "0.0"
    #         .PeriodicUseConstantAngles "False"
    #         .SetPeriodicBoundaryAngles "{thetax}", "{phix}"
    #         .SetPeriodicBoundaryAnglesDirection "inward"
    #         .UnitCellFitToBoundingBox "False"
    #         .UnitCellDs1 "{jiaodux}"
    #         .UnitCellDs2 "{jiaoduy}"
    #         .UnitCellAngle "30"
    #     End With'''
    #     self.modeler.add_to_history('define boundary', boundary_command)

    # 定义背景条件
    def define_background(self):
        background_command = '''With Background
            .ResetBackground 
            .XminSpace "0.0" 
            .XmaxSpace "0.0" 
            .YminSpace "0.0" 
            .YmaxSpace "0.0" 
            .ZminSpace "0.0" 
            .ZmaxSpace "0.0" 
            .ApplyInAllDirections "False" 
        End With '''
        self.modeler.add_to_history('define background', background_command)

    ###################        画图   #########################

    # *************三维结构*********************
    # 1.建立长方体模型，xyzs是一个2*3的列表[[x1, y1, z1],[x2,y2,z2]]
    def create_brick(self, name, material_name, brick_xyzs, component="component1"):
        create_brick_command = f'''With Brick
            .Reset
            .Name "{name}"
            .Component "{component}"
            .Material "{material_name}"
            .Xrange "{brick_xyzs[0][0]}", "{brick_xyzs[1][0]}"
            .Yrange "{brick_xyzs[0][1]}", "{brick_xyzs[1][1]}"
            .Zrange "{brick_xyzs[0][2]}", "{brick_xyzs[1][2]}"
            .Create
        End With'''
        self.modeler.add_to_history(f"draw a brick {name}", create_brick_command)

    # 2. 画一个圆柱体，输入xycenter中心二维元组或者列表
    def creat_cylinder(self, cylinder_name, material_name="Copper (annealed)", xy_center=[0, 0], outerR=10, innerR=0,
                       zRange=[0, 10], axis="z",
                       component="component1"):
        creat_cylinderCommand = f'''With Cylinder 
             .Reset 
             .Name "{cylinder_name}" 
             .Component "{component}" 
             .Material "{material_name}" 
             .OuterRadius "{outerR}" 
             .InnerRadius "{innerR}" 
             .Axis "{axis}" 
             .Zrange "{zRange[0]}", "{zRange[1]}" 
             .Xcenter "{xy_center[0]}" 
             .Ycenter "{xy_center[1]}" 
             .Segments "0" 
             .Create 
        End With 
        '''
        self.modeler.add_to_history(f"draw a cylinder-{cylinder_name}", creat_cylinderCommand)
        return cylinder_name

    # 画一个六边形
    def creat_phoenix(self, phoenix_name, material_name="Rogers RO4003C (lossy)", xy_center=[0, 0], outetR=10, innerR=0,
                      zRange=[0, 10], axis="z", number="6",
                      component="component1"):
        creat_cylinderCommand = f'''With Cylinder 
             .Reset 
             .Name "{phoenix_name}" 
             .Component "{component}" 
             .Material "{material_name}" 
             .OuterRadius "{outetR}" 
             .InnerRadius "{innerR}" 
             .Axis "{axis}" 
             .Zrange "{zRange[0]}", "{zRange[1]}" 
             .Xcenter "{xy_center[0]}" 
             .Ycenter "{xy_center[1]}" 
             .Segments "{number}" 
             .Create 
        End With 
        '''
        self.modeler.add_to_history(f"draw a cylinder-{phoenix_name}", creat_cylinderCommand)
        return phoenix_name

    # 画一个三角形
    def creat_triangle(self, triangle_name, material_name="PEC", xy_center=[0, 0], outetR=1, innerR=0, zRange=[0, 10],
                       axis="z",
                       component="component1"):
        creat_cylinderCommand = f'''With Cylinder 
             .Reset 
             .Name "{triangle_name}" 
             .Component "{component}" 
             .Material "{material_name}" 
             .OuterRadius "{outetR}" 
             .InnerRadius "{innerR}" 
             .Axis "{axis}" 
             .Zrange "{zRange[0]}", "{zRange[0]}" 
             .Xcenter "{xy_center[0]}" 
             .Ycenter "{xy_center[1]}" 
             .Segments "3" 
             .Create 
        End With 
        '''
        self.modeler.add_to_history(f"draw a cylinder-{triangle_name}", creat_cylinderCommand)
        return triangle_name

    # ******************画线平面结构************************
    # 1. 建立平面多边形折线，xyzs是一个n*2的列表
    def create_curve_polygon(self, polygon_name, curve_name, curve_xyzs):
        temp = f'\t.Point "{curve_xyzs[0][0]}", "{curve_xyzs[0][1]}"\n'
        for xyz in curve_xyzs[1:]:
            temp += f'\t.LineTo "{xyz[0]}", "{xyz[1]}"\n'
        create_polygon_curve_command = f'''With Polygon 
            .Reset 
            .Name "{polygon_name}" 
            .Curve "{curve_name}" 
            {temp}\t.Create 
        End With'''
        self.modeler.add_to_history(f"define curve polygon: {curve_name}:{polygon_name}", create_polygon_curve_command)

    # 2.画二维曲线，传入xys=[[x1,y1],[x2,y2]]

    def creat_2D_line(self, line2D_name, xys, curve_name="curve1"):
        creat_2D_lineCommand = f'''With Line
             .Reset 
             .Name "{line2D_name}" 
             .Curve "{curve_name}" 
             .X1 "{xys[0][0]}" 
             .Y1 "{xys[0][1]}" 
             .X2 "{xys[1][0]}" 
             .Y2 "{xys[1][1]}" 
             .Create
        End With'''
        self.modeler.add_to_history(f"draw a 2D line: {curve_name}:{line2D_name}", creat_2D_lineCommand)
        return line2D_name

    # 3.画二维弧线

    def creat_2D_arc(self, arc2D_name, curve_name, center_xys, init_xys, angle):
        creat_2D_arcCommand = f'''With Arc
             .Reset 
             .Name "{arc2D_name}" 
             .Curve "{curve_name}" 
             .Orientation "Clockwise" 
             .XCenter "{center_xys[0]}" 
             .YCenter "{center_xys[1]}" 
             .X1 "{init_xys[0]}" 
             .Y1 "{init_xys[1]}"  
             .X2 "0.0" 
             .Y2 "0.0" 
             .Angle "{angle}"  
             .UseAngle "True" 
             .Segments "0" 
             .Create
        End With'''
        self.modeler.add_to_history(f"draw a 2D line: {curve_name}:{arc2D_name}", creat_2D_arcCommand)
        return arc2D_name

    # ***************画空间曲线********************************
    # 1. 空间参数方程曲线，返回曲线名称
    def creat_analytical_curve(self, analytical_curve_name, lawX='t', lawY='t', lawZ='0', tRange=(),
                               curve_name="curve1"):
        creat_analytical_curveCommand = f'''With AnalyticalCurve
             .Reset 
             .Name "{analytical_curve_name}" 
             .Curve "{curve_name}" 
             .LawX "{lawX}" 
             .LawY "{lawY}" 
             .LawZ "{lawZ}" 
             .ParameterRange "{tRange[0]}", "{tRange[1]}" 
             .Create
        End With'''
        self.modeler.add_to_history(f"draw a analytical curve:{curve_name}:{analytical_curve_name}",
                                    creat_analytical_curveCommand)
        return analytical_curve_name

    # 2. 三维多段线 # 输入xyzs=[[x1 y1 z1],[x2 y2 z2],[x3 y3 z3]]
    def creat_3D_polygon(self, polygon3D_name, xyzs, curve_name="curve1"):
        str = ''''''

        for i in range(len(xyzs)):
            str += '''.Point "%s", "%s", "%s"\n''' % (xyzs[i][0], xyzs[i][1], xyzs[i][2])

        creat_3DpolygonCommand = f'''With Polygon3D 
             .Reset
             .Version 10 
             .Name "{polygon3D_name}"
             .Curve "{curve_name}"
             ''' + str + '''.Create
        End With'''
        self.modeler.add_to_history(f"draw a 3D polygon:{curve_name}:{polygon3D_name}", creat_3DpolygonCommand)
        return polygon3D_name

    # **************布尔操作**********************
    # 布尔加操作：added_name为母体，add_names为其他要与之加和的个体
    def boolean_add(self, added_name, add_names, component="component1"):
        for add_name in add_names:
            self.modeler.add_to_history(f"boolean_add {added_name} and {add_name}", \
                                        f'Solid.Add "{component}:{added_name}", "{component}:{add_name}"')

    # 布尔减操作: subtracted_name为母体，subtract_names为其他要与之相减的个体
    def boolean_subtract(self, subtracted_name, subtract_names, component="component1"):
        for subtract_name in subtract_names:
            self.modeler.add_to_history(f"boolean_subtract {subtracted_name} and {subtract_name}", \
                                        f'Solid.Subtract "{component}:{subtracted_name}", "{component}:{subtract_name}"')

    # 布尔插入操作：inserted_name为母体，insert_names为其他从中掏出去但是不删除掉的个体
    def boolean_insert(self, inserted_name, insert_names, component="component1"):
        for insert_name in insert_names:
            self.modeler.add_to_history(f"boolean_insert {inserted_name} by {insert_name}", \
                                        f'Solid.Insert "{component}:{inserted_name}", \"{component}:{insert_name}"')

    # 布尔交叉操作：
    def boolean_intersect(self, intersected_name, intersect_name, component="component1"):
        intersect_command = f'''Solid.Intersect "{component}:{intersected_name}", "{component}:{intersect_name}" '''
        self.modeler.add_to_history(f"boolean_intersect {intersected_name} by {intersect_name}", intersect_command)

    # ***************对称操作***********************
    # 平移操作 translated_name
    def translate_structure(self, translated_name, translate_xyz, enable_copy=False, enable_unite=False,
                            repetition=1, component="component1"):
        translate_command = f'''With Transform 
            .Reset 
            .Name "{component}:{translated_name}" 
            .Vector "{translate_xyz[0]}", "{translate_xyz[1]}", "{translate_xyz[2]}" 
            .UsePickedPoints "False" 
            .InvertPickedPoints "False" 
            .MultipleObjects "{enable_copy}" 
            .GroupObjects "{enable_unite}" 
            .Repetitions "{repetition}" 
            .MultipleSelection "False" 
            .Transform "Shape", "Translate" 
        End With'''
        self.modeler.add_to_history(f'transform: translate {component}:{translated_name}', translate_command)

    # 旋转操作 center为旋转中心，angle为各个坐标轴旋转角度，repetition是复制个数，enable_unite为是否合为一体。
    def rotation_structure(self, rotated_name, center=[0, 0, 0], angle=[0, 0, 0], repetition=1, enable_unite=False,
                           enable_copy=False, component='component1'):
        rotation_command = f'''With Transform 
            .Reset 
            .Name "{component}:{rotated_name}"
            .AddName "" 
            .Origin "Free" 
            .Center "{center[0]}", "{center[1]}", "{center[1]}" 
            .Angle "{angle[0]}", "{angle[1]}", "{angle[2]}" 
            .MultipleObjects "{enable_copy}" 
            .GroupObjects "{enable_unite}" 
            .Repetitions "{repetition}" 
            .MultipleSelection "False" 
            .Destination "" 
            .Material "" 
            .Transform "Shape", "Rotate" 
        End With'''
        self.modeler.add_to_history(f"rotate {rotated_name} for {repetition} times", rotation_command)

    # 旋转曲线操作 center为旋转中心，angle为各个坐标轴旋转角度，repetition是复制个数，enable_unite为是否合为一体。
    def rotation_curve(self, rotated_name, center=[0, 0, 0], angle=[0, 0, 0], repetition=1, enable_unite=False,
                           enable_copy=False, curve='curve1'):
        rotation_command = f'''With Transform 
            .Reset 
            .Name "{curve}:{rotated_name}"
            .Origin "Free" 
            .Center "{center[0]}", "{center[1]}", "{center[1]}" 
            .Angle "{angle[0]}", "{angle[1]}", "{angle[2]}" 
            .MultipleObjects "{enable_copy}" 
            .GroupObjects "{enable_unite}" 
            .Repetitions "{repetition}" 
            .MultipleSelection "False" 
            .Transform "Curve", "Rotate"
        End With'''
        self.modeler.add_to_history(f"transform curve: rotate {curve}:{rotated_name}", rotation_command)


    # 镜像操作
    def mirror_structure(self, mirrored_name, mirror_xyz, enable_copy=False, enable_unite=False,
                         component="component1"):
        mirror_commnand = f'''With Transform 
             .Reset 
             .Name "{component}:{mirrored_name}" 
             .Origin "Free" 
             .Center "0", "0", "0" 
             .PlaneNormal "{mirror_xyz[0]}", "{mirror_xyz[1]}", "{mirror_xyz[2]}" 
             .MultipleObjects "{enable_copy}" 
             .GroupObjects "{enable_unite}" 
             .Repetitions "1" 
             .MultipleSelection "False" 
             .Destination "" 
             .Material "" 
             .Transform "Shape", "Mirror" 
        End With '''
        self.modeler.add_to_history(f'transform: mirror {component}:{mirrored_name}', mirror_commnand)

    # 镜像操作曲线
    def mirror_curve(self, mirrored_name, mirror_xyz, enable_copy=False, enable_unite=False,
                         curve="curve1"):
        mirror_commnand = f'''With Transform 
             .Reset 
             .Name "{curve}:{mirrored_name}" 
             .Origin "Free" 
             .Center "0", "0", "0" 
             .PlaneNormal "{mirror_xyz[0]}", "{mirror_xyz[1]}", "{mirror_xyz[2]}" 
             .MultipleObjects "{enable_copy}" 
             .GroupObjects "{enable_unite}" 
             .Repetitions "1" 
             .MultipleSelection "False" 
             .Destination "" 
             .Transform "Curve", "Mirror" 
        End With '''
        self.modeler.add_to_history(f'transform curve: mirror {curve}:{mirrored_name}', mirror_commnand)
    # 曲线形成面或者体
    # 1.由折线覆盖成面
    def cover_profile(self, name, polygon_name, curve_name, material_name, delete_curve=True, component='component1'):
        cover_profile_command = f'''With CoverCurve
            .Reset 
            .Name "{name}" 
            .Component "{component}" 
            .Material "{material_name}" 
            .Curve "{curve_name}:{polygon_name}" 
            .DeleteCurve "{delete_curve}" 
            .Create
        End With'''
        self.modeler.add_to_history(f"define cover profile: {component}:{name}", cover_profile_command)

    # 2.拉伸封闭曲线成体
    # 注意，需要加入已有材料，拉伸的曲线为extrude_curve_name，拉成的体为solid_name
    def extrude_curve(self, solid_name, extrude_curve_name, thickness, material, curve_name="curve1",
                      component="component1"):
        extrude_curveCommand = f'''With ExtrudeCurve
              .Reset 
              .Name "{solid_name}" 
              .Component "{component}" 
              .Material "{material}" 
              .Thickness "{thickness}" 
              .Twistangle "0.0" 
              .Taperangle "0.0" 
              .DeleteProfile "True" 
              .Curve "{curve_name}:{extrude_curve_name}" 
              .Create
         End With'''
        self.modeler.add_to_history(f"extrude curve to {solid_name}", extrude_curveCommand)
        return solid_name

    # 3.由折线变成有宽度的线条
    def trace_from_curve(self, name, polygon_name, curve_name, width, thick=0, material='PEC',
                         component='component1'):
        trace_from_curve_command = f'''With TraceFromCurve 
             .Reset 
             .Name "{name}" 
             .Component "{component}" 
             .Material "{material}" 
             .Curve "{curve_name}:{polygon_name}" 
             .Thickness "{thick}" 
             .Width "{width}" 
             .RoundStart "False" 
             .RoundEnd "False" 
             .DeleteCurve "True" 
             .GapType "2" 
             .Create 
        End With'''
        self.modeler.add_to_history(f"{name} trace from curve", trace_from_curve_command)
        return name

    # 选点操作
    # 1. 选取pointOncurve_name曲线上的一个端点endpoint_name(='1'或者'2'), 返回pointnumber即存储的第几个点
    def pick_point(self, point_number, pointOncurve_name, endpoint_name, curve_name="curve1"):
        pickCommand = f'''Pick.NextPickToDatabase "{point_number}"
            Pick.PickCurveEndpointFromId "{curve_name}:{pointOncurve_name}", "{endpoint_name}"'''
        self.modeler.add_to_history(f"pick point-{point_number}", pickCommand)
        return point_number

    # 2. 获取指定点的xyz坐标(获得CST可以识别的选点的xyz坐标字符串)
    def get_pointxyz(self, pickPoint_name):
        xyz = ['xp(%s)' % (pickPoint_name), 'yp(%s)' % (pickPoint_name), 'zp(%s)' % (pickPoint_name)]
        return xyz

    # 3. 取消选点操作
    def clear_picks(self):
        clear_pickCommand = '''
        Pick.ClearAllPicks 
        '''
        self.modeler.add_to_history("clear all the picks", clear_pickCommand)

    def modify_solver(self):
        pass

    def delete_shape(self, name, component='component1'):
        self.modeler.add_to_history(f'Delete "{component}:{name}"', f'Solid.Delete "{component}:{name}"')

    def delete_model(self, component='component1'):
        del_component_command = f'''Component.Delete"{component}"'''
        self.modeler.add_to_history("delete a component", del_component_command)

    def change_para_box(self, para_box):
        self.para_box = para_box
