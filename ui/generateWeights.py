import maya.cmds as cmds
import glTools.utils.deformer
import glTools.tools.generateWeights


def generateWeightsUI():
    """
    """
    win = 'generateWeightsUI'
    if cmds.window(win, ex=True): cmds.deleteUI(win)
    win = cmds.window(win, t='Generate Weights', wh=[560, 285], s=True)

    # FormLayout
    fl = cmds.formLayout(numberOfDivisions=100)

    # UI Elements
    genWt_targetAttrTFG = cmds.textFieldGrp('genWt_targetAttrTFG', label='Target Attribute')

    genWt_targetGeoTFG = cmds.textFieldButtonGrp('genWt_targetGeoTFG', l='Target Geometry', bl='Select')
    cmds.textFieldButtonGrp(genWt_targetGeoTFG, e=True, bc='glTools.ui.utils.loadObjectSel("' + genWt_targetGeoTFG + '")')

    genWt_smoothISG = cmds.intSliderGrp('genWt_smoothWeightTFG', label='Smooth', f=True, minValue=0, maxValue=5,
                                      fieldMinValue=0, fieldMaxValue=100, value=0)

    genWt_generateB = cmds.button(label='Generate Weights', c='glTools.ui.generateWeights.generateWeightsFromUI()')
    genWt_cancelB = cmds.button(label='Cancel', c='cmds.deleteUI("' + win + '")')

    # TabLayout
    genWt_tabLayout = cmds.tabLayout('genWt_tabLayout', innerMarginWidth=5, innerMarginHeight=5)

    # Layout
    cmds.formLayout(fl, e=True, af=[(genWt_targetAttrTFG, 'left', 5), (genWt_targetAttrTFG, 'top', 5),
                                  (genWt_targetAttrTFG, 'right', 5)])
    cmds.formLayout(fl, e=True, af=[(genWt_targetGeoTFG, 'left', 5), (genWt_targetGeoTFG, 'right', 5)],
                  ac=[(genWt_targetGeoTFG, 'top', 5, genWt_targetAttrTFG)])
    cmds.formLayout(fl, e=True, af=[(genWt_smoothISG, 'left', 5), (genWt_smoothISG, 'right', 5)],
                  ac=[(genWt_smoothISG, 'top', 5, genWt_targetGeoTFG)])
    cmds.formLayout(fl, e=True, af=[(genWt_tabLayout, 'left', 5), (genWt_tabLayout, 'right', 5)],
                  ac=[(genWt_tabLayout, 'top', 5, genWt_smoothISG), (genWt_tabLayout, 'bottom', 5, genWt_generateB)])
    cmds.formLayout(fl, e=True, af=[(genWt_generateB, 'left', 5), (genWt_generateB, 'bottom', 5)],
                  ap=[(genWt_generateB, 'right', 5, 50)])
    cmds.formLayout(fl, e=True, af=[(genWt_cancelB, 'right', 5), (genWt_cancelB, 'bottom', 5)],
                  ap=[(genWt_cancelB, 'left', 5, 50)])

    # ---------------------------
    # - Gradient Weights Layout -
    # ---------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    gradWt_columnLayout = cmds.columnLayout(dtg='gradient')

    # UI Elements
    gradWt_pt1TFB = cmds.textFieldButtonGrp('genWt_gradWtPt1_TFB', l='Point 1', text='', bl='Select')
    cmds.textFieldButtonGrp(gradWt_pt1TFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + gradWt_pt1TFB + '")')

    gradWt_pt2TFB = cmds.textFieldButtonGrp('genWt_gradWtPt2_TFB', l='Point 2', text='', bl='Select')
    cmds.textFieldButtonGrp(gradWt_pt2TFB, e=True, bc='glTools.ui.utils.loadObjectSel("' + gradWt_pt2TFB + '")')

    cmds.setParent('..')

    # -------------------------
    # - Radial Weights Layout -
    # -------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    radWt_columnLayout = cmds.columnLayout(dtg='radial')

    # UI Elements
    cmds.floatSliderGrp('genWt_radWtRadiusFSG', label='Radius', f=True, minValue=0.001, maxValue=10.0,
                      fieldMinValue=0.001, fieldMaxValue=1000000, value=1.0)
    cmds.floatSliderGrp('genWt_radWtInRadiusFSG', label='Inner Radius', f=True, minValue=0.0, maxValue=10.0,
                      fieldMinValue=0.0, fieldMaxValue=1000000, value=0.0)

    cmds.separator(style='single', w=1000, h=20)

    radWt_centFFG = cmds.floatFieldGrp('genWt_radWtCent_TFB', numberOfFields=3, label='Center', value1=0.0, value2=0.0,
                                     value3=0.0)
    radWt_centB = cmds.button(label='Get Point', c='glTools.ui.utils.setPointValue("' + radWt_centFFG + '")')

    cmds.setParent('..')

    # -------------------------
    # - Volume Weights Layout -
    # -------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    volWt_columnLayout = cmds.columnLayout(dtg='volume')

    # UI Elements
    genWt_volBoundaryTFB = cmds.textFieldButtonGrp('genWt_volBoundaryTFB', l='Volume Boundary', bl='Select')
    cmds.textFieldButtonGrp(genWt_volBoundaryTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_volBoundaryTFB + '")')

    genWt_volInteriorTFB = cmds.textFieldButtonGrp('genWt_volInteriorTFB', l='Volume Interior', bl='Select')
    cmds.textFieldButtonGrp(genWt_volInteriorTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_volInteriorTFB + '")')

    cmds.separator(style='single', w=1000, h=20)

    volWt_centFFG = cmds.floatFieldGrp('genWt_volWtCent_TFB', numberOfFields=3, label='Volume Center', value1=0.0,
                                     value2=0.0, value3=0.0)
    volWt_centB = cmds.button(label='Get Point', c='glTools.ui.utils.setPointValue("' + volWt_centFFG + '")')

    cmds.setParent('..')

    # ----------------------------------
    # - Geometry Volume Weights Layout -
    # ----------------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    geoVolWt_columnLayout = cmds.columnLayout(dtg='geometryVolume')

    # UI Elements
    genWt_geoBoundaryTFB = cmds.textFieldButtonGrp('genWt_geoBoundaryTFB', l='Volume Boundary', bl='Select')
    cmds.textFieldButtonGrp(genWt_geoBoundaryTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_geoBoundaryTFB + '")')

    genWt_geoInteriorTFB = cmds.textFieldButtonGrp('genWt_geoInteriorTFB', l='Volume Interior', bl='Select')
    cmds.textFieldButtonGrp(genWt_geoInteriorTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_geoInteriorTFB + '")')

    cmds.separator(style='single', w=1000, h=20)

    geoVolWt_centFFG = cmds.floatFieldGrp('genWt_geoVolWtCent_TFB', numberOfFields=3, label='Volume Center', value1=0.0,
                                        value2=0.0, value3=0.0)
    geoVolWt_centB = cmds.button(label='Get Point', c='glTools.ui.utils.setPointValue("' + volWt_centFFG + '")')

    cmds.setParent('..')

    # ----------------------------------
    # - Curve Proximity Weights Layout -
    # ----------------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    curveWt_columnLayout = cmds.columnLayout(dtg='curveProximity')

    # UI Elements
    genWt_curveWtCurveTFB = cmds.textFieldButtonGrp('genWt_curveWtCurveTFB', l='Curve', bl='Select')
    cmds.textFieldButtonGrp(genWt_curveWtCurveTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_curveWtCurveTFB + '")')

    cmds.floatSliderGrp('genWt_curveWtMinDistFSG', label='Min Distance', f=True, minValue=0.0, maxValue=10.0,
                      fieldMinValue=0.0, fieldMaxValue=1000000, value=0.0)
    cmds.floatSliderGrp('genWt_curveWtMaxDistFSG', label='Max Distance', f=True, minValue=0.001, maxValue=10.0,
                      fieldMinValue=0.001, fieldMaxValue=1000000, value=1.0)

    cmds.setParent('..')

    # ------------------------------
    # - Mesh Offset Weights Layout -
    # ------------------------------

    cmds.setParent(genWt_tabLayout)

    # Layout
    meshOffsetWt_columnLayout = cmds.columnLayout(dtg='meshOffset')

    # UI Elements
    genWt_meshOffsetBaseTFB = cmds.textFieldButtonGrp('genWt_meshOffsetBaseTFB', l='Base Mesh', bl='Select')
    cmds.textFieldButtonGrp(genWt_meshOffsetBaseTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_meshOffsetBaseTFB + '")')

    genWt_meshOffsetTargetTFB = cmds.textFieldButtonGrp('genWt_meshOffsetTargetTFB', l='Target Mesh', bl='Select')
    cmds.textFieldButtonGrp(genWt_meshOffsetTargetTFB, e=True,
                          bc='glTools.ui.utils.loadObjectSel("' + genWt_meshOffsetTargetTFB + '")')

    genWt_meshOffsetNormalizeCBG = cmds.checkBoxGrp('genWt_meshOffsetNormalizeCBG', numberOfCheckBoxes=1,
                                                  label='Normalize')
    genWt_meshOffsetNormalRayCBG = cmds.checkBoxGrp('genWt_meshOffsetNormalRayCBG', numberOfCheckBoxes=1,
                                                  label='Normal Ray Intersect')

    cmds.setParent('..')

    # --------------
    # - End Layout -
    # --------------

    # Set TabLayout Labels
    cmds.tabLayout(genWt_tabLayout, e=True, tabLabel=(
    (gradWt_columnLayout, 'Gradient'), (radWt_columnLayout, 'Radial'), (volWt_columnLayout, 'Volume'),
    (geoVolWt_columnLayout, 'Geometry Volume'), (curveWt_columnLayout, 'Curve Proximity'),
    (meshOffsetWt_columnLayout, 'Mesh Offset')))

    # Display UI
    cmds.showWindow(win)
    cmds.window(win, e=True, wh=[560, 285])


def generateWeightsFromUI():
    """
    """
    # Get source geometry
    geometry = cmds.textFieldGrp('genWt_targetGeoTFG', q=True, tx=True)

    # Get smooth value
    smoothVal = cmds.intSliderGrp('genWt_smoothWeightTFG', q=True, v=True)

    # ------------------------
    # - Get Target Attribute -
    # ------------------------

    targetAttr = cmds.textFieldGrp('genWt_targetAttrTFG', q=True, tx=True)

    # Check target attr
    if not targetAttr: raise Exception('No target attribute specified!')
    if not cmds.objExists(targetAttr): raise Exception('Attribute "' + targetAttr + '" does not exist!')

    # Determine target attribute type
    targetNode = targetAttr.split('.')[0]
    targetType = cmds.objectType(targetNode)
    # attrIsMulti = cmds.attributeQuery('')

    # --------------------
    # - Generate Weights -
    # --------------------

    wt = []

    # Determine weight generation type
    selLayout = cmds.tabLayout('genWt_tabLayout', q=True, st=True)
    layoutTag = cmds.columnLayout(selLayout, q=True, dtg=True)

    if layoutTag == 'gradient':

        # Gradient
        pnt1 = cmds.textFieldButtonGrp('genWt_gradWtPt1_TFB', q=True, tx=True)
        pnt2 = cmds.textFieldButtonGrp('genWt_gradWtPt2_TFB', q=True, tx=True)
        wt = glTools.tools.generateWeights.gradientWeights(geometry, pnt1, pnt2, smoothVal)

    elif layoutTag == 'radial':

        # Radial
        radius = cmds.floatSliderGrp('genWt_radWtRadiusFSG', q=True, v=True)
        inRadius = cmds.floatSliderGrp('genWt_radWtInRadiusFSG', q=True, v=True)
        center = (cmds.floatFieldGrp('genWt_radWtCent_TFB', q=True, v1=True),
                  cmds.floatFieldGrp('genWt_radWtCent_TFB', q=True, v2=True),
                  cmds.floatFieldGrp('genWt_radWtCent_TFB', q=True, v3=True))
        wt = glTools.tools.generateWeights.radialWeights(geometry, center, radius, inRadius, smoothVal)

    elif layoutTag == 'volume':

        # Volume
        volBoundary = cmds.textFieldButtonGrp('genWt_volBoundaryTFB', q=True, tx=True)
        volInterior = cmds.textFieldButtonGrp('genWt_volInteriorTFB', q=True, tx=True)
        volCenter = (cmds.floatFieldGrp('genWt_volWtCent_TFB', q=True, v1=True),
                     cmds.floatFieldGrp('genWt_volWtCent_TFB', q=True, v2=True),
                     cmds.floatFieldGrp('genWt_volWtCent_TFB', q=True, v3=True))
        wt = glTools.tools.generateWeights.volumeWeights(geometry, volCenter, volBoundary, volInterior, smoothVal)

    elif layoutTag == 'geometryVolume':

        # Geometry Volume
        geoBoundary = cmds.textFieldButtonGrp('genWt_geoBoundaryTFB', q=True, tx=True)
        geoInterior = cmds.textFieldButtonGrp('genWt_geoInteriorTFB', q=True, tx=True)
        geoCenter = (cmds.floatFieldGrp('genWt_geoVolWtCent_TFB', q=True, v1=True),
                     cmds.floatFieldGrp('genWt_geoVolWtCent_TFB', q=True, v2=True),
                     cmds.floatFieldGrp('genWt_geoVolWtCent_TFB', q=True, v3=True))
        wt = glTools.tools.generateWeights.geometryVolumeWeights(geometry, geoCenter, geoBoundary, geoInterior,
                                                                 smoothVal)

    elif layoutTag == 'curveProximity':

        # Curve Proximity
        proximityCurve = cmds.textFieldButtonGrp('genWt_curveWtCurveTFB', q=Tru, tx=True)
        minDist = cmds.floatSliderGrp('genWt_curveWtMinDistFSG', q=True, v=True)
        maxDist = cmds.floatSliderGrp('genWt_curveWtMaxDistFSG', q=True, v=True)
        wt = glTools.tools.generateWeights.curveProximityWeights(geometry, proximityCurve, minDist, maxDist, smoothVal)

    elif layoutTag == 'meshOffset':

        # Mesh Offset
        meshBase = cmds.textFieldButtonGrp('genWt_meshOffsetBaseTFB', q=True, tx=True)
        meshTarget = cmds.textFieldButtonGrp('genWt_meshOffsetTargetTFB', q=True, tx=True)
        normalize = cmds.checkBoxGrp('genWt_meshOffsetNormalizeCBG', q=True, v1=True)
        useNormal = cmds.checkBoxGrp('genWt_meshOffsetNormalRayCBG', q=True, v1=True)
        wt = glTools.tools.generateWeights.meshOffsetWeights(meshBase, meshTarget, normalize, useNormal, smoothVal)

    # -----------------------
    # - Set Attribute Value -
    # -----------------------
