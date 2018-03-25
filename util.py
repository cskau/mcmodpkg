#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import hashlib
import os
import zipfile
import json
import re

# http://python-future.org/compatible_idioms.html#urllib-module
try:
  # Python 3
  from urllib.parse import urlparse
  from urllib.request import urlopen
  from urllib.error import HTTPError
except ImportError:
  # Python 2
  from urlparse import urlparse
  from urllib2 import urlopen
  from urllib2 import HTTPError


def md5_hexdigest(blob):
  md5 = hashlib.md5()
  md5.update(blob)
  return md5.hexdigest()


def read_mcmod_info(mod_file, mcmod_info_file='mcmod.info'):
  archive = zipfile.ZipFile(mod_file, 'r')

  if mcmod_info_file in archive.namelist():
    try:
      mcmod_info = archive.read(mcmod_info_file).decode('utf-8')
      # stupid hack for NEI
      # All newlines in strings should be escaped; elsewhere they're meaningless.
      mcmod_info = mcmod_info.replace('\n', '')
      # stupid hack for some compact-solars
      mcmod_info = mcmod_info.replace('"mcversion": 1.7.10"', '"mcversion": "1.7.10"')
      # stupid hack for unidict
      mcmod_info = mcmod_info.replace('"modId":', '"modid":')
      #
      mcmod_info = mcmod_info.replace('"modList":', '"modlist":')
      # stupid hack for Forestry
      mcmod_info = mcmod_info.replace('mod_MinecraftForge', 'forge')
      # stupid hack for Engineer's Workshop
      mcmod_info = re.sub(r',\s]\s}', ']}', mcmod_info)
      # stupid hack for simple-harvest, dense-ores
      mcmod_info = mcmod_info.replace('Example Mod', '')
      mcmod_info = mcmod_info.replace('Example placeholder mod.', '')
      mcmod_info = mcmod_info.replace('examplemod', '')
      # stupid hack for tinkers-construct
      mcmod_info = mcmod_info.replace('"version": "@VERSION@",', '')
      mcmod_info = mcmod_info.replace('"mcversion": "@MCVERSION@",', '')
      # stupid hack for extrautils
      mcmod_info = mcmod_info.replace('"version": "${version}",', '')
      mcmod_info = mcmod_info.replace('"mcversion": "${mcversion}",', '')
      # stupid hack for agricraft
      mcmod_info = mcmod_info.replace('"mcversion": "${mod.mcversion}",', '')
      # Finally, we hopefully have some readable JSON
      mcmod_info_json = json.loads(mcmod_info)
      # stupid hack for alternative mod list format
      if isinstance(mcmod_info_json, dict):
        if 'modinfoversion' in mcmod_info_json:
          mcmod_info_json['modListVersion'] = mcmod_info_json['modinfoversion']
        if 'modList' in mcmod_info_json:
          mcmod_info_json['modlist'] = mcmod_info_json['modList']
        if ('modListVersion' in mcmod_info_json
            and mcmod_info_json['modListVersion'] in (2, '2')
            and 'modlist' in mcmod_info_json):
          mcmod_info_json = mcmod_info_json['modlist']
      return mcmod_info_json
    except ValueError as e:
      print(mod_file, e)

  return None


def download(url, download_path=None):
  try:
    response = urlopen(url)
  except HTTPError as e:
    print(e)
    return None

  if not response.getcode() == 200:
    # raise Exception(
    #     'Got HTTP code {}'.format(
    #         response.getcode()))
    print('Couldn\'t download:\n{}'.format(url))
    return None

  info = response.info()

  # TODO: be smarter about not re-downloading existing files.
  # last_modified = info['Last-Modified']
  # print(last_modified)

  parsed_url = urlparse(response.geturl())
  parsed_path = parsed_url.path
  parsed_filename = os.path.basename(parsed_path)
  # stupid hack
  parsed_filename = parsed_filename.replace('%20', ' ')

  if download_path:
    file_path = download_path.format(parsed_filename)

    #
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
      os.makedirs(directory)

    #
    with open(file_path, 'wb') as output_file:
      output_file.write(response.read())
      return file_path

  return response.read()
