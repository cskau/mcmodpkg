#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from __future__ import print_function

import argparse
import json
import sys

from collections import OrderedDict


# This dictates the standard ordering of entries in the index.
KEY_ORDER = OrderedDict([
  ('name', None),
  ('description', None),
  ('modid', None),
  ('curseforge_id', None),
  ('urls', None),
  ('downloads', [OrderedDict([
    ('version', None),
    ('mcversions', None),
    # ('javaversions', None),
    ('md5', None),
    ('dependencies', None),
    ('mirrors', None),
  ])]),
])


# Traverse an input dict and order according to the order OrderedDict
def order_dict(in_dict, order=KEY_ORDER):
  out_dict = OrderedDict()
  for k in order:
    if type(order[k]) == OrderedDict:
      out_dict[k] = order_dict(
          in_dict[k],
          order=order[k],
          )
    elif type(order[k]) == list and type(order[k][0]) == OrderedDict:
      out_dict[k] = [
          order_dict(e, order=order[k][0])
          for e in in_dict[k]
          ]
    elif k in in_dict:
      out_dict[k] = in_dict[k]
    else:
      # Missing fields
      'Key not found in mod entry'
  return out_dict


def clean_up(in_dict):
  keys = set(in_dict.keys())
  for k in keys:
    if isinstance(in_dict[k], list) and isinstance(in_dict[k][0], OrderedDict):
      in_dict[k] = [clean_up(e) for e in in_dict[k]]
    if not in_dict[k]:
      # Remove empty fields
      del in_dict[k]
  return in_dict


class Index:

  def __init__(self, index_file=None):
    self.index_file = index_file


  def __enter__(self):
    self.load_index(self.index_file)
    return self


  def __exit__(self, etype, value, traceback):
    self.index_file.close()


  def load_index(self, index_file=None):
    index_file = index_file if index_file else self.index_file
    self.mod_infos = json.load(
        index_file,
        object_pairs_hook=OrderedDict,
        )


  def save_index(self, index_file=None):
    index_file = index_file if index_file else self.index_file
    mod_infos_json = json.dumps(
        self.mod_infos,
        indent=2,
        separators=(',', ': '),
        )

    with index_file:
      index_file.write(mod_infos_json)


  def sort_index(self, entry_key='modid'):
    # Sanity
    for mod_info in self.mod_infos:
      if not (entry_key in mod_info and mod_info[entry_key]):
        # raise Exception('Missing key in: {}'.format(mod_info))
        print('Missing key "{}", setting "{}" from curseforge_id.'.format(entry_key, mod_info['curseforge_id']))
        mod_info[entry_key] = mod_info['curseforge_id']
    
    # Clean up and order dict according to the standard ordering
    self.mod_infos = [
        order_dict(
            clean_up(
                mod_info
                )
            )
        for mod_info in self.mod_infos
    ]

    # Sanity checks
    seen_mods = set()
    for mod_info in self.mod_infos:
      key = mod_info[entry_key]
      if key in seen_mods:
        raise Exception('Duplicate mod: {}'.format(mod_info))
      seen_mods.add(key)

    # Sort mod entries according to entry_key
    self.mod_infos = sorted(
        self.mod_infos,
        key=lambda e:e[entry_key].lower(),
        )

    # Sort downloads by first mirror url (newest download first)
    for mod_info in self.mod_infos:
      mod_info['downloads'] = sorted(
          mod_info['downloads'],
          key=lambda e:e['mirrors'][0],
          reverse=True,
          )


def main(mcmod_info_in, mcmod_info_out):
  with Index(mcmod_info_in) as index:
    index.sort_index()
    index.save_index(mcmod_info_out)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()

  parser.add_argument(
      '-i',
      '--mcmod_info_in',
      default='index.json',
      nargs='?',
      )

  parser.add_argument(
      '-o',
      '--mcmod_info_out',
      nargs='?',
      )

  args = parser.parse_args()

  #
  with open(args.mcmod_info_in, 'r') as mcmod_info_in:

    mcmod_info_out = (
        open(args.mcmod_info_out, 'w')
        if args.mcmod_info_out else
        sys.stdout
        )

    main(mcmod_info_in, mcmod_info_out)
