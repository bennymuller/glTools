import maya.cmds as cmds
import glTools.utils.base
import glTools.utils.curve
import glTools.utils.mathUtils


def build(attachments=4, sections=9, sectionsSpans=8, minRadius=0.0, maxRadius=1.0, startPt=[0.0, 0.0, 6.0],
          endPt=[0.0, 0.0, -6.0], prefix='muscle'):
    """
    Build muscle primitive based on the input argument values between the start and end points

    @param attachments: Number of attachments points
    @type attachments: int
    @param sections: Number of profile curves
    @type sections: int
    @param sectionSpans: Number of spans for profile curves
    @type sectionSpans: int
    @param minRadius: Minimum radius for muscle profile curves
    @type minRadius: float
    @param maxRadius: Maximum radius for muscle profile curves
    @type maxRadius: float
    @param startPt: Start point of the muscle
    @type startPt: list
    @param endPt: End point of the muscle
    @type endPt: list
    @param prefix: Name prefix for muscle primitive
    @type prefix: str

    @return: Muscle mesh
    @returnType: str
    """
    # Checks

    # Get start, end and distance values
    startPoint = glTools.utils.base.getMPoint(startPt)
    endPoint = glTools.utils.base.getMPoint(endPt)
    startEndOffset = endPoint - startPoint
    startEndDist = startEndOffset.length()
    startEndInc = startEndDist / (attachments - 1)

    # Calculate attachment point positions
    attachPoints = []
    for i in range(attachments):
        attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * i))
        # Start Tangent
        if not i:
            attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * 0.5))
        # End Tangent
        if i == (attachments - 2):
            attachPoints.append(startPoint + (startEndOffset.normal() * startEndInc * (i + 0.5)))
    attachPts = [[pt.x, pt.y, pt.z] for pt in attachPoints]
    # Resize attachments value to accomodate for tangent points
    attachments = len(attachPts)

    # ------------------------
    # - Build base hierarchy -
    # ------------------------

    # Create groups
    muscleGrp = cmds.createNode('transform', n=prefix + '_group')
    muscleAttachGrp = cmds.createNode('transform', n=prefix + '_attachment_group')
    muscleProfileGrp = cmds.createNode('transform', n=prefix + '_profile_group')

    # Build hierarchy
    cmds.parent(muscleAttachGrp, muscleGrp)
    cmds.parent(muscleProfileGrp, muscleGrp)

    # ----------------------
    # - Build Muscle Curve -
    # ----------------------

    # Build muscle base curve
    muscleCurve = cmds.rename(cmds.curve(d=1, p=attachPts, k=range(len(attachPts))), prefix + '_curve')
    cmds.rebuildCurve(muscleCurve, ch=0, rpo=1, rt=0, end=1, kr=0, kcp=1, kep=1, kt=1, s=0, d=1)
    muscleCurveShape = cmds.listRelatives(muscleCurve, s=True)[0]
    cmds.parent(muscleCurve, muscleAttachGrp)

    # Add muscle attributes
    cmds.addAttr(muscleCurve, ln='muscle', at='message')
    cmds.addAttr(muscleCurve, ln='muscleObjectType', dt='string')
    cmds.setAttr(muscleCurve + '.muscleObjectType', 'spline', type='string', l=True)

    # Connect curve to attachment locators
    attachLocators = glTools.utils.curve.locatorCurve(muscleCurve, locatorScale=0.1, freeze=False, prefix=prefix)
    # Rename attachment locators and add muscle attibutes
    for i in range(len(attachLocators)):
        # Add muscle attibutes
        cmds.addAttr(attachLocators[i], ln='muscle', at='message')
        cmds.addAttr(attachLocators[i], ln='muscleObjectType', dt='string')
        cmds.setAttr(attachLocators[i] + '.muscleObjectType', 'attachment', type='string', l=True)

        # Rename attachment locators
        if not i:
            attachLocators[i] = cmds.rename(attachLocators[i], prefix + '_attachStart_locator')
        elif i == 1:
            attachLocators[i] = cmds.rename(attachLocators[i], prefix + '_attachStartTangent_locator')
            cmds.setAttr(attachLocators[i] + '.muscleObjectType', l=False)
            cmds.setAttr(attachLocators[i] + '.muscleObjectType', 'attachmentTangent', type='string', l=True)
        elif i == (attachments - 2):
            attachLocators[i] = cmds.rename(attachLocators[i], prefix + '_attachEndTangent_locator')
            cmds.setAttr(attachLocators[i] + '.muscleObjectType', l=False)
            cmds.setAttr(attachLocators[i] + '.muscleObjectType', 'attachmentTangent', type='string', l=True)
        elif i == (attachments - 1):
            attachLocators[i] = cmds.rename(attachLocators[i], prefix + '_attachEnd_locator')
        else:
            attachLocators[i] = cmds.rename(attachLocators[i], prefix + '_attachMid' + str(i - 1) + '_locator')

    # Group attachment locators
    attachLocGroup = []
    [attachLocGroup.append(glTools.utils.base.group(loc)) for loc in attachLocators]
    cmds.parent(attachLocGroup, muscleAttachGrp)

    # Create spline rebuild curve
    splineCurve = cmds.rebuildCurve(muscleCurve, ch=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=5, d=3)
    splineRebuild = cmds.rename(splineCurve[1], prefix + '_spline_rebuildCurve')
    splineCurveShape = cmds.rename(cmds.listRelatives(splineCurve[0], s=True)[0], prefix + '_spline_curveShape')
    cmds.parent(splineCurveShape, muscleCurve, s=True, r=True)
    cmds.delete(splineCurve[0])

    # Create tangent rebuild curve
    tangentCurve = cmds.rebuildCurve(muscleCurve, ch=1, rpo=0, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=2, d=3)
    tangentRebuild = cmds.rename(tangentCurve[1], prefix + '_tangent_rebuildCurve')
    tangentCurveShape = cmds.rename(cmds.listRelatives(tangentCurve[0], s=True)[0], prefix + '_tangent_curveShape')
    cmds.parent(tangentCurveShape, muscleCurve, s=True, r=True)
    cmds.delete(tangentCurve[0])

    # Create curve visibility attributes
    cmds.addAttr(muscleCurve, ln='attachment', at='enum', en='Off:On:')
    cmds.setAttr(muscleCurve + '.attachment', k=False, cb=True)
    cmds.connectAttr(muscleCurve + '.attachment', muscleCurveShape + '.v')

    cmds.addAttr(muscleCurve, ln='spline', at='enum', en='Off:On:')
    cmds.setAttr(muscleCurve + '.spline', k=False, cb=True)
    cmds.connectAttr(muscleCurve + '.spline', splineCurveShape + '.v')

    cmds.addAttr(muscleCurve, ln='tangent', at='enum', en='Off:On:')
    cmds.setAttr(muscleCurve + '.tangent', k=False, cb=True)
    cmds.connectAttr(muscleCurve + '.tangent', tangentCurveShape + '.v')

    cmds.setAttr(muscleCurve + '.attachment', 0)
    cmds.setAttr(muscleCurve + '.spline', 1)
    cmds.setAttr(muscleCurve + '.tangent', 1)

    # Setup start tangent toggle
    cmds.addAttr(attachLocators[0], ln='tangentControl', at='enum', en='Off:On:')
    cmds.setAttr(attachLocators[0] + '.tangentControl', k=False, cb=True)
    cmds.connectAttr(attachLocators[0] + '.tangentControl', attachLocGroup[1] + '.v', f=True)
    startTangentBlend = cmds.createNode('blendColors', n=prefix + '_startTangent_blendColors')
    cmds.connectAttr(attachLocators[1] + '.worldPosition[0]', startTangentBlend + '.color1', f=True)
    cmds.connectAttr(attachLocators[2] + '.worldPosition[0]', startTangentBlend + '.color2', f=True)
    cmds.connectAttr(attachLocators[0] + '.tangentControl', startTangentBlend + '.blender', f=True)
    cmds.connectAttr(startTangentBlend + '.output', muscleCurve + '.controlPoints[1]', f=True)
    # Setup end tangent toggle
    cmds.addAttr(attachLocators[-1], ln='tangentControl', at='enum', en='Off:On:')
    cmds.setAttr(attachLocators[-1] + '.tangentControl', k=False, cb=True)
    cmds.connectAttr(attachLocators[-1] + '.tangentControl', attachLocGroup[-2] + '.v', f=True)
    endTangentBlend = cmds.createNode('blendColors', n=prefix + '_endTangent_blendColors')
    cmds.connectAttr(attachLocators[-2] + '.worldPosition[0]', endTangentBlend + '.color1', f=True)
    cmds.connectAttr(attachLocators[-3] + '.worldPosition[0]', endTangentBlend + '.color2', f=True)
    cmds.connectAttr(attachLocators[-1] + '.tangentControl', endTangentBlend + '.blender', f=True)
    cmds.connectAttr(endTangentBlend + '.output', muscleCurve + '.controlPoints[' + str(attachments - 2) + ']', f=True)

    # -------------------------------
    # - Build Muscle Profile Curves -
    # -------------------------------

    # Initialize profile list
    profileList = []
    profileGrpList = []
    profileFollowList = []

    # Iterate through profiles
    profileInc = 1.0 / (sections - 1)
    for i in range(sections):

        # Create profile curve
        profile = cmds.circle(ch=0, c=(0, 0, 0), nr=(0, 0, 1), sw=360, r=1, d=3, ut=0, tol=0.01, s=sectionsSpans,
                            n=prefix + '_profile' + str(i + 1) + '_curve')[0]
        profileList.append(profile)

        # Add muscle profile attribute
        cmds.addAttr(profile, ln='muscle', at='message')
        cmds.addAttr(profile, ln='muscleObjectType', dt='string')
        cmds.setAttr(profile + '.muscleObjectType', 'profile', type='string', l=True)

        # Group profile curve
        profileGrp = glTools.utils.base.group(profile)
        profileGrpList.append(profileGrp)

        # Skip start/end profiles
        if (not i) or (i == (sections - 1)): continue

        # Add curve parameter attribute
        cmds.addAttr(profile, ln='uValue', min=0.0, max=1.0, dv=profileInc * i)
        cmds.setAttr(profile + '.uValue', k=False, cb=True)

        # Create profile pointOnCurveInfo node
        profileCurveInfo = cmds.createNode('pointOnCurveInfo', n=prefix + '_profile' + str(i + 1) + '_pointOnCurveInfo')

        # Attach profile group to point on muscle spline curve
        cmds.connectAttr(splineCurveShape + '.worldSpace[0]', profileCurveInfo + '.inputCurve', f=True)
        cmds.connectAttr(profile + '.uValue', profileCurveInfo + '.parameter', f=True)
        cmds.connectAttr(profileCurveInfo + '.position', profileGrp + '.translate', f=True)

        # Create profile follow group
        profileFollowGrp = cmds.createNode('transform', n=prefix + '_profileFollow' + str(i + 1) + '_group')
        profileFollowList.append(profileFollowGrp)
        cmds.connectAttr(profileCurveInfo + '.position', profileFollowGrp + '.translate', f=True)

    cmds.parent(profileGrpList, muscleProfileGrp)
    cmds.parent(profileFollowList, muscleProfileGrp)

    # ------------------------------------
    # - Create profile orientation setup -
    # ------------------------------------

    oddProfile = sections % 2
    intProfile = int(sections * 0.5)
    midProfile = intProfile + oddProfile
    intIncrement = 1.0 / intProfile

    # Create mid profile orientConstraint
    if oddProfile:
        midPointObject = profileFollowList[midProfile - 2]
    else:
        midPointObject = cmds.createNode('transform', n=prefix + '_midPointFollow_group')
        cmds.parent(midPointObject, muscleProfileGrp)
    midOrientCon = cmds.orientConstraint([attachLocators[0], attachLocators[-1]], midPointObject,
                                       n=prefix + '_midPoint_orientConstraint')

    # Create intermediate profile orientConstraints
    for i in range(intProfile):

        # Skip start/end profiles
        if not i: continue

        # Create orientConstraints
        startMidOriCon = cmds.orientConstraint([attachLocators[0], midPointObject], profileFollowList[i - 1])[0]
        endMidOriCon = cmds.orientConstraint([attachLocators[-1], midPointObject], profileFollowList[-(i)])[0]
        startMidOriWt = cmds.orientConstraint(startMidOriCon, q=True, weightAliasList=True)
        endMidOriWt = cmds.orientConstraint(endMidOriCon, q=True, weightAliasList=True)

        # Set constraint weights
        cmds.setAttr(startMidOriCon + '.' + startMidOriWt[0], 1.0 - (intIncrement * i))
        cmds.setAttr(startMidOriCon + '.' + startMidOriWt[1], (intIncrement * i))
        cmds.setAttr(endMidOriCon + '.' + endMidOriWt[0], 1.0 - (intIncrement * i))
        cmds.setAttr(endMidOriCon + '.' + endMidOriWt[1], (intIncrement * i))

        # Add constraint weight attribute to profile
        cmds.addAttr(profileList[i], ln='twist', min=0, max=1, dv=1.0 - (intIncrement * i), k=True)
        cmds.addAttr(profileList[-(i + 1)], ln='twist', min=0, max=1, dv=1.0 - (intIncrement * i), k=True)

        # Connect twist attribite to constraint weights
        startMidOriRev = cmds.createNode('reverse', n=profileList[i].replace('_curve', '_reverse'))
        endMidOriRev = cmds.createNode('reverse', n=profileList[-(i + 1)].replace('_curve', '_reverse'))
        cmds.connectAttr(profileList[i] + '.twist', startMidOriRev + '.inputX', f=True)
        cmds.connectAttr(profileList[i] + '.twist', startMidOriCon + '.' + startMidOriWt[0], f=True)
        cmds.connectAttr(startMidOriRev + '.outputX', startMidOriCon + '.' + startMidOriWt[1], f=True)
        cmds.connectAttr(profileList[-(i + 1)] + '.twist', endMidOriRev + '.inputX', f=True)
        cmds.connectAttr(profileList[-(i + 1)] + '.twist', endMidOriCon + '.' + endMidOriWt[0], f=True)
        cmds.connectAttr(endMidOriRev + '.outputX', endMidOriCon + '.' + endMidOriWt[1], f=True)

    # Create Profile tangent constraints
    tangentConList = []
    for i in range(len(profileGrpList)):
        # Determine world up object
        if not i:
            # start profile
            worldUpObject = attachLocators[0]
        elif i == (len(profileGrpList) - 1):
            # end profile
            worldUpObject = attachLocators[-1]
        else:
            worldUpObject = profileFollowList[i - 1]
        # Create constraint
        tangentCon = cmds.tangentConstraint(tangentCurveShape, profileGrpList[i], aim=[0, 0, -1], u=[0, 1, 0],
                                          wu=[0, 1, 0], wut='objectrotation', wuo=worldUpObject)
        tangentConList.append(tangentCon)

    # -----------------------------
    # - Set profile radius values -
    # -----------------------------

    # Set default profile radius values
    radiusList = glTools.utils.mathUtils.distributeValue(midProfile, rangeStart=minRadius, rangeEnd=maxRadius)
    radiusList = [glTools.utils.mathUtils.smoothStep(i, minRadius, maxRadius, 0.5) for i in radiusList]
    for i in range(midProfile):
        cmds.setAttr(profileList[i] + '.scale', radiusList[i], radiusList[i], radiusList[i])
        cmds.setAttr(profileList[-(i + 1)] + '.scale', radiusList[i], radiusList[i], radiusList[i])

    # ----------------------------
    # - Generate Muscle Geometry -
    # ----------------------------

    # Loft mesh between profile curves
    loft = cmds.loft(profileList, u=0, c=0, d=3, ch=1, po=1)
    muscleMesh = cmds.rename(loft[0], prefix)
    muscleLoft = cmds.rename(loft[1], prefix + '_loft')
    muscleTess = cmds.listConnections(muscleLoft + '.outputSurface', s=False, d=True, type='nurbsTessellate')[0]
    muscleTess = cmds.rename(muscleTess, prefix + '_nurbsTessellate')
    cmds.parent(muscleMesh, muscleGrp)

    # Set nurbsTessellate settings
    cmds.setAttr(muscleTess + '.format', 2)
    cmds.setAttr(muscleTess + '.polygonType', 1)
    cmds.setAttr(muscleTess + '.uType', 1)
    cmds.setAttr(muscleTess + '.vType', 1)
    cmds.setAttr(muscleTess + '.uNumber', 20)
    cmds.setAttr(muscleTess + '.vNumber', 10)

    # Add muscle mesh attributes
    cmds.addAttr(muscleMesh, ln='precision', at='long', min=1, dv=5)
    cmds.setAttr(muscleMesh + '.precision', k=False, cb=True)
    cmds.addAttr(muscleMesh, ln='tangentPrecision', at='long', min=1, dv=2)
    cmds.setAttr(muscleMesh + '.tangentPrecision', k=False, cb=True)

    cmds.addAttr(muscleMesh, ln='uDivisions', at='long', min=4, dv=20)
    cmds.setAttr(muscleMesh + '.uDivisions', k=False, cb=True)
    cmds.addAttr(muscleMesh, ln='vDivisions', at='long', min=3, dv=10)
    cmds.setAttr(muscleMesh + '.vDivisions', k=False, cb=True)

    cmds.addAttr(muscleMesh, ln='restLength', at='float', min=0, dv=startEndDist)
    cmds.setAttr(muscleMesh + '.restLength', k=False, cb=True)
    cmds.addAttr(muscleMesh, ln='currentLength', at='float', min=0, dv=startEndDist)
    cmds.setAttr(muscleMesh + '.currentLength', k=True)
    cmds.addAttr(muscleMesh, ln='lengthScale', at='float', min=0, dv=1)
    cmds.setAttr(muscleMesh + '.lengthScale', k=True)

    cmds.addAttr(muscleMesh, ln='muscleMessage', at='message')
    cmds.addAttr(muscleMesh, ln='muscleSpline', at='message')
    cmds.addAttr(muscleMesh, ln='attachment', at='message', m=True)
    cmds.addAttr(muscleMesh, ln='profile', at='message', m=True)

    cmds.addAttr(muscleMesh, ln='muscleObjectType', dt='string')
    cmds.setAttr(muscleMesh + '.muscleObjectType', 'geo', type='string', l=True)

    # Connect muscle mesh attributes
    cmds.connectAttr(muscleCurve + '.message', muscleMesh + '.muscleSpline', f=True)
    for i in range(len(attachLocators)):
        cmds.connectAttr(attachLocators[i] + '.message', muscleMesh + '.attachment[' + str(i) + ']', f=True)
        cmds.connectAttr(muscleMesh + '.message', attachLocators[i] + '.muscle', f=True)
    for i in range(len(profileList)):
        cmds.connectAttr(profileList[i] + '.message', muscleMesh + '.profile[' + str(i) + ']', f=True)
        cmds.connectAttr(muscleMesh + '.message', profileList[i] + '.muscle', f=True)

    # Connect muscle mesh attributes to curve rebuild settings
    cmds.connectAttr(muscleMesh + '.precision', splineRebuild + '.spans', f=True)
    musclePreCondition = cmds.createNode('condition', n=prefix + '_precision_condition')
    cmds.setAttr(musclePreCondition + '.operation', 4)  # Less Than
    cmds.connectAttr(muscleMesh + '.precision', musclePreCondition + '.firstTerm', f=True)
    cmds.connectAttr(muscleMesh + '.tangentPrecision', musclePreCondition + '.secondTerm', f=True)
    cmds.connectAttr(muscleMesh + '.precision', musclePreCondition + '.colorIfTrueR', f=True)
    cmds.connectAttr(muscleMesh + '.tangentPrecision', musclePreCondition + '.colorIfFalseR', f=True)
    cmds.connectAttr(musclePreCondition + '.outColorR', tangentRebuild + '.spans', f=True)

    # Connect musle mesh attributes to nurbsTessellate settings
    cmds.connectAttr(muscleMesh + '.uDivisions', muscleTess + '.uNumber', f=True)
    cmds.connectAttr(muscleMesh + '.vDivisions', muscleTess + '.vNumber', f=True)

    # Setup length calculation
    muscleLenCurveInfo = cmds.createNode('curveInfo', n=prefix + '_length_curveInfo')
    cmds.connectAttr(splineCurveShape + '.worldSpace[0]', muscleLenCurveInfo + '.inputCurve', f=True)
    cmds.connectAttr(muscleLenCurveInfo + '.arcLength', muscleMesh + '.currentLength', f=True)
    muscleLenDiv = cmds.createNode('multiplyDivide', n=prefix + '_length_multiplyDivide')
    cmds.setAttr(muscleLenDiv + '.operation', 2)  # Divide
    cmds.setAttr(muscleLenDiv + '.input1', 1, 1, 1)
    cmds.setAttr(muscleLenDiv + '.input2', 1, 1, 1)
    cmds.connectAttr(muscleLenCurveInfo + '.arcLength', muscleLenDiv + '.input1X', f=True)
    cmds.connectAttr(muscleMesh + '.restLength', muscleLenDiv + '.input2X', f=True)
    cmds.connectAttr(muscleLenDiv + '.outputX', muscleMesh + '.lengthScale', f=True)

    # -----------
    # - Cleanup -
    # -----------

    # Parent start/end tangent locators
    cmds.parent(attachLocGroup[1], attachLocators[0])
    cmds.parent(attachLocGroup[-2], attachLocators[-1])

    # Parent start/end profiles
    cmds.parent(profileGrpList[0], attachLocators[0])
    cmds.setAttr(profileGrpList[0] + '.t', 0.0, 0.0, 0.0)
    cmds.setAttr(profileGrpList[0] + '.r', 0.0, 0.0, 0.0)
    cmds.setAttr(profileGrpList[0] + '.s', 1.0, 1.0, 1.0)

    cmds.parent(profileGrpList[-1], attachLocators[-1])
    cmds.setAttr(profileGrpList[-1] + '.t', 0.0, 0.0, 0.0)
    cmds.setAttr(profileGrpList[-1] + '.r', 0.0, 0.0, 0.0)
    cmds.setAttr(profileGrpList[-1] + '.s', 1.0, 1.0, 1.0)

    # Setup start/end profile scale compensation
    attachStartScaleCompNode = cmds.createNode('multiplyDivide', n=prefix + '_attachStart_multiplyDivide')
    cmds.setAttr(attachStartScaleCompNode + '.input1', 1, 1, 1)
    cmds.setAttr(attachStartScaleCompNode + '.operation', 2)
    cmds.connectAttr(attachLocators[0] + '.scale', attachStartScaleCompNode + '.input2', f=True)
    cmds.connectAttr(attachStartScaleCompNode + '.output', profileGrpList[0] + '.scale', f=True)
    attachEndScaleCompNode = cmds.createNode('multiplyDivide', n=prefix + '_attachEnd_multiplyDivide')
    cmds.setAttr(attachEndScaleCompNode + '.input1', 1, 1, 1)
    cmds.setAttr(attachEndScaleCompNode + '.operation', 2)
    cmds.connectAttr(attachLocators[-1] + '.scale', attachEndScaleCompNode + '.input2', f=True)
    cmds.connectAttr(attachEndScaleCompNode + '.output', profileGrpList[-1] + '.scale', f=True)

    # Lock transforms
    cmds.setAttr(muscleGrp + '.inheritsTransform', 0)
    cmds.setAttr(muscleGrp + '.t', l=True, cb=True)
    cmds.setAttr(muscleGrp + '.r', l=True, cb=True)
    cmds.setAttr(muscleGrp + '.s', l=True, cb=True)

    # Return result
    return muscleMesh


def isMuscle(muscle):
    """
    Check if input object (muscle) is a valid muscle object
    @param muscle: Object to query
    @type muscle: str
    """
    # Check obect exists
    if not cmds.objExists(muscle):
        print('Object "' + muscle + '" does not exis!')
        return False

    # Check muscle message attribute
    if not cmds.objExists(muscle + '.muscleMessage'):
        print('Object "' + muscle + '" is not a valid muscle!')
        return False

    # Return result
    return True


def getMuscleObjectType(muscleObject):
    """
    Get muscle object type of the specified muscleObject
    @param muscleObject: Muscle object to query
    @type muscleObject: str
    """
    # Check muscleObject exists
    if not cmds.objExists(muscleObject):
        raise Exception('Muscle object "' + muscleObject + '" does not exist!')

    # Check muscleObjectType attribute
    if not cmds.objExists(muscleObject + '.muscleObjectType'):
        raise Exception('Object "' + muscleObject + '" is not connected to a valid muscle!')

    # Get muscle object type
    muscleObjType = cmds.getAttr(muscleObject + '.muscleObjectType')

    # Return result
    return muscleObjType


def getMuscle(muscleObject):
    """
    Get muscle connected to the specified muscleObject
    @param muscleObject: Muscle object to query
    @type muscleObject: str
    """
    # Get muscle object type
    muscleObjType = getMuscleObjectType(muscleObject)

    # Get muscle
    muscle = ''
    if muscleObjType == 'geo':
        muscle = muscleObject
    elif (muscleObjType == 'profile') or (muscleObjType == 'attachment') or (muscleObjType == 'spline'):
        muscleConn = cmds.listConnections(muscleObject + '.muscle', s=True, d=False)
        if not muscleConn:
            raise Exception('Unable to determine muscle connection from muscleObject "' + muscleObject + '"!')
        muscle = muscleConn[0]
    elif (muscleObjType == 'attachmentTangent'):
        muscleObjParent = cmds.listRelatives(muscleObject, p=True)[0]
        muscleConn = cmds.listConnections(muscleObjParent + '.muscle', s=True, d=False)
        if not muscleConn:
            raise Exception('Unable to determine muscle connection from muscleObject "' + muscleObject + '"!')
        muscle = muscleConn[0]
    else:
        raise Exception('Invalid muscleObjectType value: "' + muscleObjType + '"!')

    # Return result
    return muscle


def getAttachments(muscleObject):
    """
    Get muscle attachments associated with the specified muscleObject
    @param muscleObject: Muscle object to query
    @type muscleObject: str
    """
    # Get muscle
    muscle = getMuscle(muscleObject)

    # Get attachments
    attachments = cmds.listConnections(muscle + '.attachment', s=True, d=False)
    if not attachments:
        raise Exception('No valid muscle attachments associated with muscleObject "' + muscleObject + '"!')

    # Return result
    return attachments


def getProfiles(muscleObject):
    """
    Get muscle profile curves associated with the specified muscleObject
    @param muscleObject: Muscle object to query
    @type muscleObject: str
    """
    # Get muscle
    muscle = getMuscle(muscleObject)

    # Get profile curves
    profiles = cmds.listConnections(muscle + '.profile', s=True, d=False)
    if not profiles:
        raise Exception('No valid muscle profiles associated with muscleObject "' + muscleObject + '"!')

    # Return result
    return profiles


def getSpline(muscleObject):
    """
    Get muscle spline associated with the specified muscleObject
    @param muscleObject: Muscle object to query
    @type muscleObject: str
    """
    # Get muscle
    muscle = getMuscle(muscleObject)

    # Get profile curves
    spline = cmds.listConnections(muscle + '.muscleSpline', s=True, d=False)
    if not spline:
        raise Exception('No valid muscle spline associated with muscleObject "' + muscleObject + '"!')

    # Return result
    return spline[0]


def setRestLength(muscle):
    """
    Set muscle rest length to be equal to the current muscle length.
    @param muscle: Muscle set rest length for
    @type muscle: str
    """
    # Check muscle
    if not isMuscle(muscle):
        raise Exception('Object "' + muscle + '" is not a valid muscle!')
    # Get current length
    length = cmds.getAttr(muscle + '.currentLength')
    # Set rest length
    cmds.setAttr(muscle + '.restLength', length)


def insertProfile(muscle, uValue):
    """
    """
    pass


def deleteProfile(profile):
    """
    """
    pass
