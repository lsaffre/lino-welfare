# -*- coding: UTF-8 -*-
# Copyright 2008-2014 Luc Saffre
# This file is part of the Lino Welfare project.
# Lino Welfare is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# Lino Welfare is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with Lino Welfare; if not, see <http://www.gnu.org/licenses/>.

from __future__ import unicode_literals
from __future__ import print_function

import logging
logger = logging.getLogger(__name__)

import os
import cgi
import datetime

from django.db import models
from django.db.models import Q
from django.db.utils import DatabaseError
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext
from django.utils.translation import string_concat
from django.utils.encoding import force_unicode
from django.utils.functional import lazy

#~ import lino
#~ logger.debug(__file__+' : started')
#~ from django.utils import translation

from lino import dd
from lino import mixins
from lino.core import dbutils
from lino.core.dbutils import resolve_field
from lino.utils.choosers import chooser
from lino.utils import mti
from lino.utils.ranges import isrange

from lino.utils.xmlgen.html import E


from lino.mixins.printable import Printable
from lino.core import actions

from lino.core.dbutils import resolve_model, UnresolvedModel

from lino.mixins import beid

households = dd.resolve_app('households')
cal = dd.resolve_app('cal')
extensible = dd.resolve_app('extensible')
properties = dd.resolve_app('properties')
contacts = dd.resolve_app('contacts')
cv = dd.resolve_app('cv')
uploads = dd.resolve_app('uploads')
users = dd.resolve_app('users')
isip = dd.resolve_app('isip')
jobs = dd.resolve_app('jobs')
#~ integ = dd.resolve_app('integ')
#~ jobs = dd.resolve_app('jobs')
#~ from lino_welfare.modlib.isip import models as isip
#~ newcomers = dd.resolve_app('newcomers')
notes = dd.resolve_app('notes')

from lino.utils import ssin

class CoachingEvents(dd.ChoiceList):
    verbose_name = _("Observed event")
    verbose_name_plural = _("Observed events")
add = CoachingEvents.add_item
add('10', _("Started"), 'started')
add('20', _("Active"), 'active')
add('30', _("Ended"), 'ended')


#~ class CoachingStates(dd.Workflow):
    #~ """Lifecycle of a :class:`Coaching`."""
    #~ @classmethod
    #~ def before_state_change(cls,obj,ar,kw,oldstate,newstate):
        #~ if newstate.name == 'ended':
            #~ obj.end_date = datetime.date.today()
        #~ elif newstate.name in ('active','standby'):
            #~ obj.end_date = None
#~ add = CoachingStates.add_item
# ~ # add('10', _("New"),'new')
# ~ # add('10', _("Suggested"),'suggested')
# ~ # add('20', _("Refused"),'refused')
# ~ # add('30', _("Confirmed"),'confirmed')
#~ add('30', _("Active"),'active')
#~ add('40', _("Standby"),'standby')
#~ add('50', _("Ended"),'ended')
class EndCoaching(dd.ChangeStateAction, dd.NotifyingAction):
    label = _("End coaching")
    help_text = _("User no longer coaches this client.")
    required = dict(states='active standby', user_groups='integ', owner=True)

    def get_notify_subject(self, ar, obj, **kw):
        return _("%(client)s no longer coached by %(coach)s") % dict(
            client=obj.client, coach=obj.user)

    #~ def action_param_defaults(self,ar,obj,**kw):
        #~ kw = super(EndCoaching,self).action_param_defaults(ar,obj,**kw)
        #~ if obj is not None:
            #~ kw.update(notify_subject=
                #~ _("%(client)s no longer coached by %(coach)s")
                #~ % dict(client=obj.client,coach=obj.user))
        #~ return kw

    #~ def update_system_note_kw(self,ar,kw,obj):
        #~ if obj is not None:
            #~ return kw.update(project=obj.client)


# CoachingStates.suggested.set_required(owner=False)
# CoachingStates.refused.add_workflow(_("refuse"),states='suggested standby',owner=True)
# CoachingStates.active.add_workflow(_("accept"),states='suggested',owner=True)
#~ CoachingStates.active.add_workflow(_("Reactivate"),
    #~ states='standby ended',owner=True,
    #~ help_text=_("Client has become active again after having been ended or standby."))
#~ CoachingStates.standby.add_workflow(states='active',owner=True)
#~ CoachingStates.ended.add_workflow(EndCoaching)
# CoachingStates.ended.add_workflow(_("End coaching"),
    # help_text=_("User no longer coaches this client."),
    # states='active standby',user_groups='integ',owner=True,notify=True)
#~ """
#~ CoachingStates.add_transition('suggested','refused',_("Refuse"),owner=True)
#~ CoachingStates.add_transition('suggested','active',_("Accept"),owner=True)
#~ CoachingStates.add_transition('active','standby',_("Standby"),owner=True)
#~ CoachingStates.add_transition('active','ended',_("End coaching"),owner=True)
#~
#~ """
class CoachingType(dd.BabelNamed):

    class Meta:
        verbose_name = _("Coaching type")
        verbose_name_plural = _('Coaching types')


class CoachingTypes(dd.Table):
    help_text = _("Liste des types d'accompagnement.")
    model = CoachingType
    column_names = 'name *'
    #~ required_user_level = UserLevels.manager
    required = dict(user_level='manager')

# ~ _("Integration"),'integ')     # DSBE
# ~ _("General"),'general')       # ASD
# ~ _("Debt mediation"),'debts')  # Schuldnerberatung
# ~ _("Accounting"),'accounting') # Buchhaltung
# ~ _("Human resources"),'human') # Personaldienst
# ~ _("Human resources"),'human') # Altenheim
# ~ _("Human resources"),'human') # Mosaik
# ~ _("Human resources"),'human') # Sekretariat
# ~ _("Human resources"),'human') # Häusliche Hilfe
# ~ _("Human resources"),'human') # Energiedienst

#~ class CoachingTypes(ChoiceList):
    #~ label = _("Coaching type")
#~ add = CoachingTypes.add_item
#~ add('10', _("Primary coach"),'primary')
#~ add('20', _("Secondary coach"),'secondary')


class CoachingEnding(dd.BabelNamed, dd.Sequenced):

    class Meta:
        verbose_name = _("Reason of termination")
        verbose_name_plural = _('Coaching termination reasons')

    #~ name = models.CharField(_("designation"),max_length=200)
    type = dd.ForeignKey(CoachingType,
                         blank=True, null=True,
                         help_text=_("If not empty, allow this ending only on coachings of specified type."))

    #~ def __unicode__(self):
        #~ return unicode(self.name)


class CoachingEndings(dd.Table):
    help_text = _("A list of reasons expressing why a coaching was ended")
    required = dict(user_groups=['integ'], user_level='manager')
    model = CoachingEnding
    column_names = 'seqno name type *'
    order_by = ['seqno']
    detail_layout = """
    id name seqno
    CoachingsByEnding
    """


#~ class Coaching(mixins.UserAuthored,mixins.ProjectRelated):
#~ class Coaching(mixins.UserAuthored,ImportedFields):
class Coaching(dd.Model, dd.ImportedFields):

    """
A Coaching (Begleitung, accompagnement) 
is when a Client is being coached by a User (a social assistant) 
during a given period.
    """

    #~ required = dict(user_level='manager')
    class Meta:
        verbose_name = _("Coaching")
        verbose_name_plural = _("Coachings")

    user = models.ForeignKey(settings.SITE.user_model,
                             verbose_name=_("Coach"),
                             related_name="%(app_label)s_%(class)s_set_by_user",
                             #~ blank=True,null=True
                             )

    allow_cascaded_delete = ['client']
    workflow_state_field = 'state'

    client = models.ForeignKey('pcsw.Client',
                               related_name="coachings_by_client")
    start_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("Coached from"))
    end_date = models.DateField(
        blank=True, null=True,
        verbose_name=_("until"))
    #~ state = CoachingStates.field(default=CoachingStates.active)
    #~ type = CoachingTypes.field()
    type = dd.ForeignKey(CoachingType, blank=True, null=True)
    primary = models.BooleanField(
        _("Primary"),
        default=False,
        help_text=_("""There's at most one primary coach per client. \
        Enabling this field will automatically make the other \
        coachings non-primary."""))

    ending = models.ForeignKey(CoachingEnding,
                               related_name="%(app_label)s_%(class)s_set",
                               blank=True, null=True)

    @classmethod
    def on_analyze(cls, site):
        super(Coaching, cls).on_analyze(site)
        #~ cls.declare_imported_fields('''client user primary start_date end_date''')
        cls.declare_imported_fields('''client user primary end_date''')

    @dd.chooser()
    def ending_choices(cls, type):
        Q = models.Q
        qs = CoachingEnding.objects.filter(
            Q(type__isnull=True) | Q(type=type))
        return qs.order_by("seqno")

    def disabled_fields(self, ar):
        rv = super(Coaching, self).disabled_fields(ar)
        if settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return self._imported_fields
            return set(['primary'])
        return rv

    def on_create(self, ar):
        """
        Default value for the `user` field is the requesting user.
        """
        if self.user_id is None:
            u = ar.get_user()
            if u is not None:
                self.user = u
        super(Coaching, self).on_create(ar)

    def disable_delete(self, ar):
        if ar is not None and settings.SITE.is_imported_partner(self.client):
            if self.primary:
                return _("Cannot delete companies and persons imported from TIM")
        return super(Coaching, self).disable_delete(ar)

    def before_ui_save(self, ar, **kw):
        #~ logger.info("20121011 before_ui_save %s",self)
        super(Coaching, self).before_ui_save(ar, **kw)
        if not self.type:
            self.type = ar.get_user().coaching_type
        if not self.start_date:
            self.start_date = datetime.date.today()
        if self.ending and not self.end_date:
            self.end_date = datetime.date.today()

    #~ def update_system_note(self,note):
        #~ note.project = self.client

    def __unicode__(self):
        #~ return _("Coaching of %(client)s by %(user)s") % dict(client=self.client,user=self.user)
        #~ return self.user.username+' / '+self.client.first_name+' '+self.client.last_name[0]
        return self.user.username + ' / ' + self.client.last_name + ' ' + self.client.first_name[0]

    def after_ui_save(self, ar):
        super(Coaching, self).after_ui_save(ar)
        if self.primary:
            for c in self.client.coachings_by_client.exclude(id=self.id):
                if c.primary:
                    c.primary = False
                    c.save()
                    ar.response.update(refresh_all=True)
        #~ return kw

    #~ def get_row_permission(self,user,state,ba):
        #~ """
        #~ """
        #~ logger.info("20121011 get_row_permission %s %s",self,ba)
        #~ if isinstance(ba.action,actions.SubmitInsert):
            #~ if not user.coaching_type:
                #~ return False
        #~ return super(Coaching,self).get_row_permission(user,state,ba)

    def full_clean(self, *args, **kw):
        if not isrange(self.start_date, self.end_date):
            raise ValidationError(_("Coaching period ends before it started."))
        if not self.start_date and not self.end_date:
            self.start_date = datetime.date.today()
        if not self.type and self.user:
            self.type = self.user.coaching_type
        super(Coaching, self).full_clean(*args, **kw)

    #~ def save(self,*args,**kw):
        #~ super(Coaching,self).save(*args,**kw)

    def summary_row(self, ar, **kw):
        return [ar.href_to(self.client), " (%s)" % self.state.text]

    def get_related_project(self, ar):
        return self.client

    def get_system_note_type(self, ar):
        return settings.SITE.site_config.system_note_type

    def get_system_note_recipients(self, ar, silent):
        yield "%s <%s>" % (unicode(self.user), self.user.email)
        for u in settings.SITE.user_model.objects.filter(coaching_supervisor=True):
            yield "%s <%s>" % (unicode(u), u.email)

#~ dd.update_field(Coaching,'user',verbose_name=_("Coach"))


class Coachings(dd.Table):
    required = dd.required(user_level='admin')
    help_text = _("Liste des accompagnements.")
    model = Coaching

    parameters = dd.ObservedPeriod(
        coached_by=models.ForeignKey(users.User,
                                     blank=True, null=True,
                                     verbose_name=_(
                "Coached by"), help_text="""Nur Begleitungen dieses Benutzers."""),
        and_coached_by=models.ForeignKey(users.User,
                                         blank=True, null=True,
                                         verbose_name=_(
                "and by"), help_text="""... und auch Begleitungen dieses Benutzers."""),
        #~ start_date = models.DateField(_("Period from"),
            #~ help_text="""Date début de la période observée"""),
        #~ end_date = models.DateField(_("until"),
            #~ help_text="""Date fin de la période observée"""),
        observed_event=CoachingEvents.field(
            blank=True, default=CoachingEvents.active),
        primary_coachings=dd.YesNo.field(_("Primary coachings"),
            blank=True, help_text="""Accompagnements primaires."""),
        coaching_type=models.ForeignKey(CoachingType,
                                        blank=True, null=True,
            help_text="""Nur Begleitungen dieses Dienstes."""),
        ending=models.ForeignKey(CoachingEnding,
                                 blank=True, null=True,
            help_text="""Nur Begleitungen mit diesem Beendigungsgrund."""),
    )
    params_layout = """
    start_date end_date observed_event coached_by and_coached_by 
    primary_coachings coaching_type ending 
    """
    params_panel_hidden = True

    #~ @classmethod
    #~ def param_defaults(self,ar,**kw):
        #~ kw = super(Coachings,self).param_defaults(ar,**kw)
        #~ D = datetime.date
        #~ kw.update(start_date = D.today())
        #~ kw.update(end_date = D.today())
        #~ return kw

    @classmethod
    def get_request_queryset(self, ar):
        qs = super(Coachings, self).get_request_queryset(ar)
        coaches = []
        for u in (ar.param_values.coached_by, ar.param_values.and_coached_by):
            if u is not None:
                coaches.append(u)
        if len(coaches):
            qs = qs.filter(user__in=coaches)

        ce = ar.param_values.observed_event
        if ar.param_values.start_date is None or ar.param_values.end_date is None:
            period = None
        else:
            period = (ar.param_values.start_date, ar.param_values.end_date)
        if ce is not None and period is not None:
            if ce == CoachingEvents.started:
                qs = qs.filter(start_date__gte=ar.param_values.start_date)
                qs = qs.filter(start_date__lte=ar.param_values.end_date)
            elif ce == CoachingEvents.ended:
                qs = qs.filter(end_date__isnull=False)
                qs = qs.filter(end_date__gte=ar.param_values.start_date)
                qs = qs.filter(end_date__lte=ar.param_values.end_date)
            elif ce == CoachingEvents.active:
                qs = qs.filter(start_date__lte=ar.param_values.end_date)
                qs = qs.filter(Q(end_date__isnull=True) |
                               Q(end_date__gte=ar.param_values.start_date))

        if ar.param_values.primary_coachings == dd.YesNo.yes:
            qs = qs.filter(primary=True)
        elif ar.param_values.primary_coachings == dd.YesNo.no:
            qs = qs.filter(primary=False)
        if ar.param_values.coaching_type is not None:
            qs = qs.filter(type=ar.param_values.coaching_type)
        if ar.param_values.ending is not None:
            qs = qs.filter(ending=ar.param_values.ending)
        return qs

    @classmethod
    def get_title_tags(self, ar):
        for t in super(Coachings, self).get_title_tags(ar):
            yield t

        if ar.param_values.observed_event:
            yield unicode(ar.param_values.observed_event)

        if ar.param_values.coached_by:
            s = unicode(self.parameters['coached_by'].verbose_name) + \
                ' ' + unicode(ar.param_values.coached_by)
            if ar.param_values.and_coached_by:
                s += " %s %s" % (unicode(_('and')),
                                 ar.param_values.and_coached_by)
            yield s

        if ar.param_values.primary_coachings:
            yield unicode(self.parameters['primary_coachings'].verbose_name) + ' ' + unicode(ar.param_values.primary_coachings)

    @classmethod
    def get_create_permission(self, ar):
        #~ logger.info("20121011 Coachings.get_create_permission()")
        if not ar.get_user().coaching_type:
            return
        return super(Coachings, self).get_create_permission(ar)


class CoachingsByClient(Coachings):

    """
    The :class:`Coachings` table in a :class:`Clients` detail.
    """
    required = dd.required()
    #~ debug_permissions = 20121016
    master_key = 'client'
    order_by = ['start_date']
    column_names = 'start_date end_date user:12 primary type:12 ending id'
    hidden_columns = 'id'
    auto_fit_column_widths = True


class CoachingsByUser(Coachings):
    required = dd.required()
    master_key = 'user'
    column_names = 'start_date end_date client type primary id'


class CoachingsByEnding(Coachings):
    master_key = 'ending'

#~ class MyCoachings(Coachings,mixins.ByUser):
    #~ column_names = 'start_date end_date client type primary id'

#~ class MySuggestedCoachings(MyCoachings):
    #~ label = _("Suggested coachings")
    #~ known_values = dict(state=CoachingStates.suggested)


__all__ = [ 
    "CoachingType", "CoachingTypes", "CoachingEnding",
    "CoachingEndings", "Coaching", "Coachings", "CoachingsByClient",
    "CoachingsByUser", "CoachingsByEnding"
]