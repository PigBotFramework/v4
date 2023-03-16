'''
This is the struct of data
'''
import yaml
# 打开yaml文件
fs = open("data.yaml",encoding="UTF-8")
yamldata = yaml.load(fs,Loader=yaml.FullLoader)

from revChatGPT.V1 import Chatbot
chatbot = Chatbot(config={
    "session_token": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..7Bnl9YHAWKY1RfG2.lmtSXNcmkA5I3XsE7ZcAmztlbymqdhTfEbtZc8BpVgqtA8V44U_7MfF3_VaQYrD7WD_9fPmpIVRfqEiclt8334ULbH3vePF_vYzzJ-LCQ704kAbvCIezY84yWdY30olKQMH2n5ON4FZCUgolqjsboMEYHWSLKKIcoIEmMKbOajKeSU1IZVgV72bJNuSgoyulI89leKoK5F787VWjMC1IPTaC93pReR4PZg1_h9-k7HkfVTebd8NQ_gX9jahnCnpHtaO8gYhRn_mIn5tSXsPufBAIDR5hCQncqKhjLut6d4zPwJCSLFvVXz5mkak-2eQpOa6bwIucWoKHTnnSnHcHlIFtzx9rxbd49Otd7kCl5iJ0_SzsRIPMKQMjigPMjoIbtBeSvgdgEq_dQJpNU9zXVUeSE4-hvxOlhIiWNJJFF-LQUyyTMUI9CtxfulHmSi2gaQhjuhVfasMQHZ4lWW-hqRQ72qn0WrteClsku4RyMj0B9SUXUDo4EFuPq0fO5yyP3vMOJKGqUILLYPei-967qtch5WSnK42czvnpAsYPz2GD_z3spBsReJS_F1RJxN-56LGCrUmZJNVLikeGcx6OYpSZZEj4Ndn0UHJN62uIDsKrfrzRzWI0yPERF1b3zz7YQFl_HY24U3KOIrTFXTRgbdBgypdnVR0k47R-6vGcEDrUTfBxE91LCKan91xMDwFfIVajY3R-ks_iks9eTNKy8bFThBJEEqVbsAqayIqfiuO-i_VSTi2SFf-DMGnQfvvwT-xdzKjOcVgtwhUl3ukXZJbchKOppgXZXH9yMPSST46FcA-pgE9oci5h7aSPFH2TBJJcLoNzt6mjl7UQF6KLFxTVk67FGoROtUfktz3k65WYALe1Q5_di5aihFSBOIQ-DjdS-cJXlDMmd8P2jeKCzrKfPPDxpuEo0cNasm_-g-ljRSK7XGCMJ6QJbtZfzZQVcw42EmlM0aKcrIJVFoXNfcGfhWBcz1ggiiZtZo5iMDL2mWqcKQlinYfpVjTG7zchKLxRbQ7ffNg8vnZ6o7ERr8DAZYXiMjPg4qIcrUfojgkNu6fXnTyOHWWUSYIoMGP_h412Bx6DZaacmPc4JwiffJzi9IKiEDIXmX22hySVIphQdPmqFGAtXfL6X8ASkS1PwfmtD_Cetl_0dDecK8RDxeqIrPKVc3d_srln9egPGmIARHDE6CvOqi_PetwRgJq_hIPIvzDyh5EpUIusfy_qJzgdr1LG0g9Cw0h68rap8ro951J5rTt0qmPxkz209x6wfGgbTtxMhZe57X4t94cNhBeSMhJCq3qweoxmRO7KQd5BHEvgnDaFkarubhrMQyv_Cv0UHimNc524svT_hjbpXWXuadJm-Avz1X3o-A9LX2sBnzmTFaPrDlM_kg74JsuH5OwMdlxv-fhO_GzcQzqY6YHvWqUG3K9B0AwI5GDRZAf4jEB-o5GX7NQaLO3EN-M-j5oEVbeGFP0rTK3KMT4o5X7gqKpuIH5DyLWpN48MkWjskuUV_jAwaHpNcbSbN7PyxrVhNzZ7cm3d24iGL1xUvHdZ3jHioAhVw8I6m1-MW09Exvk_HXBX6Q7Vc22MHyLh-bDIJD3miw28hGmTKsAOzzdNYQkw95F923BjaCElfM75QvrjTQXC5H_HF4JW6_p56eo7z-bD0-H5prPOVw9rwWpgcsKBM87wceaBDENqkeudBQOqY2UHEWUJpabBOIEum5h1yw6nH0mGzXxZHearyGye3k-OeireqCJJC-3tt9NsclKFs0aYhHq0rLMnKSU_FW4vyOBidfftkdarLHOzryPTJMmLo8MBAKtY4sI9vsLCdShMc_gQJ_owU0mfWmj4RtX5rfqilCiyn8guIGeRzK_NrOvfUXRbZ9OtOQhIKaE3temAYMt_nZxVUooVsdMNfYgIX-q-_YsxLIYa4NrznfyWro7I8T4uEV7OE9NAmOTY3XdNqYyl6-CX_llq8xJitNfcoUWJt370gkXRHz8IvVDffRZ1OW176yy1MTKfWtksP7OiGDV5ikZWJbNRByBvLhcuWGg_SBsm8gbIRMUBEoX6FY1aRz1TJZ6hMU4n61sYsGJ_wE05qwKlbNgJwcY8m-Jr4Rya2cHJoY7pKHqwRCPs2zQBJX6wXa3YgWl99bk823lA5C5iItHhw1y2ciOHNw33dGEjKokHhA5GyZUkw8z4L9IeKYa8509ijN_Tjt7SCajTi3vVkLXErMizkV9XSrARXu_AQpF85L2Hvky9xm3h_f9ShC81LZ1Fc7Lw5pGUekzJ0567cHUyaJ40Dig2zoX6eeeoEhPofuq8D-4o3sAx8B46npQYw55CJ4sD2ilZK2yzPuqzcM3NNjG1-e_xtPeaeFPQOzZwXu-sSgLZEBPixwIxghljX54J5nDASBvVkiwKjgRsaZwWgitDeYBYhLIynBmJ8Dh8EDUTQ48B6VxNh4HM9kTz-QQo19ebaPRRmR_bONeC6oHRiqLSqJMSjrh_eSBMP3ZbNMgc-yTD3V4jgdQb6GEM-dO768OWjUjiluJkXj7HhdqvElnG6IyWN3Nekr64CPNVDX4CdqNBpALbu5kYoFksd0Z9O_J6K29nMI7ivEpS-UeZup3QvAv52hCpwlZEQr4Qe3Rz.69XXemVPqisIjsYwFh13HA"
})

def noMap(ob, key: str):
    return ob

def mapDict(ob, key: str):
    obDict = {}
    for i in ob:
        obDict[i.get(key)] = i
    
    return obDict

def mapDoubleDict(ob, key: str):
    first, second = key.split()
    obDict = {}
    for i in ob:
        if (obDict.get(i.get(first)) == None):
            obDict[i.get(first)] = {}
        obDict[i.get(first)][i.get(second)] = i
    return obDict

def mapDictToList(ob, key: str):
    obDict = {}
    for i in ob:
        if (obDict.get(i.get(key)) == None):
            obDict[i.get(key)] = []
        obDict[i.get(key)].append(i)
    
    return obDict


class Struct:
    args: list = []
    messageType: str = 'qn'
    botSettings: dict = {}
    userCoin: int = -1
    userInfo: dict = {}
    pluginsList: list = []
    port: int = 1000
    se: dict = {}
    message: str = ""
    ocrImage: str = ""
    isGlobalBanned: bool = False
    uuid: str = None
    runningProgram: str = "BOT"
    groupSettings: dict = {}

    def set(self, key: str, value):
        setattr(self, key, value)
    
    def get(self, key: str):
        return getattr(self, key, None)

    def __init__(self, **kwargs):
        for i in kwargs:
            exec(f'self.{i} = kwargs.get("{i}")')
    
    def __str__(self):
        return f'<Struct Program:{self.runningProgram} Uuid:{self.uuid}>'

if __name__ == '__main__':
    struct = Struct(runningProgram='az')
    print(str(struct))