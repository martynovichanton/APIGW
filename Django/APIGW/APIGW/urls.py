"""APIGW URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include
from API import views as APIVIEWS
from APP import views as APPVIEWS

urlpatterns = [
    # path('admin/', admin.site.urls),

    path('f5api/', APIVIEWS.IndexF5.as_view(), name='INDEXF5API'),
    path('f5api/F5_SITE1_GET_TOKEN', APIVIEWS.F5Site1GetToken.as_view(), name='F5_SITE1_GET_TOKEN'),
    path('f5api/F5_SITE2_GET_TOKEN', APIVIEWS.F5Site2GetToken.as_view(), name='F5_SITE2_GET_TOKEN'),
    path('f5api/F5_SITE3_GET_TOKEN', APIVIEWS.F5Site3GetToken.as_view(), name='F5_SITE3_GET_TOKEN'),
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
