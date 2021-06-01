IBM Classic IAM permission provides permission to individual users from portal. In order to create custom Role and access groups for Classic infrastructure users, the script will facilate to automate the process to customize User role and groups for Classic using available softlayer APIs. 

**References:**
- https://sldn.softlayer.com/reference/services/SoftLayer_User_Permission_Group/
- https://sldn.softlayer.com/reference/datatypes/SoftLayer_User_Permission_Role/
- https://sldn.softlayer.com/reference/datatypes/SoftLayer_User_Customer/
- https://softlayer-api-python-client.readthedocs.io/en/latest/api/client/#softlayer-python-api-client
- https://sldn.softlayer.com/article/permission-enforcement-softlayer-api/

# softlayer_iam_permission
IAM Script to manage permission for Softlayer users

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

## Way to run this script: 
python manage_users_permission.py --help

## Usage:
- **To Create a Role:** ***manage_users_permission.py --createrolename TestRole***
- **To Delete a role:** ***manage_users_permission.py --deleteroleid 123456*** 
- **Creates a Group:** ***manage_users_permission.py --creategroupname TestGroup***
- **Deletes a group:** ***manage_users_permission.py --deletegroupid 456789***
- **Adds permission to group:** ***manage_users_permission.py --addpermissions ['HARDWARE_VIEW','VIRTUAL_GUEST_VIEW'] --permissiongroupid 22567348***
- **Link the Role with Group:** ***manage_users_permission.py --linkgroupid 456789 --linkroleid 123456***
- **Adds User to the Role:** ***manage_users_permission.py --userroleid 123456 --userid 987654***
- **Retrieves the User ID based on User first name and Last Name:** ***manage_users_permission.py --userfirstname Nitin --userlastname H***
- **Add resources to group you created earlier:** ***manage_users_permission.py --resourcegroupid 456789 --resourcetypetoadd SoftLayer_Hardware_Server --resourceidstoadd 11111,22222***
- **Remove resources to group you created earlier:** ***manage_users_permission.py --resourcegroupid 456789 --resourcetypetoremove SoftLayer_Hardware_Server --resourceidstoremove 11111,22222***
