import requests as req
from tools import handler

# 获取 cookie
LOGIN_URL = "http://note.youdao.com/login/acc/pe/getsess?product=YNOTE"

# 登录奖励
SYNC_URL = "https://note.youdao.com/yws/api/daupromotion?method=sync"

# 签到奖励
CHECKIN_URL = "https://note.youdao.com/yws/mapi/user?method=checkin"

# 广告奖励
AD_URL = "https://note.youdao.com/yws/mapi/user?method=adRandomPrompt"

# 获取用户信息
USER_INFO = "https://note.youdao.com/yws/api/self"


class Youdao:
    def __init__(self, **config) -> None:
        self.cookies = config.get("cookie")
        self.headers = {"Cookie": self.cookies}

    # 获取 cookie
    def login(self):
        cookie = ""
        res = req.get(LOGIN_URL, headers=self.headers)

        for key, value in res.cookies.items():
            cookie += f"{key}={value};"

        self.headers = {"Cookie": cookie}

        print(f"获取到新 cookie: {cookie}")

    # 登录/签到
    def checkin(self):
        try:
            print("有道云笔记登录...")
            # 登录
            res = req.request("POST", SYNC_URL, headers=self.headers).json()

            if "error" not in res:
                # 签到
                print("有道云笔记签到...")

                result = req.request("POST", CHECKIN_URL, headers=self.headers).json()

                return {
                    "status": True,
                    "msg": "签到成功",
                    "reward": res.get("rewardSpace") / (1024 * 1024),  # 登录奖励
                    "continuous_days": res.get("continuousDays"),  # 连续登录天数
                    "total": res.get("totalRewardSpace") / (1024 * 1024),  # 登录总共获得奖励
                    "checkin": result.get("space") / (1024 * 1024),  # 签到奖励
                    "checkin_total": result.get("total") / (1024 * 1024),  # 签到一共获得
                }

                # 这里应该判断签到是否成功, 但是我懒了...
            else:
                return {
                    "status": False,
                    "msg": "登录奖励获取失败",
                }
        except Exception as exp:
            print(f"登录时出现错误, 原因: {exp}")

            return {
                "status": False,
                "msg": f"出现错误, 原因: {exp}",
            }

    # 看广告
    def AD(self):
        ad = 0
        try:
            print("有道云笔记观看广告...")

            for _ in range(3):
                resp = req.request("POST", AD_URL, headers=self.headers).json()

                ad += resp.get("space")  # 看广告奖励

            return {
                "status": True,
                "msg": "看广告成功",
                "ad_space_total": resp.get("adSpaceTotal") / (1024 * 1024),
                "ad": ad / (1024 * 1024),
            }
        except Exception as exp:
            print(f"看广告时出现错误, 原因: {exp}")

            return {
                "status": False,
                "msg": f"看广告时出现错误, 原因: {exp}",
            }

    @handler
    def start(self):
        self.login()
        self.get_user_name()

        result = {
            "account": self.account,
            "name": self.name,
        }

        checkin = self.checkin()
        result.update({"checkin": checkin})

        if checkin["status"]:
            ad = self.AD()
            result.update({"ad": ad})

        return result

    def get_user_name(self):
        try:
            params = {"method": "get"}

            res = req.get(USER_INFO, headers=self.headers, params=params).json()

            self.name = res["name"]
            self.account = res["userId"]

            print(f"获取到用户名: {res['name']}")

        except Exception as ex:
            print(f"获取用户信息时出错, 原因: {ex}")

            self.name = "Unkown"
            self.account = "Unkown"
