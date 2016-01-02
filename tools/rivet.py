import maya.cmds as cmds


def create(prefix=''):
    """
    """
    # Check prefix
    if not prefix: prefix = 'rivet'

    # Get selected polygon edges
    edges = cmds.filterExpand(sm=32)

    # Check edge selection
    if edges:

        # Check selection length
        if len(edges) != 2:
            raise Exception('Select 2 poly edges or a nurbs surface point and run again!')

        # Determine object and edge indices
        obj = cmds.ls(edges[0], o=True)
        edgeIndex1 = int(edges[0].split('.')[-1].strip('e[]'))
        edgeIndex2 = int(edges[1].split('.')[-1].strip('e[]'))

        # Create curves from poly edges
        curveEdge1 = cmds.createNode('curveFromMeshEdge', n=prefix + '_edge1_curveFromMeshEdge')
        cmds.setAttr(curveEdge1 + '.ihi', 1)
        cmds.setAttr(curveEdge1 + '.ei[0]', edgeIndex1)
        curveEdge2 = cmds.createNode('curveFromMeshEdge', n=prefix + '_edge2_curveFromMeshEdge')
        cmds.setAttr(curveEdge2 + '.ihi', 1)
        cmds.setAttr(curveEdge2 + '.ei[0]', edgeIndex2)

        # Generate loft from edge curves
        loft = cmds.createNode('loft', n=prefix + '_loft')
        cmds.setAttr(loft + '.ic', s=2)
        cmds.setAttr(loft + '.u', 1)
        cmds.setAttr(loft + '.rsn', 1)

        # Create pointOnSurfaceInfo node
        pointInfo = cmds.createNode('pointOnSurfaceInfo', n=prefix + '_pointOnSurfaceInfo')
        cmds.setAttr(pointInfo + '.turnOnPercentage', 1)
        cmds.setAttr(pointInfo + '.parameterU', 0.5)
        cmds.setAttr(pointInfo + '.parameterV', 0.5)

        # Connect nodes
        cmds.connectAttr(loft + '.os', pointInfo + '.is', f=True)
        cmds.connectAttr(curveEdge1 + '.oc', loft + '.ic[0]', f=True)
        cmds.connectAttr(curveEdge2 + '.oc', loft + '.ic[1]', f=True)
        cmds.connectAttr(obj + '.w', curveEdge1 + '.im', f=True)
        cmds.connectAttr(obj + '.w', curveEdge2 + '.im', f=True)

    else:

        # Get surface point selection
        points = cmds.filterExpand(sm=41)

        # Check point selection
        if not points:
            if len(points) > 1:
                raise Exception('Select 2 poly edges or a nurbs surface point and run again!')

            # Determine object and UV parameter
            obj = cmds.ls(edges[0], o=True)
            uv = points[0].split('.')[-1].strip('uv[]').split(',')
            u = float(uv[0])
            v = float(uv[1])

            # Create pointOnSurfaceInfo node
            pointInfo = cmds.createNode('pointOnSurfaceInfo', n=prefix + '_pointOnSurfaceInfo')
            cmds.setAttr(pointInfo + '.turnOnPercentage', 1)
            cmds.setAttr(pointInfo + '.parameterU', 0.5)
            cmds.setAttr(pointInfo + '.parameterV', 0.5)

            # Connect nodes
            cmds.connectAttr(obj + '.ws', pointInfo + '.is', f=True)

    # Create rivet locator
    loc = cmds.createNode('transform', n=prefix + '_locator')

    # Create aim constraint
    aim = cmds.createNode('aicmdsonstraint', p=loc, n=prefix + '_aicmdsonstraint')
    cmds.setAttr(aim + '.tg[0].tw', 1)
    cmds.setAttr(aim + '.a', 0, 1, 0)
    cmds.setAttr(aim + '.u', 0, 0, 1)
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'v']: cmds.setAttr(aim + '.' + attr, k=0)

    cmds.connectAttr(pointInfo + '.position', loc + '.translate', f=True)
    cmds.connectAttr(pointInfo + '.normal', aim + '.tg[0].tt', f=True)
    cmds.connectAttr(pointInfo + '.tv', aim + '.wu', f=True)

    cmds.connectAttr(aim + '.crx', loc + '.rx', f=True)
    cmds.connectAttr(aim + '.cry', loc + '.ry', f=True)
    cmds.connectAttr(aim + '.crz', loc + '.rz', f=True)

    # Return result
    return loc
