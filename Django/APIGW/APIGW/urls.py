
# from django.contrib import admin
from django.urls import path, include
from API import views as APIVIEWS
from APP import views as APPVIEWS

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('f5api/', APIVIEWS.IndexF5.as_view(), name='INDEXF5API'),
    path('f5api/F5_SITE1_GET_TOKEN', APIVIEWS.F5Site1GetToken.as_view(), name='F5_SITE1_GET_TOKEN'),
    path('f5api/F5_SITE2_GET_TOKEN', APIVIEWS.F5Site2GetToken.as_view(), name='F5_SITE2_GET_TOKEN'),

    path('f5api/F5_SITE1_POOLS', APIVIEWS.F5Site1Pools.as_view(), name='F5_SITE1_POOLS'),
    path('f5api/F5_SITE1_POOL_MEMBERS/<pool_name>', APIVIEWS.F5Site1PoolMembers.as_view(), name='F5_SITE1_POOL_MEMBERS'),
    path('f5api/F5_SITE1_POOL_MEMBERS/<pool_name>/STATS', APIVIEWS.F5Site1PoolMembersStats.as_view(), name='F5_SITE1_POOL_MEMBERS_STATS'),
    path('f5api/F5_SITE1_DISABLE_POOL_MEMBER/<pool_name>/<member_name>', APIVIEWS.F5Site1DisablePoolMember.as_view(), name='F5_SITE1_DISABLE_POOL_MEMBER'),
    path('f5api/F5_SITE1_ENABLE_POOL_MEMBER/<pool_name>/<member_name>', APIVIEWS.F5Site1EnablePoolMember.as_view(), name='F5_SITE1_ENABLE_POOL_MEMBER'),
    path('f5api/F5_SITE1_ADD_TO_POOL', APIVIEWS.F5Site1AddToPool.as_view(), name='F5_SITE1_ADD_TO_POOL'),
    path('f5api/F5_SITE1_REMOVE_FROM_POOL', APIVIEWS.F5Site1RemoveFromPool.as_view(), name='F5_SITE1_REMOVE_FROM_POOL'),
    path('f5api/F5_SITE1_UPDATE_COMMANDS', APIVIEWS.F5Site1UpdateCommands.as_view(), name='F5_SITE1_UPDATE_COMMANDS'),

    path('f5api/F5_SITE2_POOLS', APIVIEWS.F5Site2Pools.as_view(), name='F5_SITE2_POOLS'),
    path('f5api/F5_SITE2_POOL_MEMBERS/<pool_name>', APIVIEWS.F5Site2PoolMembers.as_view(), name='F5_SITE2_POOL_MEMBERS'),
    path('f5api/F5_SITE2_POOL_MEMBERS/<pool_name>/STATS', APIVIEWS.F5Site2PoolMembersStats.as_view(), name='F5_SITE2_POOL_MEMBERS_STATS'),
    path('f5api/F5_SITE2_DISABLE_POOL_MEMBER/<pool_name>/<member_name>', APIVIEWS.F5Site2DisablePoolMember.as_view(), name='F5_SITE2_DISABLE_POOL_MEMBER'),
    path('f5api/F5_SITE2_ENABLE_POOL_MEMBER/<pool_name>/<member_name>', APIVIEWS.F5Site2EnablePoolMember.as_view(), name='F5_SITE2_ENABLE_POOL_MEMBER'),
    path('f5api/F5_SITE2_ADD_TO_POOL', APIVIEWS.F5Site2AddToPool.as_view(), name='F5_SITE2_ADD_TO_POOL'),
    path('f5api/F5_SITE2_REMOVE_FROM_POOL', APIVIEWS.F5Site2RemoveFromPool.as_view(), name='F5_SITE2_REMOVE_FROM_POOL'),
    path('f5api/F5_SITE2_UPDATE_COMMANDS', APIVIEWS.F5Site2UpdateCommands.as_view(), name='F5_SITE2_UPDATE_COMMANDS'),

    path('f5api/<command>', APIVIEWS.F5Commands.as_view(), name='F5_COMMANDS'),

    path('fortiapi/', APIVIEWS.IndexForti.as_view(), name='INDEXFORTIAPI'),
    path('fortiapi/FORTI_SITE1_GET_TOKEN', APIVIEWS.FortiSite1GetToken.as_view(), name='FORTI_SITE1_GET_TOKEN'),
    path('fortiapi/FORTI_SITE2_GET_TOKEN', APIVIEWS.FortiSite2GetToken.as_view(), name='FORTI_SITE2_GET_TOKEN'),

    path('fortiapi/FORTI_SITE1_ADD_TO_WHITELIST', APIVIEWS.FortiSite1AddToWhitelist.as_view(), name='FORTI_SITE1_ADD_TO_WHITELIST'),
    path('fortiapi/FORTI_SITE1_REMOVE_FROM_WHITELIST', APIVIEWS.FortiSite1RemoveFromWhitelist.as_view(), name='FORTI_SITE1_REMOVE_FROM_WHITELIST'),
    path('fortiapi/FORTI_SITE1_GET_POLICY_PKG_STATUS', APIVIEWS.FortiSite1GetPolicyPkgStatus.as_view(), name='FORTI_SITE1_GET_POLICY_PKG_STATUS'),
    path('fortiapi/FORTI_SITE1_GET_INSTALL_PREVIEW', APIVIEWS.FortiSite1GetInstallPreview.as_view(), name='FORTI_SITE1_GET_INSTALL_PREVIEW'),
    path('fortiapi/FORTI_SITE1_INSTALL_POLICY_ALL', APIVIEWS.FortiSite1InstallPolicyAll.as_view(), name='FORTI_SITE1_INSTALL_POLICY_ALL'),

    path('fortiapi/FORTI_SITE2_ADD_TO_WHITELIST', APIVIEWS.FortiSite2AddToWhitelist.as_view(), name='FORTI_SITE2_ADD_TO_WHITELIST'),
    path('fortiapi/FORTI_SITE2_REMOVE_FROM_WHITELIST', APIVIEWS.FortiSite2RemoveFromWhitelist.as_view(), name='FORTI_SITE2_REMOVE_FROM_WHITELIST'),
    path('fortiapi/FORTI_SITE2_GET_POLICY_PKG_STATUS', APIVIEWS.FortiSite2GetPolicyPkgStatus.as_view(), name='FORTI_SITE2_GET_POLICY_PKG_STATUS'),
    path('fortiapi/FORTI_SITE2_GET_INSTALL_PREVIEW', APIVIEWS.FortiSite2GetInstallPreview.as_view(), name='FORTI_SITE2_GET_INSTALL_PREVIEW'),
    path('fortiapi/FORTI_SITE2_INSTALL_POLICY_ALL', APIVIEWS.FortiSite2InstallPolicyAll.as_view(), name='FORTI_SITE2_INSTALL_POLICY_ALL'),

    path('f5app/', APPVIEWS.IndexF5.as_view(), name='INDEXF5APP'),
    path('fortiapp/', APPVIEWS.IndexForti.as_view(), name='INDEXFORTIAPP')
]
