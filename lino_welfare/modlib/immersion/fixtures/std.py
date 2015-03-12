# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
# License: BSD (see file COPYING for details)
"""Adds some training types and some training goals.

TODO: ask Mathieu and Gerd for their advice in establishing a more or
less complete/useful set of default data.  See also `leforem.be
<https://www.leforem.be/particuliers/seformer/stages/stages-en-entreprises.html>`_.

"""

from django.utils.translation import ugettext_lazy as _

from lino.api import rt, dd


def objects():
    TT = rt.modules.immersion.ContractType
    Goal = rt.modules.immersion.Goal

    def str2obj(model, name):
        return model(**dd.str2kw('name', name))

    yield str2obj(TT, _("Internal engagement"))
    yield str2obj(TT, _("Immersion training"))
    yield str2obj(TT, _("MISIP"))

    yield str2obj(Goal, _("Discover a job"))
    yield str2obj(Goal, _("Confirm a professional project"))
    yield str2obj(Goal, _("Gain work experience"))
    yield str2obj(Goal, _("Show competences"))

    kw = dict(
        email_template='Default.eml.html',
        body_template='immersion.body.html',
        primary=True, certifying=True,
        template='Default.odt',
        **dd.str2kw('name', _("Immersion training")))
    rt.modules.excerpts.ExcerptType.update_for_model(
        'immersion.Contract', **kw)
