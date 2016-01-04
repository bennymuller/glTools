import maya.cmds as cmds
import glTools.utils.reference


def addDefaultAttrState(objList):
    """
    Add a default attribute state multi attribute that will be used to store specified attribute values which can be restored on command.
    @param objList: List of objects to add the default attribute state multi attribute to.
    @type objList: list
    """
    # Check objList
    if not objList:
        return

    # Define defaultAttrState attribute name
    defAttr = 'defaultAttrState'

    # For each object in list
    attrList = []
    for obj in objList:

        # Check Object
        if not cmds.objExists(obj):
            raise Exception('Object "' + obj + '" does not exist!')

        # Check Attr
        if not cmds.attributeQuery(defAttr, n=obj, ex=True):

            # Add attribute
            cmds.addAttr(obj, ln=defAttr, dv=-1, m=True)
            attrList.append(obj + '.' + defAttr)

        else:

            print ('Object "' + obj + '" already has a "' + defAttr + '" attribute! Skipping...')

    # Return Result
    return attrList


def setDefaultAttrState(objList, attrList, valueList=[]):
    """
    Set default attribute state values for a specified list of object attributes.
    @param objList: List of objects to store default attribute state values for.
    @type objList: list
    @param attrList: List of attributes to store default attribute state values for.
    @type attrList: list
    @param valueList: List of attributes values to assign to the default attribute states. If empty, use current object attribute values.
    @type valueList: list
    """
    # Check Object List
    if not objList: return
    if not attrList: return
    if len(attrList) != len(valueList):
        print ('Attribute and value list mis-match! Recording existing attribute values.')
        valueList = []

    # Define defaultAttrState attribute name
    defAttr = 'defaultAttrState'
    aliasSuffix = 'defaultState'

    # For each object in list
    for obj in objList:

        # Check Object
        if not cmds.objExists(obj):
            raise Exception('Object "' + obj + '" does not exist!')
        if not cmds.attributeQuery(defAttr, n=obj, ex=True):
            addDefaultAttrState([obj])

        # For each attribute in list
        for i in range(len(attrList)):

            # Get current attribute
            attr = attrList[i]
            attrAlias = attr + '_' + aliasSuffix

            # Check attribute
            if not cmds.attributeQuery(attr, n=obj, ex=True):
                raise Exception('Object "' + obj + '" has no attribute "' + attr + '"!')

            # Get attribute value
            if valueList:
                value = valueList[i]
            else:
                value = cmds.getAttr(obj + '.' + attr)

            # Add default attribute state
            if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
                try:
                    index = cmds.getAttr(obj + '.' + defAttr, s=True)
                except:
                    print('Error getting multi length from "' + obj + '.' + defAttr + '"')
                cmds.setAttr(obj + '.' + defAttr + '[' + str(index) + ']', 0)
                try:
                    cmds.aliasAttr(attrAlias, obj + '.' + defAttr + '[' + str(index) + ']')
                except:
                    print(
                    'Error setting attribute alias ("' + attrAlias + '") for node attr "' + obj + '.' + defAttr + '[' + str(
                        index) + ']"')

            # Set default attribute state
            try:
                cmds.setAttr(obj + '.' + attrAlias, value)
            except:
                print(
                'Unable to set default attr state ("' + attrAlias + '") for object "' + obj + '" to value (' + str(
                    value) + ')!')


def setToDefaultState(objList=[], attrList=[]):
    """
    Set object attributes to their recorded default state values.
    @param objList: List of objects to restore default attribute state values for. If empty, use all object with a "defaultAttrState" attribute.
    @type objList: list
    @param attrList: List of attributes to store default attribute state values for. If empty, apply all stored defaultAttrStates.
    @type attrList: list
    """
    # Define defaultAttrState attribute name
    defAttr = 'defaultAttrState'
    aliasSuffix = 'defaultState'

    # Check object list
    if not objList:
        objList = cmds.ls('*.' + defAttr, o=True)
    if not objList:
        return

    # For each object in list
    for obj in objList:

        if not cmds.attributeQuery(defAttr, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no attribute "' + defAttr + '"!')

        # Get attribute list
        attrAliasList = []
        if not attrList:
            attrAliasList = cmds.listAttr(obj + '.' + defAttr, m=True)
            attrList = [attrAlias.replace('_' + aliasSuffix, '') for attrAlias in attrAliasList]
        if not attrList:
            raise Exception('No valid attribute list supplied!')

        # For each attribute
        for attr in attrList:

            # Check attribute
            if not cmds.attributeQuery(attr, n=obj, ex=True):
                raise Exception('Object "' + obj + '" has no attribute "' + attr + '"!')

            # Get associated attribute alias
            attrAlias = attr + '_' + aliasSuffix
            if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
                raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')

            # Get default attribute state value
            attrVal = cmds.getAttr(obj + '.' + attrAlias)

            # Check attribute locked state
            isLocked = cmds.getAttr(obj + '.' + attr, l=True)
            if isLocked:
                try:
                    cmds.setAttr(obj + '.' + attr, l=False)
                except:
                    raise Exception('Unable to unlock attribute "' + obj + '.' + attr + '"!')

            # Check attribute connected state
            isConnected = bool(cmds.listConnections(obj + '.' + attr, s=True, d=False))

            # Set to recorded default attribute state
            if not isConnected: cmds.setAttr(obj + '.' + attr, attrVal)

            # Restore Lock state
            if isLocked: cmds.setAttr(obj + '.' + attr, l=True)


def setAttrValue(attr, value):
    """
    Set a specified attribute to the given value. Checks for locked and connected attribute channels.
    @param attr: The attribute to set a value for.
    @type attr: str
    @param value: The value to set the specified attribute to.
    @type value: str
    """
    # Check attribute
    if not cmds.objExists(attr):
        raise Exception('Attribute "' + attr + '" does not exist!')

    # Check attribute locked state
    isLocked = cmds.getAttr(attr, l=True)
    if isLocked:
        try:
            cmds.setAttr(attr, l=False)
        except:
            raise Exception('Unable to unlock attribute "' + attr + '"!')

    # Check attribute connected state
    isConnected = bool(cmds.listConnections(attr, s=True, d=False))

    # Set to recorded default attribute state
    if not isConnected:
        try:
            cmds.setAttr(attr, value)
        except:
            raise Exception('Unable to set attribute "' + attr + '" using value (' + str(value) + ')!')

    # Restore Lock state
    if isLocked: cmds.setAttr(attr, l=True)


def recordVisibility(objList=[]):
    """
    Record the default visibility state values for a specified list of objects.
    @param objList: List of objects to record visibility default attribute state values for. If empty, use all DAG nodes in current scene.
    @type objList: list
    """
    # Check Object List
    if not objList:
        objList = cmds.ls(dag=True)
    if not objList:
        print('No valid object list supplied for visibility state! Skipping...')
        return

    # For each object in list
    recordObjList = []
    for obj in objList:

        # Skip Referenced Nodes
        if glTools.utils.reference.isReferenced(obj): continue

        # Get visibility value
        vis = cmds.getAttr(obj + '.visibility')
        if not vis:
            # Record Visibility default attribute state
            setDefaultAttrState([obj], ['visibility'], [vis])
            # Append Record Object List
            recordObjList.append(obj)

    # Return Result
    print('Visibility attribute state recorded for - ' + str(recordObjList))


def setVisibilityState(objList=[], visibilityState=1):
    """
    Set the visibility state values for a specified list of objects.
    @param objList: List of objects to record visibility default attribute state values for. If empty, use all objects with stored visibility state values.
    @type objList: list
    @param visibilityState: Visibilty state value to apply to object list.
    @type visibilityState: int or bool
    """
    # Define attribute names
    attr = 'visibility'
    defAttr = 'defaultAttrState'
    aliasSuffix = 'defaultState'

    # Check Object List
    if not objList:
        objList = cmds.ls('*.' + attr + '_' + aliasSuffix, o=True, r=True)
    if not objList:
        print('No valid object list supplied for visibility state! Skipping...')
        return

    # For each object in list
    for obj in objList:

        # Check defaultAttrState atribute
        if not cmds.attributeQuery(defAttr, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no "' + defAttr + '" attribute!')

        # Get visibility attribute alias
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')

        # Get visibility value
        if visibilityState:
            value = cmds.getAttr(obj + '.' + attrAlias)
        else:
            value = 1

        # Set visibilty state value
        setAttrValue(obj + '.' + attr, value)


def recordDisplayOverrides(objList=[]):
    """
    Record the default display override state values for a specified list of objects.
    @param objList: List of objects to record display override default attribute state values for. If empty, use all DAG nodes in current scene.
    @type objList: list
    """
    # Check Object List
    if not objList:
        objList = cmds.ls(dag=True)
    if not objList:
        print('No valid object list supplied for display overrides state! Skipping...')
        return

    # Define display override attribute list
    attrList = ['overrideEnabled',
                'overrideDisplayType',
                'overrideLevelOfDetail',
                'overrideShading',
                'overrideVisibility',
                'overrideColor']

    # For each object in list
    recordObjList = []
    for obj in objList:

        # Skip Referenced Nodes
        if glTools.utils.reference.isReferenced(obj): continue

        # Check Override Enabled
        if cmds.getAttr(obj + '.overrideEnabled'):

            # Get Display Override Value List
            valList = []
            for attr in attrList:
                # Get Display Override Value
                val = cmds.getAttr(obj + '.' + attr)
                valList.append(val)

            # Record Display Override State Values
            setDefaultAttrState([obj], attrList, valList)

            # Append Record Object List
            recordObjList.append(obj)

    # Return Result
    print('Display override attribute states recorded for - ' + str(recordObjList))


def setDisplayOverridesState(objList=[], displayOverrideState=0):
    """
    Set the display override state values for a specified list of objects.
    @param objList: List of objects to record display override default attribute state values for. If empty, use all objects with stored visibility state values.
    @type objList: list
    @param displayOverrideState: Display override state value to apply to object list.
    @type displayOverrideState: int or bool
    """
    # Define attribute names
    defAttr = 'defaultAttrState'
    aliasSuffix = 'defaultState'
    overrideAttr = 'overrideEnabled'

    overrideAttrList = ['overrideEnabled',
                        'overrideDisplayType',
                        'overrideLevelOfDetail',
                        'overrideShading',
                        'overrideVisibility',
                        'overrideColor']

    # Check Object List
    if not objList:
        objList = cmds.ls('*.' + overrideAttr + '_' + aliasSuffix, o=True, r=True)
    if not objList:
        print('No valid object list supplied for display overrides state! Skipping...')
        return

    # For each object in list
    for obj in objList:

        # Check defaultAttrState atribute
        if not cmds.attributeQuery(defAttr, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no "' + defAttr + '" attribute!')

        # Override Enabled
        attr = 'overrideEnabled'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        attrValue = cmds.getAttr(obj + '.' + attrAlias)
        setAttrValue(obj + '.' + attr, attrValue)

        # Override Display Type
        attr = 'overrideDisplayType'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        if displayOverrideState:
            attrValue = cmds.getAttr(obj + '.' + attrAlias)
        else:
            attrValue = 0
        setAttrValue(obj + '.' + attr, attrValue)

        # Override Display Type
        attr = 'overrideLevelOfDetail'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        if displayOverrideState:
            attrValue = cmds.getAttr(obj + '.' + attrAlias)
        else:
            attrValue = 0
        setAttrValue(obj + '.' + attr, attrValue)

        # Override Shading
        attr = 'overrideShading'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        if displayOverrideState:
            attrValue = cmds.getAttr(obj + '.' + attrAlias)
        else:
            attrValue = 1
        setAttrValue(obj + '.' + attr, attrValue)

        # Override Visibility
        attr = 'overrideVisibility'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        if displayOverrideState:
            attrValue = cmds.getAttr(obj + '.' + attrAlias)
        else:
            attrValue = 1
        setAttrValue(obj + '.' + attr, attrValue)

        # Override Colour
        attr = 'overrideColor'
        attrAlias = attr + '_' + aliasSuffix
        if not cmds.attributeQuery(attrAlias, n=obj, ex=True):
            raise Exception('Object "' + obj + '" has no aliased attribute "' + attrAlias + '"!')
        attrValue = cmds.getAttr(obj + '.' + attrAlias)
        setAttrValue(obj + '.' + attr, attrValue)
