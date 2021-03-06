import maya.cmds as cmds
import maya.mel as mel
import glTools.utils.deformer
import glTools.utils.blendShape
import glTools.utils.skinCluster
import glTools.tools.generateWeights


def shapeExtract_skinCluster(baseGeo, targetGeo, skinCluster, influenceList=[], deleteHistory=True, prefix=''):
    """
    @param baseGeo: Base geometry shape
    @type baseGeo: str
    @param targetGeo: Target geometry shape
    @type targetGeo: str
    @param skinCluster: SkinCluster that provides the influence weight maps used to extract shape components
    @type skinCluster: str
    @param influenceList: List of skinCluster infuences to use for shape extraction. If empty, use all influences.
    @type influenceList: list
    @param deleteHistory: Delete blendShape history
    @type deleteHistory: bool
    @param prefix: Naming prefix
    @type prefix: str
    """
    # ---------
    # - Check -
    # ---------

    suffix = ''
    if prefix: suffix = '_' + prefix

    # Check base geo
    if not cmds.objExists(baseGeo):
        raise Exception('Base geometry "' + baseGeo + '" does not exist!')

    # Check target geo
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # Check skinCluster
    if not cmds.objExists(skinCluster):
        raise Exception('SkinCluster "' + skinCluster + '" does not exist!')

    # ---------------------------
    # - Get skinCluster details -
    # ---------------------------

    # Get geometry affected by skinCluster
    skinGeo = glTools.utils.deformer.getAffectedGeometry(skinCluster).keys()[0]

    # Get skinClusterInfluence list
    if not influenceList:
        influenceList = cmds.skinCluster(skinCluster, q=True, inf=True)

    # ------------------------------
    # - Iterate through influences -
    # ------------------------------

    returnList = []
    for inf in influenceList:

        # Print progress
        print('Extracting region: ' + inf + suffix)

        # Duplicate shape base
        dupGeo = cmds.duplicate(baseGeo)[0]

        # Create blendShape to target
        blendShape = cmds.blendShape(targetGeo, dupGeo)[0]
        cmds.setAttr(blendShape + '.' + targetGeo, 1)

        # Get skinCluster influence weights
        wt = glTools.utils.skinCluster.getInfluenceWeights(skinCluster, inf)

        # Set belndShape target weights
        glTools.utils.blendShape.setTargetWeights(blendShape, targetGeo, wt, dupGeo)

        # Delete history on duplicated geometry
        if deleteHistory: cmds.delete(dupGeo, constructionHistory=True)

        # Rename extracted target
        dupGeo = cmds.rename(dupGeo, inf + suffix)

        # Append to return list
        returnList.append(dupGeo)

    # Create shape group
    grp = cmds.group(returnList, n=prefix + '_extract_grp', w=True)

    # -----------------
    # - Return result -
    # -----------------

    return returnList


def shapeExtract_weights(baseGeo, targetGeo, weightList, deleteHistory=True, name=''):
    """
    Extract a portioin of a blendShape target based on a list of vertex weight value
    @param baseGeo: Base geometry shape
    @type baseGeo: str
    @param targetGeo: Target geometry shape
    @type targetGeo: str
    @param weightList: Weight list to apply to extracted shape blendShape weights
    @type weightList: list
    @param deleteHistory: Delete blendShape history
    @type deleteHistory: bool
    @param name: Name for extracted shape
    @type name: str
    """
    # =========
    # - Check -
    # =========

    # Check base geo
    if not cmds.objExists(baseGeo):
        raise Exception('Base geometry "' + baseGeo + '" does not exist!')

    # Check target geo
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # =================
    # - Extract Shape -
    # =================

    if not name: name = targetGeo + '_extract'

    # Determine blendShape geometry
    if cmds.objExists(name):
        blendGeo = name
        m_blendShape = cmds.blendShape(baseGeo, blendGeo)[0]
        m_blendAlias = cmds.listAttr(m_blendShape + '.w', m=True)[0]
        cmds.setAttr(m_blendShape + '.' + m_blendAlias, 1.0)
        cmds.delete(blendGeo, ch=True)
    else:
        blendGeo = cmds.duplicate(baseGeo, n=name)[0]

    # Create blendShape to target
    blendShape = cmds.blendShape(targetGeo, blendGeo)[0]
    cmds.setAttr(blendShape + '.' + targetGeo, 1)

    # Set belndShape target weights
    glTools.utils.blendShape.setTargetWeights(blendShape, targetGeo, weightList, blendGeo)

    # Delete history on duplicated geometry
    if deleteHistory: cmds.delete(blendGeo, constructionHistory=True)

    # =================
    # - Return Result -
    # =================

    return blendGeo


def splitBlendTarget(baseGeo, targetGeo, pt1, pt2, smooth=0, deleteHistory=True, name=''):
    """
    @param baseGeo: Base geometry shape
    @type baseGeo: str
    @param targetGeo: Target geometry shape
    @type targetGeo: str
    @param pt1: Start point of the split falloff
    @type pt1: str or list
    @param pt2: Start point of the split falloff
    @type pt2: str or list
    @param deleteHistory: Delete blendShape history
    @type deleteHistory: bool
    @param name: Name for extracted shapes
    @type name: str
    """
    # =========
    # - Check -
    # =========

    # Check base geo
    if not cmds.objExists(baseGeo):
        raise Exception('Base geometry "' + baseGeo + '" does not exist!')

    # Check target geo
    if not cmds.objExists(targetGeo):
        raise Exception('Target geometry "' + targetGeo + '" does not exist!')

    # ==========================
    # - Generate Split Weights -
    # ==========================

    lf_wt = glTools.tools.generateWeights.gradientWeights(baseGeo, pt1, pt2, smooth)
    rt_wt = [1.0 - i for i in lf_wt]

    # =================================
    # - Split Shape to Left and Right -
    # =================================

    lf_shape = shapeExtract_weights(baseGeo, targetGeo, lf_wt, deleteHistory, 'lf_' + name)
    rt_shape = shapeExtract_weights(baseGeo, targetGeo, rt_wt, deleteHistory, 'rt_' + name)

    # =================
    # - Return Result -
    # =================

    return [lf_shape, rt_shape]
