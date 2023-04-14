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
                        "contents": [
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
                        "contents": [
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
