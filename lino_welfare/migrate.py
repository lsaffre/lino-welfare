# -*- coding: UTF-8 -*-
## Copyright 2011-2012 Luc Saffre
## This file is part of the Lino project.
## Lino is free software; you can redistribute it and/or modify 
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
## Lino is distributed in the hope that it will be useful, 
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
## GNU General Public License for more details.
## You should have received a copy of the GNU General Public License
## along with Lino; if not, see <http://www.gnu.org/licenses/>.

"""
This is a real-world example of how the application developer 
can provide automatic data migrations for 
:doc:`python dumps </topics/dumpy>`.

This module is used when loading a python dump that was 
created by a previous version.
Lino writes the corresponding ``import`` statement 
into every python dump because
:mod:`lino_welfare.settings.Lino` has
:attr:`lino.Lino.migration_module` 
set to ``"lino_welfare.modlib.pcsw.migrate"``.

"""

import datetime
from decimal import Decimal
from django.conf import settings
from lino.core.modeltools import resolve_model
from lino.utils import mti
from lino.utils import dblogger

def migrate_from_1_4_10(globals_dict):
    """
    - convert contacts.Partner.region from a CHAR to a FK(City)
    - add a Default accounts.Chart for debts module
    - debts.Account renamed to accounts.Account
    - debts.AccountGroup renamed to accounts.AccountGroup
    - convert Persons to Clients
    - fill Coachings from fields coached_from, coached_until, coach1, coach2
    - fill pcsw.Thirds from fields health_insurance, pharmacy, job_office_contact
    """
    
    countries_City = resolve_model("countries.City")
    debts_Account = resolve_model("accounts.Account")    
    debts_AccountGroup = resolve_model("accounts.Group")
    contacts_Partner = resolve_model("contacts.Partner")
    contacts_Company = resolve_model("contacts.Company")
    contacts_Person = resolve_model("contacts.Person")
    households_Household = resolve_model("households.Household")
    pcsw_Client = resolve_model("pcsw.Client")
    pcsw_Coaching = resolve_model("pcsw.Coaching")
    pcsw_ClientContact = resolve_model("pcsw.ClientContact")
    cal_Event = resolve_model("cal.Event")
    cal_Task = resolve_model("cal.Task")
    lino_HelpText = resolve_model("lino.HelpText")
    outbox_Attachment = resolve_model("outbox.Attachment")
    outbox_Mail = resolve_model("outbox.Mail")
    postings_Posting = resolve_model("postings.Posting")
    uploads_Upload = resolve_model("uploads.Upload")
    pcsw_CoachingType = resolve_model("pcsw.CoachingType")
    pcsw_ClientContactType = resolve_model("pcsw.ClientContactType")
    accounts_Chart = resolve_model("accounts.Chart")    
    isip_Contract = resolve_model("isip.Contract")
    jobs_Contract = resolve_model("jobs.Contract")
    contacts_Role = resolve_model("contacts.Role")
    
    NOW = datetime.datetime(2012,9,6,0,0)
    
    from lino.modlib.countries.models import CityTypes
    from lino.utils.mti import create_child
    from lino_welfare.modlib.pcsw import models as pcsw
    
    def convert_region(region):
        region = region.strip()
        if not region: return None
        try:
            return countries_City.objects.get(name=region,country__id='BE')
        except countries_City.DoesNotExist:
            o = countries_City(name=region,country__id='BE')
            o.full_clean()
            o.save()
            logger.info("Created region %s",o)
            return o
            
    def create_contacts_partner(id, country_id, city_id, name, addr1, street_prefix, street, street_no, street_box, addr2, zip_code, region, language, email, url, phone, gsm, fax, remarks):
        region = convert_region(region)
        return contacts_Partner(id=id,country_id=country_id,city_id=city_id,name=name,addr1=addr1,street_prefix=street_prefix,street=street,street_no=street_no,street_box=street_box,addr2=addr2,zip_code=zip_code,region=region,language=language,email=email,url=url,phone=phone,gsm=gsm,fax=fax,remarks=remarks,modified=NOW,created=NOW)
    globals_dict.update(create_contacts_partner=create_contacts_partner)
    
    def create_countries_city(id, name, country_id, zip_code, inscode):
        return countries_City(id=id,name=name,
            type=CityTypes.city,
            country_id=country_id,zip_code=zip_code,inscode=inscode)    
    globals_dict.update(create_countries_city=create_countries_city)
    
    def create_debts_account(id, name, seqno, group_id, type, required_for_household, required_for_person, periods, help_text, name_fr, name_en):
        if periods is not None: periods = Decimal(periods)
        return debts_Account(id=id,name=name,seqno=seqno,group_id=group_id,type=type,required_for_household=required_for_household,required_for_person=required_for_person,periods=periods,help_text=help_text,name_fr=name_fr,name_en=name_en)
    globals_dict.update(create_debts_account=create_debts_account)
    
    def create_debts_accountgroup(id, name, seqno, account_type, help_text, name_fr, name_en):
        #~ return debts_AccountGroup(id=id,chart_id=1,name=name,seqno=seqno,account_type=account_type,help_text=help_text,name_fr=name_fr,name_en=name_en)    
        return debts_AccountGroup(id=id,chart_id=1,name=name,ref=str(seqno),account_type=account_type,help_text=help_text,name_fr=name_fr,name_en=name_en)    
    globals_dict.update(create_debts_accountgroup=create_debts_accountgroup)
    
    def create_contacts_company(partner_ptr_id, prefix, vat_id, type_id, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, hourly_rate):
        return create_child(contacts_Partner,partner_ptr_id,contacts_Company,prefix=prefix,vat_id=vat_id,type_id=type_id,
            #~ is_active=is_active,
            #~ newcomer=newcomer,
            is_deprecated=is_deprecated,activity_id=activity_id,
            bank_account1=bank_account1,bank_account2=bank_account2,
            #~ hourly_rate=hourly_rate
            )
    globals_dict.update(create_contacts_company=create_contacts_company)
    
    def create_households_household(partner_ptr_id, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, prefix, type_id):
        return create_child(contacts_Partner,partner_ptr_id,households_Household,
          #~ is_active=is_active,newcomer=newcomer,
          is_deprecated=is_deprecated,activity_id=activity_id,bank_account1=bank_account1,bank_account2=bank_account2,prefix=prefix,type_id=type_id)    
    globals_dict.update(create_households_household=create_households_household)
    
    def create_contacts_person(partner_ptr_id, birth_date, first_name, last_name, title, gender, is_active, newcomer, is_deprecated, activity_id, bank_account1, bank_account2, remarks2, gesdos_id, is_cpas, is_senior, group_id, coached_from, coached_until, coach1_id, coach2_id, birth_place, birth_country_id, civil_state, national_id, health_insurance_id, pharmacy_id, nationality_id, card_number, card_valid_from, card_valid_until, card_type, card_issuer, noble_condition, residence_type, in_belgium_since, unemployed_since, needs_residence_permit, needs_work_permit, work_permit_suspended_until, aid_type_id, income_ag, income_wg, income_kg, income_rente, income_misc, is_seeking, unavailable_until, unavailable_why, obstacles, skills, job_agents, job_office_contact_id, broker_id, faculty_id):
        yield create_child(contacts_Partner,partner_ptr_id,contacts_Person,
            birth_date=birth_date,
            first_name=first_name,last_name=last_name,title=title,gender=gender,
            #~ is_active=is_active,newcomer=newcomer,
            is_deprecated=is_deprecated,
            activity_id=activity_id,
            bank_account1=bank_account1,bank_account2=bank_account2)
        #~ if national_id and national_id.strip() != '0' and not is_deprecated:
        if national_id.strip() == '0':
            national_id = ''
        if gesdos_id and not national_id:
            national_id = str(partner_ptr_id)
        if national_id:
            #~ if is_deprecated:
                #~ national_id += ' (A)'
            client_state = pcsw.ClientStates.coached
            if newcomer:
                client_state = pcsw.ClientStates.new
            elif not is_active:
                client_state = pcsw.ClientStates.former
            yield create_child(contacts_Person,partner_ptr_id,pcsw_Client,
                #~ birth_date=birth_date,
                #~ first_name=first_name,last_name=last_name,title=title,gender=gender,
                #~ is_active=is_active,newcomer=newcomer,is_deprecated=is_deprecated,
                #~ activity_id=activity_id,
                #~ bank_account1=bank_account1,bank_account2=bank_account2,
                remarks2=remarks2,gesdos_id=gesdos_id,is_cpas=is_cpas,
                is_senior=is_senior,group_id=group_id,
                #~ coached_from=coached_from,coached_until=coached_until,
                #~ coach1_id=coach1_id,coach2_id=coach2_id,
                birth_place=birth_place,
                birth_country_id=birth_country_id,civil_state=civil_state,
                national_id=national_id,
                client_state=client_state,
                health_insurance_id=health_insurance_id,pharmacy_id=pharmacy_id,
                nationality_id=nationality_id,card_number=card_number,card_valid_from=card_valid_from,card_valid_until=card_valid_until,card_type=card_type,card_issuer=card_issuer,noble_condition=noble_condition,residence_type=residence_type,in_belgium_since=in_belgium_since,unemployed_since=unemployed_since,needs_residence_permit=needs_residence_permit,needs_work_permit=needs_work_permit,work_permit_suspended_until=work_permit_suspended_until,aid_type_id=aid_type_id,income_ag=income_ag,income_wg=income_wg,income_kg=income_kg,income_rente=income_rente,income_misc=income_misc,is_seeking=is_seeking,unavailable_until=unavailable_until,unavailable_why=unavailable_why,obstacles=obstacles,skills=skills,job_agents=job_agents,
                job_office_contact_id=job_office_contact_id,broker_id=broker_id,faculty_id=faculty_id)
            #~ if coached_from or coached_until:
            def user2type(user_id):
                #~ pcsw_CoachingType
                if user_id in (200085,200093,200096,200099): return 2 # DSBE
                return 1
            if coach2_id and coach2_id != coach1_id:
                ti = user2type(coach2_id)
                kw = dict(
                    project_id=partner_ptr_id,
                    user_id=coach2_id,
                    type_id=ti)
                if ti == 1:
                    kw.update(start_date=coached_from,end_date=coached_until)
                yield pcsw_Coaching(**kw)
                
            if coach1_id:
                ti = user2type(coach1_id)
                kw = dict(
                    project_id=partner_ptr_id,
                    user_id=coach1_id,
                    primary=True,
                    type_id=ti)
                if ti == 1:
                    kw.update(start_date=coached_from,end_date=coached_until)
                yield pcsw_Coaching(**kw)
              
                #~ yield pcsw_Coaching(
                    #~ project_id=partner_ptr_id,
                    #~ start_date=coached_from,
                    #~ end_date=coached_until,
                    #~ primary=True,
                    #~ user_id=coach1_id,
                    #~ type_id=user2type(coach1_id))
            if health_insurance_id:
                yield pcsw_ClientContact(
                    project_id=partner_ptr_id,
                    #~ type=pcsw.ClientContactTypes.health_insurance,
                    type_id=1,
                    company_id=health_insurance_id)
            if pharmacy_id:
                yield pcsw_ClientContact(
                    project_id=partner_ptr_id,
                    #~ type=pcsw.ClientContactTypes.pharmacy,
                    type_id=2,
                    company_id=pharmacy_id)
            if job_office_contact_id:
                contact = contacts_Role.objects.get(pk=job_office_contact_id)
                yield pcsw_ClientContact(
                    project_id=partner_ptr_id,
                    #~ type=pcsw.ClientContactTypes.job_office,
                    type_id=3,
                    company_id=settings.LINO.site_config.job_office.id,
                    contact_person=contact.person)
        else:
            #~ silently ignored if lost: 
            #~ is_cpas is_senior coach1_id coach2_id 
            lost_fields = """
            remarks2 gesdos_id 
            group_id 
            coached_from coached_until
            birth_place 
            birth_country_id civil_state
            national_id
            health_insurance_id pharmacy_id
            nationality_id card_number card_valid_from
            card_valid_until card_type card_issuer
            noble_condition residence_type
            in_belgium_since unemployed_since
            needs_residence_permit needs_work_permit
            work_permit_suspended_until aid_type_id 
            income_ag income_wg income_kg income_rente
            income_misc is_seeking unavailable_until
            unavailable_why obstacles skills job_agents
            job_office_contact_id broker_id faculty_id
            """.split()
            lost = dict()
            for n in lost_fields:
                v = locals().get(n)
                if v:
                    lost[n] = v
            if lost:
                dblogger.warning("Lost data for Person %s without NISS: %s",
                    partner_ptr_id,lost)
                p = contacts_Person.objects.get(pk=partner_ptr_id)
                if p.remarks:
                    p.remarks += '\n'
                p.remarks += '20120901 lost: ' + repr(lost)
                p.save()
    globals_dict.update(create_contacts_person=create_contacts_person)
    
    
    
    from django.contrib.contenttypes.models import ContentType
    def new_content_type_id(m):
        if m is None: return m
        # if not fmn: return None
        # m = resolve_model(fmn)
        if m is contacts_Person:
            m = pcsw_Client
        ct = ContentType.objects.get_for_model(m)
        if ct is None: 
            raise Exception("Ignored GFK to unknown model %s" % m)
            #~ logger.warning("Ignored GFK to unknown model %s",m)
            #~ return None
        return ct.pk
    
    def create_cal_event(id, owner_type_id, owner_id, user_id, created, modified, project_id, build_time, start_date, start_time, end_date, end_time, uid, summary, description, calendar_id, access_class, sequence, auto_type, transparent, place_id, priority_id, state):
        owner_type_id = new_content_type_id(owner_type_id)
        return cal_Event(id=id,owner_type_id=owner_type_id,owner_id=owner_id,user_id=user_id,created=created,modified=modified,project_id=project_id,build_time=build_time,start_date=start_date,start_time=start_time,end_date=end_date,end_time=end_time,uid=uid,summary=summary,description=description,calendar_id=calendar_id,access_class=access_class,sequence=sequence,auto_type=auto_type,transparent=transparent,place_id=place_id,priority_id=priority_id,state=state)    
    globals_dict.update(create_cal_event=create_cal_event)
    def create_cal_task(id, owner_type_id, owner_id, user_id, created, modified, project_id, start_date, start_time, uid, summary, description, calendar_id, access_class, sequence, auto_type, due_date, due_time, percent, state):
        owner_type_id = new_content_type_id(owner_type_id)
        return cal_Task(id=id,owner_type_id=owner_type_id,owner_id=owner_id,user_id=user_id,created=created,modified=modified,project_id=project_id,start_date=start_date,start_time=start_time,uid=uid,summary=summary,description=description,calendar_id=calendar_id,access_class=access_class,sequence=sequence,auto_type=auto_type,due_date=due_date,due_time=due_time,percent=percent,state=state)        
    globals_dict.update(create_cal_task=create_cal_task)
    def create_lino_helptext(id, content_type_id, field, help_text):
        content_type_id = new_content_type_id(content_type_id)
        return lino_HelpText(id=id,content_type_id=content_type_id,field=field,help_text=help_text)        
    globals_dict.update(create_lino_helptext=create_lino_helptext)
    def create_outbox_attachment(id, owner_type_id, owner_id, mail_id):
        owner_type_id = new_content_type_id(owner_type_id)
        return outbox_Attachment(id=id,owner_type_id=owner_type_id,owner_id=owner_id,mail_id=mail_id)
    globals_dict.update(create_outbox_attachment=create_outbox_attachment)
    def create_outbox_mail(id, owner_type_id, owner_id, user_id, project_id, date, subject, body, sent):
        owner_type_id = new_content_type_id(owner_type_id)
        return outbox_Mail(id=id,owner_type_id=owner_type_id,owner_id=owner_id,user_id=user_id,project_id=project_id,date=date,subject=subject,body=body,sent=sent)        
    globals_dict.update(create_outbox_mail=create_outbox_mail)
    def create_postings_posting(id, owner_type_id, owner_id, user_id, project_id, partner_id, state, date):
        owner_type_id = new_content_type_id(owner_type_id)
        return postings_Posting(id=id,owner_type_id=owner_type_id,owner_id=owner_id,user_id=user_id,project_id=project_id,partner_id=partner_id,state=state,date=date)    
    globals_dict.update(create_postings_posting=create_postings_posting)
    def create_uploads_upload(id, owner_type_id, owner_id, user_id, created, modified, file, mimetype, type_id, valid_until, description):
        owner_type_id = new_content_type_id(owner_type_id)
        return uploads_Upload(id=id,owner_type_id=owner_type_id,owner_id=owner_id,user_id=user_id,created=created,modified=modified,file=file,mimetype=mimetype,type_id=type_id,valid_until=valid_until,description=description)    
    globals_dict.update(create_uploads_upload=create_uploads_upload)
    
    def create_isip_contract(id, user_id, build_time, person_id, company_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, stages, goals, duties_asd, duties_dsbe, duties_company, duties_person):
        contact = contacts_Role.objects.get(pk=contact_id)
        return isip_Contract(id=id,user_id=user_id,build_time=build_time,
          client_id=person_id,
          company_id=company_id,
          contact_person=contact.person,
          contact_role=contact.type,
          #~ contact_id=contact_id,
          language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,stages=stages,goals=goals,duties_asd=duties_asd,duties_dsbe=duties_dsbe,duties_company=duties_company,duties_person=duties_person)    
    globals_dict.update(create_isip_contract=create_isip_contract)
    
    def create_jobs_contract(id, user_id, build_time, person_id, company_id, contact_id, language, applies_from, applies_until, date_decided, date_issued, user_asd_id, exam_policy_id, ending_id, date_ended, type_id, job_id, duration, regime_id, schedule_id, hourly_rate, refund_rate, reference_person, responsibilities, remark):
        if hourly_rate is not None: hourly_rate = Decimal(hourly_rate)
        contact = contacts_Role.objects.get(pk=contact_id)
        return jobs_Contract(id=id,user_id=user_id,build_time=build_time,
          client_id=person_id,
          company_id=company_id,
          contact_person=contact.person,
          contact_role=contact.type,
          language=language,applies_from=applies_from,applies_until=applies_until,date_decided=date_decided,date_issued=date_issued,user_asd_id=user_asd_id,exam_policy_id=exam_policy_id,ending_id=ending_id,date_ended=date_ended,type_id=type_id,job_id=job_id,duration=duration,regime_id=regime_id,schedule_id=schedule_id,hourly_rate=hourly_rate,refund_rate=refund_rate,reference_person=reference_person,responsibilities=responsibilities,remark=remark)    
    globals_dict.update(create_jobs_contract=create_jobs_contract)
    
    objects = globals_dict['objects']
    def new_objects():
        yield accounts_Chart(name="debts Default")
        yield pcsw_ClientContactType(name="Krankenkasse")
        yield pcsw_ClientContactType(name="Apotheke")
        yield pcsw_ClientContactType(name="Arbeitsvermittler")
        yield pcsw_ClientContactType(name="Gerichtsvollzieher")
        yield pcsw_CoachingType(name="ASD")
        yield pcsw_CoachingType(name="DSBE")
        yield pcsw_CoachingType(name="Schuldnerberatung")
        yield objects()
    globals_dict.update(objects=new_objects)
    
    #~ return '1.4.11'
    return '0.1.0'
