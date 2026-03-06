# Translation tools
Some miscellaneous tools to help with the translation process. These are all command line tools.
Arguments in brackets are optional.

Set the env var `UMA_DATA_DIR` to the game's data root if it's not in `LocalLow app data` to use auto-load features where present.

All non-optional `_dir` (**not** `_path`) args accept the special value `tlsrc`. This will make the tool use the relevant path from the configured translation source. Otherwise, the custom path entered is used. Other tools automatically apply to the configured source.

Install dependencies in `requirements.txt` before running these tools.

## UIAnimation

- `uianimation_meta_update.py`: Update existing uianimation meta files. Arguments: `(windows_meta, android_meta, anim_dir)`

### Textures

- `an_extract`: Extract all textures from an `an_texture_sets` bundle. Arguments: `out_dir, target_name`
- `an_diff_gen.py`: Try to generate PNG diffs from all replacement `an_texture_sets` in `in_dir`. Since some of these textures cannot be directly mapped back to their uianimation bundle, it will skip files on those occasions. Arguments: `(in_dir, [target_sets, …])`. If given, only sets matching `target_sets` are processed.
- `an_meta_gen.py`: Try to generate uianimation meta files for each set in `an_texture_sets`. Since some of these textures cannot be directly mapped back to their uianimation bundle, it will skip files on those occasions. Arguments: `(windows_meta, android_meta)`
- `an_texture_update.py`: Update a translated texture to match a new version by remapping the sprites. Arguments: `(old_meta_path, tx_name, [mode])`. Set `mode` to `diff` to update only diffs, otherwise leave empty. Use `all` as the name to update all existing textures.

### Flash Text

- `flash_text_extract.py`: Write flash text files. Supports flash and flashcombine automatically. Arguments: `target_name, [update_mode [tx_name_list]]` Name is a wildcard: pf_fl_\*target_name\*. Set mode to `text` to re-extract all text, `plane` to extract planes using the specified textures, or `clean` to remove unchanged values, else skips existing.

## Atlas

- `atlas_extract.py`: Write atlases matching `target_name` to `out_dir`. Arguments: `out_dir, target_name`.
- `atlas_mattegen.py`: Generate a matte from an AtlasReference texture asset bundle.
- `atlas_diff_gen.py`: Generate PNG diffs for all replacement textures in `in_dir`. Arguments: `(in_dir, [target_names])`. If given, only atlases matching `target_names` are processed.
- `atlas_diff_janitor.py`: Try to clean up an atlas PNG diff with garbage pixels, which includes sprite areas with no opaque pixels and areas that are not within any sprite boundaries. Arguments: `(bundle_path, in_img, out_img)`
- `atlas_janitor.py`: Clean up an atlas texture by cropping off areas that are not within any sprite boundaries. Arguments: `(bundle_path, in_img, out_img)`
- `atlas_meta_gen.py`: Generate meta files for atlas replacements. Arguments: `(android_meta)`
- `atlas_update.py`: Update a (translated) atlas texture to match a newer atlas by creating a new atlas texture with the sprites remapped to their new location. Arguments: `(old_meta_path, atlas_name, mode)`. Set `mode` to `diff` to update an atlas diff, otherwise leave `mode` empty. Use `all` as the name to update all existing atlases.

## Misc

- `meta_decrypt.py`: Decrypts a meta db for browsing asset metadata. Arguments: `([src], [dst])`. By default uses installed game's meta and writes to `decrypted_metas` subdir.
- `bundle_decrypt.py`: Write decrypted bundles to `decrypted_bundles` subdir. Arguments: `path_or_hash, [bundle_key]` (When key is given, `path_or_hash` is a filepath. Else, if it includes a `/` or `_`, it is a unity path and supports multiple targets. Else it is a bundle hash.)
- `bundle_dl.py`: Download an asset bundle. Resulting file is saved at `{output_dir}/{bundle_name}_{bundle_hash}`. Default output_dir is `dl`. Arguments: `(bundle_name, [output_dir])`
- `png_diff.py`: Generate a PNG diff between two images. Arguments: `(old_path, new_path, out_path)`
- `apply_png_diff.py`: Applies a PNG diff to a base image. Arguments: `(orig_path, diff_path, out_path)`
- `calc_hname.py`: Calculate the hash name for a file from its checksum and name. This uses the calculation method that was used to produce the hash names in the meta DB. Arguments: `(file_path, name)`

Other Python scripts are libraries and do not have any functionality on their own.