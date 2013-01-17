#!/usr/bin/env python
# encoding: utf-8
"""
dropbox/__init__.py

Created by Maximillian Dornseif on 2011-02-06.
Copyright (c) 2011 HUDORA. All rights reserved.
BSD-licensed
"""

import dropbox.client
import dropbox.session


def get_dropbox_client(consumer_key, consumer_secret, access_token_key, access_token_secret):
    """Gibt ein vorkonfiguriertes Dropbox Client Object zurück.

        db_client = dropbox.get_dropbox_client(consumer_key='wj123',
                                               consumer_secret='ph123',
                                               access_token_secret='xe123',
                                               access_token_key='1w123')
    """

    session = dropbox.session.DropboxSession(consumer_key, consumer_secret, 'dropbox')
    session.set_token(access_token_key, access_token_secret)
    return dropbox.client.DropboxClient(session)
