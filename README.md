# Translation tools
Some miscellaneous tools to help with the translation process. These are all command line tools.
Arguments in brackets are optional.

Set the env var `UMA_DATA_DIR` to the game's data root if it's not in `LocalLow app data` to use auto-load features where present.

Install dependencies in `requirements.txt` before running these tools.

- `an_extract`: Extract all textures from an an_textures bundle. Arguments: `out_dir, target_an_name`
- `an_diff_gen.py`: Try to generate PNG diffs from all replacement textures in the `an_texture_sets` folder. Since some of these textures cannot be directly mapped back to their uianimation bundle, it will skip files on those occasions. Arguments: `(an_texture_sets_dir, [included_folder_names_only, …])`
- `an_meta_gen.py`: Try to generate uianimation meta files for each set in `an_texture_sets`. Since some of these textures cannot be directly mapped back to their uianimation bundle, it will skip files on those occasions. Arguments: `(windows_meta, android_meta, ld_assets_dir)`
- `apply_png_diff.py`: Applies a PNG diff. Arguments: `(orig_path, diff_path, out_path)`
- `atlas_diff_gen.py`: Generate PNG diffs for all replacement textures in the `atlas` folder. Arguments: `(meta_path, atlas_dir)`
- `atlas_diff_janitor.py`: Try to clean up an atlas PNG diff with garbage pixels, which includes sprite areas with no opaque pixels and areas that are not within any sprite boundaries. Arguments: `(bundle_path, in_path, out_path)`
- `atlas_janitor.py`: Clean up an atlas texture by cropping off areas that are not within any sprite boundaries. Arguments: `(bundle_path, in_path, out_path)`
- `atlas_meta_gen.py`: Generate meta files for atlas replacements. Arguments: `(android_meta, atlas_dir)`
- `atlas_update.py`: Update a (translated) atlas texture to match a newer atlas by creating a new atlas texture with the sprites remapped to their new location. Arguments: `(atlas_ld_root, old_meta_path, atlas_name, mode)`. Set `mode` to `diff` to update an atlas diff, otherwise leave `mode` empty.
- `bundle_dl.py`: Download an asset bundle. Resulting file is saved at `{output_dir}/{bundle_name}_{bundle_hash}`. Default output_dir is `dl`. Arguments: `(bundle_name, [output_dir])`
- `mattegen.py`: Generate a matte from an AtlasReference texture asset bundle.
- `png_diff.py`: Generate a PNG diff between two images. Arguments: `(old_path, new_path, out_path)`
- `apply_png_diff.py`: Applies a PNG diff to a base image. Arguments: `(orig_path, diff_path, out_path)`
- `uianimation_meta_update.py`: Update existing uianimation meta files. Arguments: `(windows_meta, android_meta, anim_dir)`
- `calc_hname.py`: Calculate the hash name for a file from its checksum and name. This uses the calculation method that was used to produce the hash names in the meta DB. Arguments: `(file_path, name)`
- `bundle_decrypt.py`: Write decrypted bundles to `decrypted_bundles` subdir. Arguments: `path_or_hash, [bundle_key]` (When key is given, path_or_hash is a filepath. Else, if it includes a / or _, it is a unity path and supports multiple targets. Else it is a bundle hash.)
- `flash_text_extract.py`: Write flash text files. Supports flash and flashcombine automatically. Arguments: `ld_root, target_name, [update_mode [tx_name_list]]` Name is a wildcard: pf_fl_\*target_name\*. Set mode to `text` to re-extract all text, or `plane` to extract planes using the specified textures, else skips existing.
- `meta_decrypt.py`: Decrypts a meta db for browsing asset metadata. Arguments: `([src], [dst])`

Other Python scripts are libraries and do not have any functionality on their own.