# Copyright (c) IBM Cloud, All rights reserved.

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
The script 
1. Creates User Role
2. Deletes User ROle
3. Create User Group
4. Delete User Group
5. Adds permission to User Group (https://sldn.softlayer.com/article/permission-enforcement-softlayer-api/)
6. Links the group to User Role
7. Adds Users to the Role
8. Delete User from the role
9. Add resources to the group
10. Delete resources from the group

Important manual pages:
https://sldn.softlayer.com/reference/services/SoftLayer_User_Permission_Group/
https://sldn.softlayer.com/reference/datatypes/SoftLayer_User_Permission_Role/
https://sldn.softlayer.com/reference/datatypes/SoftLayer_User_Customer/
https://softlayer-api-python-client.readthedocs.io/en/latest/api/client/#softlayer-python-api-client
https://sldn.softlayer.com/article/permission-enforcement-softlayer-api/

Way to run this program:
python manage_users_permission.py --help
Usage:
            manage_users_permission.py --createrolename TestRole ### Creates a role
            manage_users_permission.py --deleteroleid 123456 ### Deletes a role
            manage_users_permission.py --creategroupname TestGroup ### Creates a Group
            manage_users_permission.py --deletegroupid 456789 ### Deletes a group
            manage_users_permission.py --addpermissions ['HARDWARE_VIEW','VIRTUAL_GUEST_VIEW'] --permissiongroupid 22567348 ### Adds permission to group
            manage_users_permission.py --linkgroupid 456789 --linkroleid 123456 ### Link the Role with Group
            manage_users_permission.py --userroleid 123456 --userid 987654 ### Adds User to the Role
            manage_users_permission.py --userfirstname Nitin --userlastname H ### Retrieves the User ID based on User first name and Last Name
            manage_users_permission.py --resourcegroupid 456789 --resourcetypetoadd SoftLayer_Hardware_Server --resourceidstoadd 11111,22222
            manage_users_permission.py --resourcegroupid 456789 --resourcetypetoremove SoftLayer_Hardware_Server --resourceidstoremove 11111,22222
"""
from pprint import pprint
import SoftLayer
from optparse import OptionParser
import sys
import json

class Manageuser:
    
    def __init__(self):
        self.client = SoftLayer.create_client_from_env()
    
    def create_user_role(self,rolename):

        description =  rolename + " user permission role"
        templateObject = {
            "name": rolename,
            "description": description
        }

        try:
            createRole = self.client['User_Permission_Role'].createObject(templateObject)
            pprint(createRole)
            return createRole['id']

        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to create a user permission role :{}, {}'.format(e.faultCode, e.faultString))

    def delete_user_role(self,roleid):

        try:
            deleteRole = self.client['SoftLayer_User_Permission_Role'].deleteObject(id=roleid)
            pprint(deleteRole)

        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to delete role: :{}, {}'.format(e.faultCode, e.faultString))

    def create_user_group(self,groupname):
    
        description =  groupname + ": user permission group"
        templateObject = {
            "name": groupname,
            "description": description
        }

        try:
            createGroup = self.client['User_Permission_Group'].createObject(templateObject)
            pprint(createGroup)
            return(createGroup['id'])

        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to create a user permission group: {}, {}'.format(e.faultCode, e.faultString))

    def delete_user_group(self,groupid):

        try:
            deletegroup = self.client['User_Permission_Group'].deleteObject(id=groupid)
            pprint(deletegroup)

        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to delete group: :{}, {}'.format(e.faultCode, e.faultString))
    
    def add_permission(self, groupid, actions):
        bulk_actions = self.gather_actions(actions)
        try:
            result = self.client['User_Permission_Group'].addBulkActions(bulk_actions, id=groupid)
            if not result:
                resp = self.client['User_Permission_Group'].getActions(id=groupid)
                pprint(resp)
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to add user permission to group: {}, {}'.format(e.faultCode, e.faultString))

    def gather_actions(self, actions):
        """Retrieve the permissions from keyname list"""
        actions_list = []
        # Retrieve all available permissions

        permissions = self.client['User_Permission_Action'].getAllObjects()
        for permission in permissions:
            if permission['keyName'] in actions:
                actions_list.append({'id': permission['id']})
        return actions_list
    
    def link_group(self, roleid, groupid):
        group = {
            "id": groupid
        }
        try:
            result = self.client['User_Permission_Role'].linkGroup(group, id=roleid)
            if not result:
                resp = self.client['User_Permission_Role'].getGroups(id=roleid)
                pprint(resp)
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to link group to the user permission role faultCode=%s, faultString=%s'% (e.faultCode, e.faultString))

    def add_roleuser(self, roleid, userid):
        user = {
            "id": userid
        }
        try:
            addUser = self.client['User_Permission_Role'].addUser(user, id=roleid)
            if not addUser:
                actions = self.client['User_Permission_Role'].getActions(id=roleid)
                pprint('listing the User permission...')
                pprint('Newly added permission')
                for action in actions:
                    pprint('{}: {}'.format(action['name'], action['keyName']))
                allactions = self.client['User_Customer'].getActions(id=userid)
                pprint('Overall User permission')
                for action in allactions:
                    pprint('{}: {}'.format(action['name'], action['keyName']))
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to add user to the user permission role : {}, {}'.format(e.faultCode, e.faultString))

    def remove_roleuser(self, roleid, userid):
        user = {
            "id": userid
        }
        try:
            self.client['User_Permission_Role'].removeUser(user, id=roleid)
            pprint('UserID:{} removed from RoleID {}'.format(userid, roleid))
        except SoftLayer.SoftLayerAPIError as e:
            pprint('User not associated with permission role : {}, {}'.format(e.faultCode, e.faultString))
    
    def get_userid(self, firstname, lastname):
        try:
            userlist = self.client['SoftLayer_Account'].getUsers()
            for user in userlist:
                if user['firstName'] in firstname and user['lastName'] in lastname:
                    userid = user['id']
                    pprint(userid)
                    return userid
            
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to find User in the account : {}, {}'.format(e.faultCode, e.faultString))

    def add_resources(self, groupid, resourcetype, resourceids):
        bulk_resourceobjects = self.gather_resources(resourcetype, resourceids)
        print('Adding resources: {} of server type: {} to User Group: {}'.format(resourceids, resourcetype, groupid))
        try:
            resourceObject = self.client['SoftLayer_User_Permission_Group'].addBulkResourceObjects(bulk_resourceobjects, id=groupid)
            pprint(resourceObject)
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to add resources to group: {}, {}'.format(e.faultCode, e.faultString))

    def remove_resources(self, groupid, resourcetype, resourceids):
        bulk_resourceobjects = self.gather_resources(resourcetype, resourceids)
        print('Removing resources: {} of server type: {} from User Group: {}'.format(resourceids, resourcetype, groupid))
        try:
            resourceObject = self.client['SoftLayer_User_Permission_Group'].removeBulkResourceObjects(bulk_resourceobjects, id=groupid)
            pprint(resourceObject)
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Unable to remove resources to group: {}, {}'.format(e.faultCode, e.faultString))

    
    def gather_resources(self, resourcetype, resourceids):
        """list the resources to be added to group"""
        try:
            resourceobjects_list = []
            resourceids = resourceids.split(',')
            # Retrieve all available permissions
            for resourceid in resourceids:
                resourceobjects_list.append({'complexType': resourcetype, 'id': resourceid})
            return resourceobjects_list
        
        except SoftLayer.SoftLayerAPIError as e:
            pprint('Resource ID is not valid : {}, {}'.format(e.faultCode, e.faultString))

if __name__ == "__main__":
    main = Manageuser()
    usage = """
            Way to run this program:
            %prog --createrolename TestRole
            %prog --deleteroleid 123456
            %prog --creategroupname TestGroup
            %prog --deletegroupid 456789 
            %prog --addpermissions ['HARDWARE_VIEW','VIRTUAL_GUEST_VIEW'] --permissiongroupid 22567348
            %prog --linkgroupid 456789 --linkroleid 123456 
            %prog --userfirstname Nitin --userlastname H
            %prog --userroleid 123456 --userid 987654
            %prog --roleidofuser 123456 --removeuserid 987654
            %prog --resourcegroupid 456789 --resourcetypetoadd SoftLayer_Hardware_Server --resourceidstoadd 109620930,118470220
            %prog --resourcegroupid 456789 --resourcetypetoremove SoftLayer_Virtual_Guest --resourceidstoremove 109620930,118470220

    """
    parser = OptionParser(usage=usage)
    parser.add_option("--createrolename", dest="createrolename", default=None, help="Name of the role to  create")
    parser.add_option("--deleteroleid", dest="deleteroleid", default=None, help="ID of the role to  delete")
    parser.add_option("--creategroupname", dest="creategroupname", default=None, help="Name of the group to  create")
    parser.add_option("--deletegroupid", dest="deletegroupid", default=None, help="ID of the group to  delete")
    parser.add_option("--addpermissions", dest="actions", default=None, help="Add permissions to the group")
    parser.add_option("--linkgroupid", dest="linkgroupid", default=None, help="link group ID to the role")
    parser.add_option("--linkroleid", dest="linkroleid", default=None, help="Role ID to be linked with group")
    parser.add_option("--permissiongroupid", dest="permissiongroupid", default=None, help="Group ID for permissions to be added")
    parser.add_option("--userroleid", dest="userroleid", default=None, help="Role ID for User to be part of")
    parser.add_option("--userid", dest="userid", default=None, help="user ID to be part of the role")
    parser.add_option("--roleidofuser", dest="roleidofuser", default=None, help="role ID associated with User")
    parser.add_option("--removeuserid", dest="removeuserid", default=None, help="user ID to be removed of the role")
    parser.add_option("--userfirstname", dest="userfirstname", default=None, help="Firstname of the User")
    parser.add_option("--userlastname", dest="userlastname", default=None, help="Lastname of the User")
    parser.add_option("--resourcetypetoadd", dest="resourcetypetoadd", default=None, help="Type of resource (VM/BM/DH) you want to add to the group")
    parser.add_option("--resourcegroupid", dest="resourcegroupid", default=None, help="Id of the group for resources to belong to")
    parser.add_option("--resourceidstoadd", dest="resourceidstoadd", default=None, help="list of server Ids to add")
    parser.add_option("--resourcetypetoremove", dest="resourcetypetoremove", default=None, help="Type of resource (VM/BM/DH) you want to remove from the group")
    parser.add_option("--resourceidstoremove", dest="resourceidstoremove", default=None, help="list of server Ids to remove")

    (options, args) = parser.parse_args()

    if options.createrolename is not None:
        main.create_user_role(rolename=options.createrolename)
        sys.exit(0)

    if options.deleteroleid is not None:
        main.delete_user_role(roleid=options.deleteroleid)
        sys.exit(0)

    if options.creategroupname is not None:
        main.create_user_group(groupname=options.creategroupname)
        sys.exit(0)

    if options.deletegroupid is not None:
        main.delete_user_group(groupid=options.deletegroupid)
        sys.exit(0)
    
    if options.actions is not None:
        main.add_permission(groupid=options.permissiongroupid, actions=options.actions)
        sys.exit(0)

    if options.linkgroupid is not None:
        main.link_group(roleid=options.linkroleid, groupid=options.linkgroupid)
        sys.exit(0)

    if options.userid is not None:
        main.add_roleuser(roleid=options.userroleid, userid=options.userid)
        sys.exit(0)
    
    if options.roleidofuser is not None:
        main.remove_roleuser(roleid=options.roleidofuser, userid=options.removeuserid)
        sys.exit(0)
    
    if options.userfirstname is not None:
        main.get_userid(firstname=options.userfirstname, lastname=options.userlastname)
        sys.exit(0)
 
    if options.resourceidstoadd is not None:
        main.add_resources(groupid=options.resourcegroupid, resourcetype=options.resourcetypetoadd, resourceids=options.resourceidstoadd)
        sys.exit(0)
    
    if options.resourceidstoremove is not None:
        main.remove_resources(groupid=options.resourcegroupid, resourcetype=options.resourcetypetoremove, resourceids=options.resourceidstoremove)
        sys.exit(0)