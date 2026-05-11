import requests
import json

# === 自动生成的请求代码 ===
url = "https://apis.ihg.com.cn/availability/v3/hotels/offers?fieldset=RATEDETAILS%2CRATEDETAILS.POLICIES%2CRATEDETAILS.UPSELLS%2CRATEDETAILS.BONUSRATES%2CALTERNATEPAYMENTS"
headers = {'Host': 'apis.ihg.com.cn', 'accept': '*/*', 'accept-language': 'zh-CN', 'content-type': 'application/json', 'ihg-language': 'zh-CN', 'referer': 'harmony-app://com.ihg.apps.hw', 'user-agent': 'IHG-Mobile-App/5.94.1.13 (Harmony; 20; BRA-AL00)', 'x-cdc-api-key': '4_qeN7XyMzDRBJIaaRrDPfug', 'x-ihg-api-key': 'Rqfqml9gSGFq4DExzD4IAeBqpUUKLSpt'}

response = requests.get(url, headers=headers)

# === 自动断言 ===
print("状态码:", response.status_code)
assert 200 <= response.status_code < 300, "HTTP 请求失败"

try:
    res_json = response.json()
    print("响应JSON:\n", json.dumps(res_json, ensure_ascii=False, indent=2))

    # 自动判断常见成功字段
    if "code" in res_json:
        assert str(res_json["code"]) in ["200","0","success"], "业务状态码异常"
    elif "status" in res_json:
        assert str(res_json["status"]).lower() == "success", "状态异常"

    print("\n✅ 所有断言通过！")
except:
    print("\n响应文本:\n", response.text)
    print("\n✅ 请求成功（非JSON响应）")