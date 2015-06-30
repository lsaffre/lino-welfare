.. _welfare.specs.ledger:
===========================================
Ledger for Lino Welfare (Sozialbuchhaltung)
===========================================

.. How to test only this document:
  $ python setup.py test -s tests.SpecsTests.test_ledger

This document describes the new functionalities implemented as a
project called "Sozialbuchhaltung" and started in May 2015.

.. contents::
   :depth: 1
   :local:

A tested document
=================

This document is being tested using doctest with the following
initializations:

>>> from __future__ import print_function
>>> import os
>>> os.environ['DJANGO_SETTINGS_MODULE'] = \
...    'lino_welfare.projects.std.settings.doctests'
>>> from lino.utils.xmlgen.html import E
>>> from lino.api.doctest import *
>>> from lino.api import rt

Implementation notes
====================

This project integrates several plugins into Lino Welfare:
:mod:`lino.modlib.ledger`, 
:mod:`lino.modlib.vatless` and
:mod:`lino.modlib.finan`.

A **voucher** (German *Beleg*) is a document which serves as legal
proof for a transaction. A transaction is a set of **movements** whose
debit equals to their credit.

Lino Welfare uses the following voucher types:

>>> rt.show(rt.modules.ledger.VoucherTypes)
======================== ====== ======================================
 value                    name   text
------------------------ ------ --------------------------------------
 vatless.AccountInvoice          Invoice (vatless.AccountInvoice)
 finan.JournalEntry              Journal Entry (finan.JournalEntry)
 finan.PaymentOrder              Payment Order (finan.PaymentOrder)
 finan.BankStatement             Bank Statement (finan.BankStatement)
 finan.Grouper                   Grouper (finan.Grouper)
======================== ====== ======================================
<BLANKLINE>

What is a voucher type? See :class:`lino.modlib.ledger.choicelists.VoucherTypes`.


>>> rt.show(rt.modules.ledger.Journals, column_names="ref name voucher_type")
=========== =================== ================== ==================== ======================================
 Reference   Designation         Designation (fr)   Designation (de)     voucher type
----------- ------------------- ------------------ -------------------- --------------------------------------
 PRC         Purchase invoices   Factures achat     Einkaufsrechnungen   Invoice (vatless.AccountInvoice)
 KBC         KBC                 KBC                KBC                  Bank Statement (finan.BankStatement)
 POKBC       PO KBC              PO KBC             PO KBC               Payment Order (finan.PaymentOrder)
=========== =================== ================== ==================== ======================================
<BLANKLINE>

>>> rt.show(rt.modules.ledger.VoucherStates)
======= ============ ============
 value   name         text
------- ------------ ------------
 10      draft        Draft
 20      registered   Registered
 30      fixed        Fixed
======= ============ ============
<BLANKLINE>

.. technical:

    The `VoucherStates` choicelist is used by two fields: one database
    field and one parameter field.

    >>> len(rt.modules.ledger.VoucherStates._fields)
    2
    >>> for f in rt.modules.ledger.VoucherStates._fields:
    ...     model = getattr(f, 'model', None)
    ...     if model:
    ...        print("%s.%s.%s" % (model._meta.app_label, model.__name__, f.name))
    ledger.Voucher.state

    >>> obj = rt.modules.vatless.AccountInvoice.objects.get(id=1)
    >>> ar = rt.login("robin").spawn(rt.modules.vatless.Invoices)
    >>> print(E.tostring(obj.workflow_buttons(ar)))
    <span><b>Registered</b> &#8594; [Deregister]</span>
    

>>> jnl = rt.modules.ledger.Journal.get_by_ref('PRC')
>>> rt.show(rt.modules.vatless.InvoicesByJournal, jnl)
========= ========= ============================ =================== ============ ========== ============ ================
 number    Date      Client                       Partner             Amount       Due date   Author       Workflow
--------- --------- ---------------------------- ------------------- ------------ ---------- ------------ ----------------
 20        2/16/14   KAIVERS Karl (141)           Kimmel Killian      5,33                    Robin Rood   **Registered**
 19        2/21/14                                Castou Carmen       120,00                  Robin Rood   **Registered**
 18        2/26/14   JONAS Josef (139)            Wehnicht Werner     29,95                   Robin Rood   **Registered**
 17        3/3/14    JEANÉMART Jérôme (181)       Waldmann Waltraud   25,00                   Robin Rood   **Registered**
 16        3/8/14    JACOBS Jacqueline (137)      Kimmel Killian      22,50                   Robin Rood   **Registered**
 15        3/13/14   HILGERS Hildegard (133)      Waldmann Walter     5,33                    Robin Rood   **Registered**
 14        3/18/14   GROTECLAES Gregory (132)     Wehnicht Werner     120,00                  Robin Rood   **Registered**
 13        3/23/14   FAYMONVILLE Luc (130*)       Waldmann Waltraud   29,95                   Robin Rood   **Registered**
 12        3/28/14   EVERS Eberhart (127)         Kimmel Killian      25,00                   Robin Rood   **Registered**
 11        4/2/14    ENGELS Edgar (129)           Castou Carmen       22,50                   Robin Rood   **Registered**
 10        4/7/14                                 Wehnicht Werner     5,33                    Robin Rood   **Registered**
 9         4/12/14   EMONTS-GAST Erna (152)       Waldmann Waltraud   120,00                  Robin Rood   **Registered**
 8         4/17/14   EMONTS Daniel (128)          Kimmel Killian      29,95                   Robin Rood   **Registered**
 7         4/22/14   DUBOIS Robin (179)           Waldmann Walter     25,00                   Robin Rood   **Registered**
 6         4/27/14   DOBBELSTEIN Dorothée (124)   Wehnicht Werner     22,50                   Robin Rood   **Registered**
 5         5/2/14    DENON Denis (180*)           Waldmann Waltraud   5,33                    Robin Rood   **Registered**
 4         5/7/14    COLLARD Charlotte (118)      Kimmel Killian      120,00                  Robin Rood   **Registered**
 3         5/12/14   BRECHT Bernd (177)           Castou Carmen       29,95                   Robin Rood   **Registered**
 2         5/17/14   AUSDEMWALD Alfons (116)      Wehnicht Werner     25,00                   Robin Rood   **Registered**
 1         5/22/14                                Waldmann Waltraud   22,50                   Robin Rood   **Registered**
 **210**                                                              **811,12**
========= ========= ============================ =================== ============ ========== ============ ================
<BLANKLINE>
    
>>> obj = rt.modules.vatless.AccountInvoice.objects.get(id=1)
>>> obj.state
<VoucherStates.registered:20>



>>> rt.show(rt.modules.ledger.MovementsByVoucher, obj)
========= ============================================= =========== =========== ======= ===========
 Seq.No.   Account                                       Debit       Credit      Match   Satisfied
--------- --------------------------------------------- ----------- ----------- ------- -----------
 1         (820/333/01) Vorschuss auf Vergütungen o.ä.   10,00                           No
 2         (821/333/01) Vorschuss auf Pensionen          12,50                           No
 3         (4400) Suppliers                                          22,50               No
 **6**                                                   **22,50**   **22,50**           **0**
========= ============================================= =========== =========== ======= ===========
<BLANKLINE>


Relics
======

The following is no longer valid.

This project adds two new plugins :mod:`lino_welfare.modlib.ledger`
and :mod:`lino_welfare.modlib.finan`, which are extensions of
:mod:`lino.modlib.ledger` and :mod:`lino.modlib.finan` respectively.

A first important thing to add is the `recipient` concept
(Zahlungsempfänger), i.e. inject two fields `recipient` and
`bank_account` into the following models:

- into the *ledger.AccountInvoice* model
- into each *finan.FinancialVoucherItem*-based model
- into the *ledger.Movement* model

This is implemented as the
:class:`lino_welfare.modlib.ledger.mixins.PaymentRecipient` mixin.

>> from lino_welfare.modlib.ledger.mixins import PaymentRecipient
>> assert issubclass(ledger.AccountInvoice, PaymentRecipient)
>> assert issubclass(finan.BankStatementItem, PaymentRecipient)
>> assert issubclass(ledger.Movement, PaymentRecipient)

Since there is a lot of injection here, I start to wonder whether we
shouldn't rather do ticket :ticket:`246` (Work around inject_field)
first.  Also e.g. to define a choosers and validation methods for
these fields.



======= ==================== ============ ========================
 ID      Designation          Can refund   Debt collection agency
------- -------------------- ------------ ------------------------
 1       Krankenkasse         No           No
 2       Apotheke             No           No
 3       Arbeitsvermittler    No           No
 4       Gerichtsvollzieher   No           Yes
 5       Inkassounternehmen   No           Yes
 6       Facharzt             Yes          No
 7       Hausarzt             Yes          No
 8       Zahnarzt             Yes          No
 9       Gynäkologe           Yes          No
 10      Augenarzt            Yes          No
 11      Kinderarzt           Yes          No
======= ==================== ============ ========================