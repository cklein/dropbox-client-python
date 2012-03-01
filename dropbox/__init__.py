#!/usr/bin/env python
# encoding: utf-8
"""
dropbox/__init__.py

Created by Maximillian Dornseif on 2011-02-06.
Copyright (c) 2011 HUDORA. All rights reserved.
BSD-licensed
"""


def get_dropbox_client(consumer_key, consumer_secret, access_token_key, access_token_secret):
    """Gibt ein vorkonfiguriertes Dropbox Client Object zurück.

        db_client = dropbox.get_dropbox_client(consumer_key='wj123',
                                               consumer_secret='ph123',
                                               access_token='oauth_token_secret=xe123&oauth_token=1w123')
    """
    # Lazy Import
    from dropbox import session
    from dropbox import client

    session = session.DropboxSession(consumer_key, consumer_secret, 'dropbox')
    session.set_token(access_token_key, access_token_secret)
    return client.DropboxClient(session)
