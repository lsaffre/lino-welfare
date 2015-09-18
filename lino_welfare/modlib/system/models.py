# -*- coding: UTF-8 -*-
# Copyright 2013-2014 Luc Saffre
# This file is part of Lino Welfare.
#
# Lino Welfare is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Welfare is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Welfare.  If not, see
# <http://www.gnu.org/licenses/>.

"""
This module extends :mod:`lino.modlib.cal.models`
"""

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lino.api import dd, rt

from lino.modlib.system.models import *
from lino_welfare.modlib.cbss.roles import CBSSUser


class Signers(dd.Model):

    """Model mixin which adds two fields `signer1` and `signer2`,
    the two in-house signers of contracts and official documents.
    
    Inherited by :class:`SiteConfig
    <lino.modlib.system.models.SiteConfig>` and :class:`ContractBase`.

    """

    class Meta:
        abstract = True

    signer1 = models.ForeignKey(
        "contacts.Person",
        related_name="%(app_label)s_%(class)s_set_by_signer1",
        #~ default=default_signer1,
        verbose_name=_("Secretary"))

    signer2 = models.ForeignKey(
        "contacts.Person",
        related_name="%(app_label)s_%(class)s_set_by_signer2",
        #~ default=default_signer2,
        verbose_name=_("President"))

    @dd.chooser()
    def signer1_choices(cls):
        sc = settings.SITE.site_config
        kw = dict()
        if sc.signer1_function:
            kw.update(rolesbyperson__type=sc.signer1_function)
        return settings.SITE.modules.contacts.Person.objects.filter(
            rolesbyperson__company=sc.site_company, **kw)

    @dd.chooser()
    def signer2_choices(cls):
        sc = settings.SITE.site_config
        kw = dict()
        if sc.signer2_function:
            kw.update(rolesbyperson__type=sc.signer2_function)
        return settings.SITE.modules.contacts.Person.objects.filter(
            rolesbyperson__company=sc.site_company, **kw)


class SiteConfig(SiteConfig, Signers):

    """
    This adds the :class:`lino_welfare.modlib.isip.models.Signers`
    mixin to Lino's standard SiteConfig.
    
    """

    signer1_function = dd.ForeignKey(
        "contacts.RoleType",
        blank=True, null=True,
        verbose_name=_("First signer function"),
        help_text=_("""Contact function to designate the secretary."""),
        related_name="%(app_label)s_%(class)s_set_by_signer1")
    signer2_function = dd.ForeignKey(
        "contacts.RoleType",
        blank=True, null=True,
        verbose_name=_("Second signer function"),
        help_text=_(
            "Contact function to designate the president."),
        related_name="%(app_label)s_%(class)s_set_by_signer2")


dd.update_field(SiteConfig, 'signer1', blank=True, null=True)
dd.update_field(SiteConfig, 'signer2', blank=True, null=True)


class SiteConfigDetail(dd.FormLayout):

    main = "general constants cbss"

    general = dd.Panel(
        """
        site_company next_partner_id:10
        job_office master_budget
        signer1 signer2
        signer1_function signer2_function
        """, label=_("General"))

    constants = dd.Panel(
        """
        system_note_type default_build_method
        propgroup_skills propgroup_softskills propgroup_obstacles
        residence_permit_upload_type \
        work_permit_upload_type \
        driving_licence_upload_type
        # client_calendar
        default_event_type prompt_calendar
        client_guestrole team_guestrole
        """, label=_("Constants"))

    cbss = dd.Panel(
        """
        cbss_org_unit sector ssdn_user_id ssdn_email
        cbss_http_username cbss_http_password
        """,
        label=dd.apps.cbss.verbose_name,
        required_roles=dd.required(CBSSUser))


# When a Welfare Site decides to hide the "debts" app (as chatelet does)
# then we must remove the `master_budget` field.
# TODO: find a more elegant way to do this.
if not dd.is_installed('debts'):
    SiteConfigDetail.general.replace('master_budget', '')


class SiteConfigs(SiteConfigs):
    detail_layout = SiteConfigDetail()
