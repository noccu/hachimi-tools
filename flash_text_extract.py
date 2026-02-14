from decrypt import decrypt_asset_bundle
from sys import argv
from meta_db_lib import MetaDb
from pathlib import Path
import const
import UnityPy
from bundle_utils import get_bundle_data
import utils

def extract_text(motion_param_elem: dict[str, list[dict]], mpi: int, existing_data: dict):
    tpl = motion_param_elem["_textParamList"]
    tpl_out = {}
    for tpi, tpl_ele in enumerate(tpl):
        source = tpl_ele.get("_text")
        if not source:
            continue
        obj_name: str = tpl_ele.get("_objectName")
        tpl_out[tpi] = {
            "_obj_name_": obj_name,
            "text": source,
            "scale": tpl_ele.get("_scale"),
            "position_offset": tpl_ele.get("_positionOffset"),
        }
        # Clean up
        if motion_param_elem.get("_name") == obj_name:
            del tpl_out[tpi]["_obj_name_"]
        # Update
        if existing_data:
            try:
                tpl_out[tpi].update(existing_data[str(mpi)]["text_param_list"][str(tpi)])
            except (IndexError, KeyError):
                pass
    return tpl_out


def extract_planes(motion_param_elem: dict[str, list[dict]], mpi: int, existing_data: dict, target_tx_list: set):
    ppl = motion_param_elem["_planeParamList"]
    ppl_out = {}
    for ppi, ppl_ele in enumerate(ppl):
        obj_name: str = ppl_ele.get("_objectName")
        linked_tx: list = ppl_ele.get("_textureNameList")
        if len(set(linked_tx) & target_tx_list) == 0:
            continue
        ppl_out[ppi] = {
            "_obj_name_": obj_name,
            "_linked_textures_": linked_tx,
            "scale": ppl_ele.get("_scale"),
            "position_offset": ppl_ele.get("_positionOffset"),
        }
        # Clean up
        if obj_name.startswith("object"):
            del ppl_out[ppi]["_obj_name_"]
        # Update
        if existing_data:
            try:
                ppl_out[ppi].update(existing_data[str(mpi)]["plane_param_list"][str(ppi)])
            except (IndexError, KeyError):
                pass
    return ppl_out


def extract_flash(bundle: UnityPy.Environment, update_mode, existing_data:dict, target_tx_list):
    # Assume there is only one asset. (??)
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
            ele_out = {"_name_": ele.get("_name")}
            if update_mode == "plane":
                ppl = extract_planes(ele, mpi, existing_data, target_tx_list)
                if ppl:
                    ele_out["plane_param_list"] = ppl
            else:
                tpl = extract_text(ele, mpi, existing_data if update_mode == "text" else None)
                if tpl:
                    ele_out["text_param_list"] = tpl
            if len(ele_out) > 1:
                mpl_out[mpi] = ele_out
            elif update_mode and str(mpi) in existing_data:
                    mpl_out[mpi] = existing_data[str(mpi)]
        if mpl_out:
            return {"motion_parameter_list": mpl_out}


def main():
    ld_dir, target_name, *opts = argv[1:]
    try:
        update_mode = opts[0]
        if update_mode == "plane":
            target_tx_list = set(opts[1:])
            if not target_tx_list:
                print("No texture name given.")
                return
        else:
            assert update_mode == "text"
            target_tx_list = None
    except IndexError:
        update_mode = target_tx_list = None

    db = MetaDb(const.GAME_META_FILE)
    for bundle_path, bundle_hash, bundle_key in db.findall_flash_prefab(target_name):
        base_name = Path(bundle_path).stem[6:]
        # print(f"Looking for {base_name} combine from {bundle_path}")
        combine_info = db.find_flashcombine_prefab(base_name)
        combine_path = combine_info[0] if combine_info else None
        out_path = Path(ld_dir, "assets", combine_path or bundle_path).with_suffix(".json")
        if out_path.exists() and update_mode is None:
            print(f"File already exists, skipping: {out_path}")
            continue

        try:
            bundle_data = get_bundle_data(db, bundle_hash)
        except FileNotFoundError as e:
            print(f"Bundle {bundle_hash} not found.\n{e}")
            continue

        bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, bundle_key))
        if update_mode:
            fd = utils.read_json(out_path)["data"]
            if combine_path:
                fd = fd["an_root"]
            existing_data = fd["motion_parameter_list"]
        else:
            existing_data = None

        data = extract_flash(bundle, update_mode, existing_data, target_tx_list)
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
