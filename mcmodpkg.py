#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import argparse
import json

from util import download
from util import md5_hexdigest


def find_matching_mods(mod_infos, modid, target_version):
  for mod in mod_infos:
    if not 'modid' in mod:
      raise Exception('No modid found in:\n{}'.format(mod))

    if not mod['modid'].lower() == modid.lower():
      continue

    for d in mod['downloads']:
      if not 'mcversions' in d:
        raise Exception('No mcversions found in:\n{}'.format(d))

      if d['mcversions']:
        if not (target_version in d['mcversions']):
          continue

      yield d


def resolve_graph(
    mod_infos,
    modids,
    target_version,
    ignore_dependencies,
    download_dir='downloads',
    ):
  resolved_modids = set()

  modid_queue = modids
  for modid in modid_queue:
    if modid.lower() in resolved_modids:
      continue
    resolved_modids.add(modid.lower())

    if modid in ignore_dependencies:
      print('Ignoring {}'.format(modid))
      continue

    print('Resolving {}..'.format(modid))

    # The index is supposed to be ordered by newest mod first,
    # so we don't need to sort this list here.
    matches = list(find_matching_mods(mod_infos, modid, target_version))

    if not matches:
      print('No matches found for "{}"'.format(modid))
      continue

    top_match = matches[0]
    top_match_md5 = top_match['md5']
    top_match_url = top_match['mirrors'][0]

    print('Downloading {}'.format(top_match_url))
    download_path = '{}/{}/{{}}'.format(download_dir, target_version)
    mod_file = download(top_match_url, download_path)

    md5_sum = md5_hexdigest(open(mod_file, 'r').read())
    assert top_match_md5 == md5_sum, 'MD5 check sum mismatch: {} != {}'.format(top_match_md5, md5_sum)

    if 'dependencies' in top_match:
      modid_queue += top_match['dependencies']


def list_mods(mod_infos, mcversion=None):
  for mod in mod_infos:
    if 'modid' in mod:
      # Check it's available for the give MC version
      if mcversion:
        if not 'downloads' in mod:
          continue
        version_found = False
        for d in mod['downloads']:
          if 'mcversions' in d and mcversion in d['mcversions']:
            version_found = True
        if not version_found:
          continue
      #
      description = mod['description'] if 'description' in mod else ''
      entry = '{} - {}'.format(mod['modid'], description)
      print(entry)


def list_mcversions(mod_infos):
  versions = set()
  for mod in mod_infos:
    if 'downloads' in mod:
      for d in mod['downloads']:
        if 'mcversions' in d:
          versions.update(d['mcversions'])
  print(sorted(versions))


#

if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument(
      'modids',
      nargs='*',
      )

  parser.add_argument(
      '--mcmod_info_json',
      default='index.json',
      )

  parser.add_argument(
      '--mcversion',
      )

  parser.add_argument(
      '--ignore_dependencies',
      default='forge',
      )

  parser.add_argument(
      '--list',
      action='store_true',
      )

  parser.add_argument(
      '--list_mcversions',
      action='store_true',
      )

  args = parser.parse_args()

  modids = args.modids
  mcmod_info_json = args.mcmod_info_json
  mcversion = args.mcversion
  ignore_dependencies = args.ignore_dependencies
  do_list_mods = args.list
  do_list_mcversions = args.list_mcversions

  ignore_dependencies = ignore_dependencies.split(',')

  mod_infos = json.load(open(mcmod_info_json, 'r'))

  if do_list_mods:
    list_mods(mod_infos, mcversion)
    exit()
  elif do_list_mcversions:
    list_mcversions(mod_infos)
    exit()

  resolve_graph(mod_infos, modids, mcversion, ignore_dependencies)
