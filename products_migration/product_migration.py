import json
import time
from products_migration.Product import Product



def convert_migration():
    cnt = 0
    a = False
    with open('./goodlens-product-products-export.json', 'r') as f:
        data = json.load(f)

        for key in data.keys():
            # timestamp 걸러내기
            if key.isdigit() : continue
            # 실험 디비 걸러내기
            if "image_front" not in data[key]["common"]: continue
            if data[key]["common"]["gtin"]["value"] == "" or data[key]["common"]["image_front"]["value"] == "": continue
            cnt = cnt+1

            common = build_common(data,key)
            kan_code = common["kan_code"]["value"]
            option = build_option(data,key,kan_code)

            product = {}
            product["source"] = "goodlens"
            product["status"] = "draft"
            product["regacy_id"] = key
            product["common"] = common
            product["option"] = option
            product["last_modified"] = int(time.time())

            api_instance = Product()

            try:
                print("ad")
                api_response = api_instance.add_product(product)
                # pprint(api_response)
            except Exception as e:
                print("Exception when calling add_video: %s\n" % e)

    print(cnt)

def build_common(data,key):
    common = None
    with open('./common.json', 'r') as f1:
        common = json.load(f1)
    # migration common building data set
    for attribute in data[key]["common"].keys():

        if attribute == "option" or attribute == "group" or attribute == "dirty" or attribute == "product_id": continue  # kan_code는 widget이 없는 특수한 경우이므로 제외시킨다
        if data[key]["common"][attribute]["value"] == "": continue  # 값이 없으면 건너뜀
        company_address = None
        if attribute == "company_address":
            company_address = data[key]["common"][attribute]["value"]
            common["manufacturer"]["widget"]["child"][0]["company_address"][0]["widget"]["value"] = company_address
            common["manufacture_seller"]["widget"]["child"]["company_address"][0]["widget"]["value"] = company_address
            common["import_trader"]["widget"]["child"]["company_address"][0]["widget"]["value"] = company_address

        if attribute in common:
            if attribute == "kan_code" or attribute == "product_unit" or attribute == "option":
                if attribute == "kan_code": common[attribute]["value"] = data[key]["common"][attribute]["value"]
                if attribute == "product_unit":
                    unit = ["단품", "번들", "패키지"]
                    common[attribute]["widget"]["value"] = unit[data[key]["common"][attribute]["value"]]
            else:
                common[attribute]["widget"]["value"] = data[key]["common"][attribute]["value"]
    return common

def build_option(data,key,kan_code):

    option = {}
    first_class_code = kan_code[0:2]
    second_class_code = kan_code[2:4]
    third_class_code = kan_code[4:6]
    fourth_class_code = kan_code[6:8]
    print(kan_code)


    with open('./attribute.json', 'r') as f:
        kan_tree = json.load(f)
        if first_class_code in kan_tree.keys():
            if kan_tree[first_class_code]["attribute"] != None:
                option.update(kan_tree[first_class_code]["attribute"])

            if second_class_code in kan_tree[first_class_code]["child"].keys() :
                if kan_tree[first_class_code]["child"][second_class_code]["attribute"] != None:
                    option.update(kan_tree[first_class_code]["child"][second_class_code]["attribute"])

                if third_class_code in kan_tree[first_class_code]["child"][second_class_code]["child"].keys():
                    if kan_tree[first_class_code]["child"][second_class_code]["child"][third_class_code]["attribute"] != None:
                        option.update(kan_tree[first_class_code]["child"][second_class_code]["child"][third_class_code]["attribute"])

                    if fourth_class_code in kan_tree[first_class_code]["child"][second_class_code]["child"][third_class_code]["child"].keys():
                        if kan_tree[first_class_code]["child"][second_class_code]["child"][third_class_code]["child"][fourth_class_code]["attribute"] != None:
                            option.update(kan_tree[first_class_code]["child"][second_class_code]["child"][third_class_code]["child"][fourth_class_code]["attribute"])

    if "processed_food" in data[key].keys() or "option" in data[key].keys():
        if "processed_food" in data[key].keys():
            option_name = "processed_food"
        elif "option" in data[key].keys():
            option_name = "option"
        for attribute in data[key][option_name].keys():
            if data[key][option_name][attribute]["value"] == "": continue  # 값이 없으면 건너뜀
            if attribute in option:
                option[attribute]["widget"]["value"] = data[key][option_name][attribute]["value"]
    return option

convert_migration()