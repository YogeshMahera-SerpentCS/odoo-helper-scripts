# -*- coding: utf-8 -*-
# Copyright © 2017-2018 Dmytro Katyukha <dmytro.katyukha@gmail.com>

#######################################################################
# This Source Code Form is subject to the terms of the Mozilla Public #
# License, v. 2.0. If a copy of the MPL was not distributed with this #
# file, You can obtain one at http://mozilla.org/MPL/2.0/.            #
#######################################################################

""" Local odoo connection lib
"""
import os
import atexit
import functools
import pkg_resources

# Odoo package import and start services logic are based on code:
#     https://github.com/tinyerp/erppeek
# With PR #92 applied: https://github.com/tinyerp/erppeek/pull/92
# Removed support of Odoo versions less then 7.0

# Import odoo package
try:
    # Odoo 10.0+

    # this is required if there are addons installed via setuptools_odoo
    pkg_resources.declare_namespace('odoo.addons')

    # import odoo itself
    import odoo
    import odoo.release  # to avoid 9.0 with odoo.py on path
except (ImportError, KeyError):
    try:
        # Odoo 9.0 and less versions
        import openerp as odoo
    except ImportError:
        raise

if odoo.release.version_info < (7,):
    raise ImportError(
        "Odoo version %s is not supported!" % odoo.release.version_info)

# Check Odoo API version
odoo._api_v7 = odoo.release.version_info < (8,)

# Prepare odoo environments
os.putenv('TZ', 'UTC')
os.putenv('PGAPPNAME', 'lodoo')


class LocalModel(object):
    """ Simple wrapper for Odoo models

        just proxy method calls to model class
    """
    def __init__(self, client, name):
        self._client = client
        self._name = name

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return self._client.call_method(self._name, name, *args, **kwargs)
        return wrapper


class LocalRegistry(object):
    """ Simple proxy for Odoo registry
    """
    def __init__(self, client, dbname):
        self._client = client
        self._dbname = dbname
        self._env = None

        if self.odoo._api_v7:
            self.registry = self.odoo.modules.registry.RegistryManager.get(self._dbname)
            self.cursor = self.registry.db.cursor()
        else:
            # For odoo 8, 9, 10, 11, +(?) there is special
            # function `odoo.registry` to get registry instance for db
            self.registry = self.odoo.registry(self._dbname)
            self.cursor = self.registry.cursor()

    @property
    def odoo(self):
        return self._client.odoo

    @property
    def env(self):
        self.require_v8_api()

        if self._env is None:
            self._env = self.odoo.api.Environment(
                self.cursor, self.odoo.SUPERUSER_ID, {})

        return self._env

    def require_v8_api(self):
        if self.odoo._api_v7:
            raise NotImplementedError(
                "Using *env* is not supported for this Odoo version")

    def recompute_fields(self, model, fields):
        """ Recompute specifed model fields

            This usualy applicable for stored, field, that was not recomputed
            due to errors in compute method for example.
        """
        Model = self.env[model]
        records = Model.search([])
        for field in fields:
            self.env.add_todo(Model._fields[field], records)
        Model.recompute()
        self.env.cr.commit()

    def recompute_parent_store(self, model):
        """ Recompute parent store

            some times parent left/right was not recomputed after update.
            this method can fix it
        """
        self.env[model]._parent_store_compute()
        self.env.cr.commit()

    def compute_translation_rate(self, lang, addons):
        trans = self.env['ir.translation'].search([
            ('module', 'in', addons),
            ('lang', '=', lang),
        ])
        bad_translations = trans.filtered(
            lambda r: not r.value or
                      not r.value.strip() or
                      r.src == r.value or
                      r.source == r.value)

        rate_by_addon = {}
        for addon in addons:
            addon_data = rate_by_addon[addon] = {}

            addon_data['terms_total'] = trans_total = len(trans.filtered(
                lambda r: r.module == addon))
            addon_data['terms_untranslated'] = trans_fail = len(
                bad_translations.filtered(lambda r: r.module == addon))

            if trans_total:
                addon_data['rate'] = 1.0 - (float(trans_fail) /
                                              float(trans_total))
            else:
                addon_data['rate'] = 0.0

            addon_data['rate'] *= 100.0

        if trans:
            total_rate = 1.0 - float(len(bad_translations)) / float(len(trans))
        else:
            total_rate = 0.0

        total_rate *= 100.0
        return {
            'total_rate': total_rate,
            'terms_total': len(trans),
            'terms_untranslated': len(bad_translations),
            'by_addon': rate_by_addon,
        }

    def print_translation_rate(self, translation_rate):
        """ Print translation rate computed by `compute_translation_rate`
        """
        name_col_width = max([len(i) for i in translation_rate['by_addon']])

        header_format_str = "%%-%ds | %%10s | %%15s | %%+10s" % name_col_width
        row_format_str = "%%-%ds | %%10s | %%15s | %%7.2f" % name_col_width
        spacer_str = "-" * (name_col_width + 3 + 10 + 3 + 15 + 3 + 10)

        # Print header
        print (header_format_str % (
               'Addon', 'Total', 'Untranslated', 'Rate'))
        print (spacer_str)

        # Print translation rate by addon
        for addon, rate_data in translation_rate['by_addon'].items():
            print(row_format_str % (
                  addon, rate_data['terms_total'],
                  rate_data['terms_untranslated'],
                  rate_data['rate']))

        # Print total translation rate
        print (spacer_str)
        print(row_format_str % (
              'TOTAL', translation_rate['terms_total'],
              translation_rate['terms_untranslated'],
              translation_rate['total_rate'],
        ))

    def assert_translation_rate(self, rate, min_total_rate=None,
                                min_addon_rate=None):
        """ Check translation rate, and return number, that can be used as exit
            code
        """
        if min_total_rate is not None and rate['total_rate'] < min_total_rate:
            return 1;

        if min_addon_rate is not None:
            for addon, rate_data in rate['by_addon'].items():
                if rate_data['rate'] < min_addon_rate:
                    return 2;
        return 0;

    def call_method(self, model, method, *args, **kwargs):
        """ Simple wrapper to call local model methods for database
        """
        if self.odoo._api_v7:
            return getattr(self.registry[model], method)(
                self.cursor, self.odoo.SUPERUSER_ID, *args, **kwargs)
        else:
            # For odoo 8, 9, 10, +(?) there is special function `odoo.registry`
            # to get registry instance for db
            return getattr(self.env[model], method)(*args, **kwargs)

    def __getitem__(self, name):
        return LocalModel(self, name)


class LocalDBService(object):
    def __init__(self, client):
        self._client = client
        self._dispatch = None

    @property
    def odoo(self):
        return self._client.odoo

    @property
    def dispatch(self):
        if self._dispatch is None:
            if self.odoo._api_v7:
                self._dispatch = self.odoo.netsvc.ExportService.getService('db').dispatch
            else:   # Odoo v8
                self._dispatch = functools.partial(self.odoo.http.dispatch_rpc, 'db')
        return self._dispatch

    def __getattr__(self, name):
        def db_service_method(*args):
            return self.dispatch(name, args)
        return db_service_method


class LOdoo(object):
    """ Wrapper for local odoo instance

        (Singleton)
    """
    __lodoo = None

    def __new__(cls, *args, **kwargs):
        if not cls.__lodoo:
            cls.__lodoo = super(LOdoo, cls).__new__(cls)
        return cls.__lodoo

    def __init__(self, options=None):
        # Set workers = 0 if other not specified
        options = options[:] if options is not None else []
        if not any(o.startswith('--workers') for o in options):
            options.append('--workers=0')

        self._options = options

        self._odoo = None
        self._registries = {}
        self._db_service = None

    @classmethod
    def get_lodoo(cls):
        return cls.__lodoo

    @property
    def odoo(self):
        """ Return initialized Odoo package
        """
        if self._odoo is None:
            odoo.tools.config.parse_config(self._options)

            if odoo._api_v7:
                odoo.service.start_internal()
            elif not hasattr(odoo.api.Environment._local, 'environments'):
                odoo.api.Environment._local.environments = odoo.api.Environments()

            self._odoo = odoo
        return self._odoo

    @property
    def db(self):
        """ Return database management service
        """
        if self._db_service is None:
            self._db_service = LocalDBService(self)
        return self._db_service

    def get_registry(self, dbname):
        registry = self._registries.get(dbname, None)
        if registry is None:
            registry = self._registries[dbname] = LocalRegistry(self, dbname)
        return registry

    def __getitem__(self, name):
        return self.get_registry(name)


# Backward comatability
LocalClient = LOdoo


@atexit.register
def cleanup():
    if odoo.release.version_info < (10,):
        Registry = odoo.modules.registry.RegistryManager
    else:
        Registry = odoo.modules.registry.Registry

    for db in Registry.registries.keys():
        odoo.sql_db.close_db(db)
