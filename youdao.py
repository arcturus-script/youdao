import requests as req


def handler(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)

        msg = [
            {
                "h4": {
                    "content": f"用户名: {res['name']}",
                },
            },
            {
                "h4": {
                    "content": f"账号: {res['account']}",
                },
            },
        ]

        checkin = res["checkin"]

        if checkin["status"]:
            msg.append(
                {
                    "table": {
                        "content": [
                            ("描述", "内容"),
                            ("登录奖励", f"{checkin['reward']}M"),
                            ("连续登录", f"{checkin['continuous_days']}天"),
                            ("总共获得", f"{checkin['total']}M"),
                            ("签到奖励", f"{checkin['checkin']}M"),
                            ("签到共计", f"{checkin['checkin_total']}M"),
                        ]
                    }
                }
            )
        else:
            msg.append(
                {
                    "txt": {
                        "content": checkin["msg"],
                    },
                }
            )

        ad = res["ad"]
        if ad["status"]:
            msg.append(
                {
                    "table": {
                        "content": [
                            ("描述", "内容"),
                            ("广告奖励", f"{ad['ad']}M"),
                            ("广告总计", f"{ad['ad_space_total']}天"),
                        ]
                    }
                }
            )
        else:
            msg.append(
                {
                    "txt": {
                        "content": ad["msg"],
                    },
                }
            )
        
        return msg

    return inner


class Youdao:
    LOGIN_URL = "http://note.youdao.com/login/acc/pe/getsess?product=YNOTE"  # 获取 cookie
    SYNC_URL = "https://note.youdao.com/yws/api/daupromotion?method=sync"  # 登录奖励
    CHECKIN_URL = "https://note.youdao.com/yws/mapi/user?method=checkin"  # 签到奖励
    AD_URL = "https://note.youdao.com/yws/mapi/user?method=adRandomPrompt"  # 广告奖励
    USER_INFO = "https://note.youdao.com/yws/api/self"  # 获取用户信息

    def __init__(self, cookie: str) -> None:
        self.cookies = cookie
        self.headers = {"Cookie": cookie}

    # 获取 cookie
    def login(self):
        cookie = ""
        res = req.get(Youdao.LOGIN_URL, headers=self.headers)

        for key, value in res.cookies.items():
            cookie += f"{key}={value};"
        self.headers = {"Cookie": cookie}
        
        print(f"获取到新 cookie: {cookie}")

    # 登录/签到
    def checkin(self):
        try:
            print("有道云笔记登录...")
            # 登录
            res = req.request("POST", Youdao.SYNC_URL, headers=self.headers).json()

            if "error" not in res:
                # 签到
                print("有道云笔记签到...")
                result = req.request(
                    "POST",
                    Youdao.CHECKIN_URL,
                    headers=self.headers,
                ).json()

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
                resp = req.request("POST", Youdao.AD_URL, headers=self.headers).json()
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

        result = {"account": self.account, "name": self.name}

        checkin = self.checkin()
        result.update({"checkin": checkin})

        if checkin["status"]:
            ad = self.AD()
            result.update({"ad": ad})

        return result

    def get_user_name(self):
        try:
            params = {"method": "get"}
            res = req.get(Youdao.USER_INFO, headers=self.headers, params=params).json()

            self.name = res["name"]
            self.account = res["userId"]

            print(f"获取到用户名: {res['name']}")
        except Exception as ex:
            print(f"获取用户信息时出错, 原因: {ex}")
            self.name = "无"
            self.account = "无"
