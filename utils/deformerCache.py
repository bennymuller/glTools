import maya.cmds as cmds


def loadPlugin():
    """
    """
    # Load plugin
    plugin = 'glToolsTools'
    if not cmds.pluginInfo(plugin, q=True, l=True): cmds.loadPlugin(plugin)


def create(input, refTargetList=[], prefix=''):
    """
    """
    # Check plugin
    loadPlugin()

    # Check prefix
    if not prefix: prefix = cmds.ls(input, o=True)[0]

    # Create deformerCache node
    deformerCache = cmds.createNode('deformerCache', n=prefix + '_deformerCache')

    # Connect Input
    cmds.connectAttr(input, deformerCache + '.inGeom', f=True)

    # Find input destinations
    destPlugs = cmds.listConnections(input, s=False, d=True, p=True)
    for destPlug in destPlugs:
        cmds.connectAttr(deformerCache + '.outGeom', destPlug, f=True)

    # Connect reference targets
    for refTarget in refTargetList:
        cmds.connectAttr(deformerCache + '.refOutGeom', refTarget, f=True)

    # Return result
    return deformerCache


def changeInput(deformerCache, input):
    """
    """
    # Connect Input
    cmds.connectAttr(input, deformerCache + '.inGeom', f=True)
    C
