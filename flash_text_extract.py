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


def extract_planes(
    motion_param_elem: dict[str, list[dict]], mpi: int, existing_data: dict, target_tx_list: set
):
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


def extract_flash(bundle: UnityPy.Environment, update_mode, existing_data: dict, target_tx_list):
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


def clean_internal(orig_mp_ele: dict, mp_ele: dict, game_key: str, key: str):
    if key not in mp_ele:
        return
    for tpi, tp_ele in mp_ele[key].items():
        orig_tp_ele = orig_mp_ele[game_key][int(tpi)]

        try:
            del tp_ele["_obj_name_"]
        except KeyError:
            pass
        try:
            if tp_ele["text"] == orig_tp_ele["_text"]:
                del tp_ele["text"]
        except KeyError:
            pass

        try:
            if all(v == orig_tp_ele["_scale"][k] for k, v in tp_ele["scale"].items()):
                del tp_ele["scale"]
        except KeyError:
            pass
        try:
            if all(v == orig_tp_ele["_positionOffset"][k] for k, v in tp_ele["position_offset"].items()):
                del tp_ele["position_offset"]
        except KeyError:
            pass


def clean_flash(bundle: UnityPy.Environment, existing_mpl: dict[str, dict]):
    # Assume there is only one asset. (??)
    for asset in bundle.objects:
        if asset.type.name != "MonoBehaviour" or not asset.serialized_type.nodes:
            continue
        tree = asset.read_typetree()
        mpg: dict = tree.get("_motionParameterGroup")
        if not mpg:
            continue
        mpl: list[dict] = mpg.get("_motionParameterList")
        if not mpl:
            continue

        for mpi, mp_ele in existing_mpl.items():
            try:
                del mp_ele["_name_"]
            except KeyError:
                pass
            orig_mp_ele = mpl[int(mpi)]
            clean_internal(orig_mp_ele, mp_ele, "_textParamList", "text_param_list")
            clean_internal(orig_mp_ele, mp_ele, "_planeParamList", "plane_param_list")

        existing_mpl = clean_dict(existing_mpl)
        return {"motion_parameter_list": existing_mpl}


def clean_dict(d: dict):
    out = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = clean_dict(v)
            if len(v) == 0:
                continue
        out[k] = v
    return out


def main():
    target_name, *opts = argv[1:]
    try:
        update_mode = opts[0]
        if update_mode == "plane":
            target_tx_list = set(opts[1:])
            if not target_tx_list:
                print("No texture name given.")
                return
        else:
            # assert update_mode == "text"
            target_tx_list = None
    except IndexError:
        update_mode = target_tx_list = None

    db = MetaDb(const.GAME_META_FILE)
    for bundle_path, bundle_hash, bundle_key in db.findall_flash_prefab(target_name):
        root_hash = bundle_hash
        base_name = Path(bundle_path).stem[6:]

        # If there's an fa_ bundle, we must use its path and add an extra an_root key.
        # Data is still in the fl_ bundle.
        combine_info = db.find_flashcombine_prefab(base_name)
        combine_path = combine_info[0] if combine_info else None

        out_path = utils.get_ld_assets_root(combine_path or bundle_path).with_suffix(".json")
        if out_path.exists() and update_mode is None:
            print(f"File already exists, skipping: {out_path}")
            continue

        # If there's a separate as_uparam bundle, that's where the data is.
        uparam = db.find_flash_uparam(base_name)
        if uparam:
            _, bundle_hash, bundle_key = uparam

        try:
            bundle_data = get_bundle_data(db, bundle_hash)
        except FileNotFoundError as e:
            print(f"Bundle {bundle_hash} not found.\n{e}")
            continue

        bundle = UnityPy.load(decrypt_asset_bundle(bundle_data, bundle_key))
        if update_mode:
            fd: dict[str, dict[str, dict]] = utils.read_json(out_path)
            root = fd["data"]
            if combine_path:
                root = root["an_root"]
            existing_mpl = root["motion_parameter_list"]
        else:
            fd = existing_mpl = None

        if update_mode == "clean":
            win_meta = fd.get("windows")
            if win_meta is None:
                print(f"No win meta in {out_path}, skipped.")
                continue
            if win_meta["bundle_name"] != bundle_hash:
                print(f"Bundle hash mismatch for {base_name}, skipped.")
                continue
            data = clean_flash(bundle, existing_mpl)
        else:
            data = extract_flash(bundle, update_mode, existing_mpl, target_tx_list)
            if data is None:
                print(f"No useful data in {base_name}")
                continue
        if combine_path:
            data = {"an_root": data}
        source_dict = {
            db.platform.lower(): {"bundle_name": root_hash},
            "data": data,
        }
        utils.write_json(out_path, source_dict)
        print(f"Wrote {bundle_path}")


if __name__ == "__main__":
    main()
