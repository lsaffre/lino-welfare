# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
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
Demo data for `lino_welfare.modlib.uploads`.
"""

from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

from lino.modlib.uploads.choicelists import Shortcuts

from lino_welfare.modlib.uploads.fixtures.std import (
    UPLOADTYPE_RESIDENCE_PERMIT,
    UPLOADTYPE_WORK_PERMIT,
    UPLOADTYPE_DRIVING_LICENSE)


def objects():
    Upload = rt.modules.uploads.Upload
    UploadType = rt.modules.uploads.UploadType
    Client = rt.modules.pcsw.Client
    ClientStates = rt.modules.pcsw.ClientStates

    # create some random uploads, all uploaded by hubert
    hubert = rt.login('hubert')
    CLIENTS = Cycler(rt.modules.pcsw.CoachedClients.request(user=hubert))
    UPLOAD_TYPES = Cycler(UploadType.objects.all())
    for i in range(3):
        cli = CLIENTS.pop()
        for j in range(2):
            obj = Upload(
                project=cli,
                owner=cli,
                # user=hubert,
                end_date=settings.SITE.demo_date(360+i*10),
                type=UPLOAD_TYPES.pop())
            obj.on_create(hubert)  # sets `user` and `needed`
            yield obj

    # some upload stories

    newcomer = Client.objects.get(id=121)
    coached = Client.objects.get(id=124)

    # assert newcomer.client_state == ClientStates.newcomer
    # assert coached.client_state == ClientStates.coached
    # true only for eupen, not for chatelet

    id_card = UploadType.objects.get(shortcut=Shortcuts.id_document)
    residence_permit = UploadType.objects.get(id=UPLOADTYPE_RESIDENCE_PERMIT)
    work_permit = UploadType.objects.get(id=UPLOADTYPE_WORK_PERMIT)
    driving_license = UploadType.objects.get(id=UPLOADTYPE_DRIVING_LICENSE)

    # a reception clerk:
    clerk = rt.login('theresia').get_user()

    # a general social agent:
    agent = rt.login('caroline').get_user()

    # an integration agent:
    ai = rt.login('alicia').get_user()

    # this newcomer has 2 id cards. one of these is no longer valid
    # (and we know it: `needed` has been unchecked). The other is
    # still valid but will expire in 3 days.

    kw = dict(owner=newcomer, type=id_card)
    yield Upload(end_date=dd.demo_date(-30), needed=False,
                 user=clerk, **kw)
    yield Upload(end_date=dd.demo_date(3), user=clerk, **kw)

    # this coached client has three documents uploaded:

    kw = dict(owner=coached)
    yield Upload(type=residence_permit, end_date=dd.demo_date(300),
                 user=clerk, **kw)
    yield Upload(type=work_permit, end_date=dd.demo_date(100),
                 user=ai, **kw)
    yield Upload(type=driving_license, end_date=dd.demo_date(10),
                 user=agent, **kw)

