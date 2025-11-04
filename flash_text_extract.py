from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
import const
import UnityPy
from bundle_utils import get_bundle_data
import utils


def extract_flash(bundle: UnityPy.Environment):
    for asset in bundle.objects:
        if asset.type.name != "MonoBehaviour" or not asset.serialized_type.nodes:
            continue
        tree = asset.read_typetree()
        mpg = tree.get("_motionParameterGroup")
        if not mpg:
            continue
        mpl = mpg.get("_motionParameterList")
        if not mpl:
            continue
        mpl_out = {}
        for mpi, ele in enumerate(mpl):
            tpl = ele.get("_textParamList")
            if not tpl:
                continue
            tpl_out = {}
            for tpi, tpl_ele in enumerate(tpl):
                source = tpl_ele.get("_text")
                if not source:
                    continue
                tpl_out[tpi] = {
                    "text": source,
                    "scale": tpl_ele.get("_scale"),
                    "position_offset": tpl_ele.get("_positionOffset"),
                }
            mpl_out[mpi] = {"text_param_list": tpl_out}
        if mpl_out:
            return {"motion_parameter_list": mpl_out}


def main():
    ld_dir, target_name = argv[1:]

    db = MetaDb(const.GAME_META_FILE)
    for bundle_path, bundle_hash, bundle_key in db.findall_flash_prefab(target_name):
        base_name = Path(bundle_path).stem[6:]
        # print(f"Looking for {base_name} combine from {bundle_path}")
        combine_info = db.find_flashcombine_prefab(base_name)
        combine_path = combine_info[0] if combine_info else None
        out_path = Path(ld_dir, "assets", combine_path or bundle_path).with_suffix(".json")
        if out_path.exists():
            print(f"File already exists, skipping: {out_path}")
            continue

        try:
            bundle_data = get_bundle_data(db, bundle_hash)
        except FileNotFoundError as e:
            print(f"Bundle {bundle_hash} not found.\n{e}")
            continue

        bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, bundle_key))
        data = extract_flash(bundle)
        if data is None:
            print(f"No useful data in {base_name}")
            continue
        if combine_path:
            data = {"an_root": data}
        source_dict = {
            db.platform.lower(): {"bundle_name": bundle_hash},
            "data": data,
        }
        utils.write_json(out_path, source_dict)
        print(f"Wrote {bundle_path}")


if __name__ == "__main__":
    main()
