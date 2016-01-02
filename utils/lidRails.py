import maya.cmds as cmds
import gLib.common.namingConvention
import gLib.rig.utilities.curve
import gLib.rig.utilities.surface


class UserInputError(Exception): pass


def lidSurface_create(curveList, spans=4, attributeObject='', collisionObject='', side='', prefix=''):
    """
    Generate a lidSurface setup from the specified curve list and input parameters
    @param curveList: List of curves to generate the lidSurface from
    @type curveList: list
    @param spans: Number of verticle spans form each lid surface
    @type spans: int
    @param attributeObject: Object that will hold attributes form manipulating the lidSurface node
    @type attributeObject: str
    @param collisionObject: Nurbs surface object that will be used as a collision object for the lid surfaces
    @type collisionObject: str
    @param side: The side of the face the eyelid is on. ("lf" or "rt")
    @type side: str
    @param prefix: Name prefix for all created nodes
    @type prefix: str
    """

    # NameUtil
    nameUtil = gLib.common.namingConvention.NamingConvention()
    # Check prefix
    if not prefix: prefix = nameUtil.stripSuffix(crvList[0], '_')
    # Check side
    if not side: side = prefix.split('_')[0]

    # Check curveList
    for crv in curveList:
        if not cmds.objExists(crv):
            raise UserInputError('Curve "' + crv + '" does not exist!')
        if not gLib.rig.utilities.curve.isCurve(crv):
            raise UserInputError('Object "' + crv + '" is not a valid nurbs curve!')

    # Create lidSurface node
    lidSurface = nameUtil.appendName(prefix, nameUtil.node['lidSurface'])
    lidSurface = cmds.createNode('lidSurface', n=lidSurface)

    # Set spans
    cmds.setAttr(lidSurface + '.spans', spans)

    # Connect curevList
    for i in range(len(curveList)):
        cmds.connectAttr(curveList[i] + '.worldSpace', lidSurface + '.inputCurve[' + str(i) + ']', f=True)

    # Check Attribute Object
    if cmds.objExists(attributeObject):
        # Check attributes
        if not cmds.objExists(attributeObject + '.' + side + 'TopLid'):
            cmds.addAttr(attributeObject, ln=side + 'TopLid', min=-1, max=1, dv=0, k=True)
        if not cmds.objExists(attributeObject + '.' + side + 'LowLid'):
            cmds.addAttr(attributeObject, ln=side + 'LowLid', min=-1, max=1, dv=0, k=True)
        if not cmds.objExists(attributeObject + '.' + side + 'LidMeet'):
            cmds.addAttr(attributeObject, ln=side + 'LidMeet', min=0, max=1, dv=0.5, k=True)
        # Connect Attributes
        cmds.connectAttr(attributeObject + '.' + side + 'TopLid', lidSurface + '.top', f=True)
        cmds.connectAttr(attributeObject + '.' + side + 'LowLid', lidSurface + '.bottom', f=True)
        cmds.connectAttr(attributeObject + '.' + side + 'LidMeet', lidSurface + '.split', f=True)

    # Check Collision Object
    if cmds.objExists(collisionObject):
        if not gLib.rig.utilities.surface.isSurface(collisionObject):
            raise UserInputError('Collision object "' + crv + '" is not a valid nurbs surface!')
        # cmds.connectAttr(collisionObject+'.worldMatrix[0]',lidSurface+'.collisionMatrix',f=True)
        cmds.connectAttr(collisionObject + '.worldSpace', lidSurface + '.collisionGeometry', f=True)

    # Create lid surfaces
    topLid_srf = nameUtil.appendName(prefix + '_tp01', nameUtil.node['surface'])
    topLid_srf = cmds.nurbsPlane(ch=0, n=topLid_srf)[0]
    lowLid_srf = nameUtil.appendName(prefix + '_lw01', nameUtil.node['surface'])
    lowLid_srf = cmds.nurbsPlane(ch=0, n=lowLid_srf)[0]

    # Attach lid surfaces
    cmds.connectAttr(lidSurface + '.topLidSurface', topLid_srf + '.create', f=True)
    cmds.connectAttr(lidSurface + '.lowLidSurface', lowLid_srf + '.create', f=True)

    # Return result
    return (topLid_srf, lowLid_srf)


def setup_threeCtrl(lf_lidrails, rt_lidrails):
    """
    Attach the lidRails/lidSurface node to a predefined (3) control template
    @param lf_lidrails: The lidRails/lidSurafce node controlling the left eyelids.
    @type lf_lidrails: str
    @param rt_lidrails: The lidRails/lidSurafce node controlling the right eyelids.
    @type rt_lidrails: str
    """
    # Declare control variables
    lf_up = ['lf_lid01_tp01_ccc', 'lf_lid01_tp02_ccc', 'lf_lid01_tp03_ccc']
    lf_dn = ['lf_lid01_dn01_ccc', 'lf_lid01_dn02_ccc', 'lf_lid01_dn03_ccc']
    rt_up = ['rt_lid01_tp01_ccc', 'rt_lid01_tp02_ccc', 'rt_lid01_tp03_ccc']
    rt_dn = ['rt_lid01_dn01_ccc', 'rt_lid01_dn02_ccc', 'rt_lid01_dn03_ccc']

    # Connect lidRails ramps to lid profile controls

    # ========
    # lf_up

    # inner
    cmds.connectAttr(lf_up[0] + '.tx', lf_lidrails + '.offsettop[0].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[0] + '.ty', lf_lidrails + '.offsettop[0].offsettop_FloatValue', f=True)
    # mid
    lf_lid01_um01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_um01_adn')
    cmds.connectAttr(lf_up[1] + '.tx', lf_lid01_um01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_um01_adn + '.input2', 0.5)
    cmds.connectAttr(lf_lid01_um01_adn + '.output', lf_lidrails + '.offsettop[1].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[1] + '.ty', lf_lidrails + '.offsettop[1].offsettop_FloatValue', f=True)
    # outer
    lf_lid01_uo01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_uo01_adn')
    cmds.connectAttr(lf_up[2] + '.tx', lf_lid01_uo01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_uo01_adn + '.input2', 1.0)
    cmds.connectAttr(lf_lid01_uo01_adn + '.output', lf_lidrails + '.offsettop[2].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[2] + '.ty', lf_lidrails + '.offsettop[2].offsettop_FloatValue', f=True)

    # ========
    # lf_dn

    # Reverse node
    lf_dn_rvn = cmds.createNode('reverse', n='lf_lid01_dn01_rv')
    # inner
    cmds.connectAttr(lf_dn[0] + '.tx', lf_lidrails + '.offsetbottom[0].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[0] + '.ty', lf_dn_rvn + '.inputX', f=True)
    cmds.connectAttr(lf_dn_rvn + '.outputX', lf_lidrails + '.offsetbottom[0].offsetbottom_FloatValue', f=True)
    # mid
    lf_lid01_dm01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_dm01_adn')
    cmds.connectAttr(lf_dn[1] + '.tx', lf_lid01_dm01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_dm01_adn + '.input2', 0.5)
    cmds.connectAttr(lf_lid01_dm01_adn + '.output', lf_lidrails + '.offsetbottom[1].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[1] + '.ty', lf_dn_rvn + '.inputY', f=True)
    cmds.connectAttr(lf_dn_rvn + '.outputY', lf_lidrails + '.offsetbottom[1].offsetbottom_FloatValue', f=True)
    # outer
    lf_lid01_do01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_do01_adn')
    cmds.connectAttr(lf_dn[2] + '.tx', lf_lid01_do01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_do01_adn + '.input2', 1.0)
    cmds.connectAttr(lf_lid01_do01_adn + '.output', lf_lidrails + '.offsetbottom[2].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[2] + '.ty', lf_dn_rvn + '.inputZ', f=True)
    cmds.connectAttr(lf_dn_rvn + '.outputZ', lf_lidrails + '.offsetbottom[2].offsetbottom_FloatValue', f=True)

    # ========
    # rt_up

    # inner
    rt_lid01_ui01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_ui01_asn')
    cmds.setAttr(rt_lid01_ui01_asn + '.input1D[0]', 1.0)
    cmds.connectAttr(rt_up[0] + '.tx', rt_lid01_ui01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_ui01_asn + '.output1D', rt_lidrails + '.offsettop[2].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[0] + '.ty', rt_lidrails + '.offsettop[2].offsettop_FloatValue', f=True)
    # mid
    rt_lid01_um01_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_um01_mdn')
    rt_lid01_um01_adn = cmds.createNode('addDoubleLinear', n='rt_lid01_um01_adn')
    cmds.connectAttr(rt_up[1] + '.tx', rt_lid01_um01_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um01_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_um01_mdn + '.output', rt_lid01_um01_adn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um01_adn + '.input2', 0.5)
    cmds.connectAttr(rt_lid01_um01_adn + '.output', rt_lidrails + '.offsettop[1].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[1] + '.ty', rt_lidrails + '.offsettop[1].offsettop_FloatValue', f=True)
    # outer
    rt_lid01_uo_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_uo_mdn')
    cmds.connectAttr(rt_up[2] + '.tx', rt_lid01_uo_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_uo_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_uo_mdn + '.output', rt_lidrails + '.offsettop[0].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[2] + '.ty', rt_lidrails + '.offsettop[0].offsettop_FloatValue', f=True)

    # ========
    # rt_dn

    # Reverse node
    rt_dn_rvn = cmds.createNode('reverse', n='rt_lid01_dn01_rv')
    # inner
    rt_lid01_di01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_di01_asn')
    cmds.setAttr(rt_lid01_di01_asn + '.operation', 2)
    cmds.setAttr(rt_lid01_di01_asn + '.input1D[0]', 1.0)
    cmds.connectAttr(rt_dn[0] + '.tx', rt_lid01_di01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_di01_asn + '.output1D', rt_lidrails + '.offsetbottom[0].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[0] + '.ty', rt_dn_rvn + '.inputX', f=True)
    cmds.connectAttr(rt_dn_rvn + '.outputX', rt_lidrails + '.offsetbottom[0].offsetbottom_FloatValue', f=True)
    # mid
    rt_lid01_dm01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_dm01_asn')
    cmds.setAttr(rt_lid01_dm01_asn + '.operation', 2)
    cmds.setAttr(rt_lid01_dm01_asn + '.input1D[0]', 0.5)
    cmds.connectAttr(rt_dn[1] + '.tx', rt_lid01_dm01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_dm01_asn + '.output1D', rt_lidrails + '.offsetbottom[1].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[1] + '.ty', rt_dn_rvn + '.inputY', f=True)
    cmds.connectAttr(rt_dn_rvn + '.outputY', rt_lidrails + '.offsetbottom[1].offsetbottom_FloatValue', f=True)
    # outer
    rt_lid01_do01_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_do01_mdn')
    cmds.connectAttr(rt_dn[2] + '.tx', rt_lid01_do01_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_do01_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_do01_mdn + '.output', rt_lidrails + '.offsetbottom[2].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[2] + '.ty', rt_dn_rvn + '.inputZ', f=True)
    cmds.connectAttr(rt_dn_rvn + '.outputZ', rt_lidrails + '.offsetbottom[2].offsetbottom_FloatValue', f=True)


def setup_fourCtrl(lf_lidrails, rt_lidrails):
    """
    Attach the lidRails/lidSurface node to a predefined (4) control template
    @param lf_lidrails: The lidRails/lidSurafce node controlling the left eyelids.
    @type lf_lidrails: str
    @param rt_lidrails: The lidRails/lidSurafce node controlling the right eyelids.
    @type rt_lidrails: str
    """
    # Declare control variables
    lf_up = ['lf_lid01_tp01_ccc', 'lf_lid01_tp02_ccc', 'lf_lid01_tp03_ccc', 'lf_lid01_tp04_ccc']
    lf_dn = ['lf_lid01_dn01_ccc', 'lf_lid01_dn02_ccc', 'lf_lid01_dn03_ccc', 'lf_lid01_dn04_ccc']
    rt_up = ['rt_lid01_tp01_ccc', 'rt_lid01_tp02_ccc', 'rt_lid01_tp03_ccc', 'rt_lid01_tp04_ccc']
    rt_dn = ['rt_lid01_dn01_ccc', 'rt_lid01_dn02_ccc', 'rt_lid01_dn03_ccc', 'rt_lid01_dn04_ccc']

    # Connect lidRails ramps to lid profile controls

    # lf_up =========

    # inner
    cmds.connectAttr(lf_up[0] + '.tx', lf_lidrails + '.offsettop[0].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[0] + '.ty', lf_lidrails + '.offsettop[0].offsettop_FloatValue', f=True)
    # mid - inner
    lf_lid01_um01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_um01_adn')
    cmds.connectAttr(lf_up[1] + '.tx', lf_lid01_um01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_um01_adn + '.input2', 0.333)
    cmds.connectAttr(lf_lid01_um01_adn + '.output', lf_lidrails + '.offsettop[1].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[1] + '.ty', lf_lidrails + '.offsettop[1].offsettop_FloatValue', f=True)
    # mid - outer
    lf_lid01_um02_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_um02_adn')
    cmds.connectAttr(lf_up[2] + '.tx', lf_lid01_um02_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_um02_adn + '.input2', 0.666)
    cmds.connectAttr(lf_lid01_um02_adn + '.output', lf_lidrails + '.offsettop[2].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[2] + '.ty', lf_lidrails + '.offsettop[2].offsettop_FloatValue', f=True)
    # outer
    lf_lid01_uo01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_uo01_adn')
    cmds.connectAttr(lf_up[3] + '.tx', lf_lid01_uo01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_uo01_adn + '.input2', 1.0)
    cmds.connectAttr(lf_lid01_uo01_adn + '.output', lf_lidrails + '.offsettop[3].offsettop_Position', f=True)
    cmds.connectAttr(lf_up[3] + '.ty', lf_lidrails + '.offsettop[3].offsettop_FloatValue', f=True)

    # lf_dn =========

    lf_dn_rvn = cmds.createNode('reverse', n='lf_lid01_dn01_rv')
    lf_dn02_rvn = cmds.createNode('reverse', n='lf_lid01_dn02_rv')
    # inner
    cmds.connectAttr(lf_dn[0] + '.tx', lf_lidrails + '.offsetbottom[0].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[0] + '.ty', lf_dn_rvn + '.inputX', f=True)
    cmds.connectAttr(lf_dn_rvn + '.outputX', lf_lidrails + '.offsetbottom[0].offsetbottom_FloatValue', f=True)
    # mid - inner
    lf_lid01_dm01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_dm01_adn')
    cmds.connectAttr(lf_dn[1] + '.tx', lf_lid01_dm01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_dm01_adn + '.input2', 0.333)
    cmds.connectAttr(lf_lid01_dm01_adn + '.output', lf_lidrails + '.offsetbottom[1].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[1] + '.ty', lf_dn_rvn + '.inputY', f=True)
    cmds.connectAttr(lf_dn_rvn + '.outputY', lf_lidrails + '.offsetbottom[1].offsetbottom_FloatValue', f=True)
    # mid - outer
    lf_lid01_dm02_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_dm02_adn')
    cmds.connectAttr(lf_dn[2] + '.tx', lf_lid01_dm02_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_dm02_adn + '.input2', 0.666)
    cmds.connectAttr(lf_lid01_dm02_adn + '.output', lf_lidrails + '.offsetbottom[2].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[2] + '.ty', lf_dn02_rvn + '.inputX', f=True)
    cmds.connectAttr(lf_dn02_rvn + '.outputX', lf_lidrails + '.offsetbottom[2].offsetbottom_FloatValue', f=True)
    # outer
    lf_lid01_do01_adn = cmds.createNode('addDoubleLinear', n='lf_lid01_do01_adn')
    cmds.connectAttr(lf_dn[3] + '.tx', lf_lid01_do01_adn + '.input1', f=True)
    cmds.setAttr(lf_lid01_do01_adn + '.input2', 1.0)
    cmds.connectAttr(lf_lid01_do01_adn + '.output', lf_lidrails + '.offsetbottom[3].offsetbottom_Position', f=True)
    cmds.connectAttr(lf_dn[3] + '.ty', lf_dn02_rvn + '.inputY')
    cmds.connectAttr(lf_dn02_rvn + '.outputY', lf_lidrails + '.offsetbottom[3].offsetbottom_FloatValue', f=True)

    # rt_up =========

    # inner
    rt_lid01_ui01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_ui01_asn')
    cmds.setAttr(rt_lid01_ui01_asn + '.input1D[0]', 1.0)
    cmds.connectAttr(rt_up[0] + '.tx', rt_lid01_ui01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_ui01_asn + '.output1D', rt_lidrails + '.offsettop[3].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[0] + '.ty', rt_lidrails + '.offsettop[3].offsettop_FloatValue', f=True)
    # mid -inner
    rt_lid01_um01_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_um01_mdn')
    rt_lid01_um01_adn = cmds.createNode('addDoubleLinear', n='rt_lid01_um01_adn')
    cmds.connectAttr(rt_up[2] + '.tx', rt_lid01_um01_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um01_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_um01_mdn + '.output', rt_lid01_um01_adn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um01_adn + '.input2', 0.333)
    cmds.connectAttr(rt_lid01_um01_adn + '.output', rt_lidrails + '.offsettop[2].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[2] + '.ty', rt_lidrails + '.offsettop[2].offsettop_FloatValue', f=True)

    # mid - outer
    rt_lid01_um02_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_um02_mdn')
    rt_lid01_um02_adn = cmds.createNode('addDoubleLinear', n='rt_lid01_um02_adn')
    cmds.connectAttr(rt_up[1] + '.tx', rt_lid01_um02_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um02_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_um02_mdn + '.output', rt_lid01_um02_adn + '.input1', f=True)
    cmds.setAttr(rt_lid01_um02_adn + '.input2', 0.666)
    cmds.connectAttr(rt_lid01_um02_adn + '.output', rt_lidrails + '.offsettop[1].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[1] + '.ty', rt_lidrails + '.offsettop[1].offsettop_FloatValue', f=True)

    # outer
    rt_lid01_uo_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_uo_mdn')
    cmds.connectAttr(rt_up[3] + '.tx', rt_lid01_uo_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_uo_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_uo_mdn + '.output', rt_lidrails + '.offsettop[0].offsettop_Position', f=True)
    cmds.connectAttr(rt_up[3] + '.ty', rt_lidrails + '.offsettop[0].offsettop_FloatValue', f=True)

    # rt_dn =========

    rt_dn_rvn = cmds.createNode('reverse', n='rt_lid01_dn01_rv')
    rt_dn02_rvn = cmds.createNode('reverse', n='rt_lid01_dn02_rv')
    # inner
    rt_lid01_di01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_di01_asn')
    cmds.setAttr(rt_lid01_di01_asn + '.operation', 2)
    cmds.setAttr(rt_lid01_di01_asn + '.input1D[0]', 1.0)
    cmds.connectAttr(rt_dn[0] + '.tx', rt_lid01_di01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_di01_asn + '.output1D', rt_lidrails + '.offsetbottom[0].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[0] + '.ty', rt_dn_rvn + '.inputX', f=True)
    cmds.connectAttr(rt_dn_rvn + '.outputX', rt_lidrails + '.offsetbottom[0].offsetbottom_FloatValue', f=True)
    # mid - inner
    rt_lid01_dm01_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_dm01_asn')
    cmds.setAttr(rt_lid01_dm01_asn + '.operation', 2)
    cmds.setAttr(rt_lid01_dm01_asn + '.input1D[0]', 0.333)
    cmds.connectAttr(rt_dn[2] + '.tx', rt_lid01_dm01_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_dm01_asn + '.output1D', rt_lidrails + '.offsetbottom[1].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[2] + '.ty', rt_dn_rvn + '.inputY', f=True)
    cmds.connectAttr(rt_dn_rvn + '.outputY', rt_lidrails + '.offsetbottom[1].offsetbottom_FloatValue', f=True)
    # mid - outer
    rt_lid01_dm02_asn = cmds.createNode('plusMinusAverage', n='rt_lid01_dm02_asn')
    cmds.setAttr(rt_lid01_dm02_asn + '.operation', 2)
    cmds.setAttr(rt_lid01_dm02_asn + '.input1D[0]', 0.666)
    cmds.connectAttr(rt_dn[1] + '.tx', rt_lid01_dm02_asn + '.input1D[1]', f=True)
    cmds.connectAttr(rt_lid01_dm02_asn + '.output1D', rt_lidrails + '.offsetbottom[2].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[1] + '.ty', rt_dn02_rvn + '.inputX', f=True)
    cmds.connectAttr(rt_dn02_rvn + '.outputX', rt_lidrails + '.offsetbottom[2].offsetbottom_FloatValue', f=True)
    # outer
    rt_lid01_do01_mdn = cmds.createNode('multDoubleLinear', n='rt_lid01_do01_mdn')
    cmds.connectAttr(rt_dn[3] + '.tx', rt_lid01_do01_mdn + '.input1', f=True)
    cmds.setAttr(rt_lid01_do01_mdn + '.input2', -1.0)
    cmds.connectAttr(rt_lid01_do01_mdn + '.output', rt_lidrails + '.offsetbottom[3].offsetbottom_Position', f=True)
    cmds.connectAttr(rt_dn[3] + '.ty', rt_dn02_rvn + '.inputY', f=True)
    cmds.connectAttr(rt_dn02_rvn + '.outputY', rt_lidrails + '.offsetbottom[3].offsetbottom_FloatValue')
