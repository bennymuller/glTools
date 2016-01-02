import maya.cmds as cmds
import maya.mel as mel


def add(srfPtList=[],
        surface="",
        anchorType="transform",
        rotate=1,
        normalAttr=0,
        tanAttr=0,
        surfPtsNode='',
        maintainOffset=1,
        scaleAttr='',
        namePrefix=''):
    """
    """
    return_list = mel.eval('surfPts_add( ' + str(srfPtList).replace("['", '{"').replace("']", '"}').replace("'",
                                                                                                           '"') + ', "' + surface + '", "' + str(
        anchorType) + '", ' + str(rotate) + ', ' + str(normalAttr) + ', ' + str(
        tanAttr) + ', "' + surfPtsNode + '", ' + str(maintainOffset) + ', "' + scaleAttr + '", "' + namePrefix + '")')
    return return_list


def gen(surface,
        targets=[]):
    """
    """
    return_list = mel.eval(
        'surfPts_gen( "' + surface + '", ' + str(targets).replace("[u", "{").replace("[", "{").replace("]",
                                                                                                       "}").replace("'",
                                                                                                                    '"') + ')')
    return return_list
