"""
The main client API you'll be working with most often.  You'll need to
configure a dropbox.session.DropboxSession for this to work, but otherwise
it's fairly self-explanatory.
"""

import re
import json

from dropbox.rest import ErrorResponse
from dropbox.rest import RESTClient

def format_path(path):
    """Normalize path for use with the Dropbox API.

    This function turns multiple adjacent slashes into single
    slashes, then ensures that there's a leading slash but
    not a trailing slash.
    """
    if not path:
        return path

    path = re.sub(r'/+', '/', path)

    if path == '/':
        return ""
    else:
        return '/' + path.strip('/')

class DropboxClient(object):
    """
    The main access point of doing REST calls on Dropbox. You should
    first create and configure a dropbox.session.DropboxSession object,
    and then pass it into DropboxClient's constructor. DropboxClient
    then does all the work of properly calling each API method
    with the correct OAuth authentication.

    You should be aware that any of these methods can raise a
    rest.ErrorResponse exception if the server returns a non-200
    or invalid HTTP response. Note that a 401 return status at any
    point indicates that the user needs to be reauthenticated.
    """

    def __init__(self, session):
        """Initialize the DropboxClient object.

        Args:
            session: A dropbox.session.DropboxSession object to use for making requests.
        """
        self.session = session

    def request(self, target, params=None, method='POST', content_server=False):
        """Make an HTTP request to a target API method.

        This is an internal method used to properly craft the url, headers, and
        params for a Dropbox API request.  It is exposed for you in case you
        need craft other API calls not in this library or if you want to debug it.

        Args:
            target: The target URL with leading slash (e.g. '/files')
            params: A dictionary of parameters to add to the request
            method: An HTTP method (e.g. 'GET' or 'POST')
            content_server: A boolean indicating whether the request is to the
               API content server, for example to fetch the contents of a file
               rather than its metadata.

        Returns:
            A tuple of (url, params, headers) that should be used to make the request.
            OAuth authentication information will be added as needed within these fields.
        """
        assert method in ['GET','POST', 'PUT'], "Only 'GET', 'POST', and 'PUT' are allowed."
        if params is None:
            params = {}

        host = self.session.API_CONTENT_HOST if content_server else self.session.API_HOST
        base = self.session.build_url(host, target)
        headers, params = self.session.build_access_headers(method, base, params)

        if method in ('GET', 'PUT'):
            url = self.session.build_url(host, target, params)
        else:
            url = self.session.build_url(host, target)

        return url, params, headers


    def account_info(self):
        """Retrieve information about the user's account.

        Returns:
            A dictionary containing account information.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#account-info
        """
        url, params, headers = self.request("/account/info", method='GET')

        return RESTClient.GET(url, headers)


    def put_file(self, full_path, file_obj, overwrite=False, parent_rev=None):
        """Upload a file.

        Args:
            full_path: The full path to upload the file to, *including the file name*.
                If the destination directory does not yet exist, it will be created.
            file_obj: A file-like object to upload. If you would like, you can pass a string as file_obj.
            overwrite: Whether to overwrite an existing file at the given path. [default False]
                If overwrite is False and a file already exists there, Dropbox
                will rename the upload to make sure it doesn't overwrite anything.
                You need to check the metadata returned for the new name.
                This field should only be True if your intent is to potentially
                clobber changes to a file that you don't know about.
            parent_rev: The rev field from the 'parent' of this upload. [optional]
                If your intent is to update the file at the given path, you should
                pass the parent_rev parameter set to the rev value from the most recent
                metadata you have of the existing file at that path. If the server
                has a more recent version of the file at the specified path, it will
                automatically rename your uploaded file, spinning off a conflict.
                Using this parameter effectively causes the overwrite parameter to be ignored.
                The file will always be overwritten if you send the most-recent parent_rev,
                and it will never be overwritten if you send a less-recent one.

        Returns:
            A dictionary containing the metadata of the newly uploaded file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#files-put

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               503: User over quota

        Note: In Python versions below version 2.6, httplib doesn't handle file-like objects.
            In that case, this code will read the entire file into memory (!).
        """
        path = "/files_put/%s%s" % (self.session.root, format_path(full_path))

        params = {
            'overwrite': bool(overwrite),
            }

        if parent_rev is not None:
            params['parent_rev'] = parent_rev

        url, params, headers = self.request(path, params, method='PUT', content_server=True)

        return RESTClient.PUT(url, file_obj.read(), headers)

    def get_file(self, from_path, rev=None):
        """Download a file.

        Unlike most other calls, get_file returns a raw HTTPResponse with the connection open.
        You should call .read() and perform any processing you need, then close the HTTPResponse.

        Args:
            from_path: The path to the file to be downloaded.
            rev: A previous rev value of the file to be downloaded. [optional]

        Returns:
            An httplib.HTTPResponse that is the result of the request.

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               404: No file was found at the given path, or the file that was there was deleted.
               200: Request was okay but response was malformed in some way.
        """
        path = "/files/%s%s" % (self.session.root, format_path(from_path))

        params = {}
        if rev is not None:
            params['rev'] = rev

        url, params, headers = self.request(path, params, method='GET', content_server=True)
        return RESTClient.request("GET", url, headers=headers, raw_response=True)

    def get_file_and_metadata(self, from_path, rev=None):
        """Download a file alongwith its metadata.

        Acts as a thin wrapper around get_file() (see get_file() comments for
        more details)

        Args:
            from_path: The path to the file to be downloaded.
            rev: A previous rev value of the file to be downloaded. [optional]

        Returns:
            - An httplib.HTTPResponse that is the result of the request.
            - A dictionary containing the metadata of the file (see
              https://www.dropbox.com/developers/docs#metadata for details).

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               404: No file was found at the given path, or the file that was there was deleted.
               200: Request was okay but response was malformed in some way.
        """
        file_res = self.get_file(from_path, rev)
        metadata = DropboxClient.__parse_metadata_as_dict(file_res)

        return file_res, metadata

    @staticmethod
    def __parse_metadata_as_dict((status, headers, response)):
        """Parses file metadata from a raw dropbox HTTP response, raising a
        dropbox.rest.ErrorResponse if parsing fails.
        """
        metadata = None
        for header, header_val in headers.items():
            if header.lower() == 'x-dropbox-metadata':
                try:
                    metadata = json.loads(header_val)
                except ValueError:
                    raise ErrorResponse(status, headers, response)
        if not metadata:
            raise ErrorResponse(status, headers, response)
        return metadata

    def file_copy(self, from_path, to_path):
        """Copy a file or folder to a new location.

        Args:
            from_path: The path to the file or folder to be copied.

            to_path: The destination path of the file or folder to be copied.
                This parameter should include the destination filename (e.g.
                from_path: '/test.txt', to_path: '/dir/test.txt'). If there's
                already a file at the to_path, this copy will be renamed to
                be unique.

        Returns:
            A dictionary containing the metadata of the new copy of the file or folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-copy

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of:

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given from_path.
            - 503: User over storage quota.
        """
        params = {'root': self.session.root,
                  'from_path': format_path(from_path),
                  'to_path': format_path(to_path),
                  }

        url, params, headers = self.request("/fileops/copy", params)

        return RESTClient.POST(url, params, headers)


    def file_create_folder(self, path):
        """Create a folder.

        Args:
            path: The path of the new folder.

        Returns:
            A dictionary containing the metadata of the newly created folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-create-folder

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
               400: Bad request (may be due to many things; check e.error for details)
               403: A folder at that path already exists.
        """
        params = {'root': self.session.root, 'path': format_path(path)}

        url, params, headers = self.request("/fileops/create_folder", params)

        return RESTClient.POST(url, params, headers)


    def file_delete(self, path):
        """Delete a file or folder.

        Args:
            path: The path of the file or folder.

        Returns:
            A dictionary containing the metadata of the just deleted file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-delete

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given path.
        """
        params = {'root': self.session.root, 'path': format_path(path)}

        url, params, headers = self.request("/fileops/delete", params)

        return RESTClient.POST(url, params, headers)


    def file_move(self, from_path, to_path):
        """Move a file or folder to a new location.

        Args:
            from_path: The path to the file or folder to be moved.
            to_path: The destination path of the file or folder to be moved.
            This parameter should include the destination filename (e.g.
            from_path: '/test.txt', to_path: '/dir/test.txt'). If there's
            already a file at the to_path, this file or folder will be renamed to
            be unique.

        Returns:
            A dictionary containing the metadata of the new copy of the file or folder.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#fileops-move

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given from_path.
            - 503: User over storage quota.
        """
        params = {'root': self.session.root, 'from_path': format_path(from_path), 'to_path': format_path(to_path)}

        url, params, headers = self.request("/fileops/move", params)

        return RESTClient.POST(url, params, headers)


    def metadata(self, path, list=True, file_limit=10000, hash=None, rev=None, include_deleted=False):
        """Retrieve metadata for a file or folder.

        Args:
            path: The path to the file or folder.

            list: Whether to list all contained files (only applies when
                path refers to a folder).
            file_limit: The maximum number of file entries to return within
                a folder. If the number of files in the directory exceeds this
                limit, an exception is raised. The server will return at max
                10,000 files within a folder.
            hash: Every directory listing has a hash parameter attached that
                can then be passed back into this function later to save on\
                bandwidth. Rather than returning an unchanged folder's contents,\
                the server will instead return a 304.\
            rev: The revision of the file to retrieve the metadata for. [optional]
                This parameter only applies for files. If omitted, you'll receive
                the most recent revision metadata.

        Returns:
            A dictionary containing the metadata of the file or folder
            (and contained files if appropriate).

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#metadata

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 304: Current directory hash matches hash parameters, so contents are unchanged.
            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at given path.
            - 406: Too many file entries to return.
        """
        path = "/metadata/%s%s" % (self.session.root, format_path(path))

        params = {'file_limit': file_limit,
                  'list': 'true',
                  'include_deleted': include_deleted,
                  }

        if not list:
            params['list'] = 'false'
        if hash is not None:
            params['hash'] = hash
        if rev:
            params['rev'] = rev

        url, params, headers = self.request(path, params, method='GET')

        return RESTClient.GET(url, headers)

    def thumbnail(self, from_path, size='large', format='JPEG'):
        """Download a thumbnail for an image.

        Unlike most other calls, thumbnail returns a raw HTTPResponse with the connection open.
        You should call .read() and perform any processing you need, then close the HTTPResponse.

        Args:
            from_path: The path to the file to be thumbnailed.
            size: A string describing the desired thumbnail size.
               At this time, 'small', 'medium', and 'large' are
               officially supported sizes (32x32, 64x64, and 128x128
               respectively), though others may be available. Check
               https://www.dropbox.com/developers/docs#thumbnails for
               more details.

        Returns:
            An httplib.HTTPResponse that is the result of the request.

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given from_path, or files of that type cannot be thumbnailed.
            - 415: Image is invalid and cannot be thumbnailed.
        """
        assert format in ['JPEG', 'PNG'], "expected a thumbnail format of 'JPEG' or 'PNG', got %s" % format

        path = "/thumbnails/%s%s" % (self.session.root, format_path(from_path))

        url, params, headers = self.request(path, {'size': size}, method='GET', content_server=True)
        return RESTClient.request("GET", url, headers=headers, raw_response=True)  # TODO: raw_response

    def thumbnail_and_metadata(self, from_path, size='large', format='JPEG'):
        """Download a thumbnail for an image alongwith its metadata.

        Acts as a thin wrapper around thumbnail() (see thumbnail() comments for
        more details)

        Args:
            from_path: The path to the file to be thumbnailed.
            size: A string describing the desired thumbnail size. See thumbnail()
               for details.

        Returns:
            - An httplib.HTTPResponse that is the result of the request.
            - A dictionary containing the metadata of the file whose thumbnail
              was downloaded (see https://www.dropbox.com/developers/docs#metadata
              for details).

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No file was found at the given from_path, or files of that type cannot be thumbnailed.
            - 415: Image is invalid and cannot be thumbnailed.
            - 200: Request was okay but response was malformed in some way.
        """
        thumbnail_res = self.thumbnail(from_path, size, format)
        metadata = DropboxClient.__parse_metadata_as_dict(thumbnail_res)

        return thumbnail_res, metadata

    def search(self, path, query, file_limit=1000, include_deleted=False):
        """Search directory for filenames matching query.

        Args:
            path: The directory to search within.

            query: The query to search on (minimum 3 characters).

            file_limit: The maximum number of file entries to return within a folder.
               The server will return at max 1,000 files.

            include_deleted: Whether to include deleted files in search results.

        Returns:
            A list of the metadata of all matching files (up to
            file_limit entries).  For a detailed description of what
            this call returns, visit:
            https://www.dropbox.com/developers/docs#search

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of
            400: Bad request (may be due to many things; check e.error
            for details)
        """
        path = "/search/%s%s" % (self.session.root, format_path(path))

        params = {
            'query': query,
            'file_limit': file_limit,
            'include_deleted': include_deleted,
            }

        url, params, headers = self.request(path, params)

        return RESTClient.POST(url, params, headers)

    def revisions(self, path, rev_limit=1000):
        """Retrieve revisions of a file.

        Args:
            path: The file to fetch revisions for. Note that revisions
                are not available for folders.
            rev_limit: The maximum number of file entries to return within
                a folder. The server will return at max 1,000 revisions.

        Returns:
            A list of the metadata of all matching files (up to rev_limit entries).

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#revisions

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: No revisions were found at the given path.
        """
        path = "/revisions/%s%s" % (self.session.root, format_path(path))

        params = {
            'rev_limit': rev_limit,
            }

        url, params, headers = self.request(path, params, method='GET')

        return RESTClient.GET(url, headers)

    def restore(self, path, rev):
        """Restore a file to a previous revision.

        Args:
            path: The file to restore. Note that folders can't be restored.
            rev: A previous rev value of the file to be restored to.

        Returns:
            A dictionary containing the metadata of the newly restored file.

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#restore

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given revision.
        """
        path = "/restore/%s%s" % (self.session.root, format_path(path))

        params = {
            'rev': rev,
            }

        url, params, headers = self.request(path, params)

        return RESTClient.POST(url, params, headers)

    def media(self, path):
        """Get a temporary unauthenticated URL for a media file.

        All of Dropbox's API methods require OAuth, which may cause problems in
        situations where an application expects to be able to hit a URL multiple times
        (for example, a media player seeking around a video file). This method
        creates a time-limited URL that can be accessed without any authentication,
        and returns that to you, along with an expiration time.

        Args:
            path: The file to return a URL for. Folders are not supported.

        Returns:
            A dictionary that looks like the following example:

            ``{'url': 'https://dl.dropbox.com/0/view/wvxv1fw6on24qw7/file.mov', 'expires': 'Thu, 16 Sep 2011 01:01:25 +0000'}``

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#media

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given path.
        """
        path = "/media/%s%s" % (self.session.root, format_path(path))

        url, params, headers = self.request(path, method='GET')

        return RESTClient.GET(url, headers)

    def share(self, path):
        """Create a shareable link to a file or folder.

        Shareable links created on Dropbox are time-limited, but don't require any
        authentication, so they can be given out freely. The time limit should allow
        at least a day of shareability, though users have the ability to disable
        a link from their account if they like.

        Args:
            path: The file or folder to share.

        Returns:
            A dictionary that looks like the following example:

            ``{'url': 'http://www.dropbox.com/s/m/a2mbDa2', 'expires': 'Thu, 16 Sep 2011 01:01:25 +0000'}``

            For a detailed description of what this call returns, visit:
            https://www.dropbox.com/developers/docs#share

        Raises:
            A dropbox.rest.ErrorResponse with an HTTP status of

            - 400: Bad request (may be due to many things; check e.error for details)
            - 404: Unable to find the file at the given path.
        """
        path = "/shares/%s%s" % (self.session.root, format_path(path))

        url, params, headers = self.request(path, method='GET')

        return RESTClient.GET(url, headers)
