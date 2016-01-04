import maya.cmds as cmds
import maya.mel as mel


class MeshCombineUtilities(object):
    def __init__(self):
        pass

    def combine(self, objs=[], new_name="", keepHistory=0):
        """
        Combines the geometry and stores the names.
        This is useful for speeding up the rigs and seperating in a predictible way.
        @param objs: Mesh objects to combine
        @type objs: list
        @param new_name: New name for the combined mesh
        @type new_name: str
        @param keepHistory: Maintain history after function has completed
        @type keepHistory: bool
        """
        # Check input arguments
        if not objs:
            raise Exception('Input list "objs" is not a valid list!')
        for obj in objs:
            if not cmds.objExists(obj):
                raise Exception('Object ' + obj + ' does not exist!')
        if cmds.objExists(new_name):
            raise Exception('An object of name ' + new_name + ' already exists! Please choose another name!')

        # Combine multiple mesh objects to a single mesh
        new_obj = cmds.polyUnite(objs, n=new_name)
        cmds.addAttr(new_obj[0], ln='origNames', dt='string', multi=True)
        # Recond original names list on new mesh transform
        for i in range(len(objs)):
            cmds.setAttr(new_obj[0] + '.origNames[' + str(i) + ']', objs[i], type='string')
        # Delete history
        if not keepHistory:
            cmds.delete(new_obj[1])
        cmds.delete(objs)

        return new_obj[0]

    def separate(self, obj):
        """
        Seperates the geometry that has been combined with the combine method.
        This proc restores the names to what they were in the state before the combine.
        @param obj: Mesh object to separate
        @type obj: str
        """
        # Check origNames attribute
        if not cmds.objExists(obj + '.origNames'):
            raise Exception('Object ' + obj + ' does not have a "origNames" attribute!')

        origNamesIsMulti = True
        if not cmds.addAttr(obj + '.origNames', q=True, multi=True):
            origNamesIsMulti = False
        # Need to phase out the old format origNames attribute
        # -------------------------------------------------------
        # raise Exception(obj+'.origNames attribute is not in the correct format! Please run MeshCombineUtilities.updateOrigNamesFormat().')

        # Deal with scene namespace
        scene_ns = mel.eval('getOfficialNS')
        mel.eval('pauseNS')
        ns = ''
        if obj.count(':'):
            ns = obj.split(':')[0] + ':'
        obj_parent = cmds.listRelatives(obj, p=1, pa=True)
        obj_fPath = cmds.ls(obj, l=1)
        objs = []
        try:
            objs = cmds.polySeparate(obj, ch=1)
        except:
            raise Exception('Separate failed on object "' + obj + '"!')

        # Get original names list
        nameList = []
        if origNamesIsMulti:
            for i in range(cmds.getAttr(obj + '.origNames', s=True)):
                nameList.append(cmds.getAttr(obj + '.origNames[' + str(i) + ']'))
        else:
            for attr in cmds.listAttr(obj + '.origNames')[1:]:
                nameList.append(cmds.getAttr(obj + '.origNames.' + attr))

        # Rename separated objects
        for i in range(len(nameList)):
            nameList[i] = cmds.rename(objs[i], ns + nameList[i])
            # Re-Parent separated objects
            if cmds.objExists(obj_parent[0]):
                cmds.parent(nameList[i], obj_parent[0])
            elif cmds.objExists(ns + 'model'):
                cmds.parent(nameList[i], ns + 'model')
            else:
                cmds.parent(nameList[i], w=1)

        # Cleanup:
        # Removed rename of original objects: Objects that are referenced can't be renamed #
        orig_child = cmds.listRelatives(obj_fPath, c=1, ni=1, pa=True)
        for i in orig_child:
            if cmds.listRelatives(i):
                cmds.delete(i)

        # handle namespace
        mel.eval('setNS("' + scene_ns + '")')
        return nameList

    def separateAll(self):
        """
        This is a wrapper of the 'seperate' command. 'seperateAll' will
        look at each namespace in the scene and model node within that for meshes that
        have been combined using the 'combine'. Then it will separate the found objects.
        """
        # Iterate through available namespaces
        all_ns = mel.eval('getAllNS')
        allSeperatedObjs = []
        for ns in all_ns:
            allSeperatedObjs.extend(self.separateActor(ns))

        # Return result
        return allSeperatedObjs

    def separateActor(self, ns=''):
        """
        This is a wrapper of the 'separate' command. 'separateActor' will
        look at the provided namespace in the scene and model node within that for meshes that
        have been combined using the 'combine'. Then it will separate the
        found objects.
        @param ns: Namespace of the actor you want to separate
        @type ns: str
        """
        # Check namespace
        if len(ns):
            ns += ':'
        # Check model node exists
        if not cmds.objExists(ns + 'model'):
            print('Actor "' + ns + '" has no model group!')
            return []

        # Iterate through mesh shapes
        meshList = cmds.listRelatives(ns + 'model', ad=1, pa=True, type='mesh')
        if not meshList:
            return []
        meshParentList = []
        for mesh in meshList:
            # Get mesh transform
            meshParent = cmds.listRelatives(mesh, p=1, pa=True)[0]
            # Check origNames attribute
            if not cmds.objExists(meshParent + ".origNames"):
                continue
            # Check intermediate object
            if cmds.getAttr(mesh + '.intermediateObject'):
                continue
            # Check current mesh against meshParentList
            if not meshParentList.count(meshParent):
                meshParentList.append(meshParent)

        # Separate
        allSeperatedObjs = []
        for mesh in meshParentList:
            print "Separating : " + mesh
            allSeperatedObjs.extend(self.separate(mesh))

        # Return result
        return allSeperatedObjs

    def getOriginalNames(self, obj):
        """
        Get the meshOrigNames stored on an object that has been combined with glTools.common.MeshCombineUtilities.combine()
        @param obj: Mesh objects to get original names for
        @type obj: str
        """
        if not cmds.objExists(obj + '.origNames'):
            raise Exception('Object ' + obj + ' does not have a "origNames" attribute!')
        if not cmds.addAttr(obj + '.origNames', q=True, multi=True):
            raise Exception(
                obj + '.origNames attribute is not in the correct format! Please run MeshCombineUtilities.updateOrigNamesFormat().')

        origNamesList = []
        for i in range(cmds.getAttr(obj + '.origNames', s=True)):
            origNamesList.append(cmds.getAttr(obj + '.origNames[' + str(i) + ']'))

        return origNamesList

    def setOriginalNames(self, name_list, obj):
        """
        Set the meshOrigNames stored on an object that has been combined with glTools.common.MeshCombineUtilities.combine()
        @param obj: Mesh set original names for
        @type obj: str
        @param name_list: List of original object names
        @type name_list: list
        """
        # Verify input arguments
        if not cmds.objExists(obj + '.origNames'):
            raise Exception('Object ' + obj + ' does not have a "origNames" attribute!')
        if not cmds.addAttr(obj + '.origNames', q=True, multi=True):
            raise Exception(
                obj + '.origNames attribute is not in the correct format! Please run MeshCombineUtilities.updateOrigNamesFormat() first.')
        # Check list length
        if len(name_list) != cmds.getAttr(obj + '.origNames', s=True):
            raise Exception('Array length mis-match between input list and target attribute!')
        # Set original name values
        for i in range(len(name_list)):
            cmds.setAttr(obj + '.origNames[' + str(i) + ']', name_list[i], type='string')

    def updateOrigNamesFormat(self, objectList=[]):
        """
        Update a combined meshes origNames attribute to the newest format.
        @param objectList: list of mesh objects to update origNames attribute on.
        @type objectList: list
        """
        # Confirm list
        if type(objectList) == str:
            objectList = [objectList]

        # Iterate through object list
        for obj in objectList:

            # Check origNames attribute
            if not cmds.objExists(obj + '.origNames'):
                raise Exception('Object ' + obj + ' does not have a "origNames" attribute!')
            if cmds.addAttr(obj + '.origNames', q=True, multi=True):
                print(obj + '.origNames is already in the correct format.')
                continue

            # Extract original names list from old format
            origNamesList = []
            index = 0
            while True:
                if cmds.objExists(obj + '.origNames.origNames_' + str(index)):
                    origNamesList.append(cmds.getAttr(obj + '.origNames.origNames_' + str(index)))
                    index += 1
                else:
                    break

            # Re-create the origNames attribute in the new format
            cmds.deleteAttr(obj + '.origNames')
            cmds.addAttr(obj, ln='origNames', dt='string', multi=True)
            for i in range(len(origNamesList)):
                cmds.setAttr(obj + '.origNames[' + str(i) + ']', origNamesList[i], type='string')

    def updateActorOrigNames(self, ns=''):
        """
        Update all combined meshes origNames attribute for a specified actor namespace.
        @param ns: Namespace of the actor you want to update.
        @type ns: str
        """
        if len(ns):
            ns += ':'
        allSeperatedObjs = []
        if not cmds.objExists(ns + 'model'):
            raise Exception('Object "' + ns + 'model" does not exist!')

        # Iterate through mesh shapes
        meshList = cmds.listRelatives(ns + 'model', ad=1, ni=1, pa=True, type='mesh')
        meshParentList = []
        [meshParentList.append(cmds.listRelatives(mesh, p=1, pa=True)[0]) for mesh in meshList if
         not meshParentList.count(cmds.listRelatives(mesh, p=1, pa=True)[0])]
        for meshParent in meshParentList:
            if not cmds.objExists(meshParent + ".origNames"):
                continue
            print "Updating: " + meshParent
            self.updateOrigNamesFormat([meshParent])
